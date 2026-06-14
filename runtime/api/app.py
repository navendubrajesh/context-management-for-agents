"""FastAPI REST surface for context-management-for-agents runtime."""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Any, Literal

from deps import PUBLIC_PATHS, require_operation, resolve_principal
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from scim_routes import router as scim_router
from tenant_routes import router as tenant_router
from approval_routes import router as approval_router
from audit_routes import router as audit_router
from finops_routes import router as finops_router

from context_iam.auth import authenticate_request, is_auth_enforced
from context_iam.identity import Principal
from context_tenancy.context import set_tenant_id
from context_tenancy.store import get_tenant_store

try:
    from context_audit.log import get_audit_log
    from context_audit.vault import redact_text
    from context_finops.quotas import get_quota_store
except ImportError:
    get_audit_log = None
    get_quota_store = None
    redact_text = lambda t: t  # noqa: E731
from context_skills import get_reference, get_skill, list_skills, route
from context_skills.policy import evaluate_policy
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
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scim_router)
app.include_router(tenant_router)
app.include_router(approval_router)
app.include_router(audit_router)
app.include_router(finops_router)


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


def _tenant_id(request: Request) -> str | None:
    return getattr(request.state, "tenant_id", None)


def _primitive_response(result, correlation_id: str) -> PrimitiveResponse:
    return PrimitiveResponse(
        output=result.output,
        metrics=result.metrics.to_dict(),
        correlation_id=correlation_id,
    )


@app.middleware("http")
async def auth_middleware(request: Request, call_next):  # noqa: ANN001
    path = request.url.path
    if not is_auth_enforced() or path in PUBLIC_PATHS:
        try:
            request.state.principal = resolve_principal(request)
            request.state.tenant_id = request.state.principal.tenant_id
        except HTTPException:
            request.state.principal = None
            request.state.tenant_id = request.headers.get("x-tenant-id", "default")
        set_tenant_id(request.state.tenant_id)
        return await call_next(request)
    try:
        principal = authenticate_request(
            authorization=request.headers.get("authorization"),
            api_key=request.headers.get("x-api-key"),
            saml_assertion=request.headers.get("x-saml-assertion"),
        )
        request.state.principal = principal
        request.state.tenant_id = principal.tenant_id
        set_tenant_id(principal.tenant_id)
    except PermissionError as exc:
        if get_audit_log:
            get_audit_log().append(
                event_type="auth.denied",
                actor="unknown",
                tenant_id="unknown",
                correlation_id=request.headers.get("x-correlation-id", ""),
                detail={"reason": redact_text(str(exc)), "path": path},
            )
        return JSONResponse(status_code=401, content={"detail": str(exc)})
    if get_audit_log:
        get_audit_log().append(
            event_type="auth.success",
            actor=principal.subject,
            tenant_id=principal.tenant_id,
            correlation_id=request.headers.get("x-correlation-id", ""),
            detail={"method": principal.auth_method, "path": path},
        )
    return await call_next(request)


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
def get_skills(
    request: Request,
    _: Principal = Depends(require_operation("skills:read")),
) -> list[dict[str, str]]:
    skills = list_skills(_repo_root(request))
    return get_tenant_store().filter_skills(_tenant_id(request) or "default", skills)


@app.get("/skills/{name}")
def get_skill_by_name(
    name: str,
    request: Request,
    principal: Principal = Depends(require_operation("skills:read")),
) -> dict[str, Any]:
    tenant_id = _tenant_id(request) or "default"
    cfg = get_tenant_store().get(tenant_id)
    if cfg and cfg.enabled_skills and name not in cfg.enabled_skills:
        raise HTTPException(status_code=404, detail=f"Skill not available for tenant: {name}")
    if not evaluate_policy("skills:read", {"principal": principal, "skill": name}):
        _log_policy_decision(principal, "skills:read", False, name)
        raise HTTPException(status_code=403, detail=f"Policy denied skill: {name}")
    _log_policy_decision(principal, "skills:read", True, name)
    try:
        return get_skill(name, _repo_root(request))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/route", response_model=RouteResponse)
def route_task(
    payload: RouteRequest,
    request: Request,
    _: Principal = Depends(require_operation("skills:read")),
) -> RouteResponse:
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
            tenant_id=_tenant_id(request),
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
def get_skill_reference(
    name: str,
    path: str,
    request: Request,
    _: Principal = Depends(require_operation("skills:read")),
) -> dict[str, str]:
    try:
        content = get_reference(name, path, _repo_root(request))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"name": name, "path": path, "content": content}


def _enforce_quota(request: Request, principal: Principal) -> None:
    if get_quota_store is None:
        return
    store = get_quota_store()
    store.record_request(principal.tenant_id)
    allowed, reason = store.check(principal.tenant_id)
    if not allowed:
        raise HTTPException(status_code=429, detail=reason)


def _log_policy_decision(principal: Principal, operation: str, allowed: bool, skill: str = "") -> None:
    if get_audit_log is None:
        return
    get_audit_log().append(
        event_type="policy.decision",
        actor=principal.subject,
        tenant_id=principal.tenant_id,
        correlation_id="",
        detail={"operation": operation, "allowed": allowed, "skill": skill},
    )


@app.post("/primitives/mask_observation", response_model=PrimitiveResponse)
def api_mask_observation(
    payload: MaskRequest,
    request: Request,
    principal: Principal = Depends(require_operation("primitives:run")),
) -> PrimitiveResponse:
    _enforce_quota(request, principal)
    cid = request.state.correlation_id
    result = run_primitive(
        mask_observation,
        tool_name=payload.tool_name,
        content=payload.content,
        query=payload.query,
        correlation_id=cid,
        tenant_id=_tenant_id(request),
    )
    return _primitive_response(result, cid)


@app.post("/primitives/compact_session", response_model=PrimitiveResponse)
def api_compact_session(
    payload: CompactRequest,
    request: Request,
    _: Principal = Depends(require_operation("primitives:run")),
) -> PrimitiveResponse:
    cid = request.state.correlation_id
    result = run_primitive(
        compact_session,
        messages=payload.messages,
        text=payload.text,
        mode=payload.mode,
        correlation_id=cid,
        tenant_id=_tenant_id(request),
    )
    return _primitive_response(result, cid)


@app.post("/primitives/budget_context", response_model=PrimitiveResponse)
def api_budget_context(
    payload: BudgetRequest,
    request: Request,
    _: Principal = Depends(require_operation("primitives:run")),
) -> PrimitiveResponse:
    cid = request.state.correlation_id
    components = [ContextComponent(**item) for item in payload.components]
    result = run_primitive(
        budget_context,
        components=components,
        token_budget=payload.token_budget,
        correlation_id=cid,
        tenant_id=_tenant_id(request),
    )
    return _primitive_response(result, cid)


@app.post("/primitives/optimize_format", response_model=PrimitiveResponse)
def api_optimize_format(
    payload: FormatRequest,
    request: Request,
    _: Principal = Depends(require_operation("primitives:run")),
) -> PrimitiveResponse:
    cid = request.state.correlation_id
    result = run_primitive(
        optimize_format,
        content=payload.content,
        kind=payload.kind,
        correlation_id=cid,
        tenant_id=_tenant_id(request),
    )
    return _primitive_response(result, cid)


@app.post("/primitives/run_context_pipeline", response_model=PrimitiveResponse)
def api_run_context_pipeline(
    payload: PipelineRequest,
    request: Request,
    _: Principal = Depends(require_operation("primitives:run")),
) -> PrimitiveResponse:
    cid = request.state.correlation_id
    result = run_primitive(
        run_context_pipeline,
        payload.session,
        correlation_id=cid,
        tenant_id=_tenant_id(request),
    )
    return _primitive_response(result, cid)


class PublishRequest(BaseModel):
    approval_id: str | None = None


@app.post("/skills/{name}/publish")
def publish_skill(
    name: str,
    payload: PublishRequest,
    request: Request,
    principal: Principal = Depends(require_operation("skills:publish")),
) -> dict[str, Any]:
    if not evaluate_policy(
        "skills:publish",
        {"principal": principal, "skill": name, "approval_id": payload.approval_id},
    ):
        raise HTTPException(status_code=403, detail="Publish denied by policy or pending approval")
    root = find_repo_root()
    scripts = root / "researcher" / "scripts"
    gates = [
        ["python", str(scripts / "validate_repo.py"), "--strict"],
        ["python", str(scripts / "skill_health.py"), "--strict", "--no-history"],
        ["python", str(scripts / "run_benchmarks.py")],
        ["python", str(scripts / "check_activation_cases.py")],
    ]
    results = []
    for cmd in gates:
        proc = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True)  # noqa: S603
        results.append({"cmd": cmd[1], "ok": proc.returncode == 0})
        if proc.returncode != 0:
            raise HTTPException(status_code=422, detail={"gate_failed": cmd[1], "results": results})
    if get_audit_log:
        get_audit_log().append(
            event_type="skills.publish",
            actor=principal.subject,
            tenant_id=principal.tenant_id,
            correlation_id=request.state.correlation_id,
            detail={"skill": name, "gates": results},
        )
    return {"skill": name, "status": "published", "gates": results}


@app.get("/usage")
def get_usage(
    request: Request,
    limit: int = 50,
    _: Principal = Depends(require_operation("usage:read")),
) -> dict[str, Any]:
    tenant_id = _tenant_id(request)
    if is_auth_enforced() and tenant_id:
        records = get_usage_sink().recent(limit=limit, tenant_id=tenant_id)
    else:
        records = get_usage_sink().recent(limit=limit)
    return {"records": records}


@app.on_event("startup")
def _configure_runtime() -> None:
    app.state.repo_root = find_repo_root()
    init_telemetry(os.environ.get("OTEL_SERVICE_NAME", "context-skills-api"))
    if os.environ.get("CONTEXT_SKILLS_CONSOLE", "").lower() in {"1", "true", "enabled"}:
        console_dir = find_repo_root() / "control-plane" / "console"
        if console_dir.is_dir():
            app.mount("/console", StaticFiles(directory=str(console_dir), html=True), name="console")
