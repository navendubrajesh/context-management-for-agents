"""Unified authentication entrypoint."""

from __future__ import annotations

from typing import Any

import jwt

from context_iam.api_keys import validate_api_key
from context_iam.config import AuthConfig, is_auth_enforced, load_auth_config
from context_iam.identity import Principal
from context_iam.oidc import validate_oidc_token
from context_iam.saml import SAMLValidationError, validate_saml_assertion

ANONYMOUS = Principal(subject="anonymous", tenant_id="default", roles=("admin",), auth_method="anonymous")


def authenticate_request(
    *,
    authorization: str | None = None,
    api_key: str | None = None,
    saml_assertion: str | None = None,
    config: AuthConfig | None = None,
) -> Principal:
    config = config or load_auth_config()
    if not is_auth_enforced():
        return ANONYMOUS

    if api_key:
        try:
            return validate_api_key(api_key, config)
        except ValueError as exc:
            raise PermissionError(str(exc)) from exc

    if saml_assertion:
        return validate_saml_assertion(saml_assertion, config)

    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        try:
            return validate_oidc_token(token, config)
        except jwt.PyJWTError as exc:
            raise PermissionError("Invalid bearer token") from exc

    raise PermissionError("Authentication required")


def principal_from_headers(headers: dict[str, str]) -> Principal:
    return authenticate_request(
        authorization=headers.get("authorization") or headers.get("Authorization"),
        api_key=headers.get("x-api-key") or headers.get("X-API-Key"),
        saml_assertion=headers.get("x-saml-assertion") or headers.get("X-SAML-Assertion"),
    )
