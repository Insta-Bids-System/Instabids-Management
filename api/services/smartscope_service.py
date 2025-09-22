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
    SMARTSCOPE_METADATA_FIELDS,
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

    async def process_analysis(
        self, payload: AnalysisRequest, current_user: User
    ) -> SmartScopeAnalysis:
        """Run the AI pipeline and persist the resulting analysis."""

        logger.info("Starting SmartScope analysis for project %s", payload.project_id)
        vision_result = await self.vision_service.analyse(payload)
        analysis_payload = vision_result["analysis"]
        metadata_dict = vision_result["metadata"]

        raw_payload = vision_result.get("raw_response", {})

        metadata_payload = self._filter_metadata(metadata_dict)
        metadata_payload["requested_by"] = str(current_user.id)
        processing_status = metadata_payload.get("processing_status", "completed")

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
            metadata=metadata_payload,
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
            "metadata": metadata_payload,
            "processing_status": processing_status,
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
        await self._track_costs(record_id, metadata_payload)
        logger.info("SmartScope analysis %s created", record_id)

        return self._build_analysis_from_record(result.data[0], metadata_payload)

    async def get_analysis(self, analysis_id: UUID) -> SmartScopeAnalysis:
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
        metadata = self._extract_metadata(record)
        return self._build_analysis_from_record(record, metadata)

    async def list_analyses(
        self, project_id: UUID, page: int = 1, per_page: int = 20
    ) -> Tuple[List[SmartScopeAnalysis], int]:
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
            .order("created_at", desc=True)
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
        await self.cost_monitor.track_analysis_cost(
            str(analysis_id),
            approximate_cost,
            tokens_used,
            metadata.get("processing_time_ms"),
        )

    @staticmethod
    def _build_analysis_from_record(
        record: Dict[str, Any], metadata: Dict[str, Any]
    ) -> SmartScopeAnalysis:
        created_at = datetime.fromisoformat(record["created_at"]) if isinstance(record.get("created_at"), str) else record.get("created_at")
        updated_at = datetime.fromisoformat(record["updated_at"]) if isinstance(record.get("updated_at"), str) else record.get("updated_at")
        metadata_model = AnalysisMetadata(
            processing_status=metadata.get("processing_status", record.get("processing_status", "completed")),
            model_version=str(metadata.get("model_version", "unknown")),
            tokens_used=metadata.get("tokens_used"),
            api_cost=metadata.get("api_cost"),
            processing_time_ms=metadata.get("processing_time_ms"),
            requested_by=UUID(metadata.get("requested_by")) if metadata.get("requested_by") else None,
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
            metadata=metadata_model,
            created_at=created_at,
            updated_at=updated_at or created_at,
        )

    @staticmethod
    def _extract_metadata(record: Dict[str, Any]) -> Dict[str, Any]:
        combined: Dict[str, Any] = {}
        metadata_column = record.get("metadata")
        if isinstance(metadata_column, dict):
            combined.update(metadata_column)

        raw = record.get("openai_response_raw") or {}
        if isinstance(raw, dict):
            metadata_raw = raw.get("metadata")
            if isinstance(metadata_raw, dict):
                combined = {**metadata_raw, **combined}

        filtered: Dict[str, Any] = {}
        for key in SMARTSCOPE_METADATA_FIELDS:
            if combined.get(key) is not None:
                filtered[key] = combined.get(key)

        if "processing_status" not in filtered:
            filtered["processing_status"] = record.get("processing_status", "completed")
        if "model_version" not in filtered:
            filtered["model_version"] = combined.get("model_version", "unknown")
        return filtered

    @staticmethod
    def _filter_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        filtered: Dict[str, Any] = {}
        for key in SMARTSCOPE_METADATA_FIELDS:
            if metadata.get(key) is not None:
                filtered[key] = metadata.get(key)

        filtered.setdefault("processing_status", metadata.get("processing_status", "completed"))
        filtered.setdefault("model_version", metadata.get("model_version", "unknown"))
        return filtered


__all__ = ["SmartScopeService"]