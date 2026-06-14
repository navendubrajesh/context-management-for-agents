"""Default allow-all policy hook — Phase 3 extension point."""

from __future__ import annotations

from typing import Any


def evaluate_policy(operation: str, context: dict[str, Any] | None = None) -> bool:
    """Return True when an operation is permitted. Always allow-all in Phase 2."""
    _ = (operation, context)
    return True
