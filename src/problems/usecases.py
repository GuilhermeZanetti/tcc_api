import uuid
from datetime import datetime, timezone

from fastapi import Depends
from pydantic import UUID4

from src.contrib.exceptions import ObjectNotFound
from src.problems.models import ProblemModel
from src.problems.repositories import ProblemRepository
from src.problems.schemas import (
    ProblemCollectionResponse,
    ProblemIn,
    ProblemOut,
    ProblemUpdate,
)


class ProblemUseCase:
    def __init__(
        self,
        repository: ProblemRepository = Depends(),
    ) -> None:
        self.repository = repository

    async def create(self, problem_in: ProblemIn) -> ProblemOut:
        problem_out = ProblemOut(
            id=str(uuid.uuid4()),
            created_at=datetime.now(timezone.utc),
            **problem_in.model_dump(),
        )

        problem_model = ProblemModel(**problem_out.model_dump())

        async with await self.repository.start_transaction() as transaction:
            await self.repository.insert(
                model=problem_model, session=transaction.session
            )

        return problem_out

    async def get(self, id: UUID4) -> ProblemOut:
        problem = await self.repository.get(filter={'id': id})

        if not problem:
            raise ObjectNotFound(
                message=f'Object not found on Problems for id: {id}'
            )

        return ProblemOut(**problem)

    async def query(self) -> ProblemCollectionResponse:
        problems = await self.repository.query()

        return ProblemCollectionResponse.create(results=problems)

    async def update(self, id: UUID4, problem_in: ProblemUpdate) -> ProblemOut:
        problem = await self.get(id=id)

        problem_updated = problem.model_copy(
            update=problem_in.model_dump(exclude_unset=True)
        )
        problem_updated.updated_at = datetime.now(timezone.utc)

        problem_model = ProblemModel(**problem_updated.model_dump())

        async with await self.repository.start_transaction() as transaction:
            await self.repository.update(
                data=problem_model.model_dump(),
                filter={'id': id},
                session=transaction.session,
            )

        return problem_updated

    async def delete(self, id: UUID4) -> None:
        problem = await self.get(id=id)

        async with await self.repository.start_transaction() as transaction:
            await self.repository.delete(
                filter={'id': problem.id}, session=transaction.session
            )
