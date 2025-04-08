import uuid
from datetime import datetime, timezone

from fastapi import Depends, BackgroundTasks
from pydantic import UUID4

from judge.contrib.constants import SUPPORTED_LANGUAGES
from judge.submissions.models import SubmissionModel
from judge.submissions.repositories import SubmissionRepository
from judge.problems.repositories import ProblemRepository
from judge.contrib.exceptions import ObjectNotFound, ValidationError
from judge.contrib.base64 import Base64Utils
from judge.contrib.judge import Judge
from judge.submissions.schemas import (
    SubmissionCollectionResponse,
    SubmissionIn,
    SubmissionOut,
)


class SubmissionUseCase:
    def __init__(
        self,
        repository: SubmissionRepository = Depends(),
        problem_repository: ProblemRepository = Depends(),
    ) -> None:
        self.repository = repository
        self.problem_repository = problem_repository
        self.judge = Judge(repository=repository)

    async def create(self, submission_in: SubmissionIn, background_tasks: BackgroundTasks) -> SubmissionOut:
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

        background_tasks.add_task(self.judge.process_submission, submission=submission_out, data=problem)

        return submission_out

    async def get(self, id: UUID4) -> SubmissionOut:
        submission = await self.repository.get(filter={'id': id})

        if not submission:
            raise ObjectNotFound(
                message=f'Object not found on Submissions for id: {id}'
            )

        return SubmissionOut(**submission)
    
    
    async def get_by_user_id(self, user_id: UUID4) -> SubmissionCollectionResponse:
        submissions = await self.repository.query(filter={'user_id': user_id})

        return SubmissionCollectionResponse.create(results=submissions)

    async def query(self) -> SubmissionCollectionResponse:
        submissions = await self.repository.query()

        return SubmissionCollectionResponse.create(results=submissions)
