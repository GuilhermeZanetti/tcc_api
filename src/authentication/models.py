from datetime import datetime
from typing import List

from pydantic import Field
from src.contrib.models.base import BaseModelMixin

class Integrator(BaseModelMixin):
    name: str = Field(..., description="Nome do integrador externo")
    hashed_api_key: str = Field(..., description="Hash da chave de API do integrador")
    is_active: bool = Field(True, description="Indica se o integrador está ativo")
    permissions: List[str] = Field([], description="Lista de permissões/escopos do integrador")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criação do integrador")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data da última atualização do integrador")

    class Config:
        collection = "authentication"
        indexes = [
            ("hashed_api_key", {"unique": True})
        ]
