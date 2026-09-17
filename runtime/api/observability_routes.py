"""Session health and efficiency metrics endpoints (CM-601/602)."""

from __future__ import annotations

from typing import Any

from deps import require_operation
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from context_finops.chargeback import chargeback_report
from context_iam.identity import Principal
from context_skills.metering import get_usage_sink
from context_skills.session_health import classify_session_health

router = APIRouter(tags=["observability"])


class SessionHealthRequest(BaseModel):
    token_count: int = Field(..., ge=0)
    context_limit: int | None = Field(default=None, ge=1000)


@router.post("/session/health")
def session_health(
    body: SessionHealthRequest,
    _: Principal = Depends(require_operation("primitives:run")),
) -> dict[str, Any]:
    return classify_session_health(body.token_count, context_limit=body.context_limit)


@router.get("/metrics/efficiency")
def efficiency_metrics(
    principal: Principal = Depends(require_operation("usage:read")),
) -> dict[str, Any]:
    records = get_usage_sink().recent(limit=1000, tenant_id=principal.tenant_id)
    chargeback = chargeback_report(records)
    total_before = sum(t["tokens_before"] for t in chargeback["tenants"])
    total_after = sum(t["tokens_after"] for t in chargeback["tenants"])
    saved = max(0, total_before - total_after)
    savings_pct = round((saved / total_before) * 100, 2) if total_before else 0.0
    cost = sum(t["est_cost_usd"] for t in chargeback["tenants"])
    ops = sum(t["operations"] for t in chargeback["tenants"])
    return {
        "tenant_id": principal.tenant_id,
        "operations": ops,
        "tokens_before": total_before,
        "tokens_after": total_after,
        "tokens_saved": saved,
        "savings_pct": savings_pct,
        "est_cost_usd": round(cost, 6),
        "cost_per_operation_usd": round(cost / ops, 8) if ops else 0.0,
        "trend_by_team": chargeback["tenants"],
        "disclaimer": chargeback["disclaimer"],
    }
