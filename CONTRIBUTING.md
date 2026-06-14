# Contributing to Context Management for Agents

Thanks for your interest in contributing. This project combines **Agent Skills content** (`skills/`), a **callable runtime** (`runtime/`), and a **researcher validation OS** (`researcher/`).

## Code of conduct

Participation is governed by our [Code of Conduct](CODE_OF_CONDUCT.md).

## What to contribute

| Area | Location | Notes |
|------|----------|-------|
| Skills | `skills/*/SKILL.md` | Follow `template/SKILL.md`; 500-line budget |
| Runtime | `runtime/` | Reuse `context_skills` public APIs only |
| Docs | `docs/` | MkDocs site; regenerate skills catalog when skills change |
| Benchmarks | `researcher/benchmarks/` | Keep fixtures realistic; document methodology |

## Skill authoring rules

1. **Progressive disclosure** — index metadata in frontmatter; deep content in `references/`.
2. **Ownership boundaries** — explicit "When to Activate" and "Do not activate" sections.
3. **Claims** — volatile facts go in `researcher/claims/` with sources; do not invent benchmarks.
4. **No gate weakening** — if validation fails, fix content or code properly; do not disable checks.

## Development setup

```bash
git clone https://github.com/navendubrajesh/context-management-for-agents.git
cd context-management-for-agents
pip install -e runtime/core -e runtime/api -e runtime/mcp -e runtime/sdk-python
pip install -r docs/requirements.txt
python examples/demo/run_demo.py
```

## Required validation (four gates)

Run before every commit / PR:

```bash
python researcher/scripts/validate_repo.py --strict
python researcher/scripts/skill_health.py --strict --no-history
python researcher/scripts/run_benchmarks.py
python researcher/scripts/check_activation_cases.py
```

Additional checks:

```bash
python -m pytest runtime/tests/ -q
python docs/scripts/check_skills_catalog.py
mkdocs build --strict
```

## Skills catalog (docs drift check)

When adding, removing, or renaming a skill:

```bash
python docs/scripts/generate_skills_catalog.py
git add docs/skills/index.md
```

CI fails if the catalog does not match `EXPECTED_SKILLS`.

## Pull requests

1. Fork and branch from `main`.
2. Keep changes focused; one concern per PR when possible.
3. Ensure all gates and tests pass.
4. Fill out the PR template.
5. Preserve MIT attribution (Navendu Brajesh; maybeanns; Muratcan Koylan).

## Honesty requirements

- Benchmark numbers must include the project-fixture caveat.
- Cost = **estimated**; pricing is operator-configured.
- Compliance = **supports/maps to** — never claim SOC 2, FedRAMP, ISO, etc.
- No fabricated logos, customers, or ratings.

## Questions

Open a [Discussion](https://github.com/navendubrajesh/context-management-for-agents/discussions) or issue with the `question` label.
