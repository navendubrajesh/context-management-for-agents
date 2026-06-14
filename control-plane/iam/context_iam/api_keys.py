"""API key authentication for service-to-service callers."""

from __future__ import annotations

from context_iam.config import AuthConfig
from context_iam.identity import Principal


def parse_api_keys(raw: str | None) -> dict[str, tuple[str, str]]:
    """Parse CONTEXT_SKILLS_API_KEYS as key_id:role:tenant_id entries."""
    if not raw:
        return {}
    mapping: dict[str, tuple[str, str]] = {}
    for entry in raw.split(","):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split(":")
        if len(parts) != 3:
            continue
        key_id, role, tenant_id = parts
        mapping[key_id] = (role, tenant_id)
    return mapping


def validate_api_key(key: str, config: AuthConfig) -> Principal:
    mapping = parse_api_keys(config.api_keys_raw)
    if key not in mapping:
        raise ValueError("Invalid API key")
    role, tenant_id = mapping[key]
    return Principal(
        subject=f"api-key:{key}",
        tenant_id=tenant_id,
        roles=(role,),
        auth_method="api_key",
        claims={"key_id": key},
    )
