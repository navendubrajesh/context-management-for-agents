---
name: amazonq-context-architecture
description: Understand how Amazon Q Developer assembles context — .amazonq/rules/ glob loading, README and AmazonQ.md defaults, /context profiles, context file token budgets, and IDE vs CLI context channels. Use when tuning what Q sees, diagnosing oversized context files, or budgeting against token limits. Do not activate for general context theory (context-fundamentals) or authoring rules (amazonq-customization).
---

# Amazon Q Developer Context Architecture

Amazon Q Developer loads **project rules** from `.amazonq/rules/` (markdown files, optionally nested), plus default globs for `README.md` and `AmazonQ.md`. The **Q CLI** adds **context profiles**, explicit `/context add`, and hard token limits on matched files. Chat uses the open file plus explicitly added context; rules apply automatically when matched.

## When to Activate

Activate this skill when:
- Diagnosing why Q ignores project conventions or loads too many rule tokens
- Using `/context show` to audit what Q CLI includes
- Understanding glob-based rule matching and subdirectories
- Hitting ValidationException errors from oversized context files in CLI
- Choosing between IDE chat context and CLI global context profiles

Do not activate this skill for adjacent work owned by other skills:
- Do not activate for platform-agnostic attention theory: `context-fundamentals`.
- Do not activate for writing `.amazonq/rules/` content: `amazonq-customization`.
- Do not activate for chat compaction and `/compact`: `amazonq-session-management`.
- Do not activate for custom external RAG: `memory-systems`.

## Core Concepts

### Project rules loading

On first interaction, Q scans `.amazonq/rules/` and loads applicable markdown rules into context. Rules can live in subdirectories (e.g., `.amazonq/rules/frontend/react.rule.md`). Filename is organizational — Q reads all `.md` files in the tree.

Rules apply automatically in IDE chat; developers can toggle individual rules on/off per session via the Rules button.

### Default context globs (CLI)

Q CLI typically matches:
- `.amazonq/rules/**/*.md`
- `README.md`
- `AmazonQ.md`

Use `/context show` to see matched files and approximate token counts per file.

### Context profiles (CLI)

Profiles organize which context files apply to a session. Global vs profile-scoped files appear in `/context show` breakdown. Enterprise **Q Developer profiles** (IAM Identity Center) are subscription/settings collections — distinct from CLI context profiles but affect which features and settings apply.

### Token limits on context files

Q CLI enforces context file size limits (documentation and issue trackers reference ~200K total window with ~150K practical limit for context files). Oversized matched files can cause ValidationException on all model calls until removed. CLI may skip largest files with user notification when limits approached.

### IDE chat context model

Q uses the **currently open file** (language, path) as default context. Developers add files, folders, or workspace scope during chat. Session context persists within a chat tab but not across tabs — up to ~10 concurrent tabs in supported IDEs.

### MCP integration

Q CLI and IDE support MCP servers — tool schemas add fixed overhead to each request when enabled.

## Gotchas

- **Glob rules can match unexpectedly.** Broad patterns pull large rule sets into every request.
- **Huge single rule files break CLI.** Split rules by concern; monitor token counts with `/context show`.
- **Rules toggle in IDE only affects current session** — file changes persist, toggle state may not.
- **Open file ≠ full repo.** Q doesn't automatically load unrelated project rules unless files match scan patterns.
- **Profile vs project rules confusion.** Enterprise Q Developer profile is subscription config, not the same as CLI context profile display.

## Integration

- `amazonq-customization` covers authoring effective `.amazonq/rules/` and CLI agents.
- `amazonq-session-management` covers `/compact`, auto-nudge at ~80%, and `/clear`.
- `context-fundamentals` explains token budgeting for always-loaded rules.
- `tool-design` informs MCP selection loaded into Q sessions.

## References

- `references/amazonq-context-internals.md` — Rule loading flow, CLI context commands, token limit behavior.
- `claim-amazonq-context-architecture-limits`: Context window and context-file token limits follow AWS Q Developer documentation and CLI behavior (2025–2026) and may change between releases.
