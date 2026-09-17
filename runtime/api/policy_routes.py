"""Policy bundle metadata and rollout endpoints (CM-038/039)."""

from __future__ import annotations

from typing import Any

from deps import require_operation
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from context_iam.identity import Principal
from context_policy.bundle_info import bundle_version, load_bundle_manifest
from context_policy.rollout import get_rollout_store

router = APIRouter(prefix="/policy", tags=["policy"])


@router.get("/version")
def policy_version(request: Request) -> dict[str, Any]:
    manifest = load_bundle_manifest()
    tenant_id = getattr(request.state, "tenant_id", None) or "default"
    resolved = get_rollout_store().resolve_version(tenant_id)
    return {
        "bundle": manifest.get("name", "contextskills"),
        "version": resolved,
        "default_version": bundle_version(),
        "tenant_id": tenant_id,
        "rego_files": manifest.get("rego_files", []),
        "updated": manifest.get("updated"),
    }


class RolloutPayload(BaseModel):
    version: str = Field(..., min_length=1)
    tenant_ids: list[str] = Field(default_factory=list)
    canary: bool = False


@router.get("/rollout/status")
def rollout_status(
    _: Principal = Depends(require_operation("policies:manage")),
) -> dict[str, Any]:
    return get_rollout_store().status()


@router.post("/rollout")
def policy_rollout(
    body: RolloutPayload,
    _: Principal = Depends(require_operation("policies:manage")),
) -> dict[str, Any]:
    event = get_rollout_store().rollout(
        version=body.version,
        tenant_ids=body.tenant_ids or None,
        canary=body.canary,
    )
    return {"status": "ok", "event": event}


@router.post("/rollback")
def policy_rollback(
    _: Principal = Depends(require_operation("policies:manage")),
) -> dict[str, Any]:
    event = get_rollout_store().rollback()
    return {"status": "ok", "event": event}
