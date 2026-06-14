from __future__ import annotations

from pathlib import Path

import pytest

from context_skills.loader import get_reference, get_skill, list_skills
from context_skills.manifest import build_skill_manifest, validate_all_skill_manifests, validate_manifest
from context_skills.paths import find_repo_root


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return find_repo_root(Path(__file__))


def test_list_skills_progressive_disclosure(repo_root: Path) -> None:
    skills = list_skills(repo_root)
    assert len(skills) == 28
    assert set(skills[0].keys()) == {"name", "description"}
    assert all(item["name"] and item["description"] for item in skills)


def test_get_skill_includes_body_and_references(repo_root: Path) -> None:
    skill = get_skill("context-compression", repo_root)
    assert skill["name"] == "context-compression"
    assert "compression" in skill["body"].lower()
    assert "references/compression-strategies.md" in skill["references"]


def test_get_reference_content(repo_root: Path) -> None:
    content = get_reference(
        "context-compression",
        "references/compression-strategies.md",
        repo_root,
    )
    assert "compression" in content.lower()


def test_manifest_schema_validation(repo_root: Path) -> None:
    manifest = build_skill_manifest("context-compression", repo_root)
    validate_manifest(manifest)
    assert manifest["category"] == "foundational"
    assert manifest["activation_triggers"]


def test_all_skill_manifests_validate(repo_root: Path) -> None:
    errors = validate_all_skill_manifests(repo_root)
    assert errors == []
