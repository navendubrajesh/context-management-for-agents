---
name: antigravity-context-architecture
description: Understand how Google Antigravity assembles and persists context — AGENTS.md discovery, Knowledge Items, Skills in .agents/, Artifacts (plans, task lists, walkthroughs), Editor vs Manager surfaces, and browser/tool subagents. Use when tuning Antigravity context behavior, designing durable project memory, or diagnosing agent drift across sessions. Do not activate for general context theory (context-fundamentals) or authoring AGENTS.md (antigravity-customization).
---

# Antigravity Context Architecture

Google Antigravity is an **agent-first development platform** with two surfaces: an **Editor** (synchronous, hands-on) and a **Manager** (asynchronous multi-agent orchestration). Context is not just chat history — it combines **AGENTS.md**, **Skills**, **Knowledge Items (KIs)**, **Artifacts**, and **workflows** into persistent, reviewable state.

## When to Activate

Activate this skill when:
- Designing how Antigravity retains knowledge across conversations
- Understanding Artifacts vs Knowledge Items vs conversation history
- Orchestrating multiple agents via Manager Surface
- Deciding what belongs in AGENTS.md vs `.agents/skills/` vs Knowledge Items
- Diagnosing why Antigravity repeats work or ignores prior decisions

Do not activate this skill for adjacent work owned by other skills:
- Do not activate for platform-agnostic attention theory: `context-fundamentals`.
- Do not activate for writing AGENTS.md and skills manifests: `antigravity-customization`.
- Do not activate for Artifact lifecycle across long Manager sessions: `antigravity-session-management`.
- Do not activate for custom external RAG: `memory-systems`.

## Core Concepts

### AGENTS.md as first-read context

Antigravity reads `AGENTS.md` at session start — project overview, constraints, verification commands, and "Do Not" rules. It is the highest-priority user-authored context layer and should stay lean; depth belongs in Skills or Knowledge Items.

### Skills (.agents/skills/)

Skills follow the `SKILL.md` + optional `references/` pattern — loaded on demand when relevant, mirroring progressive disclosure. Use for reusable capability packages (deployment procedures, domain workflows) rather than repo-wide invariants.

### Knowledge Items (persistent memory)

KIs are curated facts distilled from past work — stored in Antigravity's Knowledge directory and checked at session start to avoid redundant rediscovery. Unlike chat history, KIs are **edited, deduplicated knowledge** — API schemas, business rules, architecture decisions.

### Artifacts (transparent agent output)

Agents generate structured Artifacts: task lists, implementation plans, walkthroughs, screenshots, browser recordings. Artifacts are reviewable deliverables — comment on them like docs and the agent incorporates feedback without stopping execution. Artifacts become part of persistent context for future sessions.

### Editor vs Manager context

- **Editor View**: synchronous coding with tab completions and inline commands — familiar IDE loop.
- **Manager Surface**: spawn and observe agents across workspaces asynchronously — context flows through Artifacts and KIs rather than a single chat thread.

### Subagents and browser tools

Antigravity agents can use browser and tool subagents for verification. Subagent output should flow back as Artifacts or summarized KIs — not raw dumps into primary context.

## Gotchas

- **Chat alone doesn't persist.** Without KIs, Artifacts, or updated AGENTS.md, new sessions start cold.
- **Artifact sprawl.** Unreviewed Artifacts accumulate stale plans that mislead future agents.
- **AGENTS.md bloat competes with code.** Every line loads at session start — audit like a system prompt.
- **Skills vs KIs confusion.** Skills are procedural; KIs are factual reference — mixing them creates duplication.
- **Manager multi-agent conflicts** need explicit orchestration rules in AGENTS.md or Manager config.

## Integration

- `antigravity-customization` covers authoring AGENTS.md, skills, and workflows.
- `antigravity-session-management` covers Artifact and KI hygiene across long Manager runs.
- `context-fundamentals` explains attention budgeting for always-on AGENTS.md.
- `filesystem-context` complements Artifacts with workspace file patterns.
- `multi-agent-patterns` informs Manager Surface orchestration design.

## References

- `references/antigravity-internals.md` — Context pillars, Artifact types, Editor/Manager split, `.agents/` layout.
- `claim-antigravity-context-architecture-artifacts`: Artifact types and Knowledge Item behavior follow Google Antigravity documentation (2025–2026) and may evolve between releases.
