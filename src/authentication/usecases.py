from typing import Optional
from fastapi import Depends
from src.authentication.models import Integrator
from src.authentication.repositories import IntegratorRepository


class AuthenticationUseCase:
    def __init__(
        self, 
        repository: IntegratorRepository = Depends()
        ) -> None:
        self.repository = repository

    async def get_by_hashed_api_key(self, hashed_api_key: str) -> Optional[Integrator]:
        return await self.repository.query({"hashed_api_key": hashed_api_key})
