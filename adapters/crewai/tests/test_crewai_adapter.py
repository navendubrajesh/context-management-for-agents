from __future__ import annotations

from pathlib import Path

import pytest

from context_adapters_crewai.tools import create_context_tools

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_create_context_tools_portable_mode() -> None:
    tools = create_context_tools(repo_root=REPO_ROOT)
    assert len(tools) == 3
    assert tools[0]["name"] == "route_task"
    output = tools[0]["run"]("manage context window budget")
    assert "context" in output.lower()


def test_route_tool_returns_ranked_skills() -> None:
    tools = create_context_tools(repo_root=REPO_ROOT)
    route_tool = next(t for t in tools if t["name"] == "route_task")
    result = route_tool["run"]("compact long conversation history")
    assert "skill" in result or "context-compression" in result
