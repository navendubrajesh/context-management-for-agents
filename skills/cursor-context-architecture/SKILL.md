---
name: cursor-context-architecture
description: Understand how Cursor assembles, indexes, and budgets context — semantic codebase indexing, @-mention attachments, rule injection, subagent isolation, and context-window compression. Use when tuning what Cursor Agent sees, diagnosing missed files in search, or budgeting against effective context limits. Do not activate for general context theory (context-fundamentals) or authoring .mdc rules (cursor-customization).
---

# Cursor Context Architecture

Cursor's context system combines **automatic codebase indexing**, **user-selected @ attachments**, **project/user/team rules**, and **agent tool chains** into a single fixed-size context window. Unlike inline-tab completion systems, Cursor Agent actively searches, reads, and compresses — but every component competes for the same token budget.

## When to Activate

Activate this skill when:
- Diagnosing why Cursor Agent cannot find relevant code despite it existing in the repo
- Understanding what @-mentions, rules, MCP servers, and skills cost in the context ring
- Tuning `.cursorignore` / `.cursorindexingignore` for indexing vs access control
- Deciding when to use @ files vs letting Agent search autonomously
- Evaluating Max mode or large-context models against effective usable capacity

Do not activate this skill for adjacent work owned by other skills:
- Do not activate for platform-agnostic attention mechanics: `context-fundamentals`.
- Do not activate for writing or restructuring `.mdc` rules: `cursor-customization`.
- Do not activate for long-session compaction tactics: `cursor-session-management`.
- Do not activate for building external RAG pipelines: `memory-systems`.

## Core Concepts

### Codebase semantic indexing

Cursor indexes open workspaces into vector embeddings using a custom embedding model. Code is chunked at meaningful boundaries (functions, classes, logical blocks), embedded, and stored in a vector database. Indexing starts on workspace open; semantic search becomes available at ~80% index completion and syncs changed files every ~5 minutes.

Practical lever: semantic search + grep together outperform grep alone on large codebases (Cursor reports ~12.5% accuracy improvement on 1000+ file repos). Agent chains semantic search → grep → file reads without the user choosing tools.

### @-mention context channel

Typing `@` attaches explicit context: files/folders, indexed docs, terminal output, past chats, git diffs, browser state. @ mentions are the highest-precision lever when the relevant files are known; skip them when scope is unclear and let Agent search.

Rules and skills also appear in the context breakdown tray alongside system prompt, tools, MCP, and conversation history.

### Rules enter at prompt start

When applied, rule contents prepend to model context (Team Rules → Project Rules → User Rules). Rules affect **Agent (Chat) only** — not Cursor Tab inline completions or Inline Edit (Cmd/Ctrl+K). Do not expect `.mdc` style rules to steer ghost-text completions.

Glob-scoped rules attach when matching files are **in context** (referenced in chat or read by the agent during edits), not merely open in the editor.

### Subagent context isolation

Agent can spawn Explore subagents with separate context windows and faster models. Subagents run parallel searches and return summarized findings — keeping verbose raw file dumps out of the main conversation. This is Cursor's native context-partitioning pattern.

### Context window and compression

All chats share one fixed window. The context ring shows usage by category (system, tools, rules, skills, MCP, conversation, summarized history). When the window nears capacity, Cursor **compresses older turns into summaries** — lossy, similar in spirit to other agent CLIs. Monitor the ring at phase boundaries; do not assume verbatim history persists.

### Ignore files: access vs indexing

- `.cursorignore` — blocks AI access (Tab, Agent, @ mentions, semantic search)
- `.cursorindexingignore` — excludes from index only; files remain readable if explicitly referenced

Terminal and MCP tools may still reach ignored paths — treat ignore files as defense-in-depth, not a security boundary.

## Gotchas

- **Rules don't steer Tab.** Instruction investment in `.mdc` files won't fix inline completion behavior.
- **Glob rules need files in context.** Opening a matching file in the editor alone may not load the rule; @-mention or agent read triggers attachment.
- **Indexing lag.** New files may not appear in semantic search until the next sync cycle.
- **Large @ attachments dominate budget.** Attaching whole folders or lockfiles can crowd out rules and conversation.
- **Compression is silent.** Summarized history looks like normal context in the tray — verify critical constraints after heavy sessions.

## Integration

- `context-fundamentals` explains why edge-positioned rules and summaries matter.
- `cursor-customization` covers authoring `.mdc` rules and AGENTS.md that this architecture injects.
- `cursor-session-management` covers compression, `/compress`, and session hygiene.
- `filesystem-context` complements indexing with targeted grep/read discovery patterns.
- `tool-design` informs MCP server selection that loads into every Agent request.

## References

- `references/cursor-internals.md` — Indexing pipeline, @-mention catalog, context ring categories, ignore-file semantics.
- `claim-cursor-context-architecture-indexing`: Index completion threshold (~80%), sync interval (~5 min), and embedding details come from Cursor docs and may change between releases.
- `claim-cursor-context-architecture-compression`: Context compression behavior and ring categories follow Cursor's agent prompting docs and evolve with product updates.
