"""Data lineage for context primitive operations."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Any


def content_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class LineageRecord:
    id: str
    operation: str
    tenant_id: str
    correlation_id: str
    input_hash: str
    output_hash: str
    capture_payload: bool = False
    input_ref: str | None = None
    output_ref: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "operation": self.operation,
            "tenant_id": self.tenant_id,
            "correlation_id": self.correlation_id,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "capture_payload": self.capture_payload,
            "input_ref": self.input_ref,
            "output_ref": self.output_ref,
            "timestamp": self.timestamp,
        }


class LineageStore:
    def __init__(self) -> None:
        self._records: list[LineageRecord] = []
        self._lock = Lock()

    def record(
        self,
        *,
        operation: str,
        tenant_id: str,
        correlation_id: str,
        input_value: Any,
        output_value: Any,
        capture_payload: bool = False,
    ) -> LineageRecord:
        rec = LineageRecord(
            id=str(uuid.uuid4()),
            operation=operation,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            input_hash=content_hash(input_value),
            output_hash=content_hash(output_value),
            capture_payload=capture_payload,
            input_ref=str(input_value)[:200] if capture_payload else None,
            output_ref=str(output_value)[:200] if capture_payload else None,
        )
        with self._lock:
            self._records.append(rec)
        return rec

    def recent(self, tenant_id: str | None = None, limit: int = 50) -> list[LineageRecord]:
        with self._lock:
            items = list(self._records)
        if tenant_id:
            items = [r for r in items if r.tenant_id == tenant_id]
        return list(reversed(items[-limit:]))

    def clear(self) -> None:
        with self._lock:
            self._records.clear()


_GLOBAL = LineageStore()


def get_lineage_store() -> LineageStore:
    return _GLOBAL
