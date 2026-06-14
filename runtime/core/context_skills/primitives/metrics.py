"""Shared metrics for runtime context primitives."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PrimitiveMetrics:
    """Token and cost metrics for a primitive invocation."""

    operation: str
    tokens_before: int
    tokens_after: int
    est_cost_usd: float | None = None

    @property
    def tokens_saved(self) -> int:
        return max(0, self.tokens_before - self.tokens_after)

    @property
    def savings_pct(self) -> float:
        if self.tokens_before == 0:
            return 0.0
        return (1 - self.tokens_after / self.tokens_before) * 100

    def to_dict(self) -> dict:
        return {
            "operation": self.operation,
            "tokens_before": self.tokens_before,
            "tokens_after": self.tokens_after,
            "tokens_saved": self.tokens_saved,
            "savings_pct": round(self.savings_pct, 1),
            "est_cost_usd": self.est_cost_usd,
        }


@dataclass(frozen=True)
class PrimitiveResult:
    """Transformed context plus metrics."""

    output: str | dict
    metrics: PrimitiveMetrics

    def to_dict(self) -> dict:
        output = self.output if isinstance(self.output, str) else self.output
        return {"output": output, "metrics": self.metrics.to_dict()}
