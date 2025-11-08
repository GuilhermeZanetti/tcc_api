from typing import Any, List

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.config import settings
from src.contrib.repository.mongodb_utils import (
    close_mongo_connection,
    connect_to_mongo,
)
# from src.logging_config import setup_logging
from src.contrib.middleware.audit import AuditMiddleware
from src.utils import load_identifier

# setup_logging()


class Application(FastAPI):
    def __init__(
        self: 'Application', routers: List[str], *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(
            title='Judge',
            version='0.0.1',
            *args,
            **kwargs,
        )

        self.add_middleware(AuditMiddleware)

        self._load_routes(routers)

        self.add_event_handler('startup', self.init)
        self.add_event_handler('shutdown', self.terminate)

        if settings.BACKEND_CORS_ORIGINS:
            self.add_middleware(
                CORSMiddleware,
                allow_origins=[
                    str(origin) for origin in settings.BACKEND_CORS_ORIGINS
                ],
                allow_credentials=True,
                allow_methods=['*'],
                allow_headers=['*'],
            )

    def _load_routes(self: 'Application', routers: List[str]) -> None:
        for router_name in routers:
            router = load_identifier(router_name)
            self.include_router(router)

    async def init(self) -> None:
        await connect_to_mongo()

    async def terminate(self) -> None:
        await close_mongo_connection()
