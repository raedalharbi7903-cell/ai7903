"""Explicit reviewed retention configuration; never supplies a default duration."""

from pydantic import BaseModel, ConfigDict, Field


class RetentionPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    retention_seconds: int = Field(gt=0)
    approval_reference: str = Field(min_length=1, max_length=200, pattern=r"\S")
