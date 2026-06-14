"""Approval workflow routes."""

from __future__ import annotations

from typing import Any

from deps import require_operation
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from context_iam.identity import Principal
from context_policy.approvals import get_approval_store

router = APIRouter(prefix="/approvals", tags=["approvals"])


class CreateApprovalPayload(BaseModel):
    operation: str = Field(..., min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)


class DecidePayload(BaseModel):
    approve: bool
    reason: str = ""


@router.get("")
def list_approvals(
    principal: Principal = Depends(require_operation("approvals:manage")),
) -> dict[str, Any]:
    pending = get_approval_store().list_pending(tenant_id=principal.tenant_id)
    return {"approvals": [item.to_dict() for item in pending]}


@router.post("", status_code=201)
def create_approval(
    body: CreateApprovalPayload,
    principal: Principal = Depends(require_operation("skills:publish")),
) -> dict[str, Any]:
    req = get_approval_store().create(
        body.operation,
        principal.tenant_id,
        principal.subject,
        body.payload,
    )
    return req.to_dict()


@router.post("/{approval_id}/decide")
def decide_approval(
    approval_id: str,
    body: DecidePayload,
    principal: Principal = Depends(require_operation("approvals:manage")),
) -> dict[str, Any]:
    try:
        req = get_approval_store().decide(
            approval_id,
            approver=principal.subject,
            approve=body.approve,
            reason=body.reason,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if req.tenant_id != principal.tenant_id and "admin" not in principal.roles:
        raise HTTPException(status_code=403, detail="Cross-tenant approval denied")
    return req.to_dict()
