"""Pydantic models for SmartScope AI analysis workflows."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, Field, HttpUrl, field_validator, ConfigDict


SMARTSCOPE_SEVERITIES = ("Emergency", "High", "Medium", "Low")
SMARTSCOPE_SCOPE_ITEM_FIELDS = (
    "title",
    "description",
    "trade",
    "materials",
    "safety_notes",
    "estimated_hours",
)
SMARTSCOPE_MATERIAL_FIELDS = ("name", "quantity", "specifications")
SMARTSCOPE_METADATA_FIELDS = (
    "processing_status",
    "model_version",
    "tokens_used",
    "api_cost",
    "processing_time_ms",
    "requested_by",
)


class ScopeItem(BaseModel):
    """Represents a single actionable scope item returned by the AI."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    title: str = Field(..., description="Human readable title summarising the work")
    description: str = Field(..., description="Detailed set of instructions for contractors")
    trade: Optional[str] = Field(
        default=None, description="Primary trade responsible for this line item"
    )
    materials: List[str] = Field(
        default_factory=list,
        description="Recommended materials or products required to complete the work",
    )
    safety_notes: List[str] = Field(
        default_factory=list, description="Relevant safety callouts for technicians"
    )
    estimated_hours: Optional[float] = Field(
        default=None, description="Estimated labour hours to complete this item"
    )


class MaterialItem(BaseModel):
    """Structured material requirements for the analysis."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    name: str
    quantity: Optional[str] = None
    specifications: Optional[str] = Field(
        default=None, description="Brand, grade or other specification details"
    )


class AnalysisRequest(BaseModel):
    """Payload required to trigger a SmartScope AI analysis run."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    project_id: UUID
    photo_urls: List[AnyHttpUrl]
    property_type: str = Field(..., description="Residential, Commercial, etc")
    area: str = Field(..., description="Location inside the property such as Kitchen")
    reported_issue: str = Field(..., description="User reported description of the problem")
    category: str = Field(..., description="Maintenance category e.g. Plumbing")
    organization_id: Optional[UUID] = Field(
        default=None, description="Organisation requesting the analysis"
    )
    requested_by: Optional[UUID] = Field(
        default=None, description="User that initiated the request"
    )
    priority: Optional[str] = Field(default=None, description="Optional priority level")

    @field_validator("category")
    @classmethod
    def _normalise_category(cls, value: str) -> str:
        return value.strip().title()


class AnalysisMetadata(BaseModel):
    """Additional metadata captured during processing."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    processing_status: str = Field(default="pending")
    model_version: str
    tokens_used: Optional[int] = None
    api_cost: Optional[float] = None
    processing_time_ms: Optional[int] = None
    requested_by: Optional[UUID] = None


class SmartScopeAnalysis(BaseModel):
    """Represents a SmartScope analysis record returned to clients."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    id: UUID
    project_id: UUID
    photo_urls: List[HttpUrl]
    primary_issue: str
    severity: str
    category: str
    scope_items: List[ScopeItem]
    materials: List[MaterialItem]
    estimated_hours: Optional[float] = None
    safety_notes: Optional[str] = None
    additional_observations: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)
    openai_response_raw: Dict[str, Any]
    metadata: AnalysisMetadata
    created_at: datetime
    updated_at: datetime

    @field_validator("severity")
    @classmethod
    def _validate_severity(cls, value: str) -> str:
        severity = value.title()
        if severity not in SMARTSCOPE_SEVERITIES:
            raise ValueError(
                f"Invalid severity '{value}'. Expected one of: {', '.join(sorted(SMARTSCOPE_SEVERITIES))}."
            )
        return severity


class SmartScopeAnalysisCreate(BaseModel):
    """Internal helper model when persisting new analysis records."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    project_id: UUID
    photo_urls: List[str]
    primary_issue: str
    severity: str
    category: str
    scope_items: List[Dict[str, Any]]
    materials: List[Dict[str, Any]]
    estimated_hours: Optional[float]
    safety_notes: Optional[str]
    additional_observations: List[str]
    confidence_score: float
    openai_response_raw: Dict[str, Any]
    metadata: Dict[str, Any]


class FeedbackRequest(BaseModel):
    """Feedback payload submitted by property managers or contractors."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    feedback_type: str
    accuracy_rating: int = Field(ge=1, le=5)
    scope_corrections: Dict[str, Any] = Field(default_factory=dict)
    material_corrections: Dict[str, Any] = Field(default_factory=dict)
    time_corrections: Optional[float] = None
    comments: Optional[str] = None


class FeedbackRecord(BaseModel):
    """Feedback record stored in the database."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    id: UUID
    analysis_id: UUID
    user_id: Optional[UUID]
    feedback_type: str
    accuracy_rating: int
    scope_corrections: Dict[str, Any]
    material_corrections: Dict[str, Any]
    time_corrections: Optional[float]
    comments: Optional[str]
    created_at: datetime


class AccuracyMetrics(BaseModel):
    """Aggregated analytics for SmartScope performance dashboards."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    total_analyses: int
    average_confidence: float
    average_accuracy_rating: Optional[float]
    category_accuracy: Dict[str, float]
    last_feedback_at: Optional[datetime]
    improvements_last_30_days: Optional[float]


class AnalysisListResponse(BaseModel):
    """Paginated listing of SmartScope analyses."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    analyses: List[SmartScopeAnalysis]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


__all__ = [
    "SMARTSCOPE_SEVERITIES",
    "SMARTSCOPE_SCOPE_ITEM_FIELDS",
    "SMARTSCOPE_MATERIAL_FIELDS",
    "SMARTSCOPE_METADATA_FIELDS",
    "ScopeItem",
    "MaterialItem",
    "AnalysisRequest",
    "AnalysisMetadata",
    "SmartScopeAnalysis",
    "SmartScopeAnalysisCreate",
    "FeedbackRequest",
    "FeedbackRecord",
    "AccuracyMetrics",
    "AnalysisListResponse",
]
