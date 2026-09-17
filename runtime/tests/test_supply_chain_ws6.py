from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from security.sbom_generator import generate_sbom, write_sbom
from security.signing import sha256_file, sign_artifact, verify_artifact
from security.vuln_allowlist import filter_findings, is_allowed, load_allowlist


REPO_ROOT = Path(__file__).resolve().parents[2]
SBOM_PATH = REPO_ROOT / "security" / "sbom" / "runtime.cdx.json"
ALLOWLIST_PATH = REPO_ROOT / "security" / "vuln-allowlist.json"


def test_verify_rejects_unsigned() -> None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        tmp.write(b'{"test": true}')
        path = Path(tmp.name)
    assert verify_artifact(path) is False
    sig = Path(str(path) + ".sha256")
    sig.write_text(sha256_file(path) + "\n", encoding="utf-8")
    assert verify_artifact(path) is True
    path.unlink(missing_ok=True)
    sig.unlink(missing_ok=True)


def test_sign_and_verify_roundtrip() -> None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        tmp.write(b'{"artifact": "release"}')
        path = Path(tmp.name)
    result = sign_artifact(path, prefer_cosign=False)
    assert result["method"] == "sha256"
    assert verify_artifact(path) is True
    Path(str(path) + ".sha256").unlink(missing_ok=True)
    path.unlink(missing_ok=True)


def test_sbom_generator_produces_components() -> None:
    sbom = generate_sbom(REPO_ROOT)
    assert sbom["bomFormat"] == "CycloneDX"
    assert len(sbom["components"]) >= 5
    names = {c["name"] for c in sbom["components"]}
    assert "context-policy" in names or "context-skills-runtime" in names


def test_sbom_strict_mode(tmp_path: Path) -> None:
    out = tmp_path / "empty.cdx.json"
    # Empty repo should fail strict
    empty_root = tmp_path / "empty"
    empty_root.mkdir()
    assert write_sbom(out, root=empty_root, strict=True) == 1


def test_committed_sbom_not_empty_stub() -> None:
    if not SBOM_PATH.is_file():
        write_sbom(SBOM_PATH, root=REPO_ROOT, strict=True)
    data = json.loads(SBOM_PATH.read_text(encoding="utf-8"))
    assert data["bomFormat"] == "CycloneDX"
    assert len(data.get("components", [])) > 0


def test_vuln_allowlist_schema() -> None:
    data = load_allowlist(ALLOWLIST_PATH)
    assert data["schema_version"] == 1
    assert isinstance(data["entries"], list)
    assert "description" in data


def test_vuln_allowlist_file_committed() -> None:
    assert ALLOWLIST_PATH.is_file()
    raw = ALLOWLIST_PATH.read_text(encoding="utf-8")
    assert "schema_version" in raw
    assert "entries" in raw


def test_vuln_allowlist_filtering() -> None:
    findings = [
        {
            "vulnerability": {"id": "CVE-2024-0001", "severity": "Critical"},
            "artifact": {"name": "lib-a"},
        },
        {
            "vulnerability": {"id": "CVE-2024-9999", "severity": "High"},
            "artifact": {"name": "lib-b"},
        },
    ]
    with patch("security.vuln_allowlist.allowed_vuln_ids", return_value={"CVE-2024-0001"}):
        blocked, allowed = filter_findings(findings, min_severity="High")
    assert len(blocked) == 1
    assert blocked[0]["vulnerability"]["id"] == "CVE-2024-9999"
    assert len(allowed) == 1


def test_is_allowed_false_for_unknown() -> None:
    assert is_allowed("CVE-2099-0000", ALLOWLIST_PATH) is False


def test_vuln_scan_offline_mode() -> None:
    from security.vuln_scan import scan_sbom

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        tmp.write(json.dumps({"bomFormat": "CycloneDX", "components": []}).encode())
        sbom = Path(tmp.name)
    # No grype in most dev envs — should skip gracefully without strict
    assert scan_sbom(sbom, strict=False) == 0
    sbom.unlink(missing_ok=True)
