"""Tenant management routes."""

from __future__ import annotations

from typing import Any

from deps import require_operation
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from context_iam.identity import Principal
from context_tenancy.store import TenantConfig, get_tenant_store

router = APIRouter(prefix="/tenants", tags=["tenants"])


class TenantPayload(BaseModel):
    tenant_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    enabled_skills: list[str] = Field(default_factory=list)
    llm_provider: str = "offline"
    pricing_tier: str = "default"
    region: str = "default"


@router.get("")
def list_tenants(_: Principal = Depends(require_operation("tenants:manage"))) -> dict[str, Any]:
    tenants = [t.to_dict() for t in get_tenant_store().list_tenants()]
    return {"tenants": tenants}


@router.post("", status_code=201)
def create_tenant(
    payload: TenantPayload,
    _: Principal = Depends(require_operation("tenants:manage")),
) -> dict[str, Any]:
    cfg = TenantConfig(**payload.model_dump())
    return get_tenant_store().upsert(cfg).to_dict()


@router.get("/{tenant_id}")
def get_tenant(
    tenant_id: str,
    principal: Principal = Depends(require_operation("tenants:manage")),
) -> dict[str, Any]:
    if principal.tenant_id != tenant_id and "admin" not in principal.roles:
        raise HTTPException(status_code=403, detail="Cross-tenant access denied")
    try:
        return get_tenant_store().require(tenant_id).to_dict()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
