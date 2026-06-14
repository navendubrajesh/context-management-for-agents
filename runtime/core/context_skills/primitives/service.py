"""Orchestration helpers — telemetry + metering for primitives."""

from __future__ import annotations

import time
from typing import Callable, TypeVar

from context_skills.metering import UsageRecord, emit_usage, estimate_cost_usd
from context_skills.primitives.metrics import PrimitiveMetrics, PrimitiveResult
from context_skills.telemetry import record_primitive_metrics, trace_operation

T = TypeVar("T")


def run_primitive(
    fn: Callable[..., PrimitiveResult],
    *args,
    correlation_id: str | None = None,
    **kwargs,
) -> PrimitiveResult:
    operation = getattr(fn, "__name__", "primitive")
    start = time.perf_counter()
    with trace_operation(operation, correlation_id=correlation_id) as cid:
        result = fn(*args, **kwargs)
        latency_ms = (time.perf_counter() - start) * 1000
        est_cost = estimate_cost_usd(
            result.metrics.tokens_before,
            result.metrics.tokens_after,
        )
        metrics = PrimitiveMetrics(
            operation=result.metrics.operation,
            tokens_before=result.metrics.tokens_before,
            tokens_after=result.metrics.tokens_after,
            est_cost_usd=est_cost,
        )
        result = PrimitiveResult(output=result.output, metrics=metrics)
        emit_usage(
            UsageRecord(
                operation=result.metrics.operation,
                tokens_before=result.metrics.tokens_before,
                tokens_after=result.metrics.tokens_after,
                est_cost_usd=est_cost,
                correlation_id=cid,
            )
        )
        record_primitive_metrics(
            operation=result.metrics.operation,
            tokens_before=result.metrics.tokens_before,
            tokens_after=result.metrics.tokens_after,
            latency_ms=latency_ms,
            correlation_id=cid,
        )
        return result
