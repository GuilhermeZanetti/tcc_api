from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    detail: str = Field(description='Detail')


class NotFoundErrorResponse(ErrorResponse):
    detail: str = 'Not Found'


class ConflictErrorResponse(ErrorResponse):
    detail: str = 'Conflict'


class UnprocessableEntityErrorResponse(ErrorResponse):
    detail: str = 'Unprocessable Entity'


class InternalServerErrorResponse(ErrorResponse):
    detail: str = 'Internal Server Error'

class ForbiddenErrorResponse(ErrorResponse):
    detail: str = 'Forbidden'
    
    
class ValidationErrorResponse(ErrorResponse):
    detail: str = 'Validation Error'
    errors: list[dict] = Field(description='List of validation errors')