"""Pydantic models that power the project creation API."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class ProjectCategory(str, Enum):
    """Supported maintenance project categories."""

    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    HVAC = "hvac"
    ROOFING = "roofing"
    PAINTING = "painting"
    LANDSCAPING = "landscaping"
    CARPENTRY = "carpentry"
    GENERAL_MAINTENANCE = "general_maintenance"
    OTHER = "other"


class ProjectUrgency(str, Enum):
    """How quickly the work must begin."""

    EMERGENCY = "emergency"
    URGENT = "urgent"
    ROUTINE = "routine"
    SCHEDULED = "scheduled"


class ProjectStatus(str, Enum):
    """Lifecycle status for a project."""

    DRAFT = "draft"
    OPEN_FOR_BIDS = "open_for_bids"
    BIDDING_CLOSED = "bidding_closed"
    AWARDED = "awarded"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BudgetRange(str, Enum):
    """Standard budget ranges presented to property managers."""

    UNDER_500 = "under_500"
    BETWEEN_500_1000 = "500_1000"
    BETWEEN_1000_5000 = "1000_5000"
    BETWEEN_5000_10000 = "5000_10000"
    OVER_10000 = "over_10000"
    OPEN = "open"


class VirtualAccessInfo(BaseModel):
    """Optional information that helps contractors access the property."""

    gate_code: Optional[str] = Field(None, max_length=50)
    lockbox_code: Optional[str] = Field(None, max_length=50)
    key_location: Optional[str] = Field(None, max_length=255)
    onsite_contact_name: Optional[str] = Field(None, max_length=255)
    onsite_contact_phone: Optional[str] = Field(
        None,
        pattern=r"^\+?1?\d{9,15}$",
        description="International E.164 formatted phone number",
    )
    parking_instructions: Optional[str] = Field(None, max_length=500)
    work_hours: Optional[str] = Field(None, max_length=255)
    hazards: Optional[str] = Field(None, max_length=500)
    pets_on_property: Optional[bool] = None

    class Config:
        anystr_strip_whitespace = True


class ProjectBase(BaseModel):
    """Shared fields used for create/update operations."""

    property_id: UUID
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=30, max_length=2000)
    category: ProjectCategory
    urgency: ProjectUrgency = ProjectUrgency.ROUTINE
    bid_deadline: datetime
    preferred_start_date: Optional[date] = None
    completion_deadline: Optional[date] = None
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    budget_range: Optional[BudgetRange] = None
    insurance_required: bool = True
    license_required: bool = True
    minimum_bids: int = Field(3, ge=1, le=20)
    is_open_bidding: bool = False
    virtual_access: Optional[VirtualAccessInfo] = None
    location_details: Optional[str] = Field(None, max_length=500)
    special_conditions: Optional[str] = Field(None, max_length=1000)

    @field_validator("bid_deadline")
    @classmethod
    def validate_bid_deadline(cls, value: datetime) -> datetime:
        now = datetime.utcnow()
        if value <= now:
            raise ValueError("Bid deadline must be in the future")
        max_deadline = now + timedelta(days=7)
        if value > max_deadline:
            raise ValueError("Bid deadline cannot be more than 7 days out")
        return value

    @field_validator("preferred_start_date", "completion_deadline", mode="before")
    @classmethod
    def parse_dates(cls, value):
        if isinstance(value, str):
            return date.fromisoformat(value)
        return value

    @model_validator(mode="after")
    def validate_dates(self) -> "ProjectBase":
        preferred_start = self.preferred_start_date
        completion = self.completion_deadline
        bid_deadline = self.bid_deadline

        if preferred_start and preferred_start < datetime.utcnow().date():
            raise ValueError("Preferred start date cannot be in the past")

        if completion and preferred_start and completion < preferred_start:
            raise ValueError("Completion deadline must be after start date")

        if preferred_start and bid_deadline and bid_deadline.date() > preferred_start:
            raise ValueError("Bid deadline must be on or before preferred start date")

        budget_min = self.budget_min
        budget_max = self.budget_max
        if (
            budget_min is not None
            and budget_max is not None
            and budget_min > budget_max
        ):
            raise ValueError("Minimum budget cannot exceed maximum budget")

        return self


class ProjectCreate(ProjectBase):
    """Payload for creating a project."""

    status: ProjectStatus = ProjectStatus.DRAFT
    publish: bool = Field(
        False,
        description="If true the project will immediately be marked open for bids",
    )


class ProjectUpdate(BaseModel):
    """Payload for updating an existing project."""

    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=30, max_length=2000)
    category: Optional[ProjectCategory] = None
    urgency: Optional[ProjectUrgency] = None
    bid_deadline: Optional[datetime] = None
    preferred_start_date: Optional[date] = None
    completion_deadline: Optional[date] = None
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    budget_range: Optional[BudgetRange] = None
    insurance_required: Optional[bool] = None
    license_required: Optional[bool] = None
    minimum_bids: Optional[int] = Field(None, ge=1, le=20)
    is_open_bidding: Optional[bool] = None
    virtual_access: Optional[VirtualAccessInfo] = None
    location_details: Optional[str] = Field(None, max_length=500)
    special_conditions: Optional[str] = Field(None, max_length=1000)
    status: Optional[ProjectStatus] = None

    @field_validator("bid_deadline")
    @classmethod
    def validate_optional_deadline(cls, value: datetime) -> datetime:
        if value <= datetime.utcnow():
            raise ValueError("Bid deadline must be in the future")
        max_deadline = datetime.utcnow() + timedelta(days=7)
        if value > max_deadline:
            raise ValueError("Bid deadline cannot be more than 7 days out")
        return value

    @model_validator(mode="after")
    def validate_budget_and_dates(self) -> "ProjectUpdate":
        budget_min = self.budget_min
        budget_max = self.budget_max
        if (
            budget_min is not None
            and budget_max is not None
            and budget_min > budget_max
        ):
            raise ValueError("Minimum budget cannot exceed maximum budget")

        preferred_start = self.preferred_start_date
        completion = self.completion_deadline
        if preferred_start and preferred_start < datetime.utcnow().date():
            raise ValueError("Preferred start date cannot be in the past")
        if completion and preferred_start and completion < preferred_start:
            raise ValueError("Completion deadline must be after start date")
        return self


class Project(BaseModel):
    """Representation of a project returned to the client."""

    id: UUID
    property_id: UUID
    created_by: UUID
    title: str
    description: str
    category: ProjectCategory
    urgency: ProjectUrgency
    bid_deadline: datetime
    preferred_start_date: Optional[date]
    completion_deadline: Optional[date]
    budget_min: Optional[float]
    budget_max: Optional[float]
    budget_range: Optional[BudgetRange]
    insurance_required: bool
    license_required: bool
    minimum_bids: int
    is_open_bidding: bool
    virtual_access: Optional[VirtualAccessInfo]
    location_details: Optional[str]
    special_conditions: Optional[str]
    status: ProjectStatus
    view_count: int = 0
    bid_count: int = 0
    question_count: int = 0
    smartscope_analysis_id: Optional[UUID]
    ai_confidence_score: Optional[float]
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    closed_at: Optional[datetime]

    class Config:
        use_enum_values = True


class ProjectListResponse(BaseModel):
    """Paginated response for project listings."""

    projects: List[Project]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class ProjectFilter(BaseModel):
    """Filters that can be applied when listing projects."""

    search: Optional[str] = None
    status: Optional[ProjectStatus] = None
    category: Optional[ProjectCategory] = None
    urgency: Optional[ProjectUrgency] = None
    property_id: Optional[UUID] = None


class ProjectStatusUpdate(BaseModel):
    """Request payload for status transitions."""

    status: ProjectStatus


class ProjectPublishRequest(BaseModel):
    """Request payload when publishing a project."""

    send_notifications: bool = True
    notify_email: Optional[EmailStr] = None


__all__ = [
    "BudgetRange",
    "Project",
    "ProjectBase",
    "ProjectCategory",
    "ProjectCreate",
    "ProjectFilter",
    "ProjectListResponse",
    "ProjectPublishRequest",
    "ProjectStatus",
    "ProjectStatusUpdate",
    "ProjectUpdate",
    "ProjectUrgency",
    "VirtualAccessInfo",
]
