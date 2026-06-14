---
name: copilot-session-management
description: Manage the context window lifecycle in GitHub Copilot CLI and agent sessions — monitoring usage with /context, automatic and manual compaction, checkpoints, and deciding between long-running sessions and fresh starts. Use when sessions grow long, Copilot forgets earlier decisions, or planning multi-phase agent work. Do not activate for Copilot's prompt-assembly internals (copilot-context-architecture) or general compression theory (context-compression).
---

# Copilot Session Management

GitHub Copilot CLI holds every user message, model response, tool call, and tool result in a fixed-size context window. This skill covers the operational lifecycle: monitoring usage, compaction, checkpoints, and session hygiene — the levers that keep long-running Copilot sessions coherent.

## When to Activate

Activate this skill when:
- A Copilot CLI session is long-running and the agent seems to forget earlier parts of the conversation
- Planning a multi-phase task (scaffold → implement → test → PR) in a single session
- Deciding whether to continue a session, compact proactively, or start fresh
- Debugging contradictions between current agent behavior and earlier decisions
- Auditing what was preserved across a compaction

Do not activate this skill for adjacent work owned by other skills:
- Do not activate for how Copilot builds prompts and retrieves context: `copilot-context-architecture`.
- Do not activate for designing compression strategies in your own agent systems: `context-compression`.
- Do not activate for diagnosing attention-level failures: `context-degradation`.

## Core Concepts

### What fills the context window

Four accumulating components:
1. **System instructions and tool definitions** — fixed overhead, always present.
2. **User messages** — every prompt sent.
3. **Model responses** — everything Copilot says back.
4. **Tool calls and results** — both request and output; tool results are often the largest contributor (long file reads, verbose command output).

### Monitoring: `/context`

The `/context` slash command displays a visual breakdown: **System/Tools** (fixed overhead), **Messages** (conversation history), **Free Space**, and **Buffer** (reserved portion that triggers automatic management). Use it when a session is long, when Copilot seems forgetful, or to check whether compaction has occurred or is imminent.

### Compaction

- **Automatic trigger**: at ~80% of capacity, compaction starts in the background, leaving a ~20% buffer so tool calls keep running. If context fills to ~95% before compaction finishes, the CLI pauses briefly until it completes.
- **Manual trigger**: `/compact` at any time — useful before starting a new phase of work. Esc cancels.
- **Mechanism**: snapshot the conversation → send the full history to the model with a summarization prompt (capturing goals, work done, key technical details, important files, next steps) → replace history with the summary plus original user instructions and current plan/to-do state → retain messages added during background compaction.
- **What is lost**: exact wording of messages, full command outputs, minor early decisions. Compaction is summarization — irreversible and lossy. Without it, the only fallback would be silently dropping old messages.

### Checkpoints

Every compaction (automatic or manual) creates a **checkpoint**: a saved copy of the compaction summary, stored as a numbered, titled file in the session workspace.

- `/session checkpoints` — list all checkpoints with number and title
- `/session checkpoints <n>` — view full content of checkpoint n

Use checkpoints to review earlier phases after multiple compactions, verify the summary captured your work before continuing, or debug confusion when the agent contradicts earlier decisions. Compactions cannot be reversed.

### Long sessions vs. fresh starts

**Stay in the session** when: working a multi-phase task, iterating on a problem where the record of what's been tried matters, or building shared codebase understanding over time.

**Start fresh** when: switching to an unrelated task (clean window = more space), the session has been through many compactions and important context is eroding, or work went in a wrong direction and reconciling old decisions would cost more than restarting.

`/resume` reopens previous sessions, including their checkpoints.

## Operational Playbook

1. **Check `/context` at phase boundaries.** Before starting a new phase, look at free space; run `/compact` proactively rather than letting auto-compaction fire mid-task.
2. **Front-load durable state outside the window.** Write plans, decisions, and constraints to files in the workspace — compaction summaries preserve "important files," and files survive compaction losslessly (see `filesystem-context`).
3. **Re-state critical constraints after compaction.** If a fine-grained detail (an exact API contract, a specific user requirement) must survive, repeat it in a fresh message — don't trust the summary to carry it.
4. **Audit the latest checkpoint after auto-compaction** when the task is high-stakes; correct any misstated decisions immediately, while the correction is cheap.
5. **One task, one session.** Task switches inherit irrelevant history and waste budget; `/resume` makes returning cheap, so fresh sessions cost little.

## Gotchas

- **Compaction is irreversible.** Once history is replaced by the summary, the originals are gone from the active context — checkpoints record the summary, not the full transcript.
- **Auto-compaction can fire mid-task.** At 80% it starts silently in the background; if you're between dependent steps, a detail you stated 30 turns ago may not survive into the next step.
- **Tool output is the silent budget killer.** A few long file reads or verbose command runs can consume more context than dozens of messages. Prefer targeted reads (specific line ranges, grep) over whole-file dumps.
- **"Forgetting" after many compactions compounds.** Each compaction summarizes a summary's successor; fidelity decays multiplicatively. Many-compaction sessions are a signal to restart with a written brief.
- **Checkpoint review ≠ context restoration.** Reading a checkpoint shows what was preserved, but pasting it back duplicates content already in the summary — restate only the missing specifics.

## Integration

- `copilot-context-architecture` explains how Copilot assembles prompts and what context enters the window in the first place.
- `context-compression` provides the general theory (hierarchical summarization, selective retention) behind compaction.
- `context-degradation` covers the attention failures long sessions exhibit even before the window fills.
- `filesystem-context` provides the offloading patterns that make state survive compaction.

## References

- `claim-copilot-session-management-thresholds`: The ~80%/~95% compaction thresholds and ~20% buffer come from GitHub's "Managing context in GitHub Copilot CLI" documentation and may change between CLI releases.
