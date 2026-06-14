---
name: cursor-customization
description: Author the files that steer Cursor Agent — .cursor/rules/*.mdc with description/globs/alwaysApply frontmatter, nested AGENTS.md, user rules, and MCP configuration. Use when writing or restructuring Cursor rules, when rules are ignored, or when rule bloat degrades Agent responses. Do not activate for Cursor indexing internals (cursor-context-architecture) or general prompt theory (context-fundamentals).
---

# Cursor Customization

Cursor exposes a layered steering surface: **Project Rules** (`.cursor/rules/*.mdc`), **User Rules**, **Team Rules**, **AGENTS.md**, and **MCP servers**. These files are the primary user-controlled context channel for Agent (Chat). This skill covers authoring them with correct activation modes and token budgeting.

## When to Activate

Activate this skill when:
- Creating or restructuring `.cursor/rules/` or root/nested `AGENTS.md`
- Choosing between Always Apply, glob-scoped, agent-requested, and manual rule modes
- Agent ignores stated conventions or applies backend rules to frontend files
- Responses degrade after rules grow ("rule bloat")
- Configuring MCP servers and deciding which to enable for Agent

Do not activate this skill for adjacent work owned by other skills:
- Do not activate for semantic indexing or @-mention mechanics: `cursor-context-architecture`.
- Do not activate for compression and session lifecycle: `cursor-session-management`.
- Do not activate for platform-agnostic instruction theory: `context-fundamentals`.
- Do not activate for MCP tool schema design: `tool-design`.

## Core Concepts

### Project rules (.mdc)

Rules live in `.cursor/rules/` as `.mdc` files with YAML frontmatter: `description`, `globs`, `alwaysApply`. Plain `.md` files in that directory are **ignored** — use `.mdc` or AGENTS.md instead.

| Mode | Frontmatter pattern | When it loads |
|------|---------------------|---------------|
| Always Apply | `alwaysApply: true` | Every Agent session |
| Glob-scoped | `globs: "src/**/*.tsx"`, `alwaysApply: false` | Matching files in context |
| Agent-requested | `description: "..."`, no globs | Agent decides from description |
| Manual | no description, no globs | `@rule-name` in chat |

Precedence on conflict: Team Rules → Project Rules → User Rules.

### Token budgeting always-on rules

`alwaysApply: true` rules prepend to **every** Agent request. Keep universal rules under ~50 lines of behavior-changing content. Push domain-specific guidance to glob-scoped or agent-requested rules — progressive disclosure native to Cursor.

### AGENTS.md alternative

For simpler projects, root or nested `AGENTS.md` files provide plain-markdown instructions without frontmatter. Nested AGENTS.md in subdirectories scopes guidance to that tree — more specific files take precedence over parents.

### MCP servers

Each enabled MCP server injects tool definitions into Agent context. Disable servers not needed for the current work — schema bloat competes with code context (see `tool-design`).

### What rules do not affect

Project/User Rules apply to **Agent (Chat) only** — not Cursor Tab, not Inline Edit (Cmd/Ctrl+K). Style rules here won't reshape inline completions.

## Authoring Playbook

1. **Start from repeated Agent mistakes** — add rules reactively, not speculatively.
2. **One concern per rule file** — `api-validation.mdc`, not `everything.mdc`.
3. **Reference canonical files** with `@filename.ts` in rule bodies instead of copying code.
4. **Use globs for directory-specific standards** — keeps React rules out of Python chats.
5. **Check rules into git** — team-wide consistency requires version control.

## Gotchas

- **Wrong extension silently ignored.** `.md` in `.cursor/rules/` without proper setup won't load as a rule.
- **Glob rules need context attachment.** Matching files must be in chat context or read by Agent — not just open in editor.
- **Team Rules can override project rules.** Enterprise teams may enforce rules developers cannot disable.
- **Duplicated AGENTS.md + alwaysApply rules** double-pay token cost for the same guidance.
- **Legacy `.cursorrules`** is deprecated — migrate to `.mdc` or AGENTS.md.

## Integration

- `cursor-context-architecture` explains how rules compete with indexing and @ attachments in the window.
- `cursor-session-management` covers what happens when rule + MCP overhead fills the window.
- `context-fundamentals` provides attention-budget reasoning for the narrowest-layer rule.
- `tool-design` owns MCP tool schemas this skill decides to enable.

## References

- `references/cursor-rules.md` — Frontmatter matrix, glob examples, AGENTS.md nesting, Team Rules precedence.
- `claim-cursor-customization-rules`: Rule types, frontmatter fields, and Agent-only application scope follow Cursor docs (2025–2026) and may change between releases.
