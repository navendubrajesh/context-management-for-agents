"""Policy enforcement — RBAC + OPA, deny-by-default when auth is enforced."""

from __future__ import annotations

from typing import Any

try:
    from context_iam.config import is_auth_enforced
    from context_iam.rbac import authorize_operation
except ImportError:
    is_auth_enforced = lambda: False  # noqa: E731
    authorize_operation = None

try:
    from context_policy.approvals import get_approval_store
    from context_policy.engine import evaluate_opa
    from context_policy.tenant_config import enrich_policy_payload
except ImportError:
    evaluate_opa = None
    get_approval_store = None
    enrich_policy_payload = None


def evaluate_policy(operation: str, context: dict[str, Any] | None = None) -> bool:
    """Return True when an operation is permitted."""
    if not is_auth_enforced():
        return True
    context = context or {}
    principal = context.get("principal")
    if principal is None or authorize_operation is None:
        return False

    rbac_allowed = authorize_operation(principal, operation)
    if evaluate_opa is None:
        return rbac_allowed

    payload = {
        "operation": operation,
        "tenant_id": principal.tenant_id,
        "roles": list(principal.roles),
        "rbac_allowed": rbac_allowed,
        "skill": context.get("skill", ""),
        "model": context.get("model", ""),
        "denied_skills": context.get("denied_skills", []),
        "denied_models": context.get("denied_models", []),
    }
    if enrich_policy_payload is not None:
        payload = enrich_policy_payload(payload)
    decision = evaluate_opa(payload)
    if not decision.allowed:
        return False
    if decision.requires_approval:
        approval_id = context.get("approval_id")
        if not approval_id or get_approval_store is None:
            return False
        req = get_approval_store().get(approval_id)
        if req is None or req.status != "approved" or req.operation != operation:
            return False
    return True
