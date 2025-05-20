from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pydantic.networks import AnyHttpUrl


class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = Field(default=[])

    MONGODB_MAX_CONNECTIONS_COUNT: int = Field(default=10)
    MONGODB_MIN_CONNECTIONS_COUNT: int = Field(default=10)
    MONGODB_URL: str = Field(default='MONGODB_URL')
    MONGODB_DATABASE: str = Field(default='judge')

    REDIS_HOST: str = Field(default='localhost')
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)
    REDIS_QUEUE: str = Field(default='submissions')

    TLE_TIMEOUT: int = Field(default=30)

    IGNORE_TRAILING_WHITESPACE: bool = Field(default=True)
    IGNORE_EMPTY_LINES: bool = Field(default=True)
    CASE_SENSITIVE: bool = Field(default=True)

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parents[1] / 'local.env'),
        env_file_encoding='utf-8',
    )


settings = Settings()
