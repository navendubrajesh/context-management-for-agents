"""OIDC JWT validation — JWKS or HMAC for mock/local IdP."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

import jwt

from context_iam.config import AuthConfig
from context_iam.identity import Principal

_JWKS_CACHE: dict[str, Any] | None = None


def _load_jwks(uri: str) -> dict[str, Any]:
    global _JWKS_CACHE
    if _JWKS_CACHE is not None:
        return _JWKS_CACHE
    request = urllib.request.Request(uri, headers={"Accept": "application/json"})  # noqa: S310
    with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310
        _JWKS_CACHE = json.loads(response.read().decode("utf-8"))
    return _JWKS_CACHE


def validate_oidc_token(token: str, config: AuthConfig) -> Principal:
    if config.oidc_hmac_secret:
        claims = jwt.decode(
            token,
            config.oidc_hmac_secret,
            algorithms=["HS256"],
            audience=config.oidc_audience,
            issuer=config.oidc_issuer,
            options={"require": ["exp", "sub"]},
        )
    elif config.oidc_jwks_uri:
        jwks = _load_jwks(config.oidc_jwks_uri)
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
        if key is None and jwks.get("keys"):
            key = jwks["keys"][0]
        if key is None:
            raise jwt.InvalidTokenError("No matching JWK")
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
        claims = jwt.decode(
            token,
            public_key,
            algorithms=[header.get("alg", "RS256")],
            audience=config.oidc_audience,
            issuer=config.oidc_issuer,
            options={"require": ["exp", "sub"]},
        )
    else:
        raise jwt.InvalidTokenError("OIDC not configured (set JWKS URI or HMAC secret)")

    roles = _claims_to_roles(claims)
    tenant_id = str(claims.get("tenant_id") or claims.get("tid") or "default")
    return Principal(
        subject=str(claims["sub"]),
        tenant_id=tenant_id,
        roles=roles,
        auth_method="oidc",
        claims=dict(claims),
    )


def _claims_to_roles(claims: dict[str, Any]) -> tuple[str, ...]:
    raw = claims.get("roles") or claims.get("groups") or claims.get("role") or "viewer"
    if isinstance(raw, str):
        return tuple(r.strip() for r in raw.split(",") if r.strip())
    if isinstance(raw, list):
        return tuple(str(r) for r in raw)
    return ("viewer",)


def reset_jwks_cache() -> None:
    global _JWKS_CACHE
    _JWKS_CACHE = None
