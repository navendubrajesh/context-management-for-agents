"""Usage records emitted per primitive / route / skill call."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class UsageRecord:
    operation: str
    tokens_before: int
    tokens_after: int
    est_cost_usd: float | None
    correlation_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tenant_id: str | None = None
    skill: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def tokens_saved(self) -> int:
        return max(0, self.tokens_before - self.tokens_after)

    @property
    def savings_pct(self) -> float:
        if self.tokens_before == 0:
            return 0.0
        return (1 - self.tokens_after / self.tokens_before) * 100

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "tokens_before": self.tokens_before,
            "tokens_after": self.tokens_after,
            "tokens_saved": self.tokens_saved,
            "savings_pct": round(self.savings_pct, 1),
            "est_cost_usd": self.est_cost_usd,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "tenant_id": self.tenant_id,
            "skill": self.skill,
            "metadata": self.metadata,
        }


def new_correlation_id() -> str:
    return str(uuid.uuid4())
