"""SmartScope AI orchestration service."""

from __future__ import annotations

import logging
from datetime import datetime
from statistics import mean
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from ..models.smartscope import (
    AccuracyMetrics,
    AnalysisMetadata,
    AnalysisRequest,
    FeedbackRecord,
    FeedbackRequest,
    SmartScopeAnalysis,
    SmartScopeAnalysisCreate,
)
from ..models.user import User
from .cost_monitor import CostMonitor
from .openai_vision import OpenAIVisionService
from .supabase import supabase_service

logger = logging.getLogger(__name__)


class SmartScopeService:
    """Coordinates analysis requests, persistence, and feedback."""

    def __init__(
        self,
        supabase: Optional[Client] = None,
        vision_service: Optional[OpenAIVisionService] = None,
        cost_monitor: Optional[CostMonitor] = None,
    ) -> None:
        self.supabase = supabase or supabase_service.client
        self.vision_service = vision_service or OpenAIVisionService()
        self.cost_monitor = cost_monitor or CostMonitor(supabase=self.supabase)

    def _get_project_and_property(
        self, project_id: UUID
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Fetch the project and associated property records."""

        project_result = (
            self.supabase.table("projects")
            .select("id, property_id")
            .eq("id", str(project_id))
            .limit(1)
            .execute()
        )

        if not project_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        project_record = project_result.data[0]
        property_id = project_record.get("property_id")
        if not property_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Project is missing associated property information",
            )

        property_result = (
            self.supabase.table("properties")
            .select("id, organization_id, manager_id")
            .eq("id", property_id)
            .limit(1)
            .execute()
        )

        if not property_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found for project",
            )

        return project_record, property_result.data[0]

    def _ensure_project_access(self, project_id: UUID, current_user: User) -> None:
        """Verify the current user can access the supplied project."""

        _, property_record = self._get_project_and_property(project_id)

        organization_id = property_record.get("organization_id")
        if (
            current_user.organization_id
            and organization_id
            and str(current_user.organization_id) != organization_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this project",
            )

        manager_id = property_record.get("manager_id")
        if (
            current_user.role == "manager"
            and manager_id
            and manager_id != str(current_user.id)
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Managers can only access their assigned projects",
            )

    async def process_analysis(
        self, payload: AnalysisRequest, current_user: User
    ) -> SmartScopeAnalysis:
        """Run the AI pipeline and persist the resulting analysis."""

        self._ensure_project_access(payload.project_id, current_user)

        if (
            payload.organization_id
            and current_user.organization_id
            and payload.organization_id != current_user.organization_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organisation mismatch for SmartScope analysis",
            )

        logger.info("Starting SmartScope analysis for project %s", payload.project_id)
        vision_result = await self.vision_service.analyse(payload)
        analysis_payload = vision_result["analysis"]
        metadata_dict = vision_result["metadata"]

        raw_payload = vision_result.get("raw_response", {})

        record = SmartScopeAnalysisCreate(
            project_id=payload.project_id,
            photo_urls=[str(url) for url in payload.photo_urls],
            primary_issue=analysis_payload.get("primary_issue", ""),
            severity=analysis_payload.get("severity", "Medium"),
            category=payload.category,
            scope_items=analysis_payload.get("scope_items", []),
            materials=analysis_payload.get("materials", []),
            estimated_hours=analysis_payload.get("estimated_hours"),
            safety_notes=analysis_payload.get("safety_notes"),
            additional_observations=analysis_payload.get("additional_observations", []),
            confidence_score=float(analysis_payload.get("confidence", 0.0)),
            openai_response_raw={
                "response": raw_payload,
                "metadata": metadata_dict,
            },
            metadata={**metadata_dict, "requested_by": str(current_user.id)},
        )

        insert_payload = {
            "project_id": str(record.project_id),
            "photo_urls": record.photo_urls,
            "primary_issue": record.primary_issue,
            "severity": record.severity,
            "category": record.category,
            "scope_items": record.scope_items,
            "materials": record.materials,
            "estimated_hours": record.estimated_hours,
            "safety_notes": record.safety_notes,
            "additional_observations": record.additional_observations,
            "confidence_score": record.confidence_score,
            "openai_response_raw": record.openai_response_raw,
            "processing_status": metadata_dict.get("processing_status", "completed"),
        }

        try:
            result = self.supabase.table("smartscope_analyses").insert(insert_payload).execute()
        except Exception as exc:  # pragma: no cover - network errors raised by supabase
            logger.exception("Failed to persist SmartScope analysis: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to store SmartScope analysis",
            ) from exc

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SmartScope analysis persistence returned no data",
            )

        record_id = UUID(result.data[0]["id"])
        await self._track_costs(record_id, metadata_dict)
        logger.info("SmartScope analysis %s created", record_id)

        return self._build_analysis_from_record(result.data[0], metadata_dict)

    async def get_analysis(
        self, analysis_id: UUID, current_user: User
    ) -> SmartScopeAnalysis:
        result = (
            self.supabase.table("smartscope_analyses")
            .select("*")
            .eq("id", str(analysis_id))
            .limit(1)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SmartScope analysis not found",
            )

        record = result.data[0]
        project_id = record.get("project_id")
        if not project_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Analysis is missing project context",
            )

        self._ensure_project_access(UUID(str(project_id)), current_user)
        metadata = self._extract_metadata(record)
        return self._build_analysis_from_record(record, metadata)

    async def list_analyses(
        self,
        project_id: UUID,
        current_user: User,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[SmartScopeAnalysis], int]:
        self._ensure_project_access(project_id, current_user)
        offset = (page - 1) * per_page
        query = (
            self.supabase.table("smartscope_analyses")
            .select("*", count="exact")
            .eq("project_id", str(project_id))
            .order("created_at", desc=True)
            .range(offset, offset + per_page - 1)
        )
        result = query.execute()
        records = result.data or []
        metadata = [self._extract_metadata(record) for record in records]
        analyses = [
            self._build_analysis_from_record(record, metadata[idx])
            for idx, record in enumerate(records)
        ]
        total = result.count or len(records)
        return analyses, total

    async def submit_feedback(
        self, analysis_id: UUID, payload: FeedbackRequest, current_user: User
    ) -> FeedbackRecord:
        # Ensure the user has access to the analysis before storing feedback
        await self.get_analysis(analysis_id, current_user)

        feedback_payload = {
            "analysis_id": str(analysis_id),
            "feedback_type": payload.feedback_type,
            "user_id": str(current_user.id) if current_user else None,
            "accuracy_rating": payload.accuracy_rating,
            "scope_corrections": payload.scope_corrections,
            "material_corrections": payload.material_corrections,
            "time_corrections": payload.time_corrections,
            "comments": payload.comments,
        }

        try:
            result = (
                self.supabase.table("smartscope_feedback").insert(feedback_payload).execute()
            )
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to submit SmartScope feedback: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to submit feedback",
            ) from exc

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Feedback submission returned no data",
            )

        record = result.data[0]
        return FeedbackRecord(
            id=UUID(record["id"]),
            analysis_id=UUID(record["analysis_id"]),
            user_id=UUID(record["user_id"]) if record.get("user_id") else None,
            feedback_type=record["feedback_type"],
            accuracy_rating=record["accuracy_rating"],
            scope_corrections=record.get("scope_corrections", {}),
            material_corrections=record.get("material_corrections", {}),
            time_corrections=record.get("time_corrections"),
            comments=record.get("comments"),
            created_at=datetime.fromisoformat(record["created_at"]),
        )

    async def get_accuracy_metrics(self) -> AccuracyMetrics:
        analyses = self.supabase.table("smartscope_analyses").select("id, category, confidence_score").execute()
        feedback = (
            self.supabase.table("smartscope_feedback")
            .select("accuracy_rating, analysis_id, created_at")
            .order("created_at", desc=True")
            .execute()
        )

        analyses_data = analyses.data or []
        feedback_data = feedback.data or []

        category_scores: Dict[str, List[float]] = {}
        for record in analyses_data:
            category_scores.setdefault(record.get("category", "Unknown"), []).append(
                float(record.get("confidence_score") or 0.0)
            )

        average_confidence = (
            mean(float(record.get("confidence_score") or 0.0) for record in analyses_data)
            if analyses_data
            else 0.0
        )

        accuracy_ratings = [float(item["accuracy_rating"]) for item in feedback_data]
        average_accuracy = mean(accuracy_ratings) if accuracy_ratings else None

        last_feedback_at = (
            datetime.fromisoformat(feedback_data[0]["created_at"]) if feedback_data else None
        )

        category_accuracy = {
            category: round(mean(scores), 2) if scores else 0.0
            for category, scores in category_scores.items()
        }

        return AccuracyMetrics(
            total_analyses=len(analyses_data),
            average_confidence=round(average_confidence, 2),
            average_accuracy_rating=round(average_accuracy, 2) if average_accuracy else None,
            category_accuracy=category_accuracy,
            last_feedback_at=last_feedback_at,
            improvements_last_30_days=None,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    async def _track_costs(self, analysis_id: UUID, metadata: Dict[str, Any]) -> None:
        tokens_used = metadata.get("tokens_used")
        if tokens_used is None:
            return
        approximate_cost = self.cost_monitor.estimate_cost(tokens_used)
        await self.cost_monitor.track_analysis_cost(str(analysis_id), approximate_cost, tokens_used)

    @staticmethod
    def _build_analysis_from_record(
        record: Dict[str, Any], metadata: Dict[str, Any]
    ) -> SmartScopeAnalysis:
        created_at = datetime.fromisoformat(record["created_at"]) if isinstance(record.get("created_at"), str) else record.get(
            "created_at"
        )
        updated_at = datetime.fromisoformat(record["updated_at"]) if isinstance(record.get("updated_at"), str) else record.get(
            "updated_at"
        )
        return SmartScopeAnalysis(
            id=UUID(record["id"]),
            project_id=UUID(record["project_id"]),
            photo_urls=record.get("photo_urls", []),
            primary_issue=record.get("primary_issue", ""),
            severity=record.get("severity", "Medium"),
            category=record.get("category", "General Maintenance"),
            scope_items=OpenAIVisionService.build_scope_items(record),
            materials=OpenAIVisionService.build_materials(record),
            estimated_hours=record.get("estimated_hours"),
            safety_notes=record.get("safety_notes"),
            additional_observations=record.get("additional_observations", []),
            confidence_score=float(record.get("confidence_score") or 0.0),
            openai_response_raw=record.get("openai_response_raw", {}),
            metadata=AnalysisMetadata(
                processing_status=record.get("processing_status", "completed"),
                model_version=metadata.get("model_version", "unknown"),
                tokens_used=metadata.get("tokens_used"),
                api_cost=metadata.get("api_cost"),
                processing_time_ms=metadata.get("processing_time_ms"),
            ),
            created_at=created_at,
            updated_at=updated_at or created_at,
        )

    @staticmethod
    def _extract_metadata(record: Dict[str, Any]) -> Dict[str, Any]:
        raw = record.get("openai_response_raw") or {}
        if isinstance(raw, dict) and "metadata" in raw:
            return raw.get("metadata", {})
        return {}


__all__ = ["SmartScopeService"]