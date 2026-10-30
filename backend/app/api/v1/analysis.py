from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.analysis.models import AnalysisInput, AnalysisResult
from app.analysis.service import AnalysisService
from app.config.settings import Settings, get_settings
from app.schemas.analysis import AnalysisRequest

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post(
    "",
    response_model=AnalysisResult,
    summary="Analyze an explicitly labeled cryptocurrency fixture",
    description=(
        "Development/demo only. No live acquisition, trading or calibrated "
        "profit prediction."
    ),
    responses={
        422: {"description": "Invalid fixture or configuration"},
        503: {"description": "Live provider unavailable"},
    },
)
def analyze(
    request: AnalysisRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> AnalysisResult:
    if settings.environment in {"staging", "production"}:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Demo analysis is disabled in production pending approved "
                "access controls."
            ),
        )
    if request.market_data is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Live data is unavailable; fixture data is required.",
        )
    payload = request.market_data.model_dump(mode="json")
    metadata = request.metadata.model_dump(mode="json", exclude_none=True)
    if request.request_id:
        metadata["request_id"] = request.request_id
    return AnalysisService().analyze(AnalysisInput(data=payload, metadata=metadata))
