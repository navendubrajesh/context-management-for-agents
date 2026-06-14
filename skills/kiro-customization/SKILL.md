---
name: kiro-customization
description: Author Amazon Kiro steering files in .kiro/steering/ and ~/.kiro/steering/ — inclusion modes (always, fileMatch, manual, auto), foundational docs, AGENTS.md, hooks, and MCP configuration. Use when writing or restructuring Kiro steering, when guidance is ignored, or when always-on steering bloat degrades responses. Do not activate for spec lifecycle management (kiro-session-management) or general prompt theory (context-fundamentals).
---

# Kiro Customization

Kiro's steering surface is **markdown files with YAML frontmatter** controlling when context loads. Combined with optional `AGENTS.md`, hooks, and MCP, this is the full user-controlled steering stack. This skill covers authoring steering well: inclusion modes, scoping, token budgeting, and failure modes.

## When to Activate

Activate this skill when:
- Creating or restructuring `.kiro/steering/` or global `~/.kiro/steering/` files
- Choosing between `inclusion: always`, `fileMatch`, `manual`, and `auto` modes
- Generating or maintaining foundational steering (product, tech, structure)
- Kiro ignores conventions or applies global rules where workspace rules should win
- Configuring hooks or MCP servers for a Kiro workspace

Do not activate this skill for adjacent work owned by other skills:
- Do not activate for spec artifact lifecycle across sessions: `kiro-session-management`.
- Do not activate for how steering composes with specs in context: `kiro-context-architecture`.
- Do not activate for platform-agnostic instruction design: `context-fundamentals`.
- Do not activate for MCP tool schema authoring: `tool-design`.

## Core Concepts

### Workspace vs global scope

- `.kiro/steering/` — project-specific; wins on conflict
- `~/.kiro/steering/` — personal/team defaults for all workspaces
- Team steering can be deployed via MDM to `~/.kiro/steering/`

Put universal personal preferences globally; put repo-specific patterns in workspace steering.

### Inclusion mode selection

| Need | Mode | Rationale |
|------|------|-----------|
| Stack, security, naming everywhere | `always` | Baseline — keep lean |
| Component/API/test standards | `fileMatch` | Loads only on relevant files |
| Rare runbooks, migrations | `manual` | `#name` or `/` slash on demand |
| Heavy domain guides | `auto` | Description-triggered like skills |

### Foundational steering

Use Kiro's Generate Steering Docs for `product.md`, `tech.md`, `structure.md`. Treat these as always-on — audit quarterly; stale tech.md sends Kiro toward deprecated libraries.

### AGENTS.md for cross-tool portability

AGENTS.md in workspace root or global steering path is **always included** with no scoping. Mirror only critical cross-tool invariants; push scoped detail into steering with `fileMatch`.

### File references over copies

Use `#[[file:path/to/example.ts]]` to point at canonical patterns. Copied snippets in steering rot when code changes.

### Hooks and MCP

Hooks automate reactions to events; MCP adds tools. Both increase system complexity — configure per workspace need, not globally by default.

## Authoring Playbook

1. **One domain per steering file** — `api-rest-conventions.md`, not `everything.md`.
2. **Keep `inclusion: always` files under ~50 lines** of behavior-changing rules.
3. **Prefer `fileMatch` for framework-specific guidance.**
4. **Review steering in code review** — steering changes steer every AI-generated diff.
5. **Never commit secrets** — steering is version-controlled like source.

## Gotchas

- **Frontmatter must be first line.** Blank lines before `---` break inclusion parsing.
- **AGENTS.md cannot be scoped.** Large AGENTS.md taxes every request with no escape hatch.
- **Manual steering invisible until invoked.** Document available `#name` references in README or always-on steering index.
- **Conflicting global vs workspace rules** — workspace wins, but duplicate content still wastes tokens.
- **Auto inclusion depends on description quality.** Vague descriptions cause missed or spurious loads.

## Integration

- `kiro-context-architecture` explains how customized steering enters Kiro's context pipeline.
- `kiro-session-management` covers keeping specs aligned with steering over long work.
- `context-fundamentals` provides progressive-disclosure theory behind inclusion modes.
- `tool-design` owns MCP schemas this skill enables.

## References

- `references/kiro-steering-authoring.md` — Frontmatter templates, naming conventions, file reference syntax.
- `claim-kiro-customization-inclusion`: Inclusion modes and AGENTS.md behavior follow [kiro.dev/docs/steering](https://kiro.dev/docs/steering) and may change between releases.
