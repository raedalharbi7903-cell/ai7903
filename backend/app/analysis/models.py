from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class EngineLifecycleStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisInput(BaseModel):
    """Standard, engine-agnostic input envelope."""

    data: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EngineOutput(BaseModel):
    """Standard output emitted by a single analysis engine."""

    engine_name: str
    status: EngineLifecycleStatus
    data: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AnalysisResult(BaseModel):
    """Aggregate result emitted after a pipeline run."""

    status: EngineLifecycleStatus
    outputs: list[EngineOutput] = Field(default_factory=list)
