"""Policy enforcement — deny-by-default when auth is enforced."""

from __future__ import annotations

from typing import Any

try:
    from context_iam.config import is_auth_enforced
    from context_iam.rbac import authorize_operation
except ImportError:
    is_auth_enforced = lambda: False  # noqa: E731
    authorize_operation = None


def evaluate_policy(operation: str, context: dict[str, Any] | None = None) -> bool:
    """Return True when an operation is permitted."""
    if not is_auth_enforced():
        return True
    context = context or {}
    principal = context.get("principal")
    if principal is None or authorize_operation is None:
        return False
    return authorize_operation(principal, operation)
