"""API endpoints for managing quote submissions."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from ..dependencies import require_contractor
from ..models.quote import QuoteFormSubmission, QuoteSubmissionResponse
from ..models.user import User
from ..services.quote_service import QuoteService

router = APIRouter(prefix="/quotes", tags=["Quotes"])


def get_quote_service() -> QuoteService:
    """Dependency injector for the quote service."""

    return QuoteService()


@router.post(
    "/submit/form",
    response_model=QuoteSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_quote_form(
    payload: QuoteFormSubmission,
    current_user: User = Depends(require_contractor),
    quote_service: QuoteService = Depends(get_quote_service),
) -> QuoteSubmissionResponse:
    """Accept a structured web form quote submission."""

    quote = await quote_service.submit_form_quote(payload, current_user)
    message = (
        "Quote draft saved successfully"
        if payload.is_draft
        else "Quote submitted successfully"
    )
    return QuoteSubmissionResponse(quote=quote, message=message)


__all__ = ["router", "get_quote_service"]
