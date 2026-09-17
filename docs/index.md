# Context Management for Agents

![Demo](../assets/demo.gif)

**28 Agent Skills** and a **callable runtime** (MCP, REST, SDKs) for context engineering across GitHub Copilot, Cursor, Kiro, Antigravity, and Amazon Q.

## Why this project

Agent quality depends on what fits in the context window. This collection teaches **progressive disclosure**, **compaction**, **masking**, and **budgeting** — with measured savings on realistic fixtures and a Skill Router that picks the right guidance for a task.

## Try it in 60 seconds

```bash
git clone https://github.com/navendubrajesh/context-management-for-agents.git
cd context-management-for-agents
pip install -e runtime/core -e runtime/mcp
python examples/demo/run_demo.py
```

You will see the router select `context-compression` for a handoff task and print **before/after token counts** from an offline primitive.

## What's included

| Layer | Location | Purpose |
|-------|----------|---------|
| Skills | `skills/` | 28 SKILL.md files (platform + foundational) |
| Runtime | `runtime/` | Router, loader, MCP, REST, Python/TS SDKs |
| Primitives | `runtime/core/context_skills/primitives/` | Masking, compaction, budgeter, pipeline |
| Validation | `researcher/scripts/` | Four deterministic quality gates |
| Enterprise | `control-plane/`, `deploy/` | IAM, tenancy, policy, audit (Phase 3) |

## Documentation map

- [Quickstart](quickstart.md) — install, demo, MCP, REST
- [Concepts](concepts.md) — context engineering techniques
- [Skills catalog](skills/index.md) — auto-generated index
- [Runtime reference](runtime.md) — MCP tools and REST endpoints
- [Benchmarks](benchmarks.md) — measured savings (with caveats)
- [Enterprise landing](https://navendubrajesh.github.io/context-management-for-agents.enterprise/) — overview and links
- [Enterprise deployment](ENTERPRISE.md) — regulated deployment patterns

## Honest claims

Measured savings (~93% on handoff fixture, ~93% aggregate on project fixtures) are **re-measured on this repository's test fixtures** — not theoretical. See [Benchmarks](benchmarks.md). Cost figures in the runtime are **estimated**; pricing is operator-configured.
