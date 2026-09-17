"""Tenant-scoped self-service for tenant admins (CM-058)."""

from __future__ import annotations

from typing import Any

from deps import require_operation
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from context_finops.quotas import get_quota_store
from context_iam.identity import Principal
from context_iam.scim import get_scim_store
from context_tenancy.store import TenantConfig, get_tenant_store

router = APIRouter(prefix="/tenant-admin", tags=["tenant-admin"])


class SkillsUpdatePayload(BaseModel):
    enabled_skills: list[str] = Field(default_factory=list)


class InviteUserPayload(BaseModel):
    email: str = Field(..., min_length=3)
    display_name: str = ""
    roles: list[str] = Field(default_factory=lambda: ["viewer"])


@router.get("/overview")
def tenant_overview(
    principal: Principal = Depends(require_operation("tenant:self")),
) -> dict[str, Any]:
    tenant = get_tenant_store().require(principal.tenant_id)
    store = get_quota_store()
    quota = store.get(principal.tenant_id)
    used, limit = store.usage_snapshot(principal.tenant_id)
    used_pct = round((used / limit) * 100, 2) if limit else 0.0
    users = [u.to_scim() for u in get_scim_store().list_users() if u.tenant_id == principal.tenant_id]
    return {
        "tenant": tenant.to_dict(),
        "quota": quota.__dict__ if quota else None,
        "usage": {"tokens_used": used, "token_limit": limit, "used_pct": used_pct},
        "users": users,
    }


@router.patch("/skills")
def update_tenant_skills(
    body: SkillsUpdatePayload,
    principal: Principal = Depends(require_operation("tenant:self")),
) -> dict[str, Any]:
    tenant = get_tenant_store().require(principal.tenant_id)
    updated = TenantConfig(
        tenant_id=tenant.tenant_id,
        name=tenant.name,
        enabled_skills=list(body.enabled_skills),
        llm_provider=tenant.llm_provider,
        pricing_tier=tenant.pricing_tier,
        region=tenant.region,
    )
    return get_tenant_store().upsert(updated).to_dict()


@router.post("/users/invite", status_code=201)
def invite_tenant_user(
    body: InviteUserPayload,
    principal: Principal = Depends(require_operation("tenant:self")),
) -> dict[str, Any]:
    user = get_scim_store().create_user(
        {
            "userName": body.email,
            "displayName": body.display_name or body.email,
            "roles": body.roles,
            "tenantId": principal.tenant_id,
        }
    )
    return user.to_scim()


@router.get("/users")
def list_tenant_users(
    principal: Principal = Depends(require_operation("tenant:self")),
) -> dict[str, Any]:
    users = [u.to_scim() for u in get_scim_store().list_users() if u.tenant_id == principal.tenant_id]
    return {"tenant_id": principal.tenant_id, "users": users}
