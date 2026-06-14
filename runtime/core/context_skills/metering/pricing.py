"""Config-driven estimated pricing — operator values, not factual claims."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModelPricing:
    input_per_1k_tokens_usd: float
    output_per_1k_tokens_usd: float


def _pricing_path() -> Path:
    return Path(__file__).with_name("pricing.json")


def load_pricing_table(path: Path | None = None) -> dict:
    table_path = path or _pricing_path()
    return json.loads(table_path.read_text(encoding="utf-8"))


def get_model_pricing(model: str | None = None, *, path: Path | None = None) -> ModelPricing:
    table = load_pricing_table(path)
    model_name = model or table.get("default_model", "gpt-4o-mini")
    entry = table["models"].get(model_name)
    if entry is None:
        entry = next(iter(table["models"].values()))
    return ModelPricing(
        input_per_1k_tokens_usd=float(entry["input_per_1k_tokens_usd"]),
        output_per_1k_tokens_usd=float(entry["output_per_1k_tokens_usd"]),
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
