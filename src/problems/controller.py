from fastapi import APIRouter, Body, Depends, status, HTTPException
from pydantic import UUID4
from src.authentication.permissions import Permissions
from src.contrib.documentation import (
    NotFoundErrorResponse,
    UnprocessableEntityErrorResponse,
    InternalServerErrorResponse,
)
from src.contrib.security import validar_jwt_integrador
from src.problems.schemas import (
    ProblemCollectionResponse,
    ProblemIn,
    ProblemOut,
    ProblemUpdate,
)
from src.problems.usecases import ProblemUseCase
from src.contrib.exceptions import ObjectNotFound


router = APIRouter(tags=['problems'], prefix='/v0/problems')


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
    dependencies=[Depends(validar_jwt_integrador([Permissions.CREATE_PROBLEMS.value]))]
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
    dependencies=[Depends(validar_jwt_integrador([Permissions.READ_PROBLEMS.value]))]
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


@router.put(
    '/{id}',
    summary='Update a Problem by id',
    status_code=status.HTTP_200_OK,
    response_model=ProblemOut,
    responses={
        200: {'model': ProblemOut},
        404: {'model': NotFoundErrorResponse},
        500: {'model': InternalServerErrorResponse},
    },
    dependencies=[Depends(validar_jwt_integrador([Permissions.UPDATE_PROBLEMS.value]))]
)
async def put(
    id: UUID4,
    use_case: ProblemUseCase = Depends(),
    problem_in: ProblemUpdate = Body(...),
) -> ProblemOut:
    try:
        problem = await use_case.update(id=id, problem_in=problem_in)
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
    dependencies=[Depends(validar_jwt_integrador([Permissions.READ_PROBLEMS.value]))]
)
async def query(
    use_case: ProblemUseCase = Depends(),
) -> ProblemCollectionResponse:
    problems = await use_case.query()

    return problems

@router.delete(
    '/{id}',
    summary='Delete a Problem by id',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Problem deleted successfully'},
        404: {'model': NotFoundErrorResponse},
        500: {'model': InternalServerErrorResponse},
    },
)
async def delete(
    id: UUID4,
    use_case: ProblemUseCase = Depends(),
) -> None:
    try:
        await use_case.delete(id=id)
    except ObjectNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
