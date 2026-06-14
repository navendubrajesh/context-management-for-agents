---
name: antigravity-customization
description: Author Google Antigravity steering files — root and nested AGENTS.md, .agents/skills/ with SKILL.md manifests, workflows, and MCP configuration. Use when writing project instructions for Antigravity, when agents ignore conventions, or when AGENTS.md bloat degrades responses. Do not activate for Artifact lifecycle (antigravity-session-management) or general prompt theory (context-fundamentals).
---

# Antigravity Customization

Antigravity's user-controlled steering surface centers on **AGENTS.md** (always read at session start) and **`.agents/skills/`** (progressive-disclosure capability modules). Workflows, optional agent definitions, and MCP extend the stack. This skill covers authoring each layer with token budgeting and clear boundaries.

## When to Activate

Activate this skill when:
- Creating or restructuring root or nested `AGENTS.md`
- Packaging reusable guidance as `.agents/skills/*/SKILL.md`
- Writing `.agents/workflows/` for multi-step procedures
- Antigravity ignores build/test instructions or violates "Do Not" rules
- Configuring MCP servers for Antigravity agents

Do not activate this skill for adjacent work owned by other skills:
- Do not activate for Knowledge Items and Artifact management: `antigravity-session-management`.
- Do not activate for how context pillars compose: `antigravity-context-architecture`.
- Do not activate for platform-agnostic instruction theory: `context-fundamentals`.
- Do not activate for MCP tool schema design: `tool-design`.

## Core Concepts

### AGENTS.md layering

Place `AGENTS.md` at repo root for global invariants. Use **nested AGENTS.md** in subdirectories (frontend/, backend/) for scoped guidance — more specific files take precedence when working in that tree.

Priority content for AGENTS.md:
- Build, test, lint commands ("what done means")
- Forbidden paths and operations
- Architecture constraints agents cannot infer from code alone
- Verification expectations (especially for async Manager agents)

Keep under ~100 lines of dense, behavior-changing rules. Move procedures to Skills.

### Skills in .agents/skills/

Follow standard skill structure: YAML frontmatter (`name`, `description`), under 500 lines, `references/` for depth. Skills load on relevance — ideal for deployment runbooks, domain-specific workflows, or compliance checklists.

### Workflows

`.agents/workflows/` holds step-by-step guides the agent follows for repeatable processes. Workflows are procedural; Skills are capability-oriented — use workflows for linear sequences, skills for reusable knowledge packages.

### MCP configuration

Enable MCP servers selectively. Each server's tool schemas consume context on every agent invocation. Match servers to current task phase in Manager runs.

### "Do Not" sections deliver fastest ROI

Convert recurring code-review corrections into explicit prohibitions in AGENTS.md. Negative constraints often outperform aspirational style guidance.

## Authoring Playbook

1. **Week 1 minimum**: project overview, tech stack, directory map, build/test commands in AGENTS.md.
2. **Week 2**: add conventions, forbidden patterns, canonical examples by reference path.
3. **Week 3**: extract stable procedures into `.agents/skills/`; promote verified facts to Knowledge Items.
4. **Version-control AGENTS.md** — review changes like CI config.
5. **Never gitignore AGENTS.md** — it is part of the agent runtime contract.

## Gotchas

- **AGENTS.md is always-on.** No inclusion modes — bloat hits every session.
- **Duplicating skill content in AGENTS.md** double-pays tokens and drifts when one copy updates.
- **Nested AGENTS.md unnoticed.** Agents in subdirectories may follow child rules humans forget exist.
- **Missing verification commands.** Async Manager agents without test instructions ship untested diffs.
- **Skills without descriptions.** Poor descriptions fail progressive disclosure matching.

## Integration

- `antigravity-context-architecture` explains how customized files enter Antigravity's pipeline.
- `antigravity-session-management` covers Artifact/KI hygiene after customization is in place.
- `context-fundamentals` provides progressive-disclosure theory for AGENTS.md vs skills split.
- `tool-design` owns MCP tool schemas this skill enables.

## References

- `references/antigravity-agents-layout.md` — Recommended `.agents/` structure, AGENTS.md template sections, skill packaging.
- `claim-antigravity-customization-agents`: AGENTS.md discovery and `.agents/skills/` layout follow Antigravity documentation (2025–2026) and may evolve.
