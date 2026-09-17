"""Per-tenant quotas and rate limits."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any, Literal

EnforcementMode = Literal["block", "throttle", "off"]


@dataclass
class TenantQuota:
    tenant_id: str
    token_limit: int
    requests_per_minute: int
    est_budget_usd: float


class QuotaStore:
    def __init__(self) -> None:
        self._quotas: dict[str, TenantQuota] = {
            "tenant-a": TenantQuota("tenant-a", token_limit=500_000, requests_per_minute=120, est_budget_usd=50.0),
            "tenant-b": TenantQuota("tenant-b", token_limit=100_000, requests_per_minute=30, est_budget_usd=10.0),
        }
        self._token_usage: dict[str, int] = {}
        self._request_windows: dict[str, list[float]] = {}
        self._lock = Lock()

    def load_from_file(self, path: Path | str) -> None:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        with self._lock:
            for item in data.get("quotas", []):
                q = TenantQuota(**item)
                self._quotas[q.tenant_id] = q

    def get(self, tenant_id: str) -> TenantQuota | None:
        with self._lock:
            return self._quotas.get(tenant_id)

    def usage_snapshot(self, tenant_id: str) -> tuple[int, int]:
        quota = self.get(tenant_id)
        with self._lock:
            used = self._token_usage.get(tenant_id, 0)
        limit = quota.token_limit if quota else 0
        return used, limit

    def record_tokens(self, tenant_id: str, tokens: int) -> None:
        with self._lock:
            self._token_usage[tenant_id] = self._token_usage.get(tenant_id, 0) + tokens
        self._maybe_quota_alert(tenant_id)

    def _maybe_quota_alert(self, tenant_id: str) -> None:
        try:
            from context_finops.quota_alerts import get_quota_alert_store
        except ImportError:
            return
        used, limit = self.usage_snapshot(tenant_id)
        if limit > 0:
            get_quota_alert_store().evaluate(tenant_id, tokens_used=used, token_limit=limit)

    def record_request(self, tenant_id: str) -> None:
        now = time.time()
        with self._lock:
            window = self._request_windows.setdefault(tenant_id, [])
            window.append(now)
            self._request_windows[tenant_id] = [t for t in window if now - t < 60]

    def check(self, tenant_id: str) -> tuple[bool, str]:
        mode = os.environ.get("CONTEXT_SKILLS_QUOTA_ENFORCE", "off").lower()
        if mode == "off":
            return True, "quota enforcement off"
        quota = self.get(tenant_id)
        if quota is None:
            return True, "no quota configured"
        with self._lock:
            used = self._token_usage.get(tenant_id, 0)
            rpm = len(self._request_windows.get(tenant_id, []))
        if used >= quota.token_limit:
            return mode != "block", f"token quota exceeded ({used}/{quota.token_limit})"
        if rpm >= quota.requests_per_minute:
            return mode != "block", f"rate limit exceeded ({rpm}/{quota.requests_per_minute} rpm)"
        return True, "within quota"

    def reset(self) -> None:
        with self._lock:
            self._token_usage.clear()
            self._request_windows.clear()
        try:
            from context_finops.quota_alerts import get_quota_alert_store

            get_quota_alert_store().reset_fired()
        except ImportError:
            pass


_GLOBAL = QuotaStore()


def get_quota_store() -> QuotaStore:
    path = os.environ.get("CONTEXT_SKILLS_QUOTAS_FILE")
    if path and Path(path).is_file():
        _GLOBAL.load_from_file(path)
    return _GLOBAL
