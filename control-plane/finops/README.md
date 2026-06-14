# FinOps enforcement

Per-tenant token quotas, rate limits, budget thresholds, and chargeback/showback reports.

Cost values are **estimated**; pricing is operator-configured via `runtime/core/context_skills/metering/pricing.json`.

## Environment

- `CONTEXT_SKILLS_QUOTA_ENFORCE=block|throttle|off` (default `off` for Phase 1–2 compat)
- Per-tenant limits in `CONTEXT_SKILLS_QUOTAS_FILE` JSON
