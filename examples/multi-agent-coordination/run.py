#!/usr/bin/env python3
"""Runnable multi-agent handoff example (CM-606)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "sdk-python"))

from context_skills_sdk.client import SkillsClient


def main() -> int:
    client = SkillsClient(repo_root=ROOT)
    handoff = client.compact_session(
        messages=[
            {"role": "user", "content": "Implement auth module"},
            {"role": "assistant", "content": "Created login route and tests."},
            {"role": "user", "content": "Hand off to reviewer agent"},
        ],
        mode="handoff_summary",
    )
    budget = client.budget_context(
        components=[
            {"name": "handoff", "content": str(handoff.get("output", "")), "priority": 10},
            {"name": "task", "content": "Review auth module for security issues", "priority": 8},
        ],
        token_budget=800,
    )
    print(json.dumps({"handoff": handoff.get("metrics"), "budget": budget.get("metrics")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
