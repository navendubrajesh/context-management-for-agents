"""FinOps routes — chargeback, pricing, quota, and budget alerts (CM-044/056/603)."""

from __future__ import annotations

from typing import Any

from deps import require_operation
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from context_finops.alerts import get_budget_alert_store
from context_finops.quota_alerts import get_quota_alert_store
from context_finops.chargeback import chargeback_report
from context_finops.quotas import get_quota_store
from context_iam.identity import Principal
from context_skills.metering import get_usage_sink
from context_skills.metering.pricing import get_model_pricing, load_pricing_table, save_pricing_table

router = APIRouter(prefix="/finops", tags=["finops"])


@router.get("/chargeback")
def get_chargeback(
    date_from: str | None = None,
    date_to: str | None = None,
    principal: Principal = Depends(require_operation("usage:read")),
) -> dict[str, Any]:
    records = get_usage_sink().recent(limit=1000, tenant_id=principal.tenant_id)
    return chargeback_report(records, date_from=date_from, date_to=date_to)


@router.get("/pricing")
def get_pricing(
    _: Principal = Depends(require_operation("usage:read")),
) -> dict[str, Any]:
    return load_pricing_table()


class PricingUpdatePayload(BaseModel):
    table: dict[str, Any]


@router.put("/pricing")
def update_pricing(
    body: PricingUpdatePayload,
    _: Principal = Depends(require_operation("tenants:manage")),
) -> dict[str, str]:
    if "models" not in body.table:
        raise HTTPException(status_code=400, detail="pricing table must include models")
    save_pricing_table(body.table)
    sample = get_model_pricing()
    return {"status": "updated", "sample_model": sample.model, "tier": sample.tier}


class BudgetAlertPayload(BaseModel):
    threshold_pct: float = Field(..., ge=1, le=100)
    callback_url: str = Field(..., min_length=8)


@router.put("/alerts/budget")
def configure_budget_alert(
    body: BudgetAlertPayload,
    principal: Principal = Depends(require_operation("tenants:manage")),
) -> dict[str, Any]:
    cfg = get_budget_alert_store().set_config(
        principal.tenant_id,
        threshold_pct=body.threshold_pct,
        callback_url=body.callback_url,
    )
    return {"tenant_id": principal.tenant_id, "threshold_pct": cfg.threshold_pct, "callback_url": cfg.callback_url}


class QuotaAlertPayload(BaseModel):
    callback_url: str = Field(..., min_length=8)
    thresholds: list[float] = Field(default_factory=lambda: [80.0, 95.0])


@router.put("/alerts/quota")
def configure_quota_alerts(
    body: QuotaAlertPayload,
    principal: Principal = Depends(require_operation("tenants:manage")),
) -> dict[str, Any]:
    cfg = get_quota_alert_store().set_config(
        principal.tenant_id,
        callback_url=body.callback_url,
        thresholds=tuple(sorted(body.thresholds)),
    )
    return {
        "tenant_id": principal.tenant_id,
        "callback_url": cfg.callback_url,
        "thresholds": list(cfg.thresholds),
    }


@router.get("/alerts/quota")
def get_quota_alert_config(
    principal: Principal = Depends(require_operation("usage:read")),
) -> dict[str, Any]:
    cfg = get_quota_alert_store().get_config(principal.tenant_id)
    if cfg is None:
        return {"tenant_id": principal.tenant_id, "configured": False}
    return {
        "tenant_id": principal.tenant_id,
        "configured": True,
        "callback_url": cfg.callback_url,
        "thresholds": list(cfg.thresholds),
        "fired_thresholds": sorted(cfg.fired),
    }


@router.get("/quota")
def get_quota_status(
    principal: Principal = Depends(require_operation("usage:read")),
) -> dict[str, Any]:
    store = get_quota_store()
    quota = store.get(principal.tenant_id)
    allowed, reason = store.check(principal.tenant_id)
    used, limit = store.usage_snapshot(principal.tenant_id)
    used_pct = round((used / limit) * 100, 2) if limit else 0.0
    return {
        "tenant_id": principal.tenant_id,
        "quota": quota.__dict__ if quota else None,
        "usage": {"tokens_used": used, "token_limit": limit, "used_pct": used_pct},
        "allowed": allowed,
        "reason": reason,
    }
