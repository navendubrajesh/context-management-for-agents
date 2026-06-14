# Kiro Steering Internals

Sources: [kiro.dev/docs/steering](https://kiro.dev/docs/steering) (2025–2026).

## Scope hierarchy

1. `~/.kiro/steering/` — global, all workspaces
2. `.kiro/steering/` — workspace-specific (overrides global on conflict)
3. `AGENTS.md` — workspace root or global steering path (always included, no inclusion modes)

## Foundational files

Generated via Kiro panel → Generate Steering Docs:
- `product.md` — purpose, users, features, business goals
- `tech.md` — frameworks, libraries, constraints
- `structure.md` — file organization, naming, architecture

Included in every interaction by default.

## Inclusion frontmatter examples

Always:
```yaml
---
inclusion: always
---
```

File match (array supported):
```yaml
---
inclusion: fileMatch
fileMatchPattern: ["**/*.ts", "**/*.tsx"]
---
```

Manual:
```yaml
---
inclusion: manual
---
```

Auto (description-driven):
```yaml
---
inclusion: auto
name: api-design
description: REST API design patterns. Use when creating or modifying API endpoints.
---
```

## File reference syntax

```markdown
#[[file:components/ui/button.tsx]]
```

Pulls live file content into steering context when the steering file loads.

## Spec workflow context

Specs produce durable markdown artifacts (requirements, design, tasks) that outlive individual chat turns — treat them as the session's external memory.
