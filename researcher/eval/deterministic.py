"""Deterministic evaluation checks for skills and context changes."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def check_skill_structure(skill_path: Path) -> dict[str, Any]:
    text = skill_path.read_text(encoding="utf-8")
    checks = {
        "has_name_frontmatter": bool(re.search(r"^name:\s*\S+", text, re.MULTILINE)),
        "has_description_frontmatter": bool(re.search(r"^description:\s*\S+", text, re.MULTILINE)),
        "has_when_to_activate": "## When to Activate" in text,
        "has_do_not_activate": "Do not activate" in text,
        "under_500_lines": text.count("\n") + 1 <= 500,
    }
    passed = all(checks.values())
    return {"name": "skill_structure", "passed": passed, "checks": checks}


def check_benchmark_threshold(
    *,
    technique: str,
    min_savings_pct: float,
    benchmark_json: Path,
) -> dict[str, Any]:
    from researcher.eval.io_utils import read_json

    data = read_json(benchmark_json)
    match = next((r for r in data.get("results", []) if r.get("technique") == technique), None)
    if match is None:
        return {
            "name": f"benchmark:{technique}",
            "passed": False,
            "reason": f"Technique not found in benchmark: {technique}",
        }
    savings = float(match.get("savings_pct", 0))
    passed = savings >= min_savings_pct
    return {
        "name": f"benchmark:{technique}",
        "passed": passed,
        "expected_min": min_savings_pct,
        "actual": savings,
    }


def run_deterministic_checks(checks: list[dict[str, Any]], repo_root: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    benchmark_path = repo_root / "researcher/benchmarks/context-savings/results/context-savings-2026-06-14.json"

    for check in checks:
        kind = check.get("type")
        if kind == "skill_structure":
            skill = check.get("skill", "")
            path = repo_root / "skills" / skill / "SKILL.md"
            if not path.is_file():
                results.append({"name": "skill_structure", "passed": False, "reason": f"Missing {path}"})
            else:
                results.append(check_skill_structure(path))
        elif kind == "benchmark_threshold":
            results.append(
                check_benchmark_threshold(
                    technique=check["technique"],
                    min_savings_pct=float(check.get("min_savings_pct", 80)),
                    benchmark_json=benchmark_path,
                )
            )
        else:
            results.append({"name": kind or "unknown", "passed": False, "reason": "Unknown check type"})
    return results
