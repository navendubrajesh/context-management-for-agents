# Cursor Context Internals

Companion to `cursor-context-architecture`. Sources: [Cursor Docs](https://cursor.com/docs) — rules, semantic search, prompting, ignore files, CLI (2025–2026).

## Indexing pipeline

1. Workspace opened → chunking at function/class/logical-block boundaries
2. Custom embedding model converts chunks to vectors
3. Vectors stored in Cursor's vector database
4. Semantic search available at ~80% index completion
5. Incremental sync ~every 5 minutes on changed files only

Multi-root workspaces: all roots indexed; some git-root-dependent features (worktrees) disabled.

## @-mention catalog

| Mention | Purpose |
|---------|---------|
| Files & folders | Direct attachment; `/` navigates into folders |
| @Docs | Indexed documentation (custom docs addable) |
| @Terminals | Terminal output as context |
| @Past Chats | Prior conversation context |
| Git diffs | Working state or branch vs main |
| @Browser | Built-in browser context |

## Context ring categories

System prompt, Tools, Rules, Skills, MCP, Subagents, Summarized conversation, Conversation — hover/click ring for per-category token share.

## Rule activation matrix

| alwaysApply | description | globs | Behavior |
|-------------|-------------|-------|----------|
| true | — | — | Always included |
| false | — | set | Auto-attached when matching file in context |
| false | set | omitted | Agent decides relevance from description |
| false | omitted | omitted | Manual @-mention only |

## Ignore semantics

`.cursorignore`: blocks Tab, Agent, @ refs, semantic search. `.cursorindexingignore`: search exclusion only. Defaults also respect `.gitignore` patterns.
