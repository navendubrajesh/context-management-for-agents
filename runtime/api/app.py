"""FastAPI REST surface for context-management-for-agents runtime."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from context_skills import get_reference, get_skill, list_skills, route
from context_skills.paths import find_repo_root

app = FastAPI(
    title="Context Skills Runtime API",
    description="Language-agnostic REST API for discovering and routing Agent Skills.",
    version="1.0.0",
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


def _repo_root(request: Request) -> Path | None:
    configured = getattr(request.app.state, "repo_root", None)
    return Path(configured) if configured else None


@app.middleware("http")
async def phase2_middleware(request: Request, call_next):  # noqa: ANN001
    """No-op middleware hook reserved for Phase 2 auth/policy/budgeting."""
    return await call_next(request)


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
    results = route(payload.task, payload.top_k, _repo_root(request))
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


@app.on_event("startup")
def _configure_repo_root() -> None:
    app.state.repo_root = find_repo_root()
