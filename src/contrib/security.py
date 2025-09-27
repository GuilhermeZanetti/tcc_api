from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.config import settings
from datetime import datetime, timedelta, timezone
import jwt

from src.contrib.constants import AUTH_ALGORITHM, SUB_AUTHORIZE, TOKEN_PAYLOAD

security = HTTPBearer()

def validar_jwt(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.API_KEY_MASTER.get_secret_value(), algorithms=[AUTH_ALGORITHM])
        if payload[TOKEN_PAYLOAD] != SUB_AUTHORIZE:
            raise HTTPException(status_code=403, detail="Token inválido")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Token inválido")

def gerar_token():
    payload = {
        TOKEN_PAYLOAD: SUB_AUTHORIZE,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=60)
    }
    token = jwt.encode(payload, settings.API_KEY_MASTER.get_secret_value(), algorithm=AUTH_ALGORITHM)
    return token

def gerar_token_integrador(integrator_id: str, permissions: list[str]):
    payload = {
        "sub": integrator_id,
        "permissions": permissions,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=1440)
    }
    token = jwt.encode(payload, settings.API_KEY_MASTER.get_secret_value(), algorithm=AUTH_ALGORITHM)
    return token

def validar_jwt_integrador(required_permissions: list[str] = []):
    async def _validate_permissions(credentials: HTTPAuthorizationCredentials = Security(security)):
        try:
            payload = jwt.decode(credentials.credentials, settings.API_KEY_MASTER.get_secret_value(), algorithms=[AUTH_ALGORITHM])
            
            if "permissions" not in payload:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token de integrador inválido")

            integrator_permissions = payload.get("permissions", [])

            if not all(perm in integrator_permissions for perm in required_permissions):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissões insuficientes")
            
            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token inválido")

    return _validate_permissions

