from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "researcher" / "scripts" / "check_claim_drift.py"


def test_claim_drift_script_passes_strict() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--strict"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    report = json.loads(proc.stdout)
    assert report["passed"] is True
    assert len(report["checks"]) >= 3
