"""Audit log and lineage routes."""

from __future__ import annotations

from typing import Any

from deps import require_operation
from fastapi import APIRouter, Depends, Response

from context_audit.log import get_audit_log
from context_audit.lineage import get_lineage_store
from context_iam.identity import Principal

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/events")
def list_audit_events(
    limit: int = 100,
    principal: Principal = Depends(require_operation("audit:read")),
) -> dict[str, Any]:
    events = get_audit_log().events(tenant_id=principal.tenant_id, limit=limit)
    return {"events": [e.to_dict() for e in events], "chain_valid": get_audit_log().verify_chain()}


@router.get("/export")
def export_audit(
    principal: Principal = Depends(require_operation("audit:read")),
) -> Response:
    return Response(content=get_audit_log().export_jsonl(), media_type="application/x-ndjson")


@router.get("/lineage")
def list_lineage(
    limit: int = 50,
    principal: Principal = Depends(require_operation("audit:read")),
) -> dict[str, Any]:
    records = get_lineage_store().recent(tenant_id=principal.tenant_id, limit=limit)
    return {"records": [r.to_dict() for r in records]}
