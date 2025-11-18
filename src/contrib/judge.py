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
            "csharp": CSharpRunner(),
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

        if not output:
            # Se não houve output e não foi um erro de compilação ou runtime,
            # pode ser um erro silencioso, mas vamos tratá-lo como WA
            # (a menos que a saída esperada também seja vazia).
            if not error:
                # Se o erro for EOF (que filtramos acima), não é falha.
                # Se não for EOF e não tiver output, é estranho.
                pass

        output_decoded = output.decode() if output else ""
        
        # 1. Comparação Estrita (Literal)
        if output_decoded == expected_output:
            print(STATUS_ACCEPTED)
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
    def run(
        self, code: bytes, data_input: str
    ) -> Tuple[Optional[bytes], Optional[bytes]]:
        """Run PHP code."""
        return self._execute(
            "php {0}",
            code,
            data_input,
            settings.TLE_TIMEOUT,
            file_suffix=".php",
        )


class JavaScriptRunner(CodeRunner):
    def run(
        self, code: bytes, data_input: str
    ) -> Tuple[Optional[bytes], Optional[bytes]]:
        """
        Run JavaScript code using Node.js with an I/O wrapper.
        The user's code is expected to be inside a function called 'main'.
        """
        user_code = code.decode() if isinstance(code, bytes) else code

        # O 'data_input' é formatado como um array de strings do JavaScript.
        # As aspas são escapadas para evitar erros de sintaxe.
        input_lines_js_array = (
            "["
            + ",".join(
                f'"{line}"'
                for line in data_input.replace("\\", "\\\\")
                .replace('"', '\\"')
                .splitlines()
            )
            + "]"
        )

        # Wrapper que lê a entrada, chama a função 'main' do usuário e executa o código.
        wrapper_code = f"""
        // --- Judge's Wrapper ---
        // O juiz prepara a entrada de dados para o participante.
        const inputLines = {input_lines_js_array};
        let currentLine = 0;

        // A função 'readline' simula a leitura linha por linha, como em outras linguagens.
        function readline() {{
            return inputLines[currentLine++];
        }}

        // --- User's Code Starts Here ---

        {user_code}

        // --- Judge's Execution ---
        // O juiz chama a função principal do usuário.
        // O participante não precisa se preocupar com I/O assíncrono.
        main();
        """

        # A entrada de dados ('data_input') é vazia, pois já foi injetada no wrapper.
        return self._execute(
            "node {0}",
            wrapper_code.encode(),
            "",
            settings.TLE_TIMEOUT,
            file_suffix=".js",
        )


class GoRunner(CodeRunner):
    def run(
        self, code: bytes, data_input: str
    ) -> Tuple[Optional[bytes], Optional[bytes]]:
        """Run Go code."""
        return self._execute(
            "go run {0}", code, data_input, settings.TLE_TIMEOUT, file_suffix=".go"
        )


class CSharpRunner(CodeRunner):
    def run(self, code: bytes, data_input: str) -> Tuple[Optional[bytes], Optional[bytes]]:
        """Compila e depois executa o código C#."""
        code_str = code.decode() if isinstance(code, bytes) else code
        data_entry = data_input.encode('utf-8')
        
        if re.search(r'static\s+void\s+Main', code_str):
            with tempfile.TemporaryDirectory() as tmp_dir:
                proj_dir = os.path.join(tmp_dir, "App")
                os.makedirs(proj_dir)
                
                # --- Etapa 1: Setup do Projeto ---
                # (dotnet new é rápido, podemos manter)
                subprocess.run(["dotnet", "new", "console", "--output", proj_dir, "--use-program-main"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                
                code_path = os.path.join(proj_dir, "Program.cs")
                with open(code_path, "w") as f:
                    f.write(code_str)
                
                # --- Etapa 2: Compilar (dotnet build) ---
                build_command = f"dotnet build --nologo --property:NoWarn=CS* --property:WarningsAsErrors=false --project {proj_dir}"
                build_process = subprocess.Popen(
                    build_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True,
                )
                _build_stdout, build_stderr = build_process.communicate()
                
                if build_process.returncode != 0:
                    return (None, f"COMPILATION_ERROR:\n{build_stderr.decode()}".encode())

                # --- Etapa 3: Executar (dotnet run) ---
                # O 'dotnet run' pode recompilar, mas como já buildamos, será rápido
                # e ele garantirá a execução.
                run_command = f"dotnet run --nologo --project {proj_dir}"
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
        else:
            # Lógica para dotnet-script (interpretado, não precisa separar)
            return self._execute("dotnet-script {0} --no-logo 2>&1 | grep -v 'warning CS'", code, data_input, settings.TLE_TIMEOUT, file_suffix='.cs')