"""Skill freshness metadata and stale detection (CM-407)."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any


DEFAULT_FRESHNESS_DAYS = 90


def parse_review_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None


def is_stale(
    *,
    last_reviewed: str | None = None,
    freshness_days: int | None = None,
    volatile: bool = False,
    today: date | None = None,
) -> bool:
    """Return True when a skill exceeds its freshness window."""
    if volatile:
        window = freshness_days if freshness_days is not None else 30
    else:
        window = freshness_days if freshness_days is not None else DEFAULT_FRESHNESS_DAYS
    reviewed = parse_review_date(last_reviewed)
    if reviewed is None:
        return False
    ref = today or datetime.now(timezone.utc).date()
    age = (ref - reviewed).days
    return age > window


def freshness_metadata(frontmatter: dict[str, str]) -> dict[str, Any]:
    last_reviewed = frontmatter.get("last_reviewed") or frontmatter.get("freshness")
    freshness_days_raw = frontmatter.get("freshness_days")
    volatile = frontmatter.get("volatile", "").lower() in {"true", "yes", "1"}
    freshness_days = int(freshness_days_raw) if freshness_days_raw and freshness_days_raw.isdigit() else None
    stale = is_stale(
        last_reviewed=last_reviewed,
        freshness_days=freshness_days,
        volatile=volatile,
    )
    return {
        "last_reviewed": last_reviewed,
        "freshness_days": freshness_days or (30 if volatile else DEFAULT_FRESHNESS_DAYS),
        "volatile": volatile,
        "stale": stale,
    }
