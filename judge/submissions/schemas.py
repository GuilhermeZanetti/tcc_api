from pydantic import BaseModel, Field

from uuid import UUID

from judge.contrib.collection_response import CollectionResponse
from judge.contrib.schemas import Model, OutMixin
from judge.submissions.examples import (
    submission_collection_response_example,
    submission_in_example,
    submission_out_example,
)


class Submission(Model):
    problem_id: UUID = Field(title='Problem id')
    user_id: UUID = Field(title='User id')
    language_type: str = Field(title='Language type')
    content: str = Field(title='Code')
    status: str = Field(title='Status')


class SubmissionIn(BaseModel):
    problem_id: UUID = Field(title='Problem id')
    user_id: UUID = Field(title='User id')
    language_type: str = Field(title='Language type')
    content: str = Field(title='Code')

    class Config:
        json_schema_extra = {'example': submission_in_example}


class SubmissionOut(Submission, OutMixin):
    class Config:
        json_schema_extra = {'example': submission_out_example}


class SubmissionCollectionResponse(CollectionResponse):
    class Config:
        json_schema_extra = {'example': submission_collection_response_example}
