from fastapi import APIRouter, Body, Depends, status, HTTPException
from pydantic import UUID4
from src.contrib.documentation import (
    ConflictErrorResponse,
    NotFoundErrorResponse,
    UnprocessableEntityErrorResponse,
    InternalServerErrorResponse,
)
from src.submissions.schemas import (
    SubmissionCollectionResponse,
    SubmissionIn,
    SubmissionOut,
    SubmissionUpdate,
)
from src.submissions.usecases import SubmissionUseCase
from src.contrib.exceptions import ObjectNotFound, ValidationError


router = APIRouter(tags=['submissions'], prefix='/v0/submissions')


@router.post(
    '',
    summary='Create a new submission',
    status_code=status.HTTP_201_CREATED,
    response_model=SubmissionOut,
    responses={
        201: {'model': SubmissionOut},
        404: {'model': NotFoundErrorResponse},
        409: {'model': ConflictErrorResponse},
        422: {'model': UnprocessableEntityErrorResponse},
        500: {'model': InternalServerErrorResponse},
    },
)
async def post(
    use_case: SubmissionUseCase = Depends(),
    submission_in: SubmissionIn = Body(...),
) -> SubmissionOut:
    try:
        submission = await use_case.create(submission_in=submission_in)
    except ObjectNotFound:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Problem with {submission_in.problem_id} id does not exist',
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(),
        )

    return submission


@router.get(
    '/{id}',
    summary='Get a Submission by id',
    status_code=status.HTTP_200_OK,
    response_model=SubmissionOut,
    responses={
        200: {'model': SubmissionOut},
        404: {'model': NotFoundErrorResponse},
        500: {'model': InternalServerErrorResponse},
    },
)
async def get(
    id: UUID4,
    use_case: SubmissionUseCase = Depends(),
) -> SubmissionOut:
    try:
        submission = await use_case.get(id=id)
    except ObjectNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return submission


@router.get(
    '',
    summary='List submissions',
    status_code=status.HTTP_200_OK,
    response_model=SubmissionCollectionResponse,
    responses={
        200: {'model': SubmissionCollectionResponse},
        500: {'model': InternalServerErrorResponse},
    },
)
async def query(
    use_case: SubmissionUseCase = Depends(),
) -> SubmissionCollectionResponse:
    submissions = await use_case.query()

    return submissions


@router.put(
    '/{id}',
    summary='Update a Submission by id',
    status_code=status.HTTP_200_OK,
    response_model=SubmissionOut,
    responses={
        200: {'model': SubmissionOut},
        404: {'model': NotFoundErrorResponse},
        422: {'model': UnprocessableEntityErrorResponse},
        500: {'model': InternalServerErrorResponse},
    },
)
async def update(
    id: UUID4,
    submission_update: SubmissionUpdate = Body(...),
    use_case: SubmissionUseCase = Depends(),
) -> SubmissionOut:
    try:
        submission = await use_case.update(id=id, submission_update=submission_update)
    except ObjectNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Submission with id {id} does not exist',
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(),
        )

    return submission
