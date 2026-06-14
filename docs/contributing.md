# Contributing

Thank you for helping improve context-management-for-agents.

## Before you start

1. Read [Concepts](concepts.md) and the [Skills catalog](skills/index.md).
2. For **skill content** changes, follow `template/SKILL.md` (500-line budget, ownership boundaries, claims for volatile facts).
3. For **runtime/code** changes, reuse public APIs in `runtime/core/context_skills/` — do not fork router or primitive logic.

## Development setup

```bash
pip install -e runtime/core -e runtime/api -e runtime/mcp -e runtime/sdk-python
pip install mkdocs-material
python examples/demo/run_demo.py
```

## Required checks (four gates)

Every PR must pass:

```bash
python researcher/scripts/validate_repo.py --strict
python researcher/scripts/skill_health.py --strict --no-history
python researcher/scripts/run_benchmarks.py
python researcher/scripts/check_activation_cases.py
```

Plus:

```bash
python -m pytest runtime/tests/ -q
python docs/scripts/check_skills_catalog.py
mkdocs build --strict
```

CI runs these automatically.

## Skills catalog

If you add or rename a skill, regenerate the docs catalog:

```bash
python docs/scripts/generate_skills_catalog.py
git add docs/skills/index.md
```

## Pull request checklist

- [ ] Four gates green locally
- [ ] Runtime tests pass
- [ ] Skills catalog updated (if skills changed)
- [ ] No fabricated benchmarks, certifications, or customer claims
- [ ] MIT attribution preserved (Navendu Brajesh; maybeanns; Muratcan Koylan)

Full policy: [CONTRIBUTING.md on GitHub](https://github.com/navendubrajesh/context-management-for-agents/blob/main/CONTRIBUTING.md).
