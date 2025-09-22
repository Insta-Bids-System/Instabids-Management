"""Business logic for quote submission and management."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from ..models.quote import (
    Quote,
    QuoteFormLineItem,
    QuoteFormSubmission,
    QuoteStatus,
    QuoteSubmissionMethod,
)
from ..models.user import User
from .supabase import supabase_service


class QuoteService:
    """Encapsulates data-access and validation for quotes."""

    def __init__(self, supabase: Optional[Client] = None) -> None:
        self.supabase = supabase or supabase_service.client

    async def submit_form_quote(
        self, payload: QuoteFormSubmission, current_user: User
    ) -> Quote:
        """Persist a quote submitted via the structured web form."""

        self._ensure_contractor_role(current_user)

        contractor_id = self._fetch_contractor_id(current_user)
        quote_insert = self._build_quote_record(payload, contractor_id)

        quotes_table = self.supabase.table("quotes")
        quote_result = quotes_table.insert(quote_insert).execute()

        if not quote_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store quote submission",
            )

        quote_record = quote_result.data[0]

        line_items_payload = self._build_line_item_records(
            payload.line_items, UUID(quote_record["id"])
        )
        if line_items_payload:
            items_table = self.supabase.table("quote_items")
            items_result = items_table.insert(line_items_payload).execute()
            if items_result.data is None:
                # Supabase returns an empty list when inserts succeed with returning=representation
                items_result.data = []

        return self._map_quote_record(quote_record, payload.line_items)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _ensure_contractor_role(self, current_user: User) -> None:
        if current_user.role not in {"contractor", "admin", "manager"}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only contractors can submit quotes",
            )

    def _build_quote_record(
        self, payload: QuoteFormSubmission, contractor_id: UUID
    ) -> Dict[str, object]:
        standardized_payload = self._build_standardized_payload(payload)
        now = datetime.now(UTC).isoformat()

        return {
            "project_id": str(payload.project_id),
            "contractor_id": str(contractor_id),
            "invitation_id": str(payload.invitation_id)
            if payload.invitation_id
            else None,
            "submission_method": QuoteSubmissionMethod.WEB_FORM.value,
            "standardized_data": standardized_payload,
            "confidence_score": self._confidence_for_form(payload),
            "total_amount": float(payload.total_amount),
            "labor_cost": self._optional_decimal(payload.labor_cost),
            "materials_cost": self._optional_decimal(payload.materials_cost),
            "other_costs": self._optional_decimal(payload.other_costs),
            "tax_amount": self._optional_decimal(payload.tax_amount),
            "can_start_date": payload.can_start_date.isoformat()
            if payload.can_start_date
            else None,
            "estimated_duration_days": payload.estimated_duration_days,
            "completion_date": payload.completion_date.isoformat()
            if payload.completion_date
            else None,
            "payment_terms": payload.payment_terms,
            "warranty_period_months": payload.warranty_period_months,
            "status": (
                QuoteStatus.PROCESSING.value
                if payload.is_draft
                else QuoteStatus.RECEIVED.value
            ),
            "requires_clarification": bool(payload.notes),
            "clarification_notes": payload.notes,
            "submitted_at": now if not payload.is_draft else None,
        }

    def _build_standardized_payload(
        self, payload: QuoteFormSubmission
    ) -> Dict[str, object]:
        return {
            "source": QuoteSubmissionMethod.WEB_FORM.value,
            "is_draft": payload.is_draft,
            "contact": {
                "name": payload.contact_name,
                "email": payload.contact_email,
                "phone": payload.contact_phone,
            },
            "line_items": [item.model_dump() for item in payload.line_items],
            "metadata": {
                "submitted_at": datetime.now(UTC).isoformat(),
                "standardization_version": "1.0",
            },
        }

    def _fetch_contractor_id(self, current_user: User) -> UUID:
        """Look up the contractor profile id for the authenticated user."""

        try:
            response = (
                self.supabase.table("contractors")
                .select("id")
                .eq("user_id", str(current_user.id))
                .limit(1)
                .execute()
            )
        except Exception as exc:  # pragma: no cover - network errors
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to look up contractor profile",
            ) from exc

        data = getattr(response, "data", None) or []
        if not data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Contractor profile not found for current user",
            )

        return UUID(data[0]["id"])

    def _confidence_for_form(self, payload: QuoteFormSubmission) -> float:
        base_confidence = 0.9
        if payload.line_items:
            base_confidence += min(0.05, len(payload.line_items) * 0.005)
        if payload.contact_email:
            base_confidence += 0.02
        return min(base_confidence, 0.99)

    def _optional_decimal(self, value: Optional[object]) -> Optional[float]:
        if value is None:
            return None
        return float(value)

    def _build_line_item_records(
        self, line_items: List[QuoteFormLineItem], quote_id: UUID
    ) -> List[Dict[str, object]]:
        records: List[Dict[str, object]] = []
        for index, item in enumerate(line_items):
            records.append(
                {
                    "quote_id": str(quote_id),
                    "item_description": item.description,
                    "item_category": item.category,
                    "quantity": float(item.quantity) if item.quantity is not None else None,
                    "unit_of_measure": item.unit_of_measure,
                    "unit_price": self._optional_decimal(item.unit_price),
                    "line_total": float(item.line_total),
                    "is_included": item.is_included,
                    "display_order": index,
                }
            )
        return records

    def _map_quote_record(
        self, record: Dict[str, object], line_items: List[QuoteFormLineItem]
    ) -> Quote:
        return Quote(
            id=UUID(record["id"]),
            project_id=UUID(record["project_id"]),
            contractor_id=UUID(record["contractor_id"]),
            invitation_id=UUID(record["invitation_id"])
            if record.get("invitation_id")
            else None,
            submission_method=QuoteSubmissionMethod(record["submission_method"]),
            status=QuoteStatus(record["status"]),
            total_amount=record["total_amount"],
            labor_cost=record.get("labor_cost"),
            materials_cost=record.get("materials_cost"),
            other_costs=record.get("other_costs"),
            tax_amount=record.get("tax_amount"),
            confidence_score=record.get("confidence_score"),
            can_start_date=self._parse_date(record.get("can_start_date")),
            estimated_duration_days=record.get("estimated_duration_days"),
            completion_date=self._parse_date(record.get("completion_date")),
            payment_terms=record.get("payment_terms"),
            warranty_period_months=record.get("warranty_period_months"),
            requires_clarification=record.get("requires_clarification", False),
            clarification_notes=record.get("clarification_notes"),
            created_at=self._parse_datetime(record.get("created_at")),
            updated_at=self._parse_datetime(record.get("updated_at")),
            submitted_at=self._parse_datetime(
                record.get("submitted_at") or record.get("created_at")
            ),
            standardized_data=record.get("standardized_data", {}),
            line_items=line_items,
        )

    def _parse_datetime(self, value: Optional[object]) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return datetime.now(UTC)

    def _parse_date(self, value: Optional[object]):
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        return value


__all__ = ["QuoteService"]
