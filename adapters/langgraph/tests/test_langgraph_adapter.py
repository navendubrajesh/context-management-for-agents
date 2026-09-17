from __future__ import annotations

from pathlib import Path

import pytest

from context_adapters_langgraph.graph import run_default_graph
from context_adapters_langgraph.nodes import mask_observation_node, route_task_node


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_route_task_node_returns_results() -> None:
    state = route_task_node({"task": "prevent context degradation", "repo_root": str(REPO_ROOT)})
    assert "route_results" in state
    assert len(state["route_results"]) >= 1


def test_mask_observation_node_reduces_output() -> None:
    verbose = "row\n" * 200
    state = mask_observation_node(
        {
            "tool_name": "query_db",
            "content": verbose,
            "repo_root": str(REPO_ROOT),
        }
    )
    assert state.get("output") is not None


def test_run_default_graph_end_to_end() -> None:
    state = run_default_graph(
        {
            "task": "optimize agent session context",
            "repo_root": str(REPO_ROOT),
            "session": {
                "messages": [{"role": "user", "content": "implement feature x"}],
                "observations": [{"tool": "grep", "content": "match\n" * 50}],
            },
            "components": [
                {"name": "system", "content": "You are helpful.", "priority": 10},
                {"name": "history", "content": "long history " * 100, "priority": 5},
            ],
            "token_budget": 500,
        }
    )
    assert "pipeline_result" in state
    assert state["pipeline_result"].get("metrics") is not None
