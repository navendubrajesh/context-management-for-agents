# Benchmarks

## Caveat (read first)

All numbers below are **measured on this project's own test fixtures**. The harness and fixtures originate from [context-management-for-antigravity](https://github.com/maybeanns/context-management-for-antigravity) (maybeanns) and were **re-measured here** on 2026-06-14 with 28 skills across five platforms. They are **not** guarantees for your production workloads.

## Reproduce

```bash
python researcher/benchmarks/context-savings/benchmark_context_savings.py
python researcher/benchmarks/context-savings/benchmark_context_savings.py --markdown
python researcher/scripts/run_benchmarks.py   # CI gate wrapper
```

## Runnable demo (subset)

```bash
python examples/demo/run_demo.py
```

Uses the same handoff fixture family as the benchmark; expect **~93% savings** on token count for `compact_session` handoff mode.

## Summary table (project fixtures)

| Technique | Before | After | Saved | Savings % |
|-----------|-------:|------:|------:|----------:|
| Observation Masking | 2,222 | 95 | 2,127 | 95.7% |
| Hierarchical Summarization | 3,777 | 428 | 3,349 | 88.7% |
| Handoff Summary | 3,777 | 255 | 3,522 | 93.2% |
| Combined Pipeline | 2,936 | 234 | 2,702 | 92.0% |
| Progressive Disclosure | 58,790 | 3,426 | 55,364 | 94.2% |
| **Total (all techniques)** | **79,402** | **5,649** | **73,753** | **92.9%** |

Full table and methodology: root [README benchmark section](https://github.com/navendubrajesh/context-management-for-agents#context-window-savings-measured).

## Validation gates

Benchmarks are one of **four gates** that must pass on every PR:

```bash
python researcher/scripts/validate_repo.py --strict
python researcher/scripts/skill_health.py --strict --no-history
python researcher/scripts/run_benchmarks.py
python researcher/scripts/check_activation_cases.py
```
