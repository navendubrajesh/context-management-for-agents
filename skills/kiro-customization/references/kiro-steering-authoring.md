# Kiro Steering Authoring Reference

Sources: [kiro.dev/docs/steering](https://kiro.dev/docs/steering).

## Recommended filenames

- `api-rest-conventions.md`
- `testing-unit-patterns.md`
- `components-form-validation.md`
- `security-policies.md`

## Frontmatter templates

File-scoped:
```yaml
---
inclusion: fileMatch
fileMatchPattern: "app/api/**/*"
---
```

Manual (invoke with `#api-migration-guide`):
```yaml
---
inclusion: manual
---
```

Auto (description-driven activation):
```yaml
---
inclusion: auto
name: deployment-workflow
description: CI/CD and deployment procedures. Use when modifying build or release configuration.
---
```

## AGENTS.md placement

- Workspace root — always loaded
- `~/.kiro/steering/AGENTS.md` — global always loaded

No inclusion modes available for AGENTS.md — keep concise.

## Security

Steering files are committed to the repo. Never include API keys, credentials, or customer data.
