---
name: kiro-context-architecture
description: Understand how Amazon Kiro assembles context — workspace and global steering files with inclusion modes, foundational steering docs, spec artifacts (requirements/design/tasks), file references, and MCP integration. Use when tuning what Kiro sees across spec-driven workflows or diagnosing missing project context. Do not activate for general context theory (context-fundamentals) or authoring steering files (kiro-customization).
---

# Kiro Context Architecture

Kiro is a **spec-driven agentic IDE**: persistent context comes from **steering files** (`.kiro/steering/` and `~/.kiro/steering/`), **foundational docs** (product, tech, structure), **spec artifacts**, and **live file references** — not from ad-hoc chat history alone. Understanding this stack tells you which levers survive across conversations.

## When to Activate

Activate this skill when:
- Diagnosing why Kiro ignores project conventions or uses the wrong stack
- Deciding what belongs in always-on steering vs conditional vs manual inclusion
- Structuring specs (requirements, design, tasks) as durable context for multi-step work
- Choosing workspace vs global steering scope
- Integrating MCP servers and understanding their context cost

Do not activate this skill for adjacent work owned by other skills:
- Do not activate for platform-agnostic attention theory: `context-fundamentals`.
- Do not activate for writing steering frontmatter and inclusion modes: `kiro-customization`.
- Do not activate for long-horizon spec session hygiene: `kiro-session-management`.
- Do not activate for external RAG design: `memory-systems`.

## Core Concepts

### Steering as persistent context

Steering files are markdown documents with optional YAML frontmatter controlling **inclusion mode**. Workspace steering (`.kiro/steering/`) overrides global steering (`~/.kiro/steering/`) on conflict — narrowest applicable scope wins.

### Inclusion modes

| Mode | Frontmatter | Loads when |
|------|-------------|------------|
| Always (default) | `inclusion: always` | Every interaction |
| File match | `inclusion: fileMatch` + `fileMatchPattern` | Working with matching paths |
| Manual | `inclusion: manual` | `#filename` in chat or `/` slash command |
| Auto | `inclusion: auto` + `name` + `description` | Request matches description (skill-like) |

Foundational steering (`product.md`, `tech.md`, `structure.md`) is always included by default — the baseline project understanding.

### Spec-driven artifacts as context

Kiro's spec workflow generates **requirements**, **design**, and **tasks** documents before implementation. These artifacts become the authoritative task context — more durable than chat transcripts. Ambiguous specs produce ambiguous code; over-specified tasks reduce rework.

### Live file references

Steering can embed live workspace files: `#[[file:api/openapi.yaml]]`. References stay current as code changes — prefer references over copied snippets in steering.

### AGENTS.md bridge

Kiro reads `AGENTS.md` at workspace or global steering locations. AGENTS.md has **no inclusion modes** — it is always included when present. Use for cross-tool compatibility; use steering frontmatter for progressive disclosure within Kiro.

### MCP and hooks

MCP servers extend tool context; hooks automate responses to file events. Both add overhead — enable selectively for the current spec phase.

## Gotchas

- **Always-on steering accumulates silently.** Foundation + custom `inclusion: always` files compete for every request's budget.
- **Global vs workspace conflicts** resolve to workspace — but duplicate guidance still wastes tokens if both say similar things.
- **Specs without iteration fail.** Vague requirements.md produces confident wrong code — iterate specs before implementation.
- **Manual steering is easy to forget.** Specialized guides in `inclusion: manual` mode provide zero value until referenced with `#name`.
- **AGENTS.md bypasses inclusion control.** Large AGENTS.md files pay always-on cost with no scoping escape hatch.

## Integration

- `kiro-customization` covers authoring steering files and inclusion frontmatter.
- `kiro-session-management` covers spec lifecycle and when to refresh artifacts vs continue chat.
- `context-fundamentals` explains attention budgeting for always-on vs conditional loading.
- `project-development` aligns with spec-driven task-model fit decisions.
- `tool-design` informs MCP tool selection loaded into Kiro sessions.

## References

- `references/kiro-steering-internals.md` — Inclusion modes, foundational files, file reference syntax, AGENTS.md behavior.
- `claim-kiro-context-architecture-steering`: Inclusion modes and foundational steering behavior follow [kiro.dev/docs/steering](https://kiro.dev/docs/steering) and may change between releases.
