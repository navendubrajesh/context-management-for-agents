"""Request-scoped tenant context."""

from __future__ import annotations

from contextvars import ContextVar

_tenant_id: ContextVar[str | None] = ContextVar("tenant_id", default=None)


def set_tenant_id(tenant_id: str | None) -> None:
    _tenant_id.set(tenant_id)


def current_tenant_id(default: str = "default") -> str:
    return _tenant_id.get() or default
