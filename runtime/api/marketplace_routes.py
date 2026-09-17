"""Marketplace registry API — search, submit, install (CM-408/409)."""

from __future__ import annotations

from typing import Any

from deps import require_operation
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from context_iam.identity import Principal
from context_marketplace.store import get_marketplace_store
from context_policy.approvals import get_approval_store

try:
    from context_audit.log import get_audit_log
except ImportError:
    get_audit_log = None

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


class SubmitPayload(BaseModel):
    name: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    description: str = ""


@router.get("")
def search_marketplace(
    q: str = "",
    _: Principal = Depends(require_operation("skills:read")),
) -> dict[str, Any]:
    return {"entries": get_marketplace_store().search(q)}


@router.get("/catalog")
def tenant_marketplace_catalog(
    principal: Principal = Depends(require_operation("skills:read")),
) -> dict[str, Any]:
    skills = get_marketplace_store().tenant_catalog(principal.tenant_id)
    return {"tenant_id": principal.tenant_id, "skills": skills}


@router.post("/submit", status_code=201)
def submit_to_marketplace(
    body: SubmitPayload,
    principal: Principal = Depends(require_operation("skills:publish")),
) -> dict[str, Any]:
    approval = get_approval_store().create(
        "marketplace:publish",
        principal.tenant_id,
        principal.subject,
        {"name": body.name, "version": body.version},
    )
    entry = get_marketplace_store().submit(
        name=body.name,
        version=body.version,
        description=body.description,
        publisher=principal.subject,
        tenant_id=principal.tenant_id,
        approval_id=approval.id,
    )
    if get_audit_log:
        get_audit_log().append(
            event_type="marketplace.submit",
            actor=principal.subject,
            tenant_id=principal.tenant_id,
            correlation_id="",
            detail={"entry_id": entry.id, "approval_id": approval.id},
        )
    return {"entry": entry.to_dict(), "approval": approval.to_dict()}


@router.post("/{entry_id}/install")
def install_marketplace_skill(
    entry_id: str,
    principal: Principal = Depends(require_operation("skills:publish")),
) -> dict[str, Any]:
    store = get_marketplace_store()
    entry = store.get(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    if entry.status != "published":
        raise HTTPException(status_code=409, detail="Entry pending approval")
    try:
        result = store.install(entry_id, principal.tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if get_audit_log:
        get_audit_log().append(
            event_type="marketplace.install",
            actor=principal.subject,
            tenant_id=principal.tenant_id,
            correlation_id="",
            detail=result,
        )
    return result
