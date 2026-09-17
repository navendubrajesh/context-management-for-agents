"""Data residency and deployment mode enforcement (CM-070)."""

from __future__ import annotations

import os
from typing import Any


def deployment_mode() -> str:
    return os.environ.get("CONTEXT_SKILLS_DEPLOYMENT_MODE", "standard").lower()


def configured_region() -> str:
    return os.environ.get("CONTEXT_SKILLS_REGION", "").strip()


def is_air_gapped() -> bool:
    return deployment_mode() in {"air-gapped", "airgapped", "offline"}


def telemetry_allowed() -> bool:
    if is_air_gapped():
        return False
    return os.environ.get("CONTEXT_SKILLS_BLOCK_EXTERNAL_TELEMETRY", "").lower() not in {"1", "true"}


def residency_status() -> dict[str, Any]:
    region = configured_region()
    return {
        "deployment_mode": deployment_mode(),
        "region": region or None,
        "region_required": os.environ.get("CONTEXT_SKILLS_REQUIRE_REGION", "").lower() in {"1", "true"},
        "telemetry_allowed": telemetry_allowed(),
        "air_gapped": is_air_gapped(),
    }


def validate_residency_config() -> None:
    if os.environ.get("CONTEXT_SKILLS_REQUIRE_REGION", "").lower() in {"1", "true"} and not configured_region():
        raise RuntimeError("CONTEXT_SKILLS_REGION is required in regulated deployment mode")
