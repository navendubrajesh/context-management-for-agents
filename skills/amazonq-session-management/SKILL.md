---
name: amazonq-session-management
description: Manage the context-window lifecycle in Amazon Q Developer IDE chat and CLI — /context monitoring, /compact summarization, automatic compaction nudge at ~80% capacity, /clear, and saved conversations. Use when Q forgets earlier decisions, context approaches limits, or planning multi-phase CLI work. Do not activate for rule authoring (amazonq-customization) or general compression theory (context-compression).
---

# Amazon Q Session Management

Amazon Q Developer sessions accumulate chat history, tool outputs, and loaded rules in a bounded context window. **Compaction** (`/compact`) replaces detailed history with a summary; **clear** (`/clear`) wipes it entirely. The CLI adds **auto-compaction** when validation errors occur. This skill covers monitoring and hygiene for long Q sessions.

## When to Activate

Activate this skill when:
- Q suggests compaction or context approaches ~80% capacity (IDE nudge)
- A Q CLI session fails with context window validation errors
- Planning multi-phase work in one `q chat` session
- Deciding between `/compact`, `/clear`, or starting a new tab/session
- Auditing what Q preserved after compaction

Do not activate this skill for adjacent work owned by other skills:
- Do not activate for `.amazonq/rules/` authoring: `amazonq-customization`.
- Do not activate for rule glob loading and token limits: `amazonq-context-architecture`.
- Do not activate for Copilot CLI checkpoints: `copilot-session-management`.
- Do not activate for platform-agnostic compression algorithms: `context-compression`.

## Core Concepts

### What fills the window

- System instructions and tool definitions (fixed overhead)
- Loaded project rules from `.amazonq/rules/`
- User messages and Q responses
- Tool call inputs and outputs (often largest contributor)
- Explicitly added files via IDE context picker or CLI `/context add`

### Manual compaction: `/compact`

Enter `/compact` in chat. Q generates a concise summary preserving goals, work done, key technical details, important files, and next steps. The summary **replaces** detailed history for model reasoning while the full transcript may remain visible until session end (IDE).

Use proactively at phase boundaries — before starting test/refactor/PR phases.

### Automatic compaction nudge (IDE)

At approximately **80% of context capacity**, Q displays a notification suggesting compaction. Accept when transitioning phases; defer only if mid-critical-step and few turns remain.

### Auto-compaction (CLI)

CLI implements automatic summarization when context validation errors occur — server-side history summarization allows the session to continue rather than hard-failing. Treat this as a safety net, not a substitute for proactive `/compact`.

### Clear vs compact vs new session

| Action | Effect | When |
|--------|--------|------|
| `/compact` | Summary replaces history for model | Phase boundary, preserve goals |
| `/clear` | Wipes conversation context | Hard reset, unrelated pivot |
| New tab/session | Fresh window, rules reload | Unrelated task, many compactions |

### Durable state outside the window

Write plans and decisions to workspace files. Rules in `.amazonq/rules/` persist across sessions; chat summaries do not capture fine-grained tool output verbatim.

## Operational Playbook

1. **Run `/context show` (CLI) at phase boundaries** — identify token-heavy rule files.
2. **`/compact` before new phases** — don't wait for 80% nudge mid-task.
3. **Offload verbose command output** to files; reference paths in follow-up prompts.
4. **One bounded task per CLI invocation** when possible — Q performs best with focused scope.
5. **Re-state critical constraints** after compaction for high-stakes steps.

## Gotchas

- **Compaction is lossy.** Exact tool outputs and early wording disappear from model context.
- **Visible history ≠ model context.** IDE may show full transcript while model uses summary post-compaction.
- **Detailed history resets on IDE restart** after compaction — export important transcripts if needed.
- **Rule token overhead is silent.** `/context show` reveals rule cost; bloated rules accelerate fill rate.
- **CLI auto-compaction timing is unpredictable.** Proactive `/compact` beats error-driven summarization.

## Integration

- `amazonq-context-architecture` explains rule loading that competes with conversation budget.
- `amazonq-customization` reduces always-loaded rule overhead.
- `context-compression` provides theory behind summarization trade-offs.
- `filesystem-context` makes state survive compaction.

## References

- `claim-amazonq-session-management-compaction`: `/compact` behavior, ~80% nudge, and CLI auto-compaction follow [AWS Q Developer docs](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/ide-chat-history-compaction.html) and may change between releases.
