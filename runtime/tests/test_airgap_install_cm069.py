from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD = REPO_ROOT / "deploy" / "airgapped" / "scripts" / "build_bundle.sh"
INSTALL = REPO_ROOT / "deploy" / "airgapped" / "scripts" / "install.sh"


def test_airgap_bundle_build_and_install_dry_run() -> None:
    import pytest

    if sys.platform == "win32":
        pytest.skip("Air-gap shell scripts require bash on Unix CI")
    build = subprocess.run(["bash", str(BUILD)], cwd=REPO_ROOT, capture_output=True, text=True)
    assert build.returncode == 0, build.stdout + build.stderr
    install = subprocess.run(["bash", str(INSTALL), "--dry-run"], cwd=REPO_ROOT, capture_output=True, text=True)
    assert install.returncode == 0, install.stdout + install.stderr
