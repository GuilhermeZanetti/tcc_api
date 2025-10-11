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

        code = Base64Utils.decode(submission.content)

        test_cases = data.get("test_cases", [])
        results = []

        for test_case in test_cases:
            input_str = "\n".join(test_case.get("input_lines", []))
            expected_output_str = "\n".join(test_case.get("output_lines", []))

            response = runner.run(code, input_str)
            status = self._evaluate(response, expected_output_str)
            results.append(status)

            if status != STATUS_ACCEPTED:
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

    def _evaluate(
        self, response: Tuple[Optional[bytes], Optional[bytes]], expected_output: str
    ) -> str:
        """
        Evaluate the response and return the corresponding status.
        """
        output, error = response if response != "TLE" else (None, None)

        if response == "TLE":
            return STATUS_TIME_LIMIT_EXCEEDED

        if error:
            error_str = error.decode()
            if "EOFError: EOF when reading a line" not in error_str:
                if "MemoryError" in error_str or "out of memory" in error_str:
                    return STATUS_MEMORY_LIMIT_EXCEEDED

                print(f"Runtime Error:\t{error_str}")
                return STATUS_RUNTIME_ERROR

        if not output:
            # Se o erro for EOF não consideramos como falha.
            if not error:
                return STATUS_COMPILATION_ERROR

        output_decoded = output.decode() if output else ""

        if settings.IGNORE_TRAILING_WHITESPACE:
            output_decoded = "\n".join(
                line.rstrip() for line in output_decoded.splitlines()
            )
            expected_output = "\n".join(
                line.rstrip() for line in expected_output.splitlines()
            )

        if settings.IGNORE_EMPTY_LINES:
            output_decoded = "\n".join(
                line for line in output_decoded.splitlines() if line.strip()
            )
            expected_output = "\n".join(
                line for line in expected_output.splitlines() if line.strip()
            )

        if not settings.CASE_SENSITIVE:
            output_decoded = output_decoded.lower()
            expected_output = expected_output.lower()

        if output_decoded == expected_output:
            return STATUS_ACCEPTED

        if output_decoded.strip() == expected_output.strip():
            return STATUS_PRESENTATION_ERROR

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
        wrapper_code = f"""import sys
from io import StringIO

# Prepare input data
input_data = '''{data_input}'''
sys.stdin = StringIO(input_data)

# Original code starts here
{code.decode() if isinstance(code, bytes) else code}"""

        # Pass an empty string for data_input to _execute, as it's handled in the wrapper.
        return self._execute(
            "python -u {0}", wrapper_code.encode(), "", settings.TLE_TIMEOUT
        )


class CRunner(CodeRunner):
    def run(
        self, code: bytes, data_input: str
    ) -> Tuple[Optional[bytes], Optional[bytes]]:
        """Run C code."""
        return self._execute(
            "gcc -o {1}_exec {0} -lm && {1}_exec && rm {1}_exec",
            code,
            data_input,
            settings.TLE_TIMEOUT,
            file_suffix=".c",
        )


class CppRunner(CodeRunner):
    def run(
        self, code: bytes, data_input: str
    ) -> Tuple[Optional[bytes], Optional[bytes]]:
        """Run C++ code."""
        return self._execute(
            "g++ -o {1}_exec {0} -lm && {1}_exec && rm {1}_exec",
            code,
            data_input,
            settings.TLE_TIMEOUT,
            file_suffix=".cpp",
        )


class JavaRunner(CodeRunner):
    def run(
        self, code: bytes, data_input: str
    ) -> Tuple[Optional[bytes], Optional[bytes]]:
        """Run Java code."""
        code_str = code.decode() if isinstance(code, bytes) else code
        match = re.search(r"public\s+class\s+([A-Za-z_][A-Za-z0-9_]*)", code_str)
        class_name = match.group(1) if match else "Main"
        file_name = f"{class_name}.java"

        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = os.path.join(tmp_dir, file_name)
            with open(file_path, "w") as f:
                f.write(code_str)
            command = f"javac {file_path} && java -cp {tmp_dir} {class_name}"
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            data_entry = data_input.encode("utf-8")
            try:
                output, error = process.communicate(
                    data_entry, timeout=settings.TLE_TIMEOUT
                )
                return output, error
            except subprocess.TimeoutExpired:
                process.kill()
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
        """Run JavaScript code using Node.js."""
        return self._execute(
            "node {0}", code, data_input, settings.TLE_TIMEOUT, file_suffix=".js"
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
    def run(
        self, code: bytes, data_input: str
    ) -> Tuple[Optional[bytes], Optional[bytes]]:
        """Run C# code. Detecta se é script (dotnet-script) ou programa tradicional (dotnet run)."""
        code_str = code.decode() if isinstance(code, bytes) else code
        if re.search(r"static\s+void\s+Main", code_str):
            with tempfile.TemporaryDirectory() as tmp_dir:
                proj_dir = os.path.join(tmp_dir, "App")
                os.makedirs(proj_dir)
                subprocess.run(
                    [
                        "dotnet",
                        "new",
                        "console",
                        "--output",
                        proj_dir,
                        "--use-program-main",
                    ],
                    check=True,
                )
                code_path = os.path.join(proj_dir, "Program.cs")
                with open(code_path, "w") as f:
                    f.write(code_str)
                command = f"dotnet run --nologo --property:NoWarn=CS* --property:WarningsAsErrors=false --project {proj_dir}"
                process = subprocess.Popen(
                    command,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True,
                )
                data_entry = data_input.encode("utf-8")
                try:
                    output, error = process.communicate(
                        data_entry, timeout=settings.TLE_TIMEOUT
                    )
                    return output, error
                except subprocess.TimeoutExpired:
                    process.kill()
                    return "TLE", None
                except Exception as e:
                    return None, str(e).encode()
        else:
            return self._execute(
                "dotnet-script {0} --no-logo 2>&1 | grep -v 'warning CS'",
                code,
                data_input,
                settings.TLE_TIMEOUT,
                file_suffix=".cs",
            )
