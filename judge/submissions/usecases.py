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
    SubmissionUpdate,
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
        # Certifique-se de buscar os dados mais recentes do banco de dados
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
