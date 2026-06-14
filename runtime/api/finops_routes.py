"""FinOps routes — chargeback and quota status."""

from __future__ import annotations

from typing import Any

from deps import require_operation
from fastapi import APIRouter, Depends, HTTPException

from context_finops.chargeback import chargeback_report
from context_finops.quotas import get_quota_store
from context_iam.identity import Principal
from context_skills.metering import get_usage_sink

router = APIRouter(prefix="/finops", tags=["finops"])


@router.get("/chargeback")
def get_chargeback(
    principal: Principal = Depends(require_operation("usage:read")),
) -> dict[str, Any]:
    records = get_usage_sink().recent(limit=1000, tenant_id=principal.tenant_id)
    return chargeback_report(records)


@router.get("/quota")
def get_quota_status(
    principal: Principal = Depends(require_operation("usage:read")),
) -> dict[str, Any]:
    store = get_quota_store()
    quota = store.get(principal.tenant_id)
    allowed, reason = store.check(principal.tenant_id)
    return {
        "tenant_id": principal.tenant_id,
        "quota": quota.__dict__ if quota else None,
        "allowed": allowed,
        "reason": reason,
    }
