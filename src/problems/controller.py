from fastapi import APIRouter, Body, Depends, status, HTTPException
from pydantic import UUID4
from src.contrib.documentation import (
    NotFoundErrorResponse,
    UnprocessableEntityErrorResponse,
    InternalServerErrorResponse,
)
from src.contrib.security import validar_jwt
from src.problems.schemas import (
    ProblemCollectionResponse,
    ProblemIn,
    ProblemOut,
)
from src.problems.usecases import ProblemUseCase
from src.contrib.exceptions import ObjectNotFound


router = APIRouter(tags=['problems'], prefix='/v0/problems', dependencies=[Depends(validar_jwt)])


@router.post(
    '',
    summary='Create a new problem',
    status_code=status.HTTP_201_CREATED,
    response_model=ProblemOut,
    responses={
        201: {'model': ProblemOut},
        404: {'model': NotFoundErrorResponse},
        422: {'model': UnprocessableEntityErrorResponse},
        500: {'model': InternalServerErrorResponse},
    },
)
async def post(
    use_case: ProblemUseCase = Depends(),
    problem_in: ProblemIn = Body(...),
) -> ProblemOut:
    problem = await use_case.create(problem_in=problem_in)

    return problem


@router.get(
    '/{id}',
    summary='Get a Problem by id',
    status_code=status.HTTP_200_OK,
    response_model=ProblemOut,
    responses={
        200: {'model': ProblemOut},
        404: {'model': NotFoundErrorResponse},
        500: {'model': InternalServerErrorResponse},
    },
)
async def get(
    id: UUID4,
    use_case: ProblemUseCase = Depends(),
) -> ProblemOut:
    try:
        problem = await use_case.get(id=id)
    except ObjectNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return problem


@router.get(
    '',
    summary='List problems',
    status_code=status.HTTP_200_OK,
    response_model=ProblemCollectionResponse,
    responses={
        200: {'model': ProblemCollectionResponse},
        500: {'model': InternalServerErrorResponse},
    },
)
async def query(
    use_case: ProblemUseCase = Depends(),
) -> ProblemCollectionResponse:
    problems = await use_case.query()

    return problems
