"""In-memory eval result store — queryable by run id."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Any


@dataclass
class EvalRunRecord:
    id: str
    created_at: str
    passed: bool
    checks: list[dict[str, Any]] = field(default_factory=list)
    judge: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "passed": self.passed,
            "checks": self.checks,
            "judge": self.judge,
            "metadata": self.metadata,
        }


class EvalStore:
    def __init__(self) -> None:
        self._runs: dict[str, EvalRunRecord] = {}
        self._lock = Lock()

    def save(
        self,
        *,
        passed: bool,
        checks: list[dict[str, Any]],
        judge: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> EvalRunRecord:
        run_id = str(uuid.uuid4())
        record = EvalRunRecord(
            id=run_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            passed=passed,
            checks=checks,
            judge=judge,
            metadata=metadata or {},
        )
        with self._lock:
            self._runs[run_id] = record
        return record

    def get(self, run_id: str) -> EvalRunRecord | None:
        with self._lock:
            return self._runs.get(run_id)

    def list_runs(self, limit: int = 50) -> list[EvalRunRecord]:
        with self._lock:
            items = list(self._runs.values())
        return list(reversed(items[-limit:]))

    def clear(self) -> None:
        with self._lock:
            self._runs.clear()


_GLOBAL = EvalStore()


def get_eval_store() -> EvalStore:
    return _GLOBAL
