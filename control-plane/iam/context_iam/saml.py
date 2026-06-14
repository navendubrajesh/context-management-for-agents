"""SAML assertion validation — config-driven metadata; mock-friendly for tests."""

from __future__ import annotations

import base64
import json
from typing import Any

from context_iam.config import AuthConfig
from context_iam.identity import Principal


class SAMLValidationError(Exception):
    pass


def validate_saml_assertion(assertion_b64: str, config: AuthConfig) -> Principal:
    """
    Validate a base64-encoded SAML assertion payload.

    Production deployments should wire a full SAML library against `config.saml_metadata_url`.
    For offline tests, assertions may be base64-encoded JSON with keys: sub, tenant_id, roles.
    """
    if not config.saml_entity_id:
        raise SAMLValidationError("SAML entity ID not configured")

    try:
        raw = base64.b64decode(assertion_b64)
        payload = json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, ValueError) as exc:
        raise SAMLValidationError("Invalid SAML assertion encoding") from exc

    if payload.get("aud") != config.saml_entity_id:
        raise SAMLValidationError("SAML audience mismatch")

    roles_raw = payload.get("roles", ["viewer"])
    roles = tuple(roles_raw) if isinstance(roles_raw, list) else (str(roles_raw),)
    return Principal(
        subject=str(payload["sub"]),
        tenant_id=str(payload.get("tenant_id", "default")),
        roles=roles,
        auth_method="saml",
        claims=payload,
    )
