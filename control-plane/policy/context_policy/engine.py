"""Policy evaluation — OPA HTTP client with embedded offline fallback."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from context_policy.tenant_config import enrich_policy_payload

# Backward-compatible exports for tests and operators.
from context_policy.tenant_config import TENANT_DENIED_MODELS, TENANT_DENIED_SKILLS  # noqa: F401


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str
    requires_approval: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "requires_approval": self.requires_approval,
        }


def _approval_required_operations() -> set[str]:
    raw = os.environ.get("CONTEXT_SKILLS_APPROVAL_REQUIRED", "skills:publish,tenants:manage")
    return {item.strip() for item in raw.split(",") if item.strip()}


def _embedded_evaluate(payload: dict[str, Any]) -> PolicyDecision:
    """Mirror bundled Rego policy (contextskills.rego) for offline/dev mode."""
    if not payload.get("rbac_allowed"):
        return PolicyDecision(False, "RBAC denied")

    skill = payload.get("skill") or ""
    model = payload.get("model") or ""
    operation = payload.get("operation", "")
    denied_skills = payload.get("denied_skills") or []
    denied_models = payload.get("denied_models") or []

    if skill and skill in denied_skills:
        return PolicyDecision(False, f"Skill denied by policy: {skill}")
    if model and model in denied_models:
        return PolicyDecision(False, f"Model denied by policy: {model}")

    requires = operation in _approval_required_operations()
    return PolicyDecision(True, "allowed", requires_approval=requires)


def _parse_opa_result(result: dict[str, Any]) -> PolicyDecision:
    allowed = bool(result.get("allow"))
    requires = bool(result.get("require_approval"))
    reason = "allowed" if allowed else "OPA denied"
    return PolicyDecision(allowed, reason, requires_approval=requires)


def evaluate_opa(payload: dict[str, Any]) -> PolicyDecision:
    """Evaluate policy via OPA HTTP API, falling back to embedded Rego mirror."""
    enriched = enrich_policy_payload(payload)
    url = os.environ.get("CONTEXT_SKILLS_OPA_URL")
    if not url:
        return _embedded_evaluate(enriched)

    endpoint = url.rstrip("/") + "/v1/data/contextskills"
    body = json.dumps({"input": enriched}).encode("utf-8")
    request = urllib.request.Request(  # noqa: S310
        endpoint,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:  # noqa: S310
            data = json.loads(response.read().decode("utf-8"))
        return _parse_opa_result(data.get("result", {}))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return _embedded_evaluate(enriched)
