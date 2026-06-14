#!/usr/bin/env python3
"""Offline demo: Skill Router + context primitive with measured token savings."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_DIR = REPO_ROOT / "runtime" / "core"
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

from context_skills import route  # noqa: E402
from context_skills.paths import find_repo_root  # noqa: E402
from context_skills.primitives.compaction import compact_session  # noqa: E402


def main() -> None:
    find_repo_root(REPO_ROOT)
    task = "compress conversation history for a handoff"
    print("=" * 60)
    print("Context Management for Agents — Runnable Demo")
    print("=" * 60)
    print(f"\nTask: {task!r}\n")

    print("--- Skill Router ---")
    results = route(task, top_k=3, repo_root=REPO_ROOT)
    for i, item in enumerate(results, start=1):
        marker = " <- selected" if i == 1 else ""
        print(f"  {i}. {item['skill']} (score {item['score']:.1f}){marker}")

    expected = "context-compression"
    top = results[0]["skill"]
    if top != expected:
        print(f"\n[!] Expected top skill {expected!r}, got {top!r}")
        sys.exit(1)
    print(f"\nRouter selected: {top}")

    messages_path = Path(__file__).parent / "sample_conversation.json"
    if not messages_path.is_file():
        messages_path = Path(__file__).parent / "sample_messages.json"
    messages = json.loads(messages_path.read_text(encoding="utf-8"))
    print("\n--- Context primitive: compact_session (handoff_summary) ---")
    result = compact_session(messages=messages, mode="handoff_summary")
    before = result.metrics.tokens_before
    after = result.metrics.tokens_after
    saved = before - after
    pct = (saved / before * 100) if before else 0.0

    print(f"  Tokens before: {before:,}")
    print(f"  Tokens after:  {after:,}")
    print(f"  Tokens saved:  {saved:,} ({pct:.1f}%)")
    print("\nHandoff summary (first 400 chars):")
    print("-" * 40)
    print(str(result.output)[:400].strip())
    if len(str(result.output)) > 400:
        print("...")
    print("-" * 40)
    print("\n[+] Demo complete (offline, no credentials).")


if __name__ == "__main__":
    main()
