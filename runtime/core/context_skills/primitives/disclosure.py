"""Progressive disclosure helper — index, body, and reference tiers."""

from __future__ import annotations

from enum import Enum
from typing import Any

from context_skills import get_reference, get_skill, list_skills
from context_skills.metering import TokenCounter
from context_skills.primitives.metrics import PrimitiveMetrics, PrimitiveResult


class DisclosureTier(str, Enum):
    INDEX = "index"
    BODY = "body"
    REFERENCES = "references"


def disclose_skill(
    *,
    name: str | None = None,
    tier: DisclosureTier = DisclosureTier.INDEX,
    reference_path: str | None = None,
    repo_root: Any = None,
    counter: TokenCounter | None = None,
) -> PrimitiveResult:
    """Load skill content at the requested progressive-disclosure tier."""
    counter = counter or TokenCounter(prefer_heuristic=True)

    if tier == DisclosureTier.INDEX or name is None:
        index = list_skills(repo_root)
        before_parts = []
        for skill_name in sorted(item["name"] for item in index):
            detail = get_skill(skill_name, repo_root)
            before_parts.append(detail["body"])
            for ref in detail.get("references", []):
                try:
                    before_parts.append(get_reference(skill_name, ref, repo_root))
                except FileNotFoundError:
                    continue
        before = "\n\n".join(before_parts)
        after = "\n".join(f"- {item['name']}: {item['description']}" for item in index)
        operation = "disclose_skill:index"
    elif tier == DisclosureTier.BODY:
        detail = get_skill(name, repo_root)
        before = detail["body"]
        for ref in detail.get("references", []):
            try:
                before += "\n\n" + get_reference(name, ref, repo_root)
            except FileNotFoundError:
                continue
        after = f"# {detail['name']}\n\n{detail['description']}\n\n{detail['body']}"
        operation = f"disclose_skill:body:{name}"
    else:
        if not reference_path:
            raise ValueError("reference_path required for REFERENCES tier")
        detail = get_skill(name, repo_root)
        before = detail["body"]
        for ref in detail.get("references", []):
            try:
                before += "\n\n" + get_reference(name, ref, repo_root)
            except FileNotFoundError:
                continue
        after = get_reference(name, reference_path, repo_root)
        operation = f"disclose_skill:references:{name}"

    return PrimitiveResult(
        output=after,
        metrics=PrimitiveMetrics(
            operation=operation,
            tokens_before=counter.count(before),
            tokens_after=counter.count(after),
        ),
    )
