from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

class IntegratorCreate(BaseModel):
    name: str = Field(..., description="Nome do integrador externo")
    permissions: List[str] = Field([], description="Lista de permissões/escopos do integrador")

class IntegratorUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Nome do integrador externo")
    is_active: Optional[bool] = Field(None, description="Indica se o integrador está ativo")
    permissions: Optional[List[str]] = Field(None, description="Lista de permissões/escopos do integrador")

class IntegratorResponse(BaseModel):
    id: str = Field(..., description="ID do integrador")
    name: str = Field(..., description="Nome do integrador externo")
    is_active: bool = Field(..., description="Indica se o integrador está ativo")
    permissions: List[str] = Field(..., description="Lista de permissões/escopos do integrador")
    created_at: datetime = Field(..., description="Data de criação do integrador")
    updated_at: datetime = Field(..., description="Data da última atualização do integrador")

    class Config:
        from_attributes = True

class IntegratorAuthRequest(BaseModel):
    api_key: str = Field(..., description="Chave de API do integrador", examples=["57fba00c-aa3d-4009-87d6-700f58a4032b"])

class IntegratorAuthResponse(BaseModel):
    access_token: str = Field(..., description="Token de acesso JWT")
    token_type: str = Field("bearer", description="Tipo do token")
