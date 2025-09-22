"""Pydantic models for the quote submission workflow."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, condecimal, validator


class QuoteSubmissionMethod(str, Enum):
    """Supported intake channels for quotes."""

    PDF = "pdf"
    EMAIL = "email"
    PHOTO = "photo"
    WEB_FORM = "web_form"


class QuoteStatus(str, Enum):
    """Lifecycle states for quote processing."""

    RECEIVED = "received"
    PROCESSING = "processing"
    STANDARDIZED = "standardized"
    NEEDS_CLARIFICATION = "needs_clarification"
    UPDATED = "updated"
    WITHDRAWN = "withdrawn"


Currency = condecimal(max_digits=12, decimal_places=2, ge=0)


class QuoteFormLineItem(BaseModel):
    """Line item entered via the structured web form."""

    description: str = Field(..., min_length=3, max_length=500)
    category: Optional[str] = Field(
        None,
        max_length=100,
        description="Standardized category label such as labor, materials, etc.",
    )
    quantity: Optional[condecimal(max_digits=10, decimal_places=2, ge=0)] = Field(
        1, description="Quantity of the item."
    )
    unit_of_measure: Optional[str] = Field(
        None,
        max_length=20,
        description="Unit of measure such as each, hours, or sq ft.",
    )
    unit_price: Optional[Currency] = Field(None, description="Price per unit if provided.")
    line_total: Currency = Field(..., description="Extended total for the line item.")
    is_included: bool = Field(
        True, description="False indicates an exclusion or optional add-on."
    )


class QuoteLineItem(QuoteFormLineItem):
    """Stored representation of a quote line item."""

    id: UUID
    quote_id: UUID
    display_order: int = 0
    created_at: datetime


class QuoteFormSubmission(BaseModel):
    """Payload supplied when a contractor submits a quote via the web form."""

    project_id: UUID
    invitation_id: Optional[UUID] = Field(
        None, description="Invitation that prompted the quote, when applicable."
    )
    total_amount: Currency = Field(..., description="Total quoted amount.")
    labor_cost: Optional[Currency] = Field(None, description="Labor portion of the quote.")
    materials_cost: Optional[Currency] = Field(
        None, description="Materials portion of the quote."
    )
    other_costs: Optional[Currency] = Field(
        None, description="Miscellaneous additional costs."
    )
    tax_amount: Optional[Currency] = Field(None, description="Calculated taxes, if any.")
    can_start_date: Optional[date] = Field(
        None,
        description="Earliest date work can begin.",
    )
    estimated_duration_days: Optional[int] = Field(
        None, ge=0, description="Number of days the work is expected to take."
    )
    completion_date: Optional[date] = Field(
        None, description="Expected completion date for the project."
    )
    payment_terms: Optional[str] = Field(
        None,
        max_length=1000,
        description="Payment schedule or milestones provided by the contractor.",
    )
    warranty_period_months: Optional[int] = Field(
        None,
        ge=0,
        le=120,
        description="Length of warranty coverage in months.",
    )
    notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Additional clarifications supplied by the contractor.",
    )
    line_items: List[QuoteFormLineItem] = Field(
        default_factory=list,
        description="Structured breakdown of the quote.",
    )
    contact_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Point of contact for follow-up questions.",
    )
    contact_email: Optional[EmailStr] = Field(
        None, description="Email for the contractor representative."
    )
    contact_phone: Optional[str] = Field(
        None,
        pattern=r"^\+?1?\d{9,15}$",
        description="Phone number in E.164 format for easy dialing.",
    )
    is_draft: bool = Field(
        False, description="When true the submission should be stored as an editable draft."
    )

    @validator("line_items")
    def ensure_line_item_totals(cls, items: List[QuoteFormLineItem]) -> List[QuoteFormLineItem]:
        if len(items) > 100:
            raise ValueError("A quote cannot contain more than 100 line items")
        return items


class Quote(BaseModel):
    """Quote representation returned from the API."""

    id: UUID
    project_id: UUID
    contractor_id: UUID
    invitation_id: Optional[UUID] = None
    submission_method: QuoteSubmissionMethod
    status: QuoteStatus
    total_amount: Currency
    labor_cost: Optional[Currency] = None
    materials_cost: Optional[Currency] = None
    other_costs: Optional[Currency] = None
    tax_amount: Optional[Currency] = None
    confidence_score: Optional[condecimal(max_digits=3, decimal_places=2, ge=0, le=1)] = (
        None
    )
    can_start_date: Optional[date] = None
    estimated_duration_days: Optional[int] = None
    completion_date: Optional[date] = None
    payment_terms: Optional[str] = None
    warranty_period_months: Optional[int] = None
    requires_clarification: bool = False
    clarification_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    submitted_at: datetime
    standardized_data: dict
    line_items: List[QuoteFormLineItem] = Field(default_factory=list)


class QuoteSubmissionResponse(BaseModel):
    """Response payload for quote submission endpoints."""

    quote: Quote
    message: str = Field(
        ...,
        description="Human friendly status message explaining the result of the submission.",
    )


__all__ = [
    "Quote",
    "QuoteFormLineItem",
    "QuoteFormSubmission",
    "QuoteLineItem",
    "QuoteStatus",
    "QuoteSubmissionMethod",
    "QuoteSubmissionResponse",
]
