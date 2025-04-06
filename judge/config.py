from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr
from pydantic.networks import AnyHttpUrl
from dotenv import load_dotenv

load_dotenv("local.env")

class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = Field(default=[])

    MONGODB_MAX_CONNECTIONS_COUNT: int = Field(default=10)
    MONGODB_MIN_CONNECTIONS_COUNT: int = Field(default=10)
    MONGODB_URL: str
    MONGODB_DATABASE: str = Field(default='judge')

    TLE_TIMEOUT: int = Field(default=30)

    SECRET_KEY: SecretStr
    API_KEY_MASTER: SecretStr = Field(env='API_KEY_MASTER')
    
    JWT_ALGORITHM: str = Field(default="MAVI1701")

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parents[1] / '.env'),
        env_file_encoding='utf-8',
    )


settings = Settings()
