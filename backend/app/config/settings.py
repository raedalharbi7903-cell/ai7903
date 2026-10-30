from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from environment variables or .env."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"), env_file_encoding="utf-8", extra="ignore"
    )
    app_name: str = Field(validation_alias="APP_NAME")
    environment: Literal["development", "testing", "staging", "production"] = Field(
        validation_alias="APP_ENVIRONMENT"
    )
    log_level: Literal["INFO", "WARNING", "ERROR"] = Field(validation_alias="LOG_LEVEL")
    database_url: str = Field(validation_alias="DATABASE_URL")
    api_v1_prefix: str = Field(default="/api/v1", validation_alias="API_V1_PREFIX")
    history_enabled: bool = Field(default=False, validation_alias="HISTORY_ENABLED")
    history_mutations_enabled: bool = Field(
        default=False, validation_alias="HISTORY_MUTATIONS_ENABLED"
    )
    history_allowed_origin: AnyHttpUrl | None = Field(
        default=None, validation_alias="HISTORY_ALLOWED_ORIGIN"
    )
    history_audit_retention_seconds: int | None = Field(
        default=None, gt=0, validation_alias="HISTORY_AUDIT_RETENTION_SECONDS"
    )
    history_audit_policy_reference: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        pattern=r"\S",
        validation_alias="HISTORY_AUDIT_POLICY_REFERENCE",
    )
    history_retention_seconds: int | None = Field(
        default=None, gt=0, validation_alias="HISTORY_RETENTION_SECONDS"
    )
    history_policy_reference: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        pattern=r"\S",
        validation_alias="HISTORY_POLICY_REFERENCE",
    )
    founder_identity_issuer: str | None = Field(
        default=None, validation_alias="FOUNDER_IDENTITY_ISSUER"
    )
    founder_identity_subject: str | None = Field(
        default=None, validation_alias="FOUNDER_IDENTITY_SUBJECT"
    )
    market_data_provider: str | None = Field(
        default=None, validation_alias="MARKET_DATA_PROVIDER"
    )
    market_data_api_key: str | None = Field(
        default=None, validation_alias="MARKET_DATA_API_KEY"
    )
    market_data_base_url: str | None = Field(
        default=None, validation_alias="MARKET_DATA_BASE_URL"
    )

    @model_validator(mode="after")
    def safe_history_origin(self) -> "Settings":
        origin = self.history_allowed_origin
        if origin is not None:
            if (
                origin.username is not None
                or origin.password is not None
                or origin.path not in (None, "", "/")
                or origin.query is not None
                or origin.fragment is not None
                or not origin.host
                or "*" in origin.host
            ):
                raise ValueError(
                    "History origin must contain only scheme, host and port"
                )
            if origin.scheme != "https" and (
                self.environment not in {"development", "testing"}
                or origin.host not in {"localhost", "127.0.0.1", "::1", "[::1]"}
            ):
                raise ValueError(
                    "History origin requires HTTPS outside loopback development"
                )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
