"""Token budget alert webhooks for orchestrators (CM-603)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BudgetAlertConfig:
    threshold_pct: float = 80.0
    callback_url: str = ""


class BudgetAlertStore:
    def __init__(self) -> None:
        self._configs: dict[str, BudgetAlertConfig] = {}

    def set_config(self, tenant_id: str, *, threshold_pct: float, callback_url: str) -> BudgetAlertConfig:
        cfg = BudgetAlertConfig(threshold_pct=threshold_pct, callback_url=callback_url)
        self._configs[tenant_id] = cfg
        return cfg

    def get_config(self, tenant_id: str) -> BudgetAlertConfig | None:
        return self._configs.get(tenant_id)

    def maybe_alert(
        self,
        tenant_id: str,
        *,
        tokens_used: int,
        token_budget: int,
        operation: str,
        correlation_id: str = "",
    ) -> dict[str, Any] | None:
        cfg = self._configs.get(tenant_id)
        if not cfg or not cfg.callback_url or token_budget <= 0:
            return None
        used_pct = (tokens_used / token_budget) * 100
        if used_pct < cfg.threshold_pct:
            return None
        payload = {
            "tenant_id": tenant_id,
            "operation": operation,
            "tokens_used": tokens_used,
            "token_budget": token_budget,
            "used_pct": round(used_pct, 2),
            "threshold_pct": cfg.threshold_pct,
            "correlation_id": correlation_id,
        }
        self._dispatch(cfg.callback_url, payload)
        return payload

    def _dispatch(self, url: str, payload: dict[str, Any]) -> None:
        if os.environ.get("CONTEXT_SKILLS_DISABLE_WEBHOOKS", "").lower() in {"1", "true"}:
            return
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:  # noqa: S310
                resp.read()
        except (urllib.error.URLError, TimeoutError):
            pass


_STORE: BudgetAlertStore | None = None


def get_budget_alert_store() -> BudgetAlertStore:
    global _STORE
    if _STORE is None:
        _STORE = BudgetAlertStore()
    return _STORE
