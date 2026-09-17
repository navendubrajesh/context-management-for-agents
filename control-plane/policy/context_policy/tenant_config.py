"""Tenant-scoped policy configuration — shared by embedded and OPA evaluators."""

from __future__ import annotations

from typing import Any

# Operator-configurable tenant denials (mirrors bundled Rego policy inputs).
TENANT_DENIED_SKILLS: dict[str, list[str]] = {
    "tenant-c": ["advanced-evaluation"],
}

TENANT_DENIED_MODELS: dict[str, list[str]] = {
    "tenant-c": ["gpt-4o"],
}


def tenant_denials(tenant_id: str) -> dict[str, list[str]]:
    """Return denied skills/models for a tenant."""
    return {
        "denied_skills": list(TENANT_DENIED_SKILLS.get(tenant_id, [])),
        "denied_models": list(TENANT_DENIED_MODELS.get(tenant_id, [])),
    }


def enrich_policy_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Ensure OPA input includes tenant-scoped denials for Rego bundle evaluation."""
    enriched = dict(payload)
    tenant_id = str(enriched.get("tenant_id", "default"))
    denials = tenant_denials(tenant_id)

    skills = list(enriched.get("denied_skills") or [])
    models = list(enriched.get("denied_models") or [])
    for skill in denials["denied_skills"]:
        if skill not in skills:
            skills.append(skill)
    for model in denials["denied_models"]:
        if model not in models:
            models.append(model)

    enriched["denied_skills"] = skills
    enriched["denied_models"] = models
    return enriched
