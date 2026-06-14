---
name: cursor-session-management
description: Manage the context-window lifecycle in Cursor Agent and CLI sessions — reading the context ring, automatic conversation compression, manual /compress, and deciding when to start fresh chats. Use when Cursor forgets earlier decisions, the context ring is near full, or planning multi-phase agent work. Do not activate for Cursor indexing or @-mentions (cursor-context-architecture) or general compression theory (context-compression).
---

# Cursor Session Management

Cursor Agent sessions accumulate messages, tool outputs, rules, MCP definitions, and @ attachments in one shared context window. When the window fills, Cursor **summarizes older turns** — a lossy compaction distinct from simply starting a new chat. This skill covers monitoring, manual compression, and session hygiene.

## When to Activate

Activate this skill when:
- The context ring shows high utilization or categorized bloat (tools, MCP, conversation)
- Cursor Agent contradicts decisions made earlier in the same chat
- Planning multi-phase work (design → implement → test) in one Agent session
- Using Cursor CLI and needing to free context with `/compress`
- Deciding between continuing a chat vs opening a new Agent tab

Do not activate this skill for adjacent work owned by other skills:
- Do not activate for codebase indexing or semantic search: `cursor-context-architecture`.
- Do not activate for authoring rules that inflate every session: `cursor-customization`.
- Do not activate for platform-agnostic compression algorithms: `context-compression`.

## Core Concepts

### Context ring as dashboard

The ring beside the chat input shows fill level. Click it for a breakdown: system prompt, tools, rules, skills, MCP, subagents, summarized conversation, and live conversation. Use this to identify **which category** is consuming budget — disabling unused MCP servers or shrinking always-on rules often beats re-prompting.

### Automatic compression

When the window nears capacity, Cursor compresses older conversation segments into summaries to make room. Summarized content still appears in the tray but loses verbatim detail — tool outputs, exact wording, and fine-grained decisions are the first casualties.

### Manual compression (CLI)

Cursor CLI supports `/compress` to proactively summarize history and reclaim space — use at phase boundaries before starting a new major task, similar to proactive `/compact` in other agent CLIs.

### Multi-tab sessions

Cursor supports multiple chat tabs (up to ~10 in IDE). Each tab is an isolated conversation — context does not carry between tabs. Use new tabs for unrelated tasks; use filesystem artifacts to hand off state between tabs.

### Durable state outside the window

Write plans, decisions, and constraints to workspace files. Rules and AGENTS.md persist across chats; conversation does not. After compression or a new tab, re-state only the specifics that must survive.

## Operational Playbook

1. **Check the context ring at phase boundaries** before large tool-heavy steps.
2. **Run `/compress` (CLI) or start a fresh tab (IDE)** when switching unrelated tasks.
3. **Offload verbose tool output** to files; reference paths instead of pasting logs (see `filesystem-context`).
4. **Disable unused MCP servers** — their schemas load every request.
5. **Re-state critical constraints** after compression if the task is high-stakes.

## Gotchas

- **Compression is irreversible in active context.** Summaries replace verbatim history for model reasoning.
- **Rules and MCP are fixed overhead.** They consume budget even when irrelevant to the current task.
- **Subagents help but aren't free.** Launching many Explore subagents still costs coordination tokens in the main thread.
- **New tab ≠ saved handoff.** Without written artifacts, a fresh tab starts cold except for rules/index.

## Integration

- `cursor-context-architecture` explains what fills the window (indexing, @ mentions, rules).
- `cursor-customization` reduces always-on rule overhead that accelerates fill rate.
- `context-compression` provides theory behind summarization trade-offs.
- `filesystem-context` makes state survive compression and tab switches.

## References

- `claim-cursor-context-architecture-compression`: Automatic summarization triggers and CLI `/compress` behavior follow Cursor docs and may change between releases.
