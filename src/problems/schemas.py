from pydantic import Field, ConfigDict, BaseModel
from typing import List

from src.contrib.collection_response import CollectionResponse
from src.contrib.schemas import Model, OutMixin

class TestCase(BaseModel):
    input_lines: List[str] = Field(title='List of input lines for the test case', default_factory=list)
    output_lines: List[str] = Field(title='List of expected output lines for the test case', default_factory=list)

class Problem(Model):
    name: str = Field(title='Problem name')
    description: str = Field(title='Problem description')
    test_cases: List[TestCase] = Field(title='List of test cases for the problem', default_factory=list)
    entry_description: str = Field(title='Problem entry description')
    output_description: str = Field(title='Problem output description')


class ProblemIn(Problem):
    pass


class ProblemOut(Problem, OutMixin):
    pass


class ProblemCollectionResponse(CollectionResponse):
    pass

class ProblemUpdate(Model):
    name: str | None = Field(title='Problem name', default=None)
    description: str | None = Field(title='Problem description', default=None)
    test_cases: List[TestCase] | None = Field(title='List of test cases for the problem', default=None)
    entry_description: str | None = Field(title='Problem entry description', default=None)
    output_description: str | None = Field(title='Problem output description', default=None)