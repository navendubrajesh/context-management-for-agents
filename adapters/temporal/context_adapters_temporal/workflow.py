"""Example workflow with handoff compaction at phase boundaries (CM-403)."""

from __future__ import annotations

from typing import Any

from context_adapters_temporal.activities import (
    budget_context_activity,
    compact_session_activity,
    mask_observation_activity,
    run_pipeline_activity,
)


def run_phase_workflow(initial_state: dict[str, Any]) -> dict[str, Any]:
    """Offline sequential workflow when Temporal SDK is unavailable."""
    state = dict(initial_state)
    repo_root = state.get("repo_root")
    session = state.get("session", {})

    if session.get("observations"):
        obs = session["observations"][0]
        state["mask_result"] = mask_observation_activity(
            tool_name=obs.get("tool", "tool"),
            content=obs.get("content", ""),
            repo_root=repo_root,
        )

    state["handoff"] = compact_session_activity(
        messages=session.get("messages"),
        text=session.get("handoff_text"),
        mode="handoff_summary",
        repo_root=repo_root,
    )

    state["budget_result"] = budget_context_activity(
        components=state.get("components", []),
        token_budget=int(state.get("token_budget", 1000)),
        repo_root=repo_root,
    )

    compacted_session = {
        **session,
        "messages": [{"role": "system", "content": state["handoff"].get("output", "")}],
    }
    state["pipeline_result"] = run_pipeline_activity(session=compacted_session, repo_root=repo_root)
    return state


def build_temporal_workflow():
    try:
        from temporalio import workflow

        @workflow.defn
        class ContextPhaseWorkflow:
            @workflow.run
            async def run(self, initial_state: dict[str, Any]) -> dict[str, Any]:
                return run_phase_workflow(initial_state)

        return ContextPhaseWorkflow
    except ImportError as exc:
        raise ImportError(
            "temporalio is required for build_temporal_workflow(). "
            "Install with: pip install context-adapters-temporal[temporal]"
        ) from exc
