"""SCIM 2.0 provisioning routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from context_iam.identity import Principal
from context_iam.scim import get_scim_store
from deps import require_operation

router = APIRouter(prefix="/scim/v2", tags=["scim"])


@router.get("/Users")
def list_users(_: Principal = Depends(require_operation("scim:manage"))) -> dict[str, Any]:
    users = [u.to_scim() for u in get_scim_store().list_users()]
    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
        "totalResults": len(users),
        "Resources": users,
    }


@router.post("/Users", status_code=201)
def create_user(
    payload: dict[str, Any],
    _: Principal = Depends(require_operation("scim:manage")),
) -> dict[str, Any]:
    if not payload.get("userName"):
        raise HTTPException(status_code=400, detail="userName required")
    return get_scim_store().create_user(payload).to_scim()


@router.get("/Groups")
def list_groups(_: Principal = Depends(require_operation("scim:manage"))) -> dict[str, Any]:
    groups = [g.to_scim() for g in get_scim_store().list_groups()]
    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
        "totalResults": len(groups),
        "Resources": groups,
    }


@router.post("/Groups", status_code=201)
def create_group(
    payload: dict[str, Any],
    _: Principal = Depends(require_operation("scim:manage")),
) -> dict[str, Any]:
    if not payload.get("displayName"):
        raise HTTPException(status_code=400, detail="displayName required")
    return get_scim_store().create_group(payload).to_scim()
