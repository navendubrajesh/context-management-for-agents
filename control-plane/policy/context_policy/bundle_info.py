"""Policy bundle metadata — version and manifest for API/audit."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


def bundle_root() -> Path:
    return Path(__file__).resolve().parents[1] / "bundles"


@lru_cache(maxsize=1)
def load_bundle_manifest() -> dict:
    path = bundle_root() / "manifest.json"
    if not path.is_file():
        return {"name": "contextskills", "version": "0.0.0", "rego_files": []}
    return json.loads(path.read_text(encoding="utf-8"))


def bundle_version() -> str:
    return str(load_bundle_manifest().get("version", "0.0.0"))
