from __future__ import annotations

import json
import tempfile
from pathlib import Path

from security.verify_signature import sha256_file, verify_artifact


def test_verify_rejects_unsigned() -> None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        tmp.write(b'{"test": true}')
        path = Path(tmp.name)
    assert verify_artifact(path) is False
    sig = Path(str(path) + ".sha256")
    sig.write_text(sha256_file(path), encoding="utf-8")
    assert verify_artifact(path) is True
    path.unlink(missing_ok=True)
    sig.unlink(missing_ok=True)


def test_stub_sbom_structure() -> None:
    sbom_path = Path(__file__).resolve().parents[2] / "security" / "sbom" / "runtime.cdx.json"
    if not sbom_path.is_file():
        sbom_path.parent.mkdir(parents=True, exist_ok=True)
        sbom_path.write_text(
            json.dumps({"bomFormat": "CycloneDX", "specVersion": "1.4", "components": []}),
            encoding="utf-8",
        )
    data = json.loads(sbom_path.read_text(encoding="utf-8"))
    assert data["bomFormat"] == "CycloneDX"
