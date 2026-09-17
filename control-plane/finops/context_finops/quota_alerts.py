"""Real-time quota threshold webhooks with retry/backoff (CM-045)."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any


DEFAULT_THRESHOLDS = (80.0, 95.0)


@dataclass
class QuotaAlertConfig:
    callback_url: str
    thresholds: tuple[float, ...] = DEFAULT_THRESHOLDS
    fired: set[float] = field(default_factory=set)


class QuotaAlertStore:
    def __init__(self) -> None:
        self._configs: dict[str, QuotaAlertConfig] = {}

    def set_config(
        self,
        tenant_id: str,
        *,
        callback_url: str,
        thresholds: tuple[float, ...] | None = None,
    ) -> QuotaAlertConfig:
        existing = self._configs.get(tenant_id)
        fired = existing.fired if existing else set()
        cfg = QuotaAlertConfig(
            callback_url=callback_url,
            thresholds=thresholds or DEFAULT_THRESHOLDS,
            fired=fired,
        )
        self._configs[tenant_id] = cfg
        return cfg

    def get_config(self, tenant_id: str) -> QuotaAlertConfig | None:
        return self._configs.get(tenant_id)

    def reset_fired(self, tenant_id: str | None = None) -> None:
        if tenant_id is None:
            for cfg in self._configs.values():
                cfg.fired.clear()
            return
        cfg = self._configs.get(tenant_id)
        if cfg is not None:
            cfg.fired.clear()

    def evaluate(self, tenant_id: str, *, tokens_used: int, token_limit: int) -> list[dict[str, Any]]:
        if token_limit <= 0:
            return []
        cfg = self._configs.get(tenant_id)
        if cfg is None or not cfg.callback_url:
            return []
        used_pct = round((tokens_used / token_limit) * 100, 2)
        dispatched: list[dict[str, Any]] = []
        for threshold in sorted(cfg.thresholds):
            if used_pct >= threshold and threshold not in cfg.fired:
                payload = {
                    "tenant_id": tenant_id,
                    "alert_type": "quota_threshold",
                    "threshold_pct": threshold,
                    "used_pct": used_pct,
                    "tokens_used": tokens_used,
                    "token_limit": token_limit,
                }
                ok = self._dispatch_with_retry(cfg.callback_url, payload)
                cfg.fired.add(threshold)
                dispatched.append({**payload, "delivered": ok})
        return dispatched

    def _dispatch_with_retry(self, url: str, payload: dict[str, Any]) -> bool:
        if os.environ.get("CONTEXT_SKILLS_DISABLE_WEBHOOKS", "").lower() in {"1", "true"}:
            return True
        data = json.dumps(payload).encode("utf-8")
        delays = (0.0, 0.5, 1.5)
        for delay in delays:
            if delay:
                time.sleep(delay)
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=5) as resp:  # noqa: S310
                    resp.read()
                return True
            except (urllib.error.URLError, TimeoutError):
                continue
        return False


_STORE: QuotaAlertStore | None = None


def get_quota_alert_store() -> QuotaAlertStore:
    global _STORE
    if _STORE is None:
        _STORE = QuotaAlertStore()
    return _STORE
