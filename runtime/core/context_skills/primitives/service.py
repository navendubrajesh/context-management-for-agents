"""Orchestration helpers — telemetry + metering for primitives."""

from __future__ import annotations

import time
from typing import Callable, TypeVar

from context_skills.metering import UsageRecord, emit_usage, estimate_cost_usd

try:
    from context_tenancy.context import current_tenant_id
except ImportError:

    def current_tenant_id(default: str = "default") -> str:  # noqa: ARG001
        return default
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
    tenant_id = kwargs.pop("tenant_id", None) or current_tenant_id()
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
                tenant_id=tenant_id,
            )
        )
        try:
            from context_audit.lineage import get_lineage_store
            from context_finops.quotas import get_quota_store

            get_lineage_store().record(
                operation=operation,
                tenant_id=tenant_id,
                correlation_id=cid,
                input_value={"args": str(args)[:500], "kwargs_keys": list(kwargs.keys())},
                output_value=result.output,
            )
            get_quota_store().record_tokens(tenant_id, result.metrics.tokens_after)
        except ImportError:
            pass
        record_primitive_metrics(
            operation=result.metrics.operation,
            tokens_before=result.metrics.tokens_before,
            tokens_after=result.metrics.tokens_after,
            latency_ms=latency_ms,
            correlation_id=cid,
        )
        return result
