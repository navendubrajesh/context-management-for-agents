"""SAML SP endpoints — metadata and assertion consumer."""

from __future__ import annotations

import os

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import Response

from context_iam.auth import authenticate_request
from context_iam.config import load_auth_config
from context_iam.saml import SAMLValidationError, generate_sp_metadata, validate_saml_assertion

router = APIRouter(prefix="/auth/saml", tags=["saml"])


def _acs_url(request: Request) -> str:
    configured = os.environ.get("CONTEXT_SKILLS_SAML_ACS_URL")
    if configured:
        return configured
    return str(request.url_for("saml_acs"))


@router.get("/metadata")
def saml_metadata(request: Request) -> Response:
    config = load_auth_config()
    xml = generate_sp_metadata(config, acs_url=_acs_url(request))
    return Response(content=xml, media_type="application/samlmetadata+xml")


@router.post("/acs")
def saml_acs(request: Request, SAMLResponse: str = Form(...)) -> dict:
    config = load_auth_config()
    try:
        principal = validate_saml_assertion(SAMLResponse, config)
    except SAMLValidationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return {
        "subject": principal.subject,
        "tenant_id": principal.tenant_id,
        "roles": list(principal.roles),
        "auth_method": principal.auth_method,
    }


@router.get("/validate-header")
def saml_validate_header(request: Request) -> dict:
    """Debug/helper endpoint — validates X-SAML-Assertion header."""
    assertion = request.headers.get("x-saml-assertion") or request.headers.get("X-SAML-Assertion")
    if not assertion:
        raise HTTPException(status_code=400, detail="X-SAML-Assertion header required")
    config = load_auth_config()
    try:
        principal = authenticate_request(saml_assertion=assertion, config=config)
    except PermissionError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return {
        "subject": principal.subject,
        "tenant_id": principal.tenant_id,
        "roles": list(principal.roles),
    }
