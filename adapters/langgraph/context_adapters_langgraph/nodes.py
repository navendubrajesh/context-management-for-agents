"""LangGraph-compatible node functions wrapping context-skills primitives."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from context_skills_sdk.client import SkillsClient


def _client(state: dict[str, Any]) -> SkillsClient:
    base_url = state.get("api_base_url")
    repo_root = state.get("repo_root")
    root = Path(repo_root) if repo_root else None
    return SkillsClient(base_url=base_url, repo_root=root)


def mask_observation_node(state: dict[str, Any]) -> dict[str, Any]:
    client = _client(state)
    result = client.mask_observation(
        tool_name=state.get("tool_name", "tool"),
        content=state.get("content", ""),
        query=state.get("query"),
    )
    return {**state, "mask_result": result, "output": result.get("output")}


def compact_session_node(state: dict[str, Any]) -> dict[str, Any]:
    client = _client(state)
    result = client.compact_session(
        messages=state.get("messages"),
        text=state.get("text"),
        mode=state.get("compact_mode", "hierarchical"),
    )
    return {**state, "compact_result": result, "output": result.get("output")}


def budget_context_node(state: dict[str, Any]) -> dict[str, Any]:
    client = _client(state)
    result = client.budget_context(
        components=state.get("components", []),
        token_budget=int(state.get("token_budget", 1000)),
    )
    return {**state, "budget_result": result, "output": result.get("output")}


def run_pipeline_node(state: dict[str, Any]) -> dict[str, Any]:
    client = _client(state)
    session = state.get("session", {})
    result = client.run_context_pipeline(session)
    return {**state, "pipeline_result": result, "output": result.get("output")}


def route_task_node(state: dict[str, Any]) -> dict[str, Any]:
    client = _client(state)
    task = state.get("task", "")
    top_k = int(state.get("top_k", 5))
    results = client.route(task, top_k=top_k)
    return {**state, "route_results": results, "output": results}
