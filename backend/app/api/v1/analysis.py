from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.analysis.models import AnalysisInput, AnalysisResult
from app.analysis.service import AnalysisService

router = APIRouter(prefix="/analysis", tags=["analysis"])


class AnalysisRequest(BaseModel):
    """Fixture-only contract; live provider acquisition is intentionally absent."""

    pair: str = Field(min_length=3, max_length=32, pattern=r"^[A-Z0-9-]+$")
    timeframe: str = Field(min_length=2, max_length=8)
    request_id: str | None = Field(default=None, max_length=128)
    market_data: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


@router.post("", response_model=AnalysisResult)
def analyze(request: AnalysisRequest) -> AnalysisResult:
    if request.market_data is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Live data is unavailable; fixture data is required.",
        )
    payload = dict(request.market_data)
    if (
        payload.get("instrument") != request.pair
        or payload.get("timeframe") != request.timeframe
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pair and timeframe must match supplied market data provenance.",
        )
    metadata = dict(request.metadata)
    if request.request_id:
        metadata["request_id"] = request.request_id
    return AnalysisService().analyze(AnalysisInput(data=payload, metadata=metadata))
