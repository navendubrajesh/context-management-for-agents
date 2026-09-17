from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = [
    REPO_ROOT / "examples" / "digital-brain-skill" / "run.py",
    REPO_ROOT / "examples" / "research-pipeline" / "run.py",
    REPO_ROOT / "examples" / "multi-agent-coordination" / "run.py",
]


def test_runnable_examples_exit_zero() -> None:
    for script in EXAMPLES:
        proc = subprocess.run([sys.executable, str(script)], cwd=REPO_ROOT, capture_output=True, text=True)
        assert proc.returncode == 0, proc.stderr
