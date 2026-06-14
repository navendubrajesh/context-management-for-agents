"""Skill manifest builder and JSON Schema validator."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import jsonschema

from context_skills.constants import (
    DEFAULT_SKILL_VERSION,
    EXPECTED_SKILLS,
    SKILL_CATEGORIES,
    VALID_CATEGORIES,
)
from context_skills.loader import get_skill
from context_skills.paths import corpus_index_path, find_repo_root

_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "skill-manifest.schema.json"
_ACTIVATION_SECTION_RE = re.compile(
    r"## When to Activate\s*\n(.*?)(?=\n## |\Z)", re.DOTALL
)


def _load_schema() -> dict[str, Any]:
    with _SCHEMA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def _load_corpus(repo_root: Path) -> dict[str, Any]:
    path = corpus_index_path(repo_root)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return data.get("skills", {})


def extract_activation_triggers(body: str) -> list[str]:
    """Parse bullet triggers from the When to Activate section."""
    match = _ACTIVATION_SECTION_RE.search(body)
    if not match:
        return []

    section = match.group(1)
    triggers: list[str] = []
    in_activate_block = False

    for line in section.splitlines():
        lowered = line.lower()
        if "do not activate" in lowered:
            break
        if "activate this skill when" in lowered:
            in_activate_block = True
            continue
        if in_activate_block and line.strip().startswith("-"):
            trigger = line.strip().lstrip("-").strip()
            if trigger:
                triggers.append(trigger)

    return triggers


def infer_category(skill_name: str) -> str:
    """Return manifest category for *skill_name*."""
    category = SKILL_CATEGORIES.get(skill_name)
    if category is None:
        raise ValueError(f"No category mapping for skill: {skill_name}")
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category '{category}' for skill: {skill_name}")
    return category


def build_skill_manifest(skill_name: str, repo_root: Path | str | None = None) -> dict[str, Any]:
    """Build a runtime manifest for *skill_name* without mutating skill content."""
    root = repo_root or find_repo_root()
    detail = get_skill(skill_name, root)
    corpus = _load_corpus(root)
    corpus_entry = corpus.get(skill_name, {})

    claim_ids = corpus_entry.get("claims", [])
    triggers = extract_activation_triggers(detail["body"])
    if not triggers:
        triggers = [detail["description"]]

    manifest = {
        "name": detail["name"],
        "description": detail["description"],
        "version": DEFAULT_SKILL_VERSION,
        "category": infer_category(skill_name),
        "references": detail["references"],
        "claims": claim_ids,
        "activation_triggers": triggers,
    }
    return manifest


def validate_manifest(manifest: dict[str, Any]) -> None:
    """Validate *manifest* against skill-manifest.schema.json."""
    schema = _load_schema()
    jsonschema.validate(instance=manifest, schema=schema)


def validate_all_skill_manifests(repo_root: Path | str | None = None) -> list[str]:
    """Validate manifests for all expected skills. Returns error messages."""
    root = repo_root or find_repo_root()
    errors: list[str] = []

    for skill_name in sorted(EXPECTED_SKILLS):
        try:
            manifest = build_skill_manifest(skill_name, root)
            validate_manifest(manifest)
        except Exception as exc:  # noqa: BLE001 - aggregate validation errors
            errors.append(f"{skill_name}: {exc}")

    return errors
