from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from uuid import UUID

from src.contrib.collection_response import CollectionResponse
from src.contrib.schemas import Model, OutMixin
from src.submissions.examples import (
    submission_collection_response_example,
    submission_in_example,
    submission_out_example,
)
from src.contrib.constants import (
    STATUS_ACCEPTED, 
    STATUS_PRESENTATION_ERROR, 
    STATUS_WRONG_ANSWER, 
    STATUS_COMPILATION_ERROR, 
    STATUS_TIME_LIMIT_EXCEEDED, 
    STATUS_MEMORY_LIMIT_EXCEEDED, 
    STATUS_RUNTIME_ERROR,
    STATUS_SECURITY_ERROR,
)

class InvalidStatusTransition(Exception):
    """Exceção customizada para transições de status inválidas."""
    pass

class SubmissionStatus(str, Enum):
    """Define os estados possíveis para uma submissão."""
    
 
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    
    
    ACCEPTED = STATUS_ACCEPTED
    PRESENTATION_ERROR = STATUS_PRESENTATION_ERROR
    WRONG_ANSWER = STATUS_WRONG_ANSWER
    COMPILATION_ERROR = STATUS_COMPILATION_ERROR
    TIME_LIMIT_EXCEEDED = STATUS_TIME_LIMIT_EXCEEDED
    MEMORY_LIMIT_EXCEEDED = STATUS_MEMORY_LIMIT_EXCEEDED
    RUNTIME_ERROR = STATUS_RUNTIME_ERROR
    SECURITY_ERROR = STATUS_SECURITY_ERROR


class SubmissionUpdateStatusIn(BaseModel):
    """Schema de entrada para atualizar apenas o status de uma submissão."""
    status: SubmissionStatus = Field(
        title='Status', 
        description='O novo status da submissão. Deve ser um dos valores válidos.',
    )



class Submission(Model):
    problem_id: UUID = Field(title='Problem id')
    language_type: str = Field(title='Language type')
    content: str = Field(title='Code')
    status: str = Field(title='Status')


class SubmissionIn(BaseModel):
    problem_id: UUID = Field(title='Problem id')
    language_type: str = Field(title='Language type')
    content: str = Field(title='Code')

    model_config = ConfigDict(json_schema_extra={'example': submission_in_example})


class SubmissionOut(Submission, OutMixin):
    model_config = ConfigDict(json_schema_extra={'example': submission_out_example})


class SubmissionCollectionResponse(CollectionResponse):
    model_config = ConfigDict(json_schema_extra={'example': submission_collection_response_example})
