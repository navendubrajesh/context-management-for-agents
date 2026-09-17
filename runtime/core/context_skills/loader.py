"""Skill loader with progressive disclosure over skills/*/SKILL.md."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from context_skills.constants import EXPECTED_SKILLS
from context_skills.freshness import freshness_metadata
from context_skills.paths import find_repo_root, skills_dir

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL | re.MULTILINE)


@dataclass(frozen=True)
class SkillSummary:
    """Lightweight skill index entry (progressive disclosure tier 1)."""

    name: str
    description: str
    last_reviewed: str | None = None
    freshness_days: int | None = None
    volatile: bool = False
    stale: bool = False

    def to_dict(self) -> dict[str, str | bool | int | None]:
        return {
            "name": self.name,
            "description": self.description,
            "last_reviewed": self.last_reviewed,
            "freshness_days": self.freshness_days,
            "volatile": self.volatile,
            "stale": self.stale,
        }


@dataclass(frozen=True)
class SkillDetail:
    """Full skill payload (progressive disclosure tier 2)."""

    name: str
    description: str
    body: str
    references: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "body": self.body,
            "references": list(self.references),
        }


def _parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return {}, content

    frontmatter: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()

    body = content[match.end() :]
    return frontmatter, body


def _list_reference_paths(skill_dir: Path) -> list[str]:
    refs_dir = skill_dir / "references"
    if not refs_dir.is_dir():
        return []

    paths: list[str] = []
    for ref_file in sorted(refs_dir.rglob("*.md")):
        rel = ref_file.relative_to(skill_dir).as_posix()
        paths.append(rel)
    return paths


def _read_skill_file(skill_path: Path) -> SkillDetail:
    content = skill_path.read_text(encoding="utf-8")
    frontmatter, body = _parse_frontmatter(content)
    name = frontmatter.get("name", skill_path.parent.name)
    description = frontmatter.get("description", "")
    references = _list_reference_paths(skill_path.parent)
    return SkillDetail(name=name, description=description, body=body, references=references)


def _iter_skill_dirs(root: Path | str | None = None) -> list[Path]:
    base = skills_dir(root)
    skill_names = sorted(name for name in EXPECTED_SKILLS if (base / name / "SKILL.md").is_file())
    return [base / name for name in skill_names]


def list_skills(repo_root: Path | str | None = None) -> list[dict[str, str | bool | int | None]]:
    """Return name + description + freshness for every skill (cheap index)."""
    summaries: list[SkillSummary] = []
    for skill_dir in _iter_skill_dirs(repo_root):
        content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        frontmatter, _ = _parse_frontmatter(content)
        detail = _read_skill_file(skill_dir / "SKILL.md")
        meta = freshness_metadata(frontmatter)
        summaries.append(
            SkillSummary(
                name=detail.name,
                description=detail.description,
                last_reviewed=meta["last_reviewed"],
                freshness_days=meta["freshness_days"],
                volatile=bool(meta["volatile"]),
                stale=bool(meta["stale"]),
            )
        )
    return [item.to_dict() for item in summaries]


def get_skill(name: str, repo_root: Path | str | None = None) -> dict[str, Any]:
    """Return full skill body and reference paths for *name*."""
    root = repo_root or find_repo_root()
    skill_path = skills_dir(root) / name / "SKILL.md"
    if not skill_path.is_file():
        raise FileNotFoundError(f"Skill not found: {name}")

    return _read_skill_file(skill_path).to_dict()


def get_reference(name: str, path: str, repo_root: Path | str | None = None) -> str:
    """Return reference markdown content for *name* at relative *path*."""
    root = repo_root or find_repo_root()
    skill_dir = skills_dir(root) / name
    ref_path = (skill_dir / path).resolve()
    skill_root = skill_dir.resolve()

    if not str(ref_path).startswith(str(skill_root)):
        raise ValueError(f"Reference path escapes skill directory: {path}")
    if not ref_path.is_file():
        raise FileNotFoundError(f"Reference not found: {name}/{path}")

    return ref_path.read_text(encoding="utf-8")
