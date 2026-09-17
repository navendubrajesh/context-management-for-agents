"""Staged policy bundle rollout — per-tenant pins, canary, rollback (CM-039)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from context_policy.bundle_info import bundle_version


@dataclass
class RolloutState:
    active_version: str
    canary_version: str | None = None
    canary_tenants: set[str] = field(default_factory=set)
    tenant_pins: dict[str, str] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)


class PolicyRolloutStore:
    """In-memory rollout controller; swap for Postgres in production."""

    def __init__(self) -> None:
        self._state = RolloutState(active_version=bundle_version())

    def resolve_version(self, tenant_id: str) -> str:
        if tenant_id in self._state.tenant_pins:
            return self._state.tenant_pins[tenant_id]
        if tenant_id in self._state.canary_tenants and self._state.canary_version:
            return self._state.canary_version
        return self._state.active_version

    def rollout(
        self,
        *,
        version: str,
        tenant_ids: list[str] | None = None,
        canary: bool = False,
    ) -> dict[str, Any]:
        previous = self._state.active_version
        if canary:
            self._state.canary_version = version
            self._state.canary_tenants = set(tenant_ids or [])
            action = "canary"
        else:
            self._state.active_version = version
            self._state.canary_version = None
            self._state.canary_tenants.clear()
            if tenant_ids:
                for tenant in tenant_ids:
                    self._state.tenant_pins[tenant] = version
            action = "full" if not tenant_ids else "tenant_pin"
        event = {
            "action": action,
            "version": version,
            "previous": previous,
            "tenant_ids": tenant_ids or [],
            "at": datetime.now(timezone.utc).isoformat(),
        }
        self._state.history.append(event)
        return event

    def rollback(self) -> dict[str, Any]:
        if len(self._state.history) < 2:
            target = bundle_version()
        else:
            target = self._state.history[-2]["version"]
        previous = self._state.active_version
        self._state.active_version = target
        self._state.canary_version = None
        self._state.canary_tenants.clear()
        event = {
            "action": "rollback",
            "version": target,
            "previous": previous,
            "at": datetime.now(timezone.utc).isoformat(),
        }
        self._state.history.append(event)
        return event

    def status(self) -> dict[str, Any]:
        return {
            "active_version": self._state.active_version,
            "canary_version": self._state.canary_version,
            "canary_tenants": sorted(self._state.canary_tenants),
            "tenant_pins": dict(self._state.tenant_pins),
            "history": list(self._state.history),
        }


_STORE: PolicyRolloutStore | None = None


def get_rollout_store() -> PolicyRolloutStore:
    global _STORE
    if _STORE is None:
        _STORE = PolicyRolloutStore()
    return _STORE
