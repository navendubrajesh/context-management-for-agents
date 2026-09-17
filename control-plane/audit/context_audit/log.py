"""Tamper-evident append-only audit log with hash chain."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Any

try:
    from context_storage.database import is_database_enabled
    from context_storage.repositories import AuditRepository
except ImportError:
    is_database_enabled = lambda: False  # noqa: E731
    AuditRepository = None


def _audit_repo() -> AuditRepository | None:
    if not is_database_enabled() or AuditRepository is None:
        return None
    return AuditRepository()


def _hash_payload(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class AuditEvent:
    id: str
    timestamp: str
    event_type: str
    actor: str
    tenant_id: str
    correlation_id: str
    detail: dict[str, Any]
    prev_hash: str
    event_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "actor": self.actor,
            "tenant_id": self.tenant_id,
            "correlation_id": self.correlation_id,
            "detail": self.detail,
            "prev_hash": self.prev_hash,
            "event_hash": self.event_hash,
        }


class AuditLog:
    GENESIS = "0" * 64

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []
        self._lock = Lock()

    def _compute_hash(self, event_id: str, prev_hash: str, body: dict[str, Any]) -> str:
        canonical = json.dumps(
            {"id": event_id, "prev_hash": prev_hash, **body},
            sort_keys=True,
            separators=(",", ":"),
        )
        return _hash_payload(canonical)

    def append(
        self,
        *,
        event_type: str,
        actor: str,
        tenant_id: str,
        correlation_id: str,
        detail: dict[str, Any] | None = None,
    ) -> AuditEvent:
        detail = detail or {}
        with self._lock:
            prev = self._events[-1].event_hash if self._events else self.GENESIS
            event_id = str(uuid.uuid4())
            ts = datetime.now(timezone.utc).isoformat()
            body = {
                "timestamp": ts,
                "event_type": event_type,
                "actor": actor,
                "tenant_id": tenant_id,
                "correlation_id": correlation_id,
                "detail": detail,
            }
            event_hash = self._compute_hash(event_id, prev, body)
            event = AuditEvent(
                id=event_id,
                prev_hash=prev,
                event_hash=event_hash,
                **body,
            )
            self._events.append(event)
            repo = _audit_repo()
            if repo is not None:
                repo.append(event.to_dict())
            return event

    def events(self, tenant_id: str | None = None, limit: int = 100) -> list[AuditEvent]:
        with self._lock:
            items = list(self._events)
        if tenant_id:
            items = [e for e in items if e.tenant_id == tenant_id]
        return list(reversed(items[-limit:]))

    def verify_chain(self) -> bool:
        with self._lock:
            prev = self.GENESIS
            for event in self._events:
                if event.prev_hash != prev:
                    return False
                body = {
                    "timestamp": event.timestamp,
                    "event_type": event.event_type,
                    "actor": event.actor,
                    "tenant_id": event.tenant_id,
                    "correlation_id": event.correlation_id,
                    "detail": event.detail,
                }
                expected = self._compute_hash(event.id, prev, body)
                if event.event_hash != expected:
                    return False
                prev = event.event_hash
        return True

    def export_jsonl(self) -> str:
        return "\n".join(json.dumps(e.to_dict()) for e in self._events)

    def clear(self) -> None:
        with self._lock:
            self._events.clear()


_GLOBAL = AuditLog()


def get_audit_log() -> AuditLog:
    return _GLOBAL
