"""Cost monitoring utilities for SmartScope AI usage."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from supabase import Client

logger = logging.getLogger(__name__)

TOKEN_COST_USD = (
    0.00001  # Approximate blended rate for GPT-4.1 mini input/output tokens
)


class CostMonitor:
    """Tracks OpenAI spend and budget utilisation."""

    def __init__(
        self,
        supabase: Optional[Client] = None,
        daily_budget: float = 25.0,
        monthly_budget: float = 500.0,
    ) -> None:
        self.supabase = supabase
        self.daily_budget = daily_budget
        self.monthly_budget = monthly_budget

    def estimate_cost(self, tokens_used: int) -> float:
        """Estimate spend for a given token count."""

        return round(tokens_used * TOKEN_COST_USD, 4)

    async def track_analysis_cost(
        self,
        analysis_id: str,
        cost: float,
        tokens_used: Optional[int],
        processing_time_ms: Optional[int] = None,
    ) -> None:
        if not self.supabase:
            logger.debug("Supabase client missing; skipping cost tracking")
            return

        payload = {
            "analysis_id": analysis_id,
            "api_cost": float(cost),
            "tokens_used": int(tokens_used or 0),
            "processing_time_ms": processing_time_ms,
        }

        try:
            self.supabase.table("smartscope_costs").insert(payload).execute()
        except Exception as exc:  # pragma: no cover - supabase failure path
            logger.exception("Failed to record SmartScope cost entry: %s", exc)

    async def check_budget_status(self) -> Dict[str, Any]:
        if not self.supabase:
            return {
                "status": "unavailable",
                "message": "Supabase client not configured",
            }

        now = datetime.now(timezone.utc)
        daily_total = self._sum_costs_since(now - timedelta(days=1))
        monthly_total = self._sum_costs_since(now - timedelta(days=30))

        daily_usage = (
            (daily_total / self.daily_budget) * 100 if self.daily_budget else 0
        )
        monthly_usage = (
            (monthly_total / self.monthly_budget) * 100 if self.monthly_budget else 0
        )

        status = "green"
        if daily_usage > 90 or monthly_usage > 90:
            status = "red"
        elif daily_usage > 70 or monthly_usage > 70:
            status = "amber"

        return {
            "status": status,
            "daily_spend": round(daily_total, 4),
            "monthly_spend": round(monthly_total, 4),
            "daily_budget": self.daily_budget,
            "monthly_budget": self.monthly_budget,
            "daily_usage_percent": round(daily_usage, 2),
            "monthly_usage_percent": round(monthly_usage, 2),
        }

    async def generate_cost_report(self, timeframe: str = "30d") -> Dict[str, Any]:
        if not self.supabase:
            return {
                "timeframe": timeframe,
                "total_cost": 0.0,
                "analyses": 0,
                "average_cost": 0.0,
            }

        timeframe = timeframe.lower()
        now = datetime.now(timezone.utc)
        if timeframe.endswith("d"):
            days = int(timeframe[:-1])
            since = now - timedelta(days=days)
        elif timeframe.endswith("w"):
            weeks = int(timeframe[:-1])
            since = now - timedelta(weeks=weeks)
        else:
            since = now - timedelta(days=30)

        records = self._fetch_costs_since(since)
        total_cost = sum(float(record.get("api_cost") or 0.0) for record in records)
        analyses = len(records)

        return {
            "timeframe": timeframe,
            "total_cost": round(total_cost, 4),
            "analyses": analyses,
            "average_cost": round(total_cost / analyses, 4) if analyses else 0.0,
        }

    def send_budget_alert(self, usage_percent: float) -> None:
        if usage_percent >= 100:
            logger.warning("SmartScope budget exceeded: %.2f%%", usage_percent)
        elif usage_percent >= 80:
            logger.info("SmartScope budget warning: %.2f%% used", usage_percent)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _fetch_costs_since(self, since: datetime) -> List[Dict[str, Any]]:
        if not self.supabase:
            return []

        response = (
            self.supabase.table("smartscope_costs")
            .select("api_cost, created_at")
            .gte("created_at", since.isoformat())
            .execute()
        )
        return response.data or []

    def _sum_costs_since(self, since: datetime) -> float:
        records = self._fetch_costs_since(since)
        return sum(float(record.get("api_cost") or 0.0) for record in records)


__all__ = ["CostMonitor"]
