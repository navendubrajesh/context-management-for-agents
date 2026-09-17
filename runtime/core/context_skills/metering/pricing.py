"""Config-driven estimated pricing — operator values, not factual claims (CM-044)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModelPricing:
    input_per_1k_tokens_usd: float
    output_per_1k_tokens_usd: float
    tier: str = "standard"
    model: str = "gpt-4o-mini"


def _pricing_path() -> Path:
    override = os.environ.get("CONTEXT_SKILLS_PRICING_PATH", "").strip()
    if override:
        return Path(override)
    return Path(__file__).with_name("pricing.json")


def load_pricing_table(path: Path | None = None) -> dict:
    table_path = path or _pricing_path()
    return json.loads(table_path.read_text(encoding="utf-8"))


def save_pricing_table(table: dict, path: Path | None = None) -> None:
    table_path = path or _pricing_path()
    table_path.write_text(json.dumps(table, indent=2) + "\n", encoding="utf-8")


def resolve_model_name(table: dict, *, model: str | None = None, tier: str | None = None) -> str:
    tier_name = tier or table.get("default_tier", "standard")
    tiers = table.get("tiers", {})
    tier_cfg = tiers.get(tier_name, {})
    return model or tier_cfg.get("default_model") or table.get("default_model", "gpt-4o-mini")


def get_model_pricing(
    model: str | None = None,
    *,
    tier: str | None = None,
    path: Path | None = None,
) -> ModelPricing:
    table = load_pricing_table(path)
    model_name = resolve_model_name(table, model=model, tier=tier)
    entry = table["models"].get(model_name)
    if entry is None:
        entry = next(iter(table["models"].values()))
    tier_name = tier or table.get("default_tier", "standard")
    tier_cfg = table.get("tiers", {}).get(tier_name, {})
    discount = float(tier_cfg.get("discount_pct", 0)) / 100.0
    input_rate = float(entry["input_per_1k_tokens_usd"]) * (1.0 - discount)
    output_rate = float(entry["output_per_1k_tokens_usd"]) * (1.0 - discount)
    return ModelPricing(
        input_per_1k_tokens_usd=input_rate,
        output_per_1k_tokens_usd=output_rate,
        tier=tier_name,
        model=model_name,
    )


def estimate_cost_usd(
    tokens_before: int,
    tokens_after: int,
    *,
    model: str | None = None,
    path: Path | None = None,
) -> float:
    """Estimated USD saved by sending fewer input tokens (illustrative only)."""
    pricing = get_model_pricing(model, path=path)
    saved = max(0, tokens_before - tokens_after)
    return round((saved / 1000) * pricing.input_per_1k_tokens_usd, 8)
