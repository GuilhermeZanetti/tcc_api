from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from judge.config import settings
from datetime import datetime
import jwt

security = HTTPBearer()

async def validar_jwt(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.API_KEY_MASTER.get_secret_value(), algorithms=["HS256"])
        if payload["sub"] != "api_externa":
            raise HTTPException(status_code=403, detail="Token inválido")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Token inválido")

def gerar_token():
    payload = {
        "sub": "api_externa",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
    }
    token = jwt.encode(payload, settings.API_KEY_MASTER.get_secret_value(), algorithm="HS256")
    return token



async def validar_jwt(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.API_KEY_MASTER.get_secret_value(), algorithms=["HS256"])
        if payload["sub"] != "api_externa":
            raise HTTPException(status_code=403, detail="Token inválido")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Token inválido")