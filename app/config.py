"""Environment-backed application configuration."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Runtime configuration loaded from environment or the root .env file."""

    APP_NAME: str = "Market Analyzer"
    APP_VERSION: str = "1.1.0"
    ENVIRONMENT: str = "development"

    HOST: str = "127.0.0.1"
    PORT: int = Field(default=8000, ge=1, le=65535)

    DB_HOST: str
    DB_PORT: int = Field(default=5432, ge=1, le=65535)
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    JWT_SECRET_KEY: str = Field(min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0, le=1440)

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    """Return the cached, validated application settings."""
    return Settings()


settings = get_settings()
