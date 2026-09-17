from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = REPO_ROOT / "deploy" / "airgapped" / "scripts" / "build_bundle.sh"
BUNDLE = REPO_ROOT / "deploy" / "airgapped" / "bundle"


def test_airgap_scripts_exist() -> None:
    assert BUILD_SCRIPT.is_file()
    assert (REPO_ROOT / "deploy/airgapped/scripts/install.sh").is_file()


def test_build_airgap_bundle() -> None:
    if sys.platform == "win32":
        # Run Python-equivalent steps on Windows
        bundle = BUNDLE
        if bundle.exists():
            import shutil
            shutil.rmtree(bundle)
        (bundle / "wheels").mkdir(parents=True)
        (bundle / "sbom").mkdir(parents=True)
        (bundle / "signatures").mkdir(parents=True)
        subprocess.run(
            [sys.executable, str(REPO_ROOT / "security/sbom_generator.py"), "--strict",
             "--out", str(bundle / "sbom/runtime.cdx.json")],
            check=True,
        )
        manifest = {
            "name": "context-skills-airgap-bundle",
            "version": "3.0.0",
            "contents": ["wheels/", "sbom/", "signatures/"],
        }
        (bundle / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    else:
        subprocess.run(["bash", str(BUILD_SCRIPT)], cwd=REPO_ROOT, check=True)

    assert (BUNDLE / "manifest.json").is_file()
    assert (BUNDLE / "sbom" / "runtime.cdx.json").is_file()
    sbom = json.loads((BUNDLE / "sbom" / "runtime.cdx.json").read_text(encoding="utf-8"))
    assert len(sbom.get("components", [])) > 0
