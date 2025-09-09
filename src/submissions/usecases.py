import uuid
from datetime import datetime, timezone
import asyncio

from fastapi import Depends
from pydantic import UUID4

from src.contrib.constants import SUPPORTED_LANGUAGES
from src.submissions.models import SubmissionModel
from src.submissions.repositories import SubmissionRepository
from src.problems.repositories import ProblemRepository
from src.contrib.exceptions import ObjectNotFound, ValidationError
from src.contrib.base64 import Base64Utils
from src.contrib.judge import Judge
from src.contrib.queue import queue_manager
from src.submissions.schemas import (
    SubmissionCollectionResponse,
    SubmissionIn,
    SubmissionOut,
)


def sync_process_submission(submission_data: dict, problem_data: dict):
    """Synchronous wrapper for the async process_submission function.

    This function creates a new event loop and runs the async process_submission
    function synchronously.
    """
    from src.submissions.repositories import SubmissionRepository
    from src.contrib.repository.mongodb import db

    async def process():
        repository = SubmissionRepository(db.client)
        judge = Judge(repository=repository)
        submission = SubmissionOut(**submission_data)
        await judge.process_submission(submission, problem_data)

    asyncio.run(process())


class SubmissionUseCase:
    def __init__(
        self,
        repository: SubmissionRepository = Depends(),
        problem_repository: ProblemRepository = Depends(),
    ) -> None:
        self.repository = repository
        self.problem_repository = problem_repository
        self.judge = Judge(repository=repository)

    async def create(self, submission_in: SubmissionIn) -> SubmissionOut:
        problem = await self.problem_repository.get(
            filter={'id': submission_in.problem_id}
        )
        if not problem:
            raise ObjectNotFound()

        if submission_in.language_type not in SUPPORTED_LANGUAGES:
            raise ValidationError(
                message='Invalid language type', field='language_type'
            )

        if not Base64Utils.is_valid(submission_in.content):
            raise ValidationError(
                message='Invalid content, the content must be a valid base64.', field='content'
            )

        submission_model = SubmissionModel(
            id=uuid.uuid4(),
            created_at=datetime.now(timezone.utc),
            status='PENDING',
            **submission_in.model_dump(),
        )

        async with await self.repository.start_transaction() as transaction:
            await self.repository.insert(
                model=submission_model, session=transaction.session
            )

        submission_out = SubmissionOut.model_validate(submission_model)

        queue_manager.enqueue(
            sync_process_submission,
            submission_data=submission_out.model_dump(),
            problem_data=problem,
        )

        return submission_out

    async def get(self, id: UUID4) -> SubmissionOut:
        submission = await self.repository.get(filter={'id': id})

        if not submission:
            raise ObjectNotFound(
                message=f'Object not found on Submissions for id: {id}'
            )

        return SubmissionOut(**submission)

    async def query(self) -> SubmissionCollectionResponse:
        submissions = await self.repository.query()

        return SubmissionCollectionResponse.create(results=submissions)
