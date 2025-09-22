from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Iterable, List
from uuid import uuid4

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest

from api.models.smartscope import AnalysisRequest
from api.models.user import User
from api.services.cost_monitor import CostMonitor
from api.services.openai_vision import OpenAIVisionService, ProcessedImage
from api.services.smartscope_service import SmartScopeService


class FakePreprocessor:
    async def preprocess(self, image_urls: Iterable[str]) -> List[ProcessedImage]:
        return [
            ProcessedImage(
                source_url=url,
                base64_data="ZGF0YQ==",
                width=1024,
                height=768,
                quality_score=0.8,
            )
            for url in image_urls
        ]


class FakeOpenAIResponse:
    def __init__(self, text: str, tokens: int = 120) -> None:
        self.output = [
            {
                "content": [
                    {"type": "output_text", "text": text},
                ]
            }
        ]
        self.usage = {"total_tokens": tokens}

    def model_dump(self) -> Dict[str, Any]:
        return {"output": self.output, "usage": self.usage}


class FakeOpenAIClient:
    def __init__(self, response_text: str) -> None:
        self._response_text = response_text
        self.responses = SimpleNamespace(create=self._create)

    async def _create(self, **_: Any) -> FakeOpenAIResponse:
        return FakeOpenAIResponse(self._response_text)


class FakeTable:
    def __init__(self, storage: Dict[str, List[Dict[str, Any]]], name: str) -> None:
        self.storage = storage
        self.name = name
        self._operation = None
        self._payload: Dict[str, Any] | None = None
        self._filters: List[Dict[str, Any]] = []
        self._order: tuple[str, bool] | None = None
        self._range: tuple[int, int] | None = None
        self._limit: int | None = None

    # Insert -----------------------------------------------------------------
    def insert(self, payload: Dict[str, Any]) -> "FakeTable":
        self._operation = "insert"
        self._payload = payload
        return self

    # Select -----------------------------------------------------------------
    def select(self, *_args, count: str | None = None) -> "FakeTable":
        self._operation = "select"
        self._count = count
        return self

    def eq(self, key: str, value: Any) -> "FakeTable":
        self._filters.append({"op": "eq", "key": key, "value": value})
        return self

    def gte(self, key: str, value: Any) -> "FakeTable":
        self._filters.append({"op": "gte", "key": key, "value": value})
        return self

    def limit(self, value: int) -> "FakeTable":
        self._limit = value
        return self

    def order(self, key: str, desc: bool = False) -> "FakeTable":
        self._order = (key, desc)
        return self

    def range(self, start: int, end: int) -> "FakeTable":
        self._range = (start, end)
        return self

    # Execution --------------------------------------------------------------
    def execute(self) -> SimpleNamespace:
        if self._operation == "insert":
            record = dict(self._payload or {})
            now = datetime.now(timezone.utc).isoformat()
            record.setdefault("id", str(uuid4()))
            record.setdefault("created_at", now)
            record.setdefault("updated_at", now)
            self.storage[self.name].append(record)
            return SimpleNamespace(data=[record], count=None)

        if self._operation == "select":
            records = list(self.storage[self.name])
            for filt in self._filters:
                if filt["op"] == "eq":
                    records = [
                        r
                        for r in records
                        if str(r.get(filt["key"])) == str(filt["value"])
                    ]
                elif filt["op"] == "gte":
                    records = [
                        r
                        for r in records
                        if r.get(filt["key"]) and r[filt["key"]] >= filt["value"]
                    ]
            if self._order:
                key, desc = self._order
                records.sort(key=lambda r: r.get(key), reverse=desc)
            if self._range:
                start, end = self._range
                records = records[start : end + 1]
            if self._limit is not None:
                records = records[: self._limit]
            count = len(records) if getattr(self, "_count", None) else None
            return SimpleNamespace(data=records, count=count)

        raise NotImplementedError(f"Operation {self._operation} not supported")


class FakeSupabaseClient:
    def __init__(self) -> None:
        self.storage: Dict[str, List[Dict[str, Any]]] = {
            "smartscope_analyses": [],
            "smartscope_feedback": [],
            "smartscope_costs": [],
        }

    def table(self, name: str) -> FakeTable:
        if name not in self.storage:
            self.storage[name] = []
        return FakeTable(self.storage, name)


class FakeVisionService:
    async def analyse(self, _: AnalysisRequest) -> Dict[str, Any]:
        return {
            "analysis": {
                "primary_issue": "Leaking trap",
                "severity": "High",
                "scope_items": [
                    {
                        "title": "Replace P-trap",
                        "description": "Remove existing trap and install new PVC trap",
                        "trade": "Plumbing",
                        "materials": ['1.5" PVC P-trap'],
                        "safety_notes": ["Shut off water"],
                        "estimated_hours": 1.5,
                    }
                ],
                "materials": [
                    {
                        "name": "PVC P-trap",
                        "quantity": "1",
                        "specifications": "1.5 inch",
                    }
                ],
                "estimated_hours": 1.5,
                "safety_notes": "Use bucket to catch residual water",
                "additional_observations": ["Check cabinet for damage"],
                "confidence": 0.91,
            },
            "metadata": {
                "model_version": "test",
                "processing_status": "completed",
                "tokens_used": 200,
                "processing_time_ms": 3200,
            },
            "raw_response": {"ok": True},
        }


class FakeCostMonitor:
    def __init__(self) -> None:
        self.records: List[tuple[str, float, int | None]] = []

    def estimate_cost(self, tokens_used: int) -> float:
        return 0.01 * tokens_used / 100

    async def track_analysis_cost(
        self,
        analysis_id: str,
        cost: float,
        tokens_used: int | None,
        processing_time_ms: int | None = None,
    ) -> None:
        self.records.append((analysis_id, cost, tokens_used, processing_time_ms))


@pytest.mark.asyncio
async def test_openai_vision_service_parses_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = AnalysisRequest(
        project_id=uuid4(),
        photo_urls=["https://example.com/image.jpg"],
        property_type="Residential",
        area="Kitchen",
        reported_issue="Leaking sink",
        category="Plumbing",
    )

    service = OpenAIVisionService(
        client=FakeOpenAIClient(
            """
            {
                \"primary_issue\": \"Leak\",
                \"severity\": \"High\",
                \"scope_items\": [],
                \"materials\": [],
                \"confidence\": 0.88
            }
            """
        ),
        preprocessor=FakePreprocessor(),
    )

    result = await service.analyse(request)
    assert result["analysis"]["confidence"] >= 0.75
    assert result["metadata"]["processing_status"] == "completed"
    assert "model_version" in result["metadata"]


@pytest.mark.asyncio
async def test_smartscope_service_processes_and_persists_analysis() -> None:
    supabase = FakeSupabaseClient()
    service = SmartScopeService(
        supabase=supabase,
        vision_service=FakeVisionService(),
        cost_monitor=FakeCostMonitor(),
    )

    user = User(
        id=uuid4(),
        email="pm@example.com",
        full_name="Property Manager",
        role="manager",
        organization_id=None,
        is_active=True,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )

    request = AnalysisRequest(
        project_id=uuid4(),
        photo_urls=["https://example.com/one.jpg"],
        property_type="Residential",
        area="Bathroom",
        reported_issue="Trap leaking",
        category="Plumbing",
    )

    analysis = await service.process_analysis(request, user)
    assert analysis.primary_issue == "Leaking trap"
    assert analysis.severity == "High"
    assert analysis.confidence_score == pytest.approx(0.91)
    assert analysis.metadata.tokens_used == 200
    assert analysis.metadata.processing_time_ms == 3200
    assert analysis.metadata.requested_by == user.id
    assert supabase.storage["smartscope_analyses"], "Analysis should be stored"


@pytest.mark.asyncio
async def test_cost_monitor_budget_checks() -> None:
    supabase = FakeSupabaseClient()
    monitor = CostMonitor(supabase=supabase, daily_budget=1.0, monthly_budget=5.0)

    # Seed with synthetic costs
    yesterday = datetime.now(timezone.utc) - timedelta(hours=12)
    supabase.storage["smartscope_costs"].append(
        {
            "id": str(uuid4()),
            "analysis_id": str(uuid4()),
            "api_cost": 0.5,
            "created_at": yesterday.isoformat(),
        }
    )

    report = await monitor.check_budget_status()
    assert report["daily_spend"] == pytest.approx(0.5)
    assert report["status"] in {"green", "amber", "red"}
    assert monitor.estimate_cost(100) == pytest.approx(0.001)

    summary = await monitor.generate_cost_report("1d")
    assert summary["analyses"] >= 1


@pytest.mark.asyncio
async def test_accuracy_metrics_aggregation() -> None:
    supabase = FakeSupabaseClient()
    analysis_id = str(uuid4())
    supabase.storage["smartscope_analyses"].append(
        {
            "id": analysis_id,
            "project_id": str(uuid4()),
            "photo_urls": ["https://example.com/1.jpg"],
            "primary_issue": "Leaking trap",
            "severity": "High",
            "category": "Plumbing",
            "scope_items": [],
            "materials": [],
            "confidence_score": 0.9,
            "processing_status": "completed",
            "openai_response_raw": {"metadata": {"model_version": "test"}},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    supabase.storage["smartscope_feedback"].append(
        {
            "id": str(uuid4()),
            "analysis_id": analysis_id,
            "feedback_type": "contractor",
            "accuracy_rating": 5,
            "scope_corrections": {},
            "material_corrections": {},
            "time_corrections": None,
            "comments": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    service = SmartScopeService(
        supabase=supabase,
        vision_service=FakeVisionService(),
        cost_monitor=FakeCostMonitor(),
    )

    metrics = await service.get_accuracy_metrics()
    assert metrics.total_analyses == 1
    assert metrics.average_confidence == pytest.approx(0.9, rel=1e-2)
    assert metrics.category_accuracy["Plumbing"] == pytest.approx(0.9, rel=1e-2)