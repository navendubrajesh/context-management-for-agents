"""Deterministic lexical skill router (no LLM, no network)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from context_skills.loader import _parse_frontmatter
from context_skills.paths import find_repo_root, skills_dir
from context_skills.constants import EXPECTED_SKILLS


def get_words(text: str) -> set[str]:
    """Extract lowercase word tokens (length >= 3) from *text*."""
    return set(re.findall(r"\b[a-z0-9-]{3,}\b", text.lower()))


def load_router_index(repo_root: Path | str | None = None) -> dict[str, dict[str, Any]]:
    """Build lexical index used by :func:`score_skill_match` and :func:`route`."""
    root = repo_root or find_repo_root()
    base = skills_dir(root)
    skills_data: dict[str, dict[str, Any]] = {}

    for skill_name in EXPECTED_SKILLS:
        skill_file = base / skill_name / "SKILL.md"
        if not skill_file.is_file():
            continue

        content = skill_file.read_text(encoding="utf-8")
        frontmatter, _body = _parse_frontmatter(content)
        description = frontmatter.get("description", "")

        skills_data[skill_name] = {
            "name": skill_name,
            "description": description,
            "content": content,
            "name_words": get_words(skill_name.replace("-", " ")),
            "desc_words": get_words(description),
            "content_words": get_words(content),
        }

    return skills_data


def score_skill_match(query: str, skill_data: dict[str, Any]) -> float:
    """Score how well *query* matches a pre-built *skill_data* entry."""
    query_words = get_words(query)
    if not query_words:
        return 0.0

    name_weight = 5.0
    desc_weight = 2.0
    content_weight = 0.5

    name_matches = query_words.intersection(skill_data["name_words"])
    desc_matches = query_words.intersection(skill_data["desc_words"])
    content_matches = query_words.intersection(skill_data["content_words"])

    score = (
        len(name_matches) * name_weight
        + len(desc_matches) * desc_weight
        + len(content_matches) * content_weight
    )

    if skill_data["name"] == "context-fundamentals":
        if any(
            w in query_words
            for w in [
                "prevent",
                "failure",
                "poisoning",
                "distraction",
                "clash",
                "degrade",
                "degradation",
            ]
        ):
            score *= 0.5
    elif skill_data["name"] == "context-degradation":
        if any(
            w in query_words
            for w in [
                "prevent",
                "failure",
                "poisoning",
                "distraction",
                "clash",
                "degrade",
                "degradation",
            ]
        ):
            score *= 2.0

    if skill_data["name"] == "context-optimization":
        if any(w in query_words for w in ["compress", "history", "handoff", "summarize"]):
            score *= 0.5
    elif skill_data["name"] == "context-compression":
        if any(w in query_words for w in ["compress", "history", "handoff", "summarize"]):
            score *= 2.0

    return score


def route(task: str, top_k: int = 5, repo_root: Path | str | None = None) -> list[dict[str, Any]]:
    """Return top-*top_k* skills ranked by lexical activation score for *task*."""
    if top_k < 1:
        raise ValueError("top_k must be >= 1")

    index = load_router_index(repo_root)
    ranked = sorted(
        (
            {"skill": name, "score": score_skill_match(task, data)}
            for name, data in index.items()
        ),
        key=lambda item: item["score"],
        reverse=True,
    )

    return ranked[:top_k]
