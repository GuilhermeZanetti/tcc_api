from datetime import datetime, timezone
from typing import List

from pydantic import UUID4, BaseModel, Field
from src.contrib.models.base import BaseModelMixin

class IntegratorModel(BaseModel):
    id: UUID4 = Field(..., alias="_id", title='Identifier id') 
    name: str = Field(..., description="Nome do integrador externo")
    hashed_api_key: str = Field(..., description="Hash da chave de API do integrador")
    is_active: bool = Field(True, description="Indica se o integrador está ativo")
    permissions: List[str] = Field([], description="Lista de permissões/escopos do integrador")
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc), description="Data de criação do integrador")
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc), description="Data da última atualização do integrador")

    class Config:
        collection = "authentication"
        populate_by_name = True
        indexes = [
            ("hashed_api_key", {"unique": True})
        ]
