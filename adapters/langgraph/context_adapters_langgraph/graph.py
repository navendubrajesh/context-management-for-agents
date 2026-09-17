"""Build a LangGraph pipeline over context-skills nodes."""

from __future__ import annotations

from typing import Any

from context_adapters_langgraph.nodes import (
    budget_context_node,
    compact_session_node,
    mask_observation_node,
    route_task_node,
    run_pipeline_node,
)


def build_context_graph():
    """Return a compiled LangGraph when langgraph is installed."""
    try:
        from langgraph.graph import END, StateGraph
    except ImportError as exc:
        raise ImportError(
            "langgraph is required for build_context_graph(). "
            "Install with: pip install context-adapters-langgraph[langgraph]"
        ) from exc

    graph = StateGraph(dict)
    graph.add_node("route", route_task_node)
    graph.add_node("mask", mask_observation_node)
    graph.add_node("compact", compact_session_node)
    graph.add_node("budget", budget_context_node)
    graph.add_node("pipeline", run_pipeline_node)

    graph.set_entry_point("route")
    graph.add_edge("route", "mask")
    graph.add_edge("mask", "compact")
    graph.add_edge("compact", "budget")
    graph.add_edge("budget", "pipeline")
    graph.add_edge("pipeline", END)
    return graph.compile()


def _prepare_state(initial_state: dict[str, Any]) -> dict[str, Any]:
    state = dict(initial_state)
    session = state.get("session") or {}
    observations = session.get("observations") or []
    if observations and "content" not in state:
        first = observations[0]
        state.setdefault("tool_name", first.get("tool", "tool"))
        state.setdefault("content", first.get("content", ""))
    if session.get("messages") and "messages" not in state:
        state["messages"] = session["messages"]
    return state


def run_default_graph(initial_state: dict[str, Any]) -> dict[str, Any]:
    """Execute nodes sequentially without requiring langgraph."""
    state = _prepare_state(initial_state)
    state = route_task_node(state)
    state = mask_observation_node(state)
    state = compact_session_node(state)
    state = budget_context_node(state)
    return run_pipeline_node(state)
