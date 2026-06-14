# Context Management for Agents — Build Runbook

End-to-end plan to take the project from a skills collection to an enterprise platform, in four phases.

## Current state

| Phase | Status |
|-------|--------|
| 0 — Skills + validation OS | Done |
| 1 — Consumable runtime | Done |
| 2 — Operationalized primitives | Done |
| 3 — Enterprise hardening | Done |
| 4 — Scale & ecosystem | Planned |

See [Roadmap](roadmap.md) for Phase 4 scope.

## Standing guardrails

1. Never break the four validation gates before commits.
2. Do not fork router/primitive logic — one implementation in `runtime/core/`.
3. Do not change skill content to make code pass.
4. Honest benchmarks, estimated costs, no certification claims.
5. Preserve MIT attribution chain.
6. Deterministic offline tests (mock IdP/OPA/vault).
7. Checkpoint commits; no push unless explicitly requested.
8. Each phase lists out-of-scope items as hooks only.

## Four gates

```bash
python researcher/scripts/validate_repo.py --strict
python researcher/scripts/skill_health.py --strict --no-history
python researcher/scripts/run_benchmarks.py
python researcher/scripts/check_activation_cases.py
```

## Runnable proof

```bash
python examples/demo/run_demo.py
python examples/demo/run_mcp_demo.py
```
