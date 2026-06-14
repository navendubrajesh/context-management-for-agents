# Runnable demo

Proof that the Skill Router and context primitives work **offline** — no API keys or network.

## Quick run

From the repository root (after installing the runtime core):

```bash
pip install -e runtime/core -e runtime/mcp
python examples/demo/run_demo.py
python examples/demo/run_mcp_demo.py
```

## What each script does

| Script | Proves |
|--------|--------|
| `run_demo.py` | In-process Skill Router + `compact_session` handoff compaction |
| `run_mcp_demo.py` | MCP stdio server: `tools/list`, `route_task`, `run_context_pipeline` |

## Expected output (`run_demo.py`)

```
============================================================
Context Management for Agents — Runnable Demo
============================================================

Task: 'compress conversation history for a handoff'

--- Skill Router ---
  1. context-compression (score 14.0) ← selected
  2. context-optimization (score 1.8)
  3. copilot-session-management (score 5.0)

Router selected: context-compression

--- Context primitive: compact_session (handoff_summary) ---
  Tokens before: 3,776
  Tokens after:  255
  Tokens saved:  3,521 (93.2%)
...
[+] Demo complete (offline, no credentials).
```

Exact token counts depend on the bundled `sample_messages.json` and counter (heuristic/tiktoken). Savings should be **~90%+** on the handoff fixture — consistent with the project's measured benchmarks on similar fixtures (see [Benchmarks](../../docs/benchmarks.md); numbers are re-measured on this repo's fixtures, not theoretical).

## Expected output (`run_mcp_demo.py`)

```
============================================================
Context Management for Agents — MCP Demo
============================================================

--- tools/list (9 tools) ---
  • budget_context
  • compact_session
  ...
--- route_task: 'compress conversation history for a handoff' ---
  Top skill: context-compression (score 14.0)

--- run_context_pipeline ---
  Tokens before: 2,833
  Tokens after:  270
  Tokens saved:  2,563 (90.5%)

[+] MCP demo complete (stdio transport, offline).
```

## Sample data

- `sample_conversation.json` — full benchmark conversation for handoff compaction (~93% savings)
- `sample_messages.json` — short fallback conversation
- `sample_pipeline_session.json` — note: MCP demo builds the benchmark pipeline session inline
