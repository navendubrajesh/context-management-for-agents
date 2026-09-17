from __future__ import annotations

from pathlib import Path

from context_adapters_temporal.workflow import run_phase_workflow

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_run_phase_workflow_handoff_compaction() -> None:
    state = run_phase_workflow(
        {
            "repo_root": str(REPO_ROOT),
            "session": {
                "messages": [{"role": "user", "content": "phase one complete"}],
                "observations": [{"tool": "grep", "content": "match\n" * 20}],
            },
            "components": [{"name": "task", "content": "phase two", "priority": 10}],
            "token_budget": 500,
        }
    )
    assert "handoff" in state
    assert "pipeline_result" in state
