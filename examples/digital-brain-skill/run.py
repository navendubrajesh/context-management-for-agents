#!/usr/bin/env python3
"""Runnable digital-brain example using context-skills SDK (CM-606)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "sdk-python"))

from context_skills_sdk.client import SkillsClient


def main() -> int:
    client = SkillsClient(repo_root=ROOT)
    results = client.route("organize persistent knowledge for long-running agent", top_k=3)
    skill = results[0]["skill"] if results else "memory-systems"
    detail = client.get_skill(skill)
    print(json.dumps({"routed_skill": skill, "description": detail.get("description", "")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
