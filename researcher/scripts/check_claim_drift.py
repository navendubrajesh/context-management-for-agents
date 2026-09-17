#!/usr/bin/env python3
"""Detect drift between documented claims/benchmarks and repository artifacts (CM-406)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


_ROOT = repo_root()
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def load_claims(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def load_benchmark(path: Path) -> dict:
    from researcher.eval.io_utils import read_json

    return read_json(path)


def check_readme_savings_drift(readme: Path, benchmark: dict, tolerance: float) -> dict:
    text = readme.read_text(encoding="utf-8")
    issues = []
    for result in benchmark.get("results", []):
        technique = result.get("technique")
        savings = float(result.get("savings_pct", 0))
        pattern = rf"{re.escape(technique)}[^\n]*?(\d+\.\d+)%"
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            continue
        documented = float(match.group(1))
        if abs(documented - savings) > tolerance:
            issues.append(
                {
                    "technique": technique,
                    "documented_pct": documented,
                    "benchmark_pct": savings,
                    "delta": round(documented - savings, 2),
                }
            )
    return {"name": "readme_benchmark_drift", "passed": not issues, "issues": issues}


def check_combined_pipeline_claim(readme: Path, benchmark: dict, tolerance: float) -> dict:
    combined = next(
        (r for r in benchmark.get("results", []) if r.get("technique") == "Combined Pipeline"),
        None,
    )
    if combined is None:
        return {"name": "combined_pipeline_claim", "passed": True, "skipped": True}
    technique = combined.get("technique", "Combined Pipeline")
    benchmark_pct = float(combined.get("savings_pct", 0))
    text = readme.read_text(encoding="utf-8")
    pattern = rf"{re.escape(technique)}[^\n]*?(\d+\.\d+)%"
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return {"name": "combined_pipeline_claim", "passed": True, "note": f"No {technique} claim in README"}
    documented_pct = float(match.group(1))
    passed = abs(documented_pct - benchmark_pct) <= tolerance
    return {
        "name": "combined_pipeline_claim",
        "passed": passed,
        "documented_pct": documented_pct,
        "benchmark_pct": benchmark_pct,
    }


def check_orphan_claims(claims: list[dict], skills_dir: Path) -> dict:
    skill_names = {p.name for p in skills_dir.iterdir() if p.is_dir()}
    orphans = []
    for claim in claims:
        for skill in claim.get("skills", []):
            if skill not in skill_names:
                orphans.append({"claim_id": claim.get("id"), "missing_skill": skill})
    return {"name": "orphan_claim_skills", "passed": not orphans, "issues": orphans}


def main() -> int:
    parser = argparse.ArgumentParser(description="Check claim and benchmark drift")
    parser.add_argument("--tolerance", type=float, default=0.5, help="Allowed savings %% drift")
    parser.add_argument("--report", type=Path, help="Write JSON report to path")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on any drift")
    args = parser.parse_args()

    root = repo_root()
    claims_path = root / "researcher/claims/index.jsonl"
    benchmark_path = root / "researcher/benchmarks/context-savings/results/context-savings-2026-06-14.json"
    readme_path = root / "README.md"

    claims = load_claims(claims_path)
    benchmark = load_benchmark(benchmark_path)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "claims_count": len(claims),
        "checks": [
            check_readme_savings_drift(readme_path, benchmark, args.tolerance),
            check_combined_pipeline_claim(readme_path, benchmark, args.tolerance),
            check_orphan_claims(claims, root / "skills"),
        ],
    }
    report["passed"] = all(item.get("passed", False) for item in report["checks"])

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2))
    if args.strict and not report["passed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
