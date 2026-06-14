"""In-memory and JSONL usage sinks."""

from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Protocol

from context_skills.metering.usage import UsageRecord


class UsageSink(Protocol):
    def emit(self, record: UsageRecord) -> None: ...


class InMemoryUsageSink:
    def __init__(self, *, max_records: int = 1000) -> None:
        self.max_records = max_records
        self._records: list[UsageRecord] = []
        self._lock = Lock()

    def emit(self, record: UsageRecord) -> None:
        with self._lock:
            self._records.append(record)
            if len(self._records) > self.max_records:
                self._records = self._records[-self.max_records :]

    def recent(self, limit: int = 50) -> list[dict]:
        with self._lock:
            items = self._records[-limit:]
        return [item.to_dict() for item in reversed(items)]

    def clear(self) -> None:
        with self._lock:
            self._records.clear()


class JsonlUsageSink:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def emit(self, record: UsageRecord) -> None:
        line = json.dumps(record.to_dict(), ensure_ascii=False)
        with self._lock:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")


_GLOBAL_SINK = InMemoryUsageSink()


def get_usage_sink() -> InMemoryUsageSink:
    return _GLOBAL_SINK


def emit_usage(record: UsageRecord) -> None:
    _GLOBAL_SINK.emit(record)
