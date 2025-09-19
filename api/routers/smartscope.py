"""FastAPI router for SmartScope AI operations."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from models.user import User
from services.smartscope_service import SmartScopeService

from ..dependencies import get_current_user
from ..models.smartscope import (AccuracyMetrics, AnalysisListResponse,
                                 AnalysisRequest, FeedbackRequest,
                                 SmartScopeAnalysis, dependencies, from,
                                 get_current_user, import, models.smartscope)
from ..models.user import User
from ..services.smartscope_service import SmartScopeService

router = APIRouter(prefix="/smartscope", tags=["SmartScope AI"])


@router.post("/analyze", response_model=SmartScopeAnalysis, status_code=status.HTTP_201_CREATED)
async def analyze_project(
    payload: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    service: SmartScopeService = Depends(lambda: SmartScopeService()),
) -> SmartScopeAnalysis:
    """Trigger an AI scope analysis for the supplied project context."""

    return await service.process_analysis(payload, current_user)


@router.get("/{analysis_id}", response_model=SmartScopeAnalysis)
async def get_analysis(
    analysis_id: UUID,
    current_user: User = Depends(get_current_user),
    service: SmartScopeService = Depends(lambda: SmartScopeService()),
) -> SmartScopeAnalysis:
    """Fetch a single SmartScope analysis record."""

    return await service.get_analysis(analysis_id)


@router.get("/project/{project_id}", response_model=AnalysisListResponse)
async def list_project_analyses(
    project_id: UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: SmartScopeService = Depends(lambda: SmartScopeService()),
) -> AnalysisListResponse:
    """List SmartScope analyses for a project with pagination."""

    analyses, total = await service.list_analyses(project_id, page=page, per_page=per_page)
    return AnalysisListResponse(
        analyses=analyses,
        total=total,
        page=page,
        per_page=per_page,
        has_next=page * per_page < total,
        has_prev=page > 1,
    )


@router.post("/{analysis_id}/feedback", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def submit_feedback(
    analysis_id: UUID,
    payload: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    service: SmartScopeService = Depends(lambda: SmartScopeService()),
) -> None:
    """Submit human feedback to help calibrate SmartScope analyses."""

    await service.submit_feedback(analysis_id, payload, current_user)


@router.get("/analytics/accuracy", response_model=AccuracyMetrics)
async def get_accuracy_metrics(
    current_user: User = Depends(get_current_user),
    service: SmartScopeService = Depends(lambda: SmartScopeService()),
) -> AccuracyMetrics:
    """Retrieve aggregated SmartScope accuracy metrics."""

    return await service.get_accuracy_metrics()


__all__ = ["router"]
