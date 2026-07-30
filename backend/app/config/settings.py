from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from environment variables or .env."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"), env_file_encoding="utf-8", extra="ignore"
    )
    app_name: str = Field(validation_alias="APP_NAME")
    environment: Literal["development", "testing", "production"] = Field(validation_alias="APP_ENVIRONMENT")
    log_level: Literal["INFO", "WARNING", "ERROR"] = Field(
        validation_alias="LOG_LEVEL"
    )
    database_url: str = Field(validation_alias="DATABASE_URL")
    api_v1_prefix: str = Field(default="/api/v1", validation_alias="API_V1_PREFIX")


@lru_cache
def get_settings() -> Settings:
    return Settings()
