from typing import Optional
from fastapi import Depends
from src.authentication.models import IntegratorModel
from src.authentication.repositories import IntegratorRepository


class AuthenticationUseCase:
    def __init__(
        self, 
        repository: IntegratorRepository = Depends()
        ) -> None:
        self.repository = repository

    async def get_by_hashed_api_key(self, hashed_api_key: str) -> Optional[IntegratorModel]:
        integrator_data = await self.repository.get({"hashed_api_key": hashed_api_key})
        if integrator_data:
            return IntegratorModel(**integrator_data)
        return None
