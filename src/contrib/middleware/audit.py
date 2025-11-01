
import logging
import time
import jwt
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.config import settings
from src.contrib.constants import AUTH_ALGORITHM

logger = logging.getLogger(__name__)

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        integrator_id = "anonymous"
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(
                    token,
                    settings.API_KEY_MASTER.get_secret_value(),
                    algorithms=[AUTH_ALGORITHM],
                )
                integrator_id = payload.get("sub", "anonymous")
            except jwt.PyJWTError:
                # Token is invalid, expired, or malformed. Keep integrator_id as anonymous.
                pass

        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        log_info = {
            "message": "Request processed",
            "audit": {
                "request": {
                    "method": request.method,
                    "path": request.url.path,
                    "client_ip": request.client.host,
                    "integrator_id": integrator_id,
                },
                "response": {
                    "status_code": response.status_code,
                },
                "processing_time_ms": round(process_time, 2),
            },
        }

        logger.info(log_info)

        return response
