"""FastAPI auth dependencies — optional enforcement preserving Phase 1–2 default."""

from __future__ import annotations

from fastapi import HTTPException, Request

from context_iam.auth import authenticate_request, is_auth_enforced
from context_iam.identity import Principal
from context_iam.rbac import authorize_operation


PUBLIC_PATHS = frozenset({"/healthz", "/docs", "/openapi.json", "/redoc"})


def resolve_principal(request: Request) -> Principal:
    cached = getattr(request.state, "principal", None)
    if cached is not None:
        return cached
    try:
        principal = authenticate_request(
            authorization=request.headers.get("authorization"),
            api_key=request.headers.get("x-api-key"),
            saml_assertion=request.headers.get("x-saml-assertion"),
        )
    except PermissionError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    request.state.principal = principal
    request.state.tenant_id = principal.tenant_id
    return principal


def require_operation(operation: str):
    def _dependency(request: Request) -> Principal:
        if not is_auth_enforced() or request.url.path in PUBLIC_PATHS:
            return resolve_principal(request)
        principal = resolve_principal(request)
        if not authorize_operation(principal, operation):
            raise HTTPException(status_code=403, detail=f"Denied: {operation}")
        return principal

    return _dependency
