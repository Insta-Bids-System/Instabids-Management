"""Tests for the quote form submission endpoint and service."""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any, Dict
from uuid import UUID, uuid4

import pytest
from api.models.quote import QuoteFormSubmission
from api.models.user import User
from api.routers.quotes import submit_quote_form
from api.services.quote_service import QuoteService


class _TableStub:
    """Small helper to mimic the Supabase table interface."""

    def __init__(self, name: str, store: Dict[str, Any]):
        self.name = name
        self.store = store
        self._payload = None
        self._filters: Dict[str, Any] = {}

    def insert(self, payload: Any) -> "_TableStub":
        self._payload = payload
        return self

    def select(self, _: str) -> "_TableStub":
        return self

    def eq(self, column: str, value: Any) -> "_TableStub":
        self._filters[column] = value
        return self

    def limit(self, _: int) -> "_TableStub":
        return self

    def execute(self) -> SimpleNamespace:
        if self.name == "quotes":
            record = {
                "id": str(self.store["quote_id"]),
                "project_id": self._payload["project_id"],
                "contractor_id": self._payload["contractor_id"],
                "invitation_id": self._payload.get("invitation_id"),
                "submission_method": "web_form",
                "status": self._payload["status"],
                "total_amount": self._payload["total_amount"],
                "labor_cost": self._payload.get("labor_cost"),
                "materials_cost": self._payload.get("materials_cost"),
                "other_costs": self._payload.get("other_costs"),
                "tax_amount": self._payload.get("tax_amount"),
                "confidence_score": self._payload["confidence_score"],
                "can_start_date": self._payload.get("can_start_date"),
                "estimated_duration_days": self._payload.get(
                    "estimated_duration_days"
                ),
                "completion_date": self._payload.get("completion_date"),
                "payment_terms": self._payload.get("payment_terms"),
                "warranty_period_months": self._payload.get(
                    "warranty_period_months"
                ),
                "requires_clarification": self._payload.get(
                    "requires_clarification"
                ),
                "clarification_notes": self._payload.get("clarification_notes"),
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
                "submitted_at": self._payload.get("submitted_at")
                or datetime.now(UTC).isoformat(),
                "standardized_data": self._payload["standardized_data"],
            }
            return SimpleNamespace(data=[record])
        if self.name == "quote_items":
            self.store.setdefault("items", []).extend(self._payload)
            return SimpleNamespace(data=self._payload)
        if self.name == "contractors":
            user_id = self._filters.get("user_id")
            if user_id == str(self.store["contractor_user_id"]):
                return SimpleNamespace(
                    data=[{"id": str(self.store["contractor_id"])}]
                )
            return SimpleNamespace(data=[])
        raise AssertionError(f"Unexpected table {self.name}")


class _SupabaseStub:
    def __init__(self) -> None:
        self.store: Dict[str, Any] = {
            "quote_id": uuid4(),
            "project_id": uuid4(),
            "contractor_id": uuid4(),
            "contractor_user_id": uuid4(),
        }

    def table(self, name: str) -> _TableStub:
        return _TableStub(name, self.store)


@pytest.fixture
def supabase_stub() -> _SupabaseStub:
    return _SupabaseStub()


@pytest.fixture
def contractor_user(supabase_stub: _SupabaseStub) -> User:
    return User(
        id=supabase_stub.store["contractor_user_id"],
        email="contractor@example.com",
        full_name="Casey Contractor",
        role="contractor",
        organization_id=None,
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def form_payload() -> Dict[str, Any]:
    return {
        "project_id": str(uuid4()),
        "total_amount": "1250.50",
        "labor_cost": "800.00",
        "materials_cost": "350.00",
        "tax_amount": "100.50",
        "estimated_duration_days": 3,
        "payment_terms": "50% deposit, balance on completion",
        "warranty_period_months": 12,
        "contact_email": "bids@example.com",
        "line_items": [
            {
                "description": "Labor",
                "category": "labor",
                "quantity": "10",
                "unit_of_measure": "hours",
                "unit_price": "80",
                "line_total": "800",
                "is_included": True,
            },
            {
                "description": "Materials",
                "category": "materials",
                "quantity": "1",
                "unit_price": "350",
                "line_total": "350",
                "is_included": True,
            },
        ],
    }


@pytest.mark.asyncio
async def test_quote_service_builds_records(
    contractor_user: User, supabase_stub: _SupabaseStub
) -> None:
    service = QuoteService(supabase=supabase_stub)  # type: ignore[arg-type]

    payload = QuoteFormSubmission(
        project_id=supabase_stub.store["project_id"],
        total_amount="500",
        labor_cost="300",
        materials_cost="150",
        line_items=[
            {"description": "Labor", "line_total": "300"},
            {"description": "Materials", "line_total": "150"},
        ],
    )

    quote = await service.submit_form_quote(payload, contractor_user)

    assert quote.submission_method.value == "web_form"
    assert quote.status.value == "received"
    assert float(quote.total_amount) == 500
    assert len(quote.line_items) == 2


@pytest.mark.asyncio
async def test_submit_form_endpoint(
    contractor_user: User,
    form_payload: Dict[str, Any],
    supabase_stub: _SupabaseStub,
) -> None:
    payload = QuoteFormSubmission(**form_payload)
    service = QuoteService(supabase=supabase_stub)  # type: ignore[arg-type]

    response = await submit_quote_form(
        payload=payload,
        current_user=contractor_user,
        quote_service=service,
    )

    assert response.message.startswith("Quote")
    assert UUID(str(response.quote.id))
