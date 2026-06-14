---
name: amazonq-customization
description: Author Amazon Q Developer steering files — .amazonq/rules/ markdown rules, nested rule organization, custom CLI agents, MCP configuration, and AmazonQ.md scaffolds. Use when writing Q project rules, when rules are ignored, or when rule bloat degrades responses. Do not activate for Q context loading internals (amazonq-context-architecture) or general prompt theory (context-fundamentals).
---

# Amazon Q Customization

Amazon Q Developer's primary steering surface is **`.amazonq/rules/`** — markdown files (optionally nested) loaded automatically into chat context. The **Q CLI** supports **custom agents** and **`AmazonQ.md`** scaffolds. This skill covers authoring rules with token budgeting and organizing them for IDE and CLI consistency.

## When to Activate

Activate this skill when:
- Creating or restructuring `.amazonq/rules/` for IDE or CLI
- Organizing rules into subdirectories by domain (frontend, infra, security)
- Writing custom CLI agent definitions for specialized workflows
- Q ignores coding standards or applies backend rules to frontend work
- Responses degrade after the rules library grows

Do not activate this skill for adjacent work owned by other skills:
- Do not activate for `/context show` token auditing: `amazonq-context-architecture`.
- Do not activate for `/compact` and session lifecycle: `amazonq-session-management`.
- Do not activate for platform-agnostic instruction theory: `context-fundamentals`.
- Do not activate for MCP tool schema design: `tool-design`.

## Core Concepts

### Rule file format

Rules are plain markdown in `.amazonq/rules/`. No required frontmatter — content is the instruction. Use descriptive filenames (`cdk-rules.md`, `frontend-react.rule.md`) for human maintenance; Q loads all `.md` files regardless of name.

Organize with subdirectories:
```
.amazonq/rules/
  1.project-layout-rules.md
  2.project-spec.md
  frontend/react.rule.md
  infra/cdk.rule.md
```

Numeric prefixes can enforce human reading order; Q loads all matches.

### IDE session toggles

Developers can enable/disable individual rules per chat session via the Rules button. Write rules assuming they may be toggled off — critical invariants should also be enforced by linters/CI.

### AmazonQ.md scaffold

Optional root-level `AmazonQ.md` (or similar) provides project scaffold context alongside README. CLI glob patterns often include it by default — keep concise, behavior-focused.

### Custom CLI agents

Q CLI supports custom agent definitions (typically under `.amazonq/cli-agents/` or project-configured paths — verify current format in AWS docs). Agents specify tools, context resources, and prompts for specialized workflows. Point `resources` at rule files via `file://` URIs for shared steering between IDE and CLI.

### Token budgeting

Every matched rule file consumes tokens on each request. Monitor with `/context show` in CLI. Split large rule libraries into focused files; avoid duplicating README content in rules.

### MCP servers

Configure MCP for Q CLI/IDE selectively. Each enabled server adds tool schema overhead — disable when not needed for current work.

## Authoring Playbook

1. **Add rules reactively** after observing Q do the wrong thing without them.
2. **State behavior, not philosophy** — "Use type hints on all public functions" beats "We value quality."
3. **One concern per file** — easier to toggle, audit, and token-count.
4. **Mirror critical CLI constraints in rules** IDE and CLI both read `.amazonq/rules/`.
5. **Review rule changes in PRs** — they steer every AI-generated diff.

## Gotchas

- **All matched rules load together.** No native glob scoping per rule file in IDE — organizational subdirs help humans, not automatic scoping by file type.
- **Bloated rules break CLI.** Single files with hundreds of KB exceed context-file limits.
- **Toggle state is session-local.** Disabled rules re-enable on new tabs unless files are removed.
- **Duplication with README + rules + AmazonQ.md** triple-pays token cost for the same facts.
- **Custom agent format changes.** Verify current CLI agent JSON schema in AWS docs before committing configs.

## Integration

- `amazonq-context-architecture` explains how rules enter Q's context and token limits.
- `amazonq-session-management` covers compaction when rule + chat overhead fills the window.
- `context-fundamentals` provides attention-budget reasoning for lean rules.
- `tool-design` owns MCP tool schemas this skill enables.

## References

- `references/amazonq-rules-authoring.md` — Directory layout, CLI agent resources, AmazonQ.md patterns.
- `claim-amazonq-customization-rules`: Rule directory conventions and CLI agent paths follow AWS Q Developer documentation (2025–2026) and may change between releases.
