# Cursor Rules Reference

Sources: [cursor.com/docs/rules](https://cursor.com/docs/rules), [cursor.com/docs/agent/prompting](https://cursor.com/docs/agent/prompting).

## Frontmatter examples

Always apply:
```yaml
---
alwaysApply: true
---
```

Glob-scoped:
```yaml
---
globs: src/components/**/*.tsx
alwaysApply: false
---
```

Agent-requested:
```yaml
---
description: RPC service conventions for backend services
alwaysApply: false
---
```

## Glob pattern reference

| Pattern | Matches |
|---------|---------|
| `**/*.ts` | All TypeScript files recursively |
| `src/**` | Everything under src/ |
| `docs/**/*.md, docs/**/*.mdx` | Comma-separated patterns |

## AGENTS.md nesting

```
project/AGENTS.md
frontend/AGENTS.md      # Overrides/adds for frontend/
backend/AGENTS.md       # Overrides/adds for backend/
```

More specific directory instructions take precedence when working in that subtree.

## Best practices (from Cursor docs)

- Keep rules under 500 lines; split composable rules
- Point to files instead of copying contents
- Avoid duplicating linter knowledge
- Rules do not affect Tab or Inline Edit
