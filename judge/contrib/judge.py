import subprocess
import tempfile
from uuid import UUID

from judge.submissions.repositories import SubmissionRepository
from judge.submissions.schemas import SubmissionOut
from judge.config import settings
from judge.contrib.base64 import Base64Utils
from judge.contrib.constants import (
    STATUS_TIME_LIMIT_EXCEEDED,
    STATUS_COMPILATION_ERROR,
    STATUS_ACCEPTED,
    STATUS_PRESENTATION_ERROR,
    STATUS_WRONG_ANSWER,
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

        try:
            code = Base64Utils.decode(submission.content)
            response = runner.run(code, data['data_entry'])
            expected_output = self._decode_output(data['data_output'])
            status = self._evaluate(response, expected_output)
        except ValueError as ve:
            status = STATUS_COMPILATION_ERROR
            print(f"Compilation error: {ve}")
        
        await self._update_submission_status(submission.id, status)

    def _get_runner(self, language_type: str):
        """
        Return the appropriate runner for the given language type.
        """
        runners = {
            'py': PythonRunner(),
            'c': CRunner(),
            'cpp': CppRunner(),
        }
        return runners.get(language_type)

    def _decode_output(self, encoded_output: str) -> str:
        """Decode the expected output from Base64 encoding."""
        return Base64Utils.decode(encoded_output).decode('unicode_escape')

    def _evaluate(self, response, expected_output: str) -> str:
        """Evaluate the response and return the corresponding status."""
        output, error = response if response != "TLE" else (None, None)

        if response == "TLE":
            return STATUS_TIME_LIMIT_EXCEEDED
        if not output:
            return STATUS_COMPILATION_ERROR
        output_decoded = output.decode()
        if expected_output == output_decoded:
            return STATUS_ACCEPTED
        if (
            output_decoded.replace('\n', '') == expected_output.replace('\n', '')
            and output_decoded.count('\n') != expected_output.count('\n')
        ):
            return STATUS_PRESENTATION_ERROR
        return STATUS_WRONG_ANSWER

    async def _update_submission_status(self, submission_id: UUID, status: str):
        """Update the submission status in the repository."""
        await self.repository.update(data={'status': status}, filter={'id': submission_id})


class CodeRunner:
    def run(self, code: bytes, data_input: str):
        """Run the code with the given input. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement 'run' method")

    def _execute(self, command_template: str, code: bytes, data_input: str, timeout: int):
        """
        Execute the given command with the provided code and input, returning the output or timeout status.
        """
        data_entry = Base64Utils.decode(data_input)
        with tempfile.NamedTemporaryFile() as tmp_file:
            tmp_file.write(code if isinstance(code, bytes) else code.encode('utf-8'))
            tmp_file.flush()
            command = command_template.format(tmp_file.name)

            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            try:
                return process.communicate(data_entry, timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                return "TLE", None


class PythonRunner(CodeRunner):
    def run(self, code: bytes, data_input: str):
        """Run Python code."""
        return self._execute("python {0}", code, data_input, settings.TLE_TIMEOUT)


class CRunner(CodeRunner):
    def run(self, code: bytes, data_input: str):
        """Run C code."""
        return self._execute("gcc -o {0}_exec {0} -lm && {0}_exec && rm {0}_exec", code, data_input, settings.TLE_TIMEOUT)


class CppRunner(CodeRunner):
    def run(self, code: bytes, data_input: str):
        """Run C++ code."""
        return self._execute("g++ -o {0}_exec {0} -lm && {0}_exec && rm {0}_exec", code, data_input, settings.TLE_TIMEOUT)
