# Amazon Q Context Internals

Sources: [AWS Q Developer — project rules](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/context-project-rules.html), Q CLI `/context` behavior (2025–2026).

## Rule loading flow (IDE)

1. Developer opens project
2. Q scans `.amazonq/rules/**/*.md`
3. Rules loaded into context for chat
4. Per-session toggle via Rules button in chat UI
5. Dynamic reload when rule files change on disk

## CLI /context commands

- `/context show` — list matched files with approximate token counts
- `/context add <path>` — attach additional files (subject to size limits)

Typical global globs:
```
.amazonq/rules/**/*.md
README.md
AmazonQ.md
```

## Token limit behavior (CLI)

When context files exceed limits:
- Hard validation may block adding files that exceed threshold
- Soft validation may skip largest files during model calls with user prompt to run `/context show`

Reported figures in CLI issue discussions: ~200K model window, ~150K practical context-file budget — verify against current docs.

## IDE session model

- Context retained within a chat tab/session
- New tab = fresh conversation (no cross-tab memory)
- Up to ~10 tabs in supported IDEs
- `/clear` removes conversation context; `/compact` summarizes history
