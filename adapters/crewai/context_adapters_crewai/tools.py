"""CrewAI tool definitions wrapping context-skills SDK."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from context_skills_sdk.client import SkillsClient


def _make_tool(name: str, description: str, fn: Callable[..., str]) -> dict[str, Any]:
    return {"name": name, "description": description, "run": fn}


def create_context_tools(
    *,
    base_url: str | None = None,
    repo_root: Path | None = None,
) -> list[dict[str, Any]]:
    """Return portable tool specs; wraps CrewAI Tool objects when crewai is installed."""
    client = SkillsClient(base_url=base_url, repo_root=repo_root)

    def route_task(task: str) -> str:
        results = client.route(task, top_k=3)
        return str(results)

    def mask_observation(tool_name: str, content: str) -> str:
        result = client.mask_observation(tool_name=tool_name, content=content)
        return str(result.get("output"))

    def run_pipeline(session_json: str) -> str:
        import json

        session = json.loads(session_json)
        result = client.run_context_pipeline(session)
        return str(result.get("output"))

    specs = [
        _make_tool("route_task", "Route a natural-language task to context skills.", route_task),
        _make_tool("mask_observation", "Mask verbose tool output to save context tokens.", mask_observation),
        _make_tool("run_context_pipeline", "Run combined context optimization pipeline on a session JSON.", run_pipeline),
    ]

    try:
        from crewai.tools import tool

        def _wrap_tool(spec: dict[str, Any]):
            fn = spec["run"]

            @tool(spec["name"])
            def _wrapped(*args, **kwargs):  # type: ignore[no-untyped-def]
                return fn(*args, **kwargs)

            _wrapped.__doc__ = spec["description"]
            return _wrapped

        return [_wrap_tool(spec) for spec in specs]
    except ImportError:
        return specs
