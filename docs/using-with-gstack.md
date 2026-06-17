# Using with GStack

[GStack](https://github.com/garrytan/gstack) is a workflow harness for AI coding agents (`/ship`, `/qa`, `/review`, `/browse`, …). **Context Management for Agents** is a context-engineering knowledge pack. They are complementary — not substitutes.

## Responsibility matrix

| Question | Use GStack | Use context-engineering skills |
|----------|-----------|-------------------------------|
| Ship this PR? | `/ship`, `/review` | — |
| Browser regression QA? | `/qa`, `/browse` | — |
| Context window nearly full? | — | `context-compression`, platform session skills |
| Verbose tool output? | — | `context-optimization`, runtime `mask_observation` |
| Design agent harness + HITL? | `/careful`, `/guard` (tactical) | `harness-engineering` (design) |
| Semantic handoff between agents? | — | `context-compression` (handoff summary) |
| Save workspace/git state? | `/context-save`, `/context-restore` | — |
| Long-horizon memory architecture? | `/learn` (tactical logs) | `memory-systems` |

## Install paths (namespaced)

| Platform | GStack | Context engineering (this repo) |
|----------|--------|--------------------------------|
| Claude Code | `.claude/skills/gstack/` | `.claude/skills/context-engineering/` |
| Cursor | `.cursor/skills/gstack/` | `.cursor/skills/context-engineering/` |
| Antigravity | `.agents/skills/gstack-*` | `.agents/skills/context-engineering/` |

```bash
# Context engineering (this repo)
npx context-management-for-agents --platform cursor --setup

# GStack (separate install — see gstack README)
git clone --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup
```

The `--setup` flag creates per-skill discovery symlinks (GStack-compatible layout).

## MCP servers

You may run both:

- GStack browse / workflow tools
- Context-skills runtime (`runtime/mcp/server.py`) for `route_task`, `compact_session`, `run_context_pipeline`

Disable unused MCP servers per task — tool schema bloat competes with code context (`tool-design`).

## Example session

1. `/office-hours` or `/plan-eng-review` (GStack) — shape the feature
2. Implement with Cursor Agent
3. Context ring fills → read `context-compression` or call runtime `compact_session`
4. `/qa` (GStack) — browser verification
5. `/ship` (GStack) — tests, PR

## Honesty

This guide describes **co-installation patterns**. It does not imply official GStack certification or partnership.
