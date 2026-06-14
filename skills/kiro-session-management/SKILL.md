---
name: kiro-session-management
description: Manage durable context across long Kiro spec-driven sessions — treating requirements/design/tasks artifacts as session memory, refreshing specs vs continuing chat, and using manual steering on demand. Use when Kiro drifts from agreed specs, multi-phase spec work spans days, or chat context diverges from steering files. Do not activate for steering inclusion modes (kiro-customization) or general compression theory (context-compression).
---

# Kiro Session Management

Kiro does not expose a Copilot-style `/compact` command. Instead, **spec artifacts and steering files are the durable session layer** — chat is ephemeral orchestration atop persisted markdown. This skill covers keeping long spec-driven work coherent without relying on verbatim chat history.

## When to Activate

Activate this skill when:
- Kiro's implementation diverges from an earlier requirements or design document
- A multi-phase feature spans multiple chat sessions over days
- Deciding whether to update specs, regenerate tasks, or start a fresh Kiro chat
- Chat suggestions conflict with always-on steering or foundational docs
- A spec task list becomes stale mid-implementation

Do not activate this skill for adjacent work owned by other skills:
- Do not activate for steering file authoring and inclusion modes: `kiro-customization`.
- Do not activate for how steering and specs enter context: `kiro-context-architecture`.
- Do not activate for Copilot-style CLI compaction: `copilot-session-management`.
- Do not activate for platform-agnostic summarization algorithms: `context-compression`.

## Core Concepts

### Specs as external memory

The spec workflow produces **requirements.md**, **design.md**, and **tasks.md** (or equivalent). These files survive chat resets and should be treated as the source of truth. When chat and spec disagree, **update the spec first**, then ask Kiro to realign — not the reverse.

### Chat is orchestration, not storage

Kiro chat drives execution against specs but does not reliably preserve fine-grained decisions across long threads. Move durable decisions into steering or spec files immediately — especially acceptance criteria, API contracts, and task boundaries.

### When to refresh specs vs continue chat

**Refresh specs** when: scope changed materially, tasks completed invalidate downstream items, or design assumptions proved wrong.

**Continue chat** when: iterating on a single task with clear acceptance criteria and steering still accurate.

**Start fresh chat** when: switching unrelated features, spec was rewritten substantially, or conversation accumulated contradictory instructions.

### Manual steering for phase-specific context

Use `inclusion: manual` steering files (`#troubleshooting-guide`) to load heavy reference material only for the current phase — keeps always-on budget lean while preserving access to deep context on demand.

### Hooks for context freshness

Kiro hooks can react to file changes (e.g., regenerate docs when API changes). Hooks complement but do not replace explicit spec updates.

## Operational Playbook

1. **Before implementation**, iterate specs until tasks are unambiguous — Kiro performs best with discrete, bounded tasks.
2. **After each completed task**, mark it done in tasks.md and commit spec changes with code.
3. **At phase boundaries**, re-read foundational steering — regenerate if stack or structure changed.
4. **On drift**, diff chat suggestions against design.md; fix design before arguing in chat.
5. **For long gaps**, open fresh chat with `#spec-file` references instead of replaying history.

## Gotchas

- **No automatic chat summarization.** Unlike some CLIs, Kiro won't silently compress chat — long threads either fill context or degrade without a spec anchor.
- **Stale tasks mislead.** Outdated task lists cause Kiro to implement superseded work confidently.
- **Always-on steering masks drift.** Foundation files may contradict new spec decisions if not updated together.
- **Over-chatting under-specified work.** Explaining in chat what belongs in requirements.md produces inconsistent results across sessions.

## Integration

- `kiro-context-architecture` explains steering inclusion and spec artifact roles.
- `kiro-customization` covers writing steering that supports multi-session work.
- `filesystem-context` provides patterns for plan persistence complementary to specs.
- `context-compression` offers theory when exporting chat summaries into spec updates.

## References

- `claim-kiro-session-management-specs`: Spec-driven workflow behavior follows Kiro docs and practitioner reports; artifact filenames and flows may evolve between releases.
