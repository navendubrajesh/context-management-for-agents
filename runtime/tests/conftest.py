"""Pytest configuration — ensure repo root is importable for security/control-plane tests."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
for path in (
    REPO_ROOT,
    REPO_ROOT / "control-plane" / "storage",
    REPO_ROOT / "control-plane" / "iam",
    REPO_ROOT / "control-plane" / "tenancy",
    REPO_ROOT / "control-plane" / "policy",
    REPO_ROOT / "control-plane" / "audit",
    REPO_ROOT / "control-plane" / "marketplace",
):
    text = str(path)
    if text not in sys.path:
        sys.path.insert(0, text)
