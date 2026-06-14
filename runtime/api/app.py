"""FastAPI REST surface for context-management-for-agents runtime."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from context_skills import get_reference, get_skill, list_skills, route
from context_skills.metering import emit_usage, get_usage_sink, new_correlation_id
from context_skills.metering.usage import UsageRecord
from context_skills.paths import find_repo_root
from context_skills.primitives import (
    budget_context,
    compact_session,
    mask_observation,
    optimize_format,
    run_context_pipeline,
)
from context_skills.primitives.budgeter import ContextComponent
from context_skills.primitives.service import run_primitive
from context_skills.telemetry import init_telemetry, record_primitive_metrics, trace_operation

app = FastAPI(
    title="Context Skills Runtime API",
    description="Language-agnostic REST API for discovering, routing, and applying Agent Skills.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RouteRequest(BaseModel):
    task: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=28)


class RouteResult(BaseModel):
    skill: str
    score: float


class RouteResponse(BaseModel):
    results: list[RouteResult]


class MaskRequest(BaseModel):
    tool_name: str
    content: str | dict[str, Any]
    query: str | None = None


class CompactRequest(BaseModel):
    messages: list[dict[str, Any]] | None = None
    text: str | None = None
    mode: Literal["hierarchical", "handoff_summary", "selective_retention"] = "hierarchical"


class BudgetRequest(BaseModel):
    components: list[dict[str, Any]]
    token_budget: int = Field(..., ge=50)


class FormatRequest(BaseModel):
    content: str | dict[str, Any] | list[Any]
    kind: Literal["json", "text", "auto"] = "auto"


class PipelineRequest(BaseModel):
    session: dict[str, Any]


class PrimitiveResponse(BaseModel):
    output: str | dict[str, Any] | list[Any]
    metrics: dict[str, Any]
    correlation_id: str


def _repo_root(request: Request) -> Path | None:
    configured = getattr(request.app.state, "repo_root", None)
    return Path(configured) if configured else None


def _correlation_id(request: Request) -> str:
    return request.headers.get("x-correlation-id") or new_correlation_id()


def _primitive_response(result, correlation_id: str) -> PrimitiveResponse:
    return PrimitiveResponse(
        output=result.output,
        metrics=result.metrics.to_dict(),
        correlation_id=correlation_id,
    )


@app.middleware("http")
async def telemetry_middleware(request: Request, call_next):  # noqa: ANN001
    correlation_id = _correlation_id(request)
    request.state.correlation_id = correlation_id
    start = time.perf_counter()
    with trace_operation(f"http {request.method} {request.url.path}", correlation_id=correlation_id):
        response = await call_next(request)
    latency_ms = (time.perf_counter() - start) * 1000
    record_primitive_metrics(
        operation=f"http:{request.method}:{request.url.path}",
        tokens_before=0,
        tokens_after=0,
        latency_ms=latency_ms,
        correlation_id=correlation_id,
    )
    response.headers["x-correlation-id"] = correlation_id
    return response


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/skills")
def get_skills(request: Request) -> list[dict[str, str]]:
    return list_skills(_repo_root(request))


@app.get("/skills/{name}")
def get_skill_by_name(name: str, request: Request) -> dict[str, Any]:
    try:
        return get_skill(name, _repo_root(request))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/route", response_model=RouteResponse)
def route_task(payload: RouteRequest, request: Request) -> RouteResponse:
    cid = request.state.correlation_id
    start = time.perf_counter()
    with trace_operation("route_task", correlation_id=cid):
        results = route(payload.task, payload.top_k, _repo_root(request))
    emit_usage(
        UsageRecord(
            operation="route_task",
            tokens_before=len(payload.task.split()),
            tokens_after=len(results),
            est_cost_usd=0.0,
            correlation_id=cid,
        )
    )
    record_primitive_metrics(
        operation="route_task",
        tokens_before=len(payload.task.split()),
        tokens_after=len(results),
        latency_ms=(time.perf_counter() - start) * 1000,
        correlation_id=cid,
    )
    return RouteResponse(results=[RouteResult(**item) for item in results])


@app.get("/skills/{name}/references/{path:path}")
def get_skill_reference(name: str, path: str, request: Request) -> dict[str, str]:
    try:
        content = get_reference(name, path, _repo_root(request))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"name": name, "path": path, "content": content}


@app.post("/primitives/mask_observation", response_model=PrimitiveResponse)
def api_mask_observation(payload: MaskRequest, request: Request) -> PrimitiveResponse:
    cid = request.state.correlation_id
    result = run_primitive(
        mask_observation,
        tool_name=payload.tool_name,
        content=payload.content,
        query=payload.query,
        correlation_id=cid,
    )
    return _primitive_response(result, cid)


@app.post("/primitives/compact_session", response_model=PrimitiveResponse)
def api_compact_session(payload: CompactRequest, request: Request) -> PrimitiveResponse:
    cid = request.state.correlation_id
    result = run_primitive(
        compact_session,
        messages=payload.messages,
        text=payload.text,
        mode=payload.mode,
        correlation_id=cid,
    )
    return _primitive_response(result, cid)


@app.post("/primitives/budget_context", response_model=PrimitiveResponse)
def api_budget_context(payload: BudgetRequest, request: Request) -> PrimitiveResponse:
    cid = request.state.correlation_id
    components = [ContextComponent(**item) for item in payload.components]
    result = run_primitive(
        budget_context,
        components=components,
        token_budget=payload.token_budget,
        correlation_id=cid,
    )
    return _primitive_response(result, cid)


@app.post("/primitives/optimize_format", response_model=PrimitiveResponse)
def api_optimize_format(payload: FormatRequest, request: Request) -> PrimitiveResponse:
    cid = request.state.correlation_id
    result = run_primitive(
        optimize_format,
        content=payload.content,
        kind=payload.kind,
        correlation_id=cid,
    )
    return _primitive_response(result, cid)


@app.post("/primitives/run_context_pipeline", response_model=PrimitiveResponse)
def api_run_context_pipeline(payload: PipelineRequest, request: Request) -> PrimitiveResponse:
    cid = request.state.correlation_id
    result = run_primitive(
        run_context_pipeline,
        payload.session,
        correlation_id=cid,
    )
    return _primitive_response(result, cid)


@app.get("/usage")
def get_usage(limit: int = 50) -> dict[str, Any]:
    return {"records": get_usage_sink().recent(limit=limit)}


@app.on_event("startup")
def _configure_runtime() -> None:
    app.state.repo_root = find_repo_root()
    init_telemetry(os.environ.get("OTEL_SERVICE_NAME", "context-skills-api"))
