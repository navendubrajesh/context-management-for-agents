"""Session context fill level and degradation zone classification (CM-601)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SessionHealthThresholds:
    healthy_max: float = 0.70
    warning_max: float = 0.85
    degraded_max: float = 0.95


def _thresholds() -> SessionHealthThresholds:
    return SessionHealthThresholds(
        healthy_max=float(os.environ.get("CONTEXT_SKILLS_HEALTH_HEALTHY_MAX", "0.70")),
        warning_max=float(os.environ.get("CONTEXT_SKILLS_HEALTH_WARNING_MAX", "0.85")),
        degraded_max=float(os.environ.get("CONTEXT_SKILLS_HEALTH_DEGRADED_MAX", "0.95")),
    )


def classify_session_health(
    token_count: int,
    *,
    context_limit: int | None = None,
) -> dict[str, Any]:
    """Return degradation zone for a session based on token fill ratio."""
    limit = context_limit or int(os.environ.get("CONTEXT_SKILLS_CONTEXT_LIMIT", "128000"))
    if limit <= 0:
        raise ValueError("context_limit must be positive")
    if token_count < 0:
        raise ValueError("token_count must be non-negative")

    fill_ratio = round(token_count / limit, 4)
    thresholds = _thresholds()
    if fill_ratio < thresholds.healthy_max:
        zone = "healthy"
        recommendation = "Continue session; compaction optional."
    elif fill_ratio < thresholds.warning_max:
        zone = "warning"
        recommendation = "Consider hierarchical compaction or observation masking."
    elif fill_ratio < thresholds.degraded_max:
        zone = "degraded"
        recommendation = "Run compact_session or handoff summary before next turn."
    else:
        zone = "critical"
        recommendation = "Reset session or run full context pipeline immediately."

    return {
        "token_count": token_count,
        "context_limit": limit,
        "fill_ratio": fill_ratio,
        "fill_pct": round(fill_ratio * 100, 2),
        "zone": zone,
        "recommendation": recommendation,
        "thresholds": {
            "healthy_max_pct": round(thresholds.healthy_max * 100, 1),
            "warning_max_pct": round(thresholds.warning_max * 100, 1),
            "degraded_max_pct": round(thresholds.degraded_max * 100, 1),
        },
    }
