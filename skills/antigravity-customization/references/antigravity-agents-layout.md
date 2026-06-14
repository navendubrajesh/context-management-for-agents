# Antigravity AGENTS.md and .agents/ Layout

## Recommended AGENTS.md sections

```markdown
# Project Name

## Overview
One paragraph: what this repo is and its primary language/framework.

## Build & Verify
- Install: `npm install`
- Test: `npm test`
- Lint: `npm run lint`

## Architecture
Key directories and where logic lives.

## Do Not
- Never edit files in `dist/` or `generated/`
- Never commit secrets or `.env` values

## Skills
Specialized skills live in `.agents/skills/`. Read a skill's SKILL.md only when the task matches its description.
```

## .agents/ directory

```
.agents/
  skills/
    deploy/SKILL.md
    security-review/SKILL.md
  workflows/
    release.md
  plans/          # gitignored session plans
  tmp/            # gitignored scratch
```

## Nested AGENTS.md

```
repo/AGENTS.md
repo/services/payments/AGENTS.md   # Payment-specific rules
```

Child AGENTS.md adds/overrides when agent works in that subtree.

## Skills vs workflows

| Type | Location | Use for |
|------|----------|---------|
| Skill | `.agents/skills/*/SKILL.md` | Reusable capability, loaded on demand |
| Workflow | `.agents/workflows/*.md` | Linear multi-step procedure |
