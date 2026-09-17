from __future__ import annotations

import json
from pathlib import Path

from context_policy.bundle_info import bundle_root, bundle_version, load_bundle_manifest

REGO = bundle_root() / "contextskills.rego"
MANIFEST = bundle_root() / "manifest.json"
TEST_REGO = bundle_root() / "contextskills_test.rego"


def test_manifest_exists_with_version() -> None:
    assert MANIFEST.is_file()
    data = load_bundle_manifest()
    assert data["name"] == "contextskills"
    assert bundle_version() == "3.0.0"
    assert "contextskills.rego" in data["rego_files"]


def test_rego_source_present() -> None:
    text = REGO.read_text(encoding="utf-8")
    assert "package contextskills" in text
    assert "require_approval" in text


def test_rego_tests_present() -> None:
    text = TEST_REGO.read_text(encoding="utf-8")
    assert "test_allow_when_rbac_and_no_denials" in text


def test_manifest_json_valid() -> None:
    json.loads(MANIFEST.read_text(encoding="utf-8"))
