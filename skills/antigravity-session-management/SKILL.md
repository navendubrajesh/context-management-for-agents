---
name: antigravity-session-management
description: Manage persistent context across long Google Antigravity agent sessions — Artifact review cycles, Knowledge Item curation, Manager Surface handoffs, and deciding when to spawn fresh agents vs continue. Use when Antigravity agents lose thread across async runs, Artifacts go stale, or multi-agent work needs coordination. Do not activate for AGENTS.md authoring (antigravity-customization) or general compression theory (context-compression).
---

# Antigravity Session Management

Antigravity sessions span **Editor chats** and **Manager-orchestrated async agents**. Durability comes from **Artifacts** and **Knowledge Items**, not verbatim chat. This skill covers keeping long agent-first work coherent across sessions and agent instances.

## When to Activate

Activate this skill when:
- Manager Surface agents produce Artifacts that need review before the next phase
- Knowledge Items contain outdated facts misleading new sessions
- Deciding whether to continue an async agent run or spawn a fresh one
- Multi-agent workflows produce conflicting Artifacts or plans
- Editor sessions lose alignment with Manager-generated plans

Do not activate this skill for adjacent work owned by other skills:
- Do not activate for writing AGENTS.md or skills: `antigravity-customization`.
- Do not activate for context pillar overview: `antigravity-context-architecture`.
- Do not activate for CLI-style `/compact` workflows: `copilot-session-management`.
- Do not activate for platform-agnostic summarization: `context-compression`.

## Core Concepts

### Artifacts as session checkpoints

Each significant agent phase should produce a reviewable Artifact (plan, task list, walkthrough). Treat approved Artifacts as **checkpoints** — the Manager Surface equivalent of compaction summaries, but human-reviewable and editable.

### Knowledge Item hygiene

KIs persist indefinitely. Stale KIs cause confident wrong behavior. Schedule KI audits when: APIs change, architecture pivots, or Artifacts supersede earlier assumptions. Delete or update — don't accumulate contradictory KIs.

### Manager Surface handoffs

When delegating end-to-end tasks:
1. Agent generates Artifacts for verification
2. Human comments on Artifact (not raw tool logs)
3. Agent continues with feedback incorporated
4. Approved Artifacts become reference for downstream agents

### Fresh agent vs continue

**Continue** when: Artifact state is current, KIs accurate, and the next task is a logical extension.

**Spawn fresh** when: scope pivoted, Artifacts contradict each other, or multiple failed iterations polluted context.

### Editor ↔ Manager alignment

Critical invariants (build commands, test gates, forbidden paths) must live in **AGENTS.md** so both Editor and Manager agents share them. Session-specific plans belong in Artifacts, not duplicated into AGENTS.md.

## Operational Playbook

1. **Require an Artifact at every phase boundary** before merging or deploying.
2. **Comment on Artifacts, not chat logs** — structured feedback propagates cleaner.
3. **Promote stable facts from Artifacts to Knowledge Items** — once verified, not before.
4. **Archive or delete stale Artifacts** in `.agents/plans/` to prevent confusion.
5. **One objective per Manager agent** — parallel agents need non-overlapping Artifact scopes.

## Gotchas

- **Unreviewed Artifacts look authoritative.** Future agents treat them as ground truth.
- **KIs without provenance.** Document source and date in KI content for future audits.
- **Multi-agent conflicts.** Without Manager orchestration rules, agents duplicate or contradict work.
- **Chat in Editor doesn't update Manager context** unless written to Artifacts/KIs/AGENTS.md.

## Integration

- `antigravity-context-architecture` explains Artifacts, KIs, and Manager Surface mechanics.
- `antigravity-customization` covers AGENTS.md that both surfaces read.
- `multi-agent-patterns` informs Manager orchestration and handoff design.
- `filesystem-context` supports plan files alongside Artifacts.

## References

- `claim-antigravity-session-management-artifacts`: Artifact feedback workflow and Manager Surface behavior follow Google Antigravity docs and may change between releases.
