"""Temporal activities wrapping context-skills primitives (CM-403)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from context_skills_sdk.client import SkillsClient


def _client(repo_root: Path | None = None, base_url: str | None = None) -> SkillsClient:
    return SkillsClient(base_url=base_url, repo_root=repo_root)


def mask_observation_activity(
    *,
    tool_name: str,
    content: str,
    repo_root: str | None = None,
    query: str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root) if repo_root else None
    return _client(root).mask_observation(tool_name=tool_name, content=content, query=query)


def compact_session_activity(
    *,
    messages: list[dict[str, Any]] | None = None,
    text: str | None = None,
    mode: str = "handoff_summary",
    repo_root: str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root) if repo_root else None
    return _client(root).compact_session(messages=messages, text=text, mode=mode)


def budget_context_activity(
    *,
    components: list[dict[str, Any]],
    token_budget: int,
    repo_root: str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root) if repo_root else None
    return _client(root).budget_context(components=components, token_budget=token_budget)


def run_pipeline_activity(*, session: dict[str, Any], repo_root: str | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root else None
    return _client(root).run_context_pipeline(session)
