from typing import Optional

from src.authentication.models import IntegratorModel
from fastapi import Depends
from motor.core import AgnosticClient

from src.contrib.repository.base import Repository
from src.contrib.repository.mongodb import mongodb_client


class IntegratorRepository(Repository):
    def __init__(
        self, 
        client: AgnosticClient = Depends(mongodb_client)
    ) -> None:
        self.client = client

    storage_name: str = 'authentication'

