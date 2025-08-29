from fastapi import APIRouter, Depends, HTTPException, status
from src.authentication.schemas import IntegratorAuthRequest, IntegratorAuthResponse
from src.authentication.repositories import IntegratorRepository
from src.authentication.usecases import AuthenticationUseCase
from src.contrib.hash import HashUtils
from src.contrib.repository.mongodb import mongodb_client
from src.contrib.security import gerar_token_integrador

router = APIRouter()

async def get_integrator_repository(mongo_client=Depends(mongodb_client)):
    return IntegratorRepository(mongo_client)

@router.post("/auth/integrator-token", response_model=IntegratorAuthResponse, status_code=status.HTTP_200_OK)
async def authenticate_integrator(
    request: IntegratorAuthRequest,
    use_case: AuthenticationUseCase = Depends()
):
    integrator = await use_case.get_by_hashed_api_key(HashUtils.hash(request.api_key))

    if not integrator or not HashUtils.verify(request.api_key, integrator.hashed_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida ou inativa",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not integrator.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Integrador inativo",
        )

    access_token = gerar_token_integrador(str(integrator.id), integrator.permissions)
    return IntegratorAuthResponse(access_token=access_token)
