"""Vulnerability allowlist loader and matcher."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any


def default_allowlist_path() -> Path:
    return Path(__file__).resolve().parent / "vuln-allowlist.json"


def load_allowlist(path: Path | None = None) -> dict[str, Any]:
    path = path or default_allowlist_path()
    if not path.is_file():
        return {"schema_version": 1, "entries": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _entry_active(entry: dict[str, Any], today: date | None = None) -> bool:
    today = today or date.today()
    expiry = entry.get("expires")
    if not expiry:
        return True
    try:
        return date.fromisoformat(str(expiry)) >= today
    except ValueError:
        return True


def allowed_vuln_ids(path: Path | None = None) -> set[str]:
    data = load_allowlist(path)
    return {
        str(entry["id"]).upper()
        for entry in data.get("entries", [])
        if entry.get("id") and _entry_active(entry)
    }


def is_allowed(vuln_id: str, path: Path | None = None) -> bool:
    return vuln_id.upper() in allowed_vuln_ids(path)


def filter_findings(
    findings: list[dict[str, Any]],
    *,
    min_severity: str = "High",
    allowlist_path: Path | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split findings into blocked vs allowlisted."""
    order = {"Negligible": 0, "Low": 1, "Medium": 2, "High": 3, "Critical": 4}
    threshold = order.get(min_severity, 3)
    blocked: list[dict[str, Any]] = []
    allowed: list[dict[str, Any]] = []

    for finding in findings:
        vuln = finding.get("vulnerability", {})
        severity = str(finding.get("severity") or vuln.get("severity") or "Unknown")
        if order.get(severity, 0) < threshold:
            continue
        vuln_id = str(vuln.get("id", ""))
        if vuln_id and is_allowed(vuln_id, allowlist_path):
            allowed.append(finding)
        else:
            blocked.append(finding)
    return blocked, allowed
