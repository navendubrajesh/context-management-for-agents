"""Chargeback / showback reports from usage records."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def chargeback_report(
    records: list[dict[str, Any]],
    *,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict[str, Any]:
    by_tenant: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"tokens_before": 0, "tokens_after": 0, "est_cost_usd": 0.0, "operations": 0}
    )
    for rec in records:
        ts = str(rec.get("timestamp") or rec.get("created_at") or "")
        if date_from and ts and ts[:10] < date_from:
            continue
        if date_to and ts and ts[:10] > date_to:
            continue
        tenant = rec.get("tenant_id") or "default"
        bucket = by_tenant[tenant]
        bucket["tokens_before"] += int(rec.get("tokens_before", 0))
        bucket["tokens_after"] += int(rec.get("tokens_after", 0))
        bucket["est_cost_usd"] += float(rec.get("est_cost_usd") or 0.0)
        bucket["operations"] += 1
    tenants = []
    for tenant_id, stats in sorted(by_tenant.items()):
        saved = max(0, stats["tokens_before"] - stats["tokens_after"])
        tenants.append(
            {
                "tenant_id": tenant_id,
                "operations": stats["operations"],
                "tokens_before": stats["tokens_before"],
                "tokens_after": stats["tokens_after"],
                "tokens_saved": saved,
                "est_cost_usd": round(stats["est_cost_usd"], 6),
                "disclaimer": "estimated — operator-configured pricing",
            }
        )
    return {
        "tenants": tenants,
        "period": {"from": date_from, "to": date_to},
        "disclaimer": "estimated — operator-configured pricing",
    }
