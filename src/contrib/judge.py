import os
import subprocess
import tempfile
import re
from uuid import UUID
from typing import List, Tuple, Dict, Optional
from src.submissions.repositories import SubmissionRepository
from src.submissions.schemas import SubmissionOut
from src.config import settings
from src.contrib.base64 import Base64Utils
from src.contrib.constants import (
    STATUS_TIME_LIMIT_EXCEEDED,
    STATUS_COMPILATION_ERROR,
    STATUS_ACCEPTED,
    STATUS_PRESENTATION_ERROR,
    STATUS_WRONG_ANSWER,
    STATUS_MEMORY_LIMIT_EXCEEDED,
    STATUS_RUNTIME_ERROR,
    STATUS_SECURITY_ERROR,
)


class Judge:
    def __init__(self, repository: SubmissionRepository) -> None:
        """Initialize the Judge class with a repository."""
        self.repository = repository

    async def process_submission(self, submission: SubmissionOut, data: dict):
        """
        Process a submission by decoding the content, running the code, and evaluating the result.
        """
        runner = self._get_runner(submission.language_type)
        if not runner:
            raise ValueError(f"Unsupported language type: {submission.language_type}")

        print(f"\n=====================================")
        print(f" Rodando submission: {submission.id}")
        print(f" Linguagem: {submission.language_type}")

        code = Base64Utils.decode(submission.content)

        test_cases = data.get("test_cases", [])
        results = []

        for test_case in test_cases:
            try:
                input_str = "\n".join(test_case.get("input_lines", []))
                expected_output_str = "\n".join(test_case.get("output_lines", []))

                response = runner.run(code, input_str)
                print(f"\nResponse: {response}")

                status = self._evaluate(response, expected_output_str)
                results.append(status)

                if status != STATUS_ACCEPTED:
                    break
            except Exception as e:
                print(e)
                results.append(STATUS_COMPILATION_ERROR)
                break

        final_status = (
            min(results, key=lambda x: self._get_status_priority(x))
            if results
            else STATUS_COMPILATION_ERROR
        )
        await self._update_submission_status(submission.id, final_status)

    def _get_runner(self, language_type: str):
        """
        Return the appropriate runner for the given language type.
        """
        runners = {
            "py": PythonRunner(),
            "c": CRunner(),
            "cpp": CppRunner(),
            "java": JavaRunner(),
            "php": PHPRunner(),
            "js": JavaScriptRunner(),
            "go": GoRunner(),
            "cs": CSharpRunner(),
        }
        return runners.get(language_type)

    def _is_code_safe(self, code: str) -> bool:
        """
        Check if the code is safe to execute.
        """
        dangerous_patterns = [
            r"import\s+os",
            r"import\s+subprocess",
            r"import\s+sys",
            r"__import__",
            r"eval\(",
            r"exec\(",
            r"open\(",
            r"file\(",
            r"system\(",
            r"popen\(",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return False

        return True

    def _get_status_priority(self, status: str) -> int:
        """
        Get the priority of a status. Lower number means higher priority (worse result).
        """
        priorities = {
            STATUS_ACCEPTED: 5,
            STATUS_PRESENTATION_ERROR: 4,
            STATUS_WRONG_ANSWER: 3,
            STATUS_TIME_LIMIT_EXCEEDED: 2,
            STATUS_MEMORY_LIMIT_EXCEEDED: 2,
            STATUS_RUNTIME_ERROR: 1,
            STATUS_COMPILATION_ERROR: 1,
            STATUS_SECURITY_ERROR: 0,
        }
        return priorities.get(status, 0)

    def _evaluate(self, response: Tuple[Optional[bytes], Optional[bytes]], expected_output: str) -> str:
        """
        Evaluate the response and return the corresponding status.
        """
        output, error = response if response != "TLE" else (None, None)

        if response == "TLE" or output == "TLE":
            print(STATUS_TIME_LIMIT_EXCEEDED)
            return STATUS_TIME_LIMIT_EXCEEDED

        if error:
            error_str = error.decode()
            
            # --- NOVA CHECAGEM DE COMPILATION ERROR ---
            # 1. Verifica CE explícito das linguagens compiladas
            if error_str.startswith("COMPILATION_ERROR:"):
                print(f"Compilation Error:\t{error_str}")
                return STATUS_COMPILATION_ERROR
            
            # 2. Verifica CE de linguagens interpretadas (ex: Python)
            if "SyntaxError:" in error_str:
                print(f"Compilation Error (SyntaxError):\t{error_str}")
                return STATUS_COMPILATION_ERROR
            # --- FIM DA NOVA CHECAGEM ---

            if "EOFError: EOF when reading a line" not in error_str:
                if "MemoryError" in error_str or "out of memory" in error_str:
                    return STATUS_MEMORY_LIMIT_EXCEEDED
                
                print(f"Runtime Error:\t{error_str}")
                return STATUS_RUNTIME_ERROR

        # 3. Verifica se NÃO há output.
            # Se output for None, "not output" é Verdadeiro.
        if not output:
            # 4. Verifica se NÃO há erro.
            # Se error for None, "not error" é Verdadeiro.
            if not error:
                # Conclusão: Sem saída e sem erro de runtime explícito = Erro de Compilação.
                return STATUS_COMPILATION_ERROR

        output_decoded = output.decode() if output else ""
        
        # 1. Comparação Estrita (Literal)
        if output_decoded == expected_output:
            print(f'{STATUS_ACCEPTED} com Literal')
            return STATUS_ACCEPTED

        # 2. Normalização para Presentation Error (PE)
        def normalize_string(s: str) -> str:
            s_normalized = s.replace('\r\n', '\n').replace('\r', '\n')
            lines = [line.rstrip() for line in s_normalized.splitlines()]
            # O .strip() final remove newlines em branco no início ou fim
            return '\n'.join(lines).strip()

        output_normalized = normalize_string(output_decoded)
        expected_normalized = normalize_string(expected_output)

        if output_normalized == expected_normalized:
            print(STATUS_PRESENTATION_ERROR)
            return STATUS_PRESENTATION_ERROR

        # 3. Verificação de Case-Insensitive (se aplicável)
        if not settings.CASE_SENSITIVE:
            if output_normalized.lower() == expected_normalized.lower():
                print(f'{STATUS_ACCEPTED} com Case-Insensitive')
                return STATUS_ACCEPTED

        # 4. Se tudo falhar, é Wrong Answer
        print("--- FINAL EXPECTED ---\n", repr(expected_normalized))
        print("--- FINAL DECODED ----\n", repr(output_normalized))
        return STATUS_WRONG_ANSWER

    async def _update_submission_status(self, submission_id: UUID, status: str):
        """Update the submission status in the repository."""
        await self.repository.update(
            data={"status": status}, filter={"id": submission_id}
        )


class CodeRunner:
    def run(
        self, code: bytes, data_input: str
    ) -> Tuple[Optional[bytes], Optional[bytes]]:
        """Run the code with the given input. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement 'run' method")

    def _execute(
        self,
        command_template: str,
        code: bytes,
        data_input: str,
        timeout: int,
        file_suffix: str = "",
    ) -> Tuple[Optional[bytes], Optional[bytes]]:
        """
        Execute the given command with the provided code and input, returning the output or timeout status.
        """
        data_entry = data_input.encode("utf-8")

        with tempfile.NamedTemporaryFile(suffix=file_suffix, delete=False) as tmp_file:
            tmp_file.write(code if isinstance(code, bytes) else code.encode("utf-8"))
            tmp_file.flush()
            tmp_file_name = tmp_file.name

        command = command_template.format(
            tmp_file_name, tmp_file_name.rsplit(".", 1)[0]
        )

        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )

        try:
            output, error = process.communicate(data_entry, timeout=timeout)
            return output, error

        except subprocess.TimeoutExpired:
            process.kill()
            return "TLE", None
        except Exception as e:
            return None, str(e).encode()
        finally:
            try:
                os.remove(tmp_file_name)
            except Exception:
                pass


class PythonRunner(CodeRunner):
    def run(
        self, code: bytes, data_input: str
    ) -> Tuple[Optional[bytes], Optional[bytes]]:
        """Run Python code."""
        print(" \nRodando Python Runner!! \n")
        return self._execute(
            "python -u {0}",
            code,
            data_input,
            settings.TLE_TIMEOUT,
            file_suffix=".py",
        )

class CRunner(CodeRunner):
    def run(self, code: bytes, data_input: str) -> Tuple[Optional[bytes], Optional[bytes]]:
        """Compila e depois executa o código C."""
        data_entry = data_input.encode('utf-8')

        with tempfile.NamedTemporaryFile(suffix=".c", delete=False) as tmp_file:
            tmp_file.write(code if isinstance(code, bytes) else code.encode('utf-8'))
            tmp_file.flush()
            tmp_file_name = tmp_file.name
        
        exec_name = f"{tmp_file_name.rsplit('.', 1)[0]}_exec"
        compile_command = f"gcc -o {exec_name} {tmp_file_name} -lm"
        
        # --- Etapa 1: Compilar ---
        compile_process = subprocess.Popen(
            compile_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )
        _compile_stdout, compile_stderr = compile_process.communicate()
        
        # --- Etapa 2: Checar Erro de Compilação ---
        if compile_process.returncode != 0:
            try:
                os.remove(tmp_file_name)
            except Exception:
                pass
            # Retorna um erro específico que _evaluate irá capturar
            return (None, f"COMPILATION_ERROR:\n{compile_stderr.decode()}".encode())

        # --- Etapa 3: Executar ---
        run_command = f"{exec_name}"
        run_process = subprocess.Popen(
            run_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )

        try:
            output, error = run_process.communicate(data_entry, timeout=settings.TLE_TIMEOUT)
            return output, error

        except subprocess.TimeoutExpired:
            run_process.kill()
            return "TLE", None
        except Exception as e:
            return None, str(e).encode()
        finally:
            # --- Etapa 4: Limpeza ---
            try:
                os.remove(tmp_file_name)
                os.remove(exec_name)
            except Exception:
                pass


class CppRunner(CodeRunner):
    def run(self, code: bytes, data_input: str) -> Tuple[Optional[bytes], Optional[bytes]]:
        """Compila e depois executa o código C++."""
        data_entry = data_input.encode('utf-8')

        with tempfile.NamedTemporaryFile(suffix=".cpp", delete=False) as tmp_file:
            tmp_file.write(code if isinstance(code, bytes) else code.encode('utf-8'))
            tmp_file.flush()
            tmp_file_name = tmp_file.name
        
        exec_name = f"{tmp_file_name.rsplit('.', 1)[0]}_exec"
        compile_command = f"g++ -o {exec_name} {tmp_file_name} -lm"
        
        # --- Etapa 1: Compilar ---
        compile_process = subprocess.Popen(
            compile_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )
        _compile_stdout, compile_stderr = compile_process.communicate()
        
        # --- Etapa 2: Checar Erro de Compilação ---
        if compile_process.returncode != 0:
            try:
                os.remove(tmp_file_name)
            except Exception:
                pass
            return (None, f"COMPILATION_ERROR:\n{compile_stderr.decode()}".encode())

        # --- Etapa 3: Executar ---
        run_command = f"{exec_name}"
        run_process = subprocess.Popen(
            run_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )

        try:
            output, error = run_process.communicate(data_entry, timeout=settings.TLE_TIMEOUT)
            return output, error

        except subprocess.TimeoutExpired:
            run_process.kill()
            return "TLE", None
        except Exception as e:
            return None, str(e).encode()
        finally:
            # --- Etapa 4: Limpeza ---
            try:
                os.remove(tmp_file_name)
                os.remove(exec_name)
            except Exception:
                pass


class JavaRunner(CodeRunner):
    def run(self, code: bytes, data_input: str) -> Tuple[Optional[bytes], Optional[bytes]]:
        """Compila e depois executa o código Java."""
        code_str = code.decode() if isinstance(code, bytes) else code
        match = re.search(r'public\s+class\s+([A-Za-z_][A-Za-z0-9_]*)', code_str)
        class_name = match.group(1) if match else "Main"
        file_name = f"{class_name}.java"

        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = os.path.join(tmp_dir, file_name)
            with open(file_path, "w") as f:
                f.write(code_str)
            
            # --- Etapa 1: Compilar ---
            compile_command = f"javac {file_path}"
            compile_process = subprocess.Popen(
                compile_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            _compile_stdout, compile_stderr = compile_process.communicate()

            # --- Etapa 2: Checar Erro de Compilação ---
            if compile_process.returncode != 0:
                return (None, f"COMPILATION_ERROR:\n{compile_stderr.decode()}".encode())

            # --- Etapa 3: Executar ---
            run_command = f"java -cp {tmp_dir} {class_name}"
            run_process = subprocess.Popen(
                run_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            
            data_entry = data_input.encode('utf-8')
            try:
                output, error = run_process.communicate(data_entry, timeout=settings.TLE_TIMEOUT)
                return output, error
            except subprocess.TimeoutExpired:
                run_process.kill()
                return "TLE", None
            except Exception as e:
                return None, str(e).encode()


class PHPRunner(CodeRunner):
    def run(self, code: bytes, data_input: str) -> Tuple[Optional[bytes], Optional[bytes]]:
        """Verifica a sintaxe (Lint) e depois executa código PHP."""
        data_entry = data_input.encode('utf-8')

        # 1. Criar arquivo temporário .php
        with tempfile.NamedTemporaryFile(suffix=".php", delete=False) as tmp_file:
            tmp_file.write(code if isinstance(code, bytes) else code.encode('utf-8'))
            tmp_file.flush()
            tmp_file_name = tmp_file.name
        
        # 2. Etapa de Verificação de Sintaxe (Lint)
        # A flag -l (lint) verifica apenas erros de sintaxe sem executar o código.
        lint_command = f"php -l {tmp_file_name}"
        
        lint_process = subprocess.Popen(
            lint_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )
        # O php -l geralmente envia a mensagem de erro para o STDOUT, não STDERR.
        lint_stdout, lint_stderr = lint_process.communicate()
        
        # Se o código de retorno for diferente de 0, houve erro de sintaxe.
        if lint_process.returncode != 0:
            try:
                os.remove(tmp_file_name)
            except Exception:
                pass
            
            # Combina stdout e stderr para garantir que capturamos a mensagem
            error_msg = (lint_stdout or b"") + (lint_stderr or b"")
            
            # Retorna o prefixo que o _evaluate identifica como CE
            # Removemos o nome do arquivo temporário da mensagem para ficar mais limpo, se desejar
            return (None, f"COMPILATION_ERROR:\n{error_msg.decode()}".encode())

        # 3. Etapa de Execução (Só ocorre se o Lint passar)
        run_command = f"php {tmp_file_name}"
        run_process = subprocess.Popen(
            run_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )

        try:
            output, error = run_process.communicate(data_entry, timeout=settings.TLE_TIMEOUT)
            return output, error

        except subprocess.TimeoutExpired:
            run_process.kill()
            return "TLE", None
        except Exception as e:
            return None, str(e).encode()
        finally:
            # 4. Limpeza
            try:
                os.remove(tmp_file_name)
            except Exception:
                pass

class JavaScriptRunner(CodeRunner):
    def run(self, code: bytes, data_input: str) -> Tuple[Optional[bytes], Optional[bytes]]:
        """Run JavaScript code using Node.js."""
        return self._execute("node {0}", code, data_input, settings.TLE_TIMEOUT, file_suffix=".js")


class GoRunner(CodeRunner):
    def run(self, code: bytes, data_input: str) -> Tuple[Optional[bytes], Optional[bytes]]:
        """Compila e depois executa código Go."""
        data_entry = data_input.encode('utf-8')

        # 1. Criar arquivo temporário .go
        with tempfile.NamedTemporaryFile(suffix=".go", delete=False) as tmp_file:
            tmp_file.write(code if isinstance(code, bytes) else code.encode('utf-8'))
            tmp_file.flush()
            tmp_file_name = tmp_file.name
        
        # Definir nome do executável de saída
        exec_name = f"{tmp_file_name.rsplit('.', 1)[0]}_exec"
        
        # 2. Etapa de Compilação (go build)
        # O flag -o define o nome do arquivo de saída
        compile_command = f"go build -o {exec_name} {tmp_file_name}"
        
        compile_process = subprocess.Popen(
            compile_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )
        _compile_stdout, compile_stderr = compile_process.communicate()
        
        # 3. Checar Erro de Compilação
        if compile_process.returncode != 0:
            # Limpar arquivo fonte
            try:
                os.remove(tmp_file_name)
            except Exception:
                pass
            
            # Retorna o prefixo mágico que o _evaluate espera
            return (None, f"COMPILATION_ERROR:\n{compile_stderr.decode()}".encode())

        # 4. Etapa de Execução (Rodar o binário gerado)
        run_command = f"{exec_name}"
        run_process = subprocess.Popen(
            run_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )

        try:
            output, error = run_process.communicate(data_entry, timeout=settings.TLE_TIMEOUT)
            return output, error

        except subprocess.TimeoutExpired:
            run_process.kill()
            return "TLE", None
        except Exception as e:
            return None, str(e).encode()
        finally:
            # 5. Limpeza (remover fonte e binário)
            try:
                os.remove(tmp_file_name)
                if os.path.exists(exec_name):
                    os.remove(exec_name)
            except Exception:
                pass


class CSharpRunner(CodeRunner):
    def run(self, code: bytes, data_input: str) -> Tuple[Optional[bytes], Optional[bytes]]:
        """Run C# code. Compiles using 'dotnet build' and then runs the executable."""
        code_str = code.decode() if isinstance(code, bytes) else code
        
        # Verifica se é um programa completo (com Main) ou script
        if re.search(r'static\s+void\s+Main', code_str):
            with tempfile.TemporaryDirectory() as tmp_dir:
                proj_dir = os.path.join(tmp_dir, "App")
                os.makedirs(proj_dir)
                
                # 1. Cria o Projeto
                try:
                    subprocess.run(
                        ["dotnet", "new", "console", "--output", proj_dir, "--use-program-main"], 
                        check=True, 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL
                    )
                except subprocess.CalledProcessError:
                    return None, None

                # 2. Escreve o Código do Usuário
                code_path = os.path.join(proj_dir, "Program.cs")
                with open(code_path, "w") as f:
                    f.write(code_str)
                
                # 3. Compila o Projeto (Build Explicito)
                # Usamos --nologo e -v quiet para limpar a saída
                build_cmd = ["dotnet", "build", proj_dir, "--configuration", "Release", "--nologo", "-v", "quiet"]
                build_process = subprocess.run(
                    build_cmd,
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE
                )
                
                # Se o build falhar (exit code != 0), retornamos None, None -> COMPILATION_ERROR
                if build_process.returncode != 0:
                    return None, None

                # 4. Executa o Binário Gerado
                # Caminho padrão do binário no .NET 8.0
                bin_path = os.path.join(proj_dir, "bin", "Release", "net8.0", "App")
                
                # Prepara o comando de execução
                # Se o binário executável não existir (Linux às vezes gera apenas a DLL dependendo do ambiente),
                # rodamos via 'dotnet App.dll'
                if not os.path.exists(bin_path):
                     bin_dll = os.path.join(proj_dir, "bin", "Release", "net8.0", "App.dll")
                     command = f"dotnet {bin_dll}"
                else:
                     command = bin_path

                # --- EXECUÇÃO DIRETA (Corrigindo o erro de permissão) ---
                # Aqui chamamos o subprocess diretamente em vez de usar self._execute
                data_entry = data_input.encode('utf-8')
                process = subprocess.Popen(
                    command,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True,
                )

                try:
                    output, error = process.communicate(data_entry, timeout=settings.TLE_TIMEOUT)
                    return output, error
                except subprocess.TimeoutExpired:
                    process.kill()
                    return "TLE", None
                except Exception as e:
                    return None, str(e).encode()
        else:
            # Mantém o suporte a Scripts (dotnet-script)
            return self._execute("dotnet-script {0} --no-logo 2>&1 | grep -v 'warning CS'", code, data_input, settings.TLE_TIMEOUT, file_suffix='.cs')