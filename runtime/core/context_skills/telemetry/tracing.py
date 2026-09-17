"""OpenTelemetry tracing and metrics — no-op safe when unset."""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Iterator

from context_skills.metering import new_correlation_id

_tracer = None
_meter = None
_tokens_saved_counter = None
_latency_histogram = None
_initialized = False


def init_telemetry(service_name: str = "context-skills-runtime") -> None:
    global _tracer, _meter, _tokens_saved_counter, _latency_histogram, _initialized
    if _initialized:
        return
    _initialized = True

    try:
        from opentelemetry import metrics, trace
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    except ImportError:
        return

    from context_skills.residency import configured_region, telemetry_allowed

    attrs = {"service.name": service_name}
    region = configured_region()
    if region:
        attrs["deployment.region"] = region
    resource = Resource.create(attrs)
    provider = TracerProvider(resource=resource)
    otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
    exporter = os.environ.get("OTEL_TRACES_EXPORTER", "console").lower()
    if otlp_endpoint and telemetry_allowed():
        try:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

            provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint)))
        except ImportError:
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    elif exporter == "console":
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)

    meter_provider = MeterProvider(resource=resource)
    metrics.set_meter_provider(meter_provider)

    _tracer = trace.get_tracer(service_name)
    _meter = metrics.get_meter(service_name)
    _tokens_saved_counter = _meter.create_counter("context.tokens_saved")
    _latency_histogram = _meter.create_histogram("context.operation.latency_ms")


def get_correlation_id(existing: str | None = None) -> str:
    return existing or new_correlation_id()


@contextmanager
def trace_operation(
    name: str,
    *,
    correlation_id: str | None = None,
    attributes: dict[str, Any] | None = None,
) -> Iterator[str]:
    cid = get_correlation_id(correlation_id)
    attrs = {"correlation_id": cid, **(attributes or {})}
    if _tracer is None:
        yield cid
        return

    with _tracer.start_as_current_span(name, attributes=attrs) as span:
        span.set_attribute("correlation_id", cid)
        yield cid


def record_primitive_metrics(
    *,
    operation: str,
    tokens_before: int,
    tokens_after: int,
    latency_ms: float,
    correlation_id: str,
) -> None:
    saved = max(0, tokens_before - tokens_after)
    if _tokens_saved_counter is not None:
        _tokens_saved_counter.add(saved, {"operation": operation})
    if _latency_histogram is not None:
        _latency_histogram.record(latency_ms, {"operation": operation})
