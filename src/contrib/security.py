from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.config import settings
from datetime import datetime
import jwt

from src.contrib.constants import AUTH_ALGORITHM, SUB_AUTHORIZE, TOKEN_PAYLOAD

security = HTTPBearer()

async def validar_jwt(credentials: HTTPAuthorizationCredentials = Security(security)):
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
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
    }
    token = jwt.encode(payload, settings.API_KEY_MASTER.get_secret_value(), algorithm=AUTH_ALGORITHM)
    return token



async def validar_jwt(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.API_KEY_MASTER.get_secret_value(), algorithms=[AUTH_ALGORITHM])
        if payload[TOKEN_PAYLOAD] != SUB_AUTHORIZE:
            raise HTTPException(status_code=403, detail="Token inválido")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Token inválido")