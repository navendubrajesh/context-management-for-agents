## Summary

<!-- What does this PR change and why? -->

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Skill content (follows template/SKILL.md)
- [ ] Runtime / API

## Validation checklist

- [ ] `python researcher/scripts/validate_repo.py --strict`
- [ ] `python researcher/scripts/skill_health.py --strict --no-history`
- [ ] `python researcher/scripts/run_benchmarks.py`
- [ ] `python researcher/scripts/check_activation_cases.py`
- [ ] `python -m pytest runtime/tests/ -q` (if runtime touched)
- [ ] `python docs/scripts/check_skills_catalog.py` (if skills added/renamed)
- [ ] `mkdocs build --strict` (if docs touched)

## Honesty / attribution

- [ ] No fabricated benchmarks or certification claims
- [ ] MIT attribution preserved
- [ ] Benchmark caveat included if numbers changed

## Related issues

Fixes #
