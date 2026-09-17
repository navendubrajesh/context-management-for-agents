#!/usr/bin/env python3
"""Runnable research pipeline example with compaction (CM-606)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "sdk-python"))

from context_skills_sdk.client import SkillsClient


def main() -> int:
    client = SkillsClient(repo_root=ROOT)
    session = {
        "messages": [{"role": "user", "content": "Summarize findings from three papers on context engineering."}],
        "observations": [{"tool": "web_search", "content": "paper abstract\n" * 80}],
    }
    compact = client.compact_session(messages=session["messages"], mode="hierarchical")
    pipeline = client.run_context_pipeline(session)
    print(json.dumps({"compact_tokens": compact.get("metrics"), "pipeline": pipeline.get("metrics")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
