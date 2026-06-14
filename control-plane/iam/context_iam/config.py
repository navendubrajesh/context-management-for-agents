"""Authentication configuration — fully operator-driven, no hardcoded IdP."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AuthConfig:
    mode: str
    oidc_issuer: str | None
    oidc_audience: str | None
    oidc_jwks_uri: str | None
    oidc_hmac_secret: str | None
    saml_entity_id: str | None
    saml_metadata_url: str | None
    api_keys_raw: str | None


def auth_mode() -> str:
    return os.environ.get("CONTEXT_SKILLS_AUTH_MODE", "disabled").strip().lower()


def is_auth_enforced() -> bool:
    return auth_mode() == "enforced"


def load_auth_config() -> AuthConfig:
    return AuthConfig(
        mode=auth_mode(),
        oidc_issuer=os.environ.get("CONTEXT_SKILLS_OIDC_ISSUER"),
        oidc_audience=os.environ.get("CONTEXT_SKILLS_OIDC_AUDIENCE"),
        oidc_jwks_uri=os.environ.get("CONTEXT_SKILLS_OIDC_JWKS_URI"),
        oidc_hmac_secret=os.environ.get("CONTEXT_SKILLS_OIDC_HMAC_SECRET"),
        saml_entity_id=os.environ.get("CONTEXT_SKILLS_SAML_ENTITY_ID"),
        saml_metadata_url=os.environ.get("CONTEXT_SKILLS_SAML_METADATA_URL"),
        api_keys_raw=os.environ.get("CONTEXT_SKILLS_API_KEYS"),
    )
