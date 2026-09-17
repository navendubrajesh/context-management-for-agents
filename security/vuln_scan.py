"""Vulnerability scan helper — grype JSON output with allowlist filtering."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from security.vuln_allowlist import default_allowlist_path, filter_findings


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run_grype(sbom_path: Path) -> list[dict[str, Any]]:
    proc = subprocess.run(
        ["grype", f"sbom:{sbom_path}", "-o", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0 and not proc.stdout.strip():
        raise RuntimeError(proc.stderr.strip() or "grype scan failed")
    data = json.loads(proc.stdout)
    return list(data.get("matches", []))


def scan_sbom(
    sbom_path: Path,
    *,
    allowlist_path: Path | None = None,
    min_severity: str = "High",
    strict: bool = False,
) -> int:
    if not sbom_path.is_file():
        print(f"SBOM not found: {sbom_path}", file=sys.stderr)
        return 1

    allowlist_path = allowlist_path or default_allowlist_path()
    try:
        findings = run_grype(sbom_path)
    except FileNotFoundError:
        if strict:
            print("grype not installed — strict mode requires grype", file=sys.stderr)
            return 1
        print("grype not installed — skipping scan (offline/dev mode)")
        return 0
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    blocked, allowed = filter_findings(
        findings,
        min_severity=min_severity,
        allowlist_path=allowlist_path,
    )

    if allowed:
        print(f"Allowlisted findings: {len(allowed)}")
        for item in allowed:
            vuln_id = item.get("vulnerability", {}).get("id", "unknown")
            print(f"  ALLOWLISTED {vuln_id} ({item.get('vulnerability', {}).get('severity')})")

    if blocked:
        print(f"Blocked findings: {len(blocked)}", file=sys.stderr)
        for item in blocked:
            vuln = item.get("vulnerability", {})
            print(
                f"  BLOCKED {vuln.get('id', 'unknown')} "
                f"({vuln.get('severity')}) — {item.get('artifact', {}).get('name')}",
                file=sys.stderr,
            )
        return 1

    print("No unallowlisted High/Critical vulnerabilities found")
    return 0


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Scan SBOM with grype + allowlist")
    parser.add_argument(
        "--sbom",
        default=str(_repo_root() / "security" / "sbom" / "runtime.cdx.json"),
    )
    parser.add_argument("--allowlist", default=str(default_allowlist_path()))
    parser.add_argument("--min-severity", default="High", choices=["Low", "Medium", "High", "Critical"])
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    return scan_sbom(
        Path(args.sbom),
        allowlist_path=Path(args.allowlist),
        min_severity=args.min_severity,
        strict=args.strict,
    )


if __name__ == "__main__":
    raise SystemExit(main())
