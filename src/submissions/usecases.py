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
    SubmissionUpdate,
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

        submission_out = SubmissionOut(
            id=str(uuid.uuid4()),
            created_at=datetime.now(timezone.utc),
            status='PENDING',
            **submission_in.model_dump(),
        )

        submission_model = SubmissionModel(**submission_out.model_dump())

        async with await self.repository.start_transaction() as transaction:
            await self.repository.insert(
                model=submission_model, session=transaction.session
            )

        queue_manager.enqueue(
            sync_process_submission,
            submission_data=submission_out.model_dump(),
            problem_data=problem
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



    async def update(self, id: UUID4, submission_update: SubmissionUpdate) -> SubmissionOut:
        
        submission_data = await self.repository.get(
            filter={'id': id}
        )
        
        print(f'submission_data: {submission_data}')
        
        if not submission_data:
            raise ObjectNotFound()
        
        try:
            submission = SubmissionModel(**submission_data)
            submission.status = submission_update.status
            
            print(f'submission: {submission}')
        
            if submission.language_type not in SUPPORTED_LANGUAGES:
                raise ValidationError(
                    message='Invalid language type', field='language_type'
                )
            
            if not Base64Utils.is_valid(submission.content):
                raise ValidationError(
                    message='Invalid content, the content must be a valid base64.', field='content'
                )
            
            response_update = await self.repository.update(submission.model_dump(), filter={'id': id})
            print(f'response_update: {response_update}')
            if not response_update:
                raise ObjectNotFound()
        except ValidationError as exc:
                    raise ValidationError(
                        message=exc.errors(), field='submission'
                    )
        except Exception as exc:
            raise exc
        
        return SubmissionOut(**submission.model_dump())