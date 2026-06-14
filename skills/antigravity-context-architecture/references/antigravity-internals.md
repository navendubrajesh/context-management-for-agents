# Antigravity Context Internals

Sources: [Google Developers Blog — Antigravity](https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/), Antigravity product documentation (2025–2026).

## Context pillars

1. **AGENTS.md** — session-start project instructions
2. **Skills** (`.agents/skills/*/SKILL.md`) — on-demand capability modules
3. **Knowledge Items** — persistent curated facts across conversations
4. **Workflows** (`.agents/workflows/`) — step-by-step guides
5. **Artifacts** — agent-generated plans, task lists, walkthroughs, media
6. **Codebase** — files, structure, git state
7. **MCP servers** — external tools and data

## Artifact types

- Task lists / checklists
- Implementation plans
- Walkthroughs with screenshots or browser recordings
- Code review deliverables

Artifacts support inline feedback comments — agent incorporates without halting.

## Recommended .agents/ layout

```
.agents/
  skills/           # SKILL.md packages
  workflows/        # procedural guides
  agents/           # optional agent definitions
  plans/            # execution plans
  tmp/              # session scratch (gitignored)
AGENTS.md           # root instructions
```

## Editor vs Manager

| Surface | Mode | Context emphasis |
|---------|------|------------------|
| Editor | Synchronous | Open files, inline edits, immediate feedback |
| Manager | Asynchronous | Artifacts, multi-workspace agents, review-at-a-glance |

## AI Studio Workspaces

Antigravity integrates with AI Studio Workspaces for cloud-side agent execution — workspace context includes repo state plus platform-managed agent environment.
