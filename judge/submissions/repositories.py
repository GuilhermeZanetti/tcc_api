from fastapi import Depends
from motor.core import AgnosticClient

from judge.contrib.repository.base import Repository
from judge.contrib.repository.mongodb import mongodb_client


class SubmissionRepository(Repository):
    def __init__(
        self, client: AgnosticClient = Depends(mongodb_client)
    ) -> None:
        self.client = client

    storage_name: str = 'submissions'

