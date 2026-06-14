# Context Management for Agents

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skills: 28](https://img.shields.io/badge/Skills-28-brightgreen.svg)](#skills-overview)
[![Platforms: 5](https://img.shields.io/badge/Platforms-5-8957e5.svg)](#platform-skills)
[![npm version](https://img.shields.io/npm/v/context-management-for-agents?label=npm)](https://www.npmjs.com/package/context-management-for-agents)

**Multi-platform Agent Skills for context engineering** — curated guidance for GitHub Copilot, Cursor, Amazon Kiro, Google Antigravity, and Amazon Q Developer, plus 13 platform-agnostic skills that transfer everywhere.

## Table of Contents

- [What is Context Engineering?](#what-is-context-engineering)
- [Skills Overview](#skills-overview)
- [Platform Skills](#platform-skills)
- [Foundational & Architectural Skills](#foundational--architectural-skills)
- [Installation](#installation)
- [Skill Activation & Use Cases](#skill-activation--use-cases)
- [Validation Gates](#validation-gates)
- [Context Window Savings (Measured)](#context-window-savings-measured)
- [Examples](#examples)
- [Contributing](#contributing)
- [Credits & Inspiration](#credits--inspiration)
- [About the Author](#about-the-author)
- [Connect & Read More](#connect--read-more)
- [License](#license)

## What is Context Engineering?

Context engineering is the discipline of managing everything that enters a language model's context window: system prompts, tool definitions, retrieved documents, message history, and tool outputs. Unlike prompt engineering, it addresses the **holistic curation** of information under attention limits — finding the smallest high-signal token set that maximizes desired outcomes.

Each agentic coding platform implements context differently. This collection documents those mechanics **per platform** while teaching transferable principles in shared skills.

## Skills Overview

**28 skills total:** 13 platform-agnostic + 15 platform-specific (3 per supported tool).

Every skill follows progressive disclosure: load names and descriptions first; read full `SKILL.md` (and `references/` only when needed) on activation.

## Platform Skills

### GitHub Copilot

| Skill | Description |
|-------|-------------|
| [copilot-context-architecture](skills/copilot-context-architecture/) | FIM prompt wishlist, Jaccard snippet ranking, semantic RAG index, instruction layering, governance |
| [copilot-session-management](skills/copilot-session-management/) | CLI `/context`, compaction, checkpoints, long-session hygiene |
| [copilot-customization](skills/copilot-customization/) | `copilot-instructions.md`, path-scoped `.instructions.md`, prompt files, `AGENTS.md`, MCP |

### Cursor

| Skill | Description |
|-------|-------------|
| [cursor-context-architecture](skills/cursor-context-architecture/) | Semantic indexing, @-mentions, rule injection, subagents, context ring |
| [cursor-session-management](skills/cursor-session-management/) | Context ring monitoring, summarization, `/compress`, multi-tab sessions |
| [cursor-customization](skills/cursor-customization/) | `.cursor/rules/*.mdc`, nested `AGENTS.md`, user/team rules, MCP |

### Amazon Kiro

| Skill | Description |
|-------|-------------|
| [kiro-context-architecture](skills/kiro-context-architecture/) | Steering inclusion modes, foundational docs, spec artifacts, file references |
| [kiro-session-management](skills/kiro-session-management/) | Spec-driven durable context (requirements/design/tasks), spec refresh heuristics |
| [kiro-customization](skills/kiro-customization/) | `.kiro/steering/` frontmatter, global vs workspace scope, hooks, MCP |

### Google Antigravity

| Skill | Description |
|-------|-------------|
| [antigravity-context-architecture](skills/antigravity-context-architecture/) | AGENTS.md, Knowledge Items, Skills, Artifacts, Editor vs Manager surfaces |
| [antigravity-session-management](skills/antigravity-session-management/) | Artifact review cycles, KI hygiene, Manager Surface handoffs |
| [antigravity-customization](skills/antigravity-customization/) | Root/nested AGENTS.md, `.agents/skills/`, workflows, MCP |

### Amazon Q Developer

| Skill | Description |
|-------|-------------|
| [amazonq-context-architecture](skills/amazonq-context-architecture/) | `.amazonq/rules/` loading, CLI context profiles, token limits |
| [amazonq-session-management](skills/amazonq-session-management/) | `/compact`, ~80% nudge, `/clear`, CLI auto-compaction |
| [amazonq-customization](skills/amazonq-customization/) | `.amazonq/rules/`, custom CLI agents, AmazonQ.md scaffolds |

## Foundational & Architectural Skills

### Foundational

| Skill | Description |
|-------|-------------|
| [context-fundamentals](skills/context-fundamentals/) | What context is, attention mechanics, U-curve, mental models |
| [context-degradation](skills/context-degradation/) | Lost-in-middle, poisoning, distraction, clash |
| [context-compression](skills/context-compression/) | Summarization, selective retention, handoff summaries |

### Architectural

| Skill | Description |
|-------|-------------|
| [multi-agent-patterns](skills/multi-agent-patterns/) | Orchestrator, peer-to-peer, hierarchical architectures |
| [memory-systems](skills/memory-systems/) | Short/long-term memory, vector RAG, knowledge graphs |
| [tool-design](skills/tool-design/) | Tool contracts, consolidation, descriptions as steering |
| [filesystem-context](skills/filesystem-context/) | Offloading, plans, sub-agent files, dynamic discovery |
| [hosted-agents](skills/hosted-agents/) | Sandboxed VMs, warm pools, snapshots, multiplayer |

### Operational & Methodology

| Skill | Description |
|-------|-------------|
| [context-optimization](skills/context-optimization/) | Masking, partitioning, prefix caching, budgets |
| [evaluation](skills/evaluation/) | Deterministic regression, pass/fail frameworks |
| [advanced-evaluation](skills/advanced-evaluation/) | LLM-as-judge, rubrics, pairwise, bias mitigation |
| [harness-engineering](skills/harness-engineering/) | Locked metrics, logs, novelty gates, rollback, HITL |
| [project-development](skills/project-development/) | Task-model fit, pipeline architecture, structured outputs |

## Installation

```bash
npm i context-management-for-agents
```

Or run directly with `npx`:

```bash
# GitHub Copilot (default) → .github/skills/ + copilot-instructions.md
npx context-management-for-agents --platform copilot

# Cursor → .cursor/skills/ + .cursor/rules/context-engineering-skills-index.mdc
npx context-management-for-agents --platform cursor

# Amazon Kiro → .kiro/skills/ + .kiro/steering/context-engineering-skills-index.md
npx context-management-for-agents --platform kiro

# Google Antigravity → .agents/skills/ + AGENTS.md index
npx context-management-for-agents --platform antigravity

# Amazon Q Developer → .amazonq/skills/ + .amazonq/rules/context-engineering-skills-index.md
npx context-management-for-agents --platform amazonq

# Copilot CLI global install
npx context-management-for-agents --platform copilot --global

# Raw copy to custom directory (no index generated)
npx context-management-for-agents --path ./my-skills-folder
```

**Git clone:**

```bash
git clone https://github.com/navendubrajesh/context-management-for-agents.git
```

## Skill Activation & Use Cases

| Skill | Activate When | Primary Use Cases |
| :--- | :--- | :--- |
| **`copilot-context-architecture`** | Tuning Copilot context, irrelevant completions, `#codebase`/indexing | Workspace/tab structure, content exclusions, effective context limits |
| **`copilot-session-management`** | Long Copilot CLI sessions, forgotten decisions | `/compact` at phase boundaries, checkpoint audits |
| **`copilot-customization`** | Authoring Copilot instruction files, instruction bloat | Path-scoped `.instructions.md`, lean `copilot-instructions.md` |
| **`cursor-context-architecture`** | Cursor search misses files, context ring bloat | Indexing tuning, @-mention strategy, ignore files |
| **`cursor-session-management`** | Context ring near full, post-summarization drift | `/compress`, fresh Agent tabs, MCP overhead reduction |
| **`cursor-customization`** | Writing `.mdc` rules, rules ignored | Glob-scoped rules, AGENTS.md nesting |
| **`kiro-context-architecture`** | Steering/spec context questions | Inclusion modes, foundational docs, spec artifacts |
| **`kiro-session-management`** | Spec drift, stale tasks.md | Spec refresh, fresh chat vs continue |
| **`kiro-customization`** | Authoring `.kiro/steering/` files | fileMatch/manual/auto inclusion, AGENTS.md scope |
| **`antigravity-context-architecture`** | KI vs Artifacts vs chat confusion | Context pillar design, Manager vs Editor |
| **`antigravity-session-management`** | Async agent Artifact review | KI hygiene, fresh agent spawn heuristics |
| **`antigravity-customization`** | AGENTS.md vs skills split | `.agents/skills/` packaging, Do Not sections |
| **`amazonq-context-architecture`** | Q CLI ValidationException, oversized rules | `/context show` auditing, token limits |
| **`amazonq-session-management`** | Q chat approaching limits | `/compact`, `/clear` decisions |
| **`amazonq-customization`** | Organizing `.amazonq/rules/` | Nested rules, CLI agent resources |
| **`context-fundamentals`** | Conceptual context questions, onboarding | Attention models, progressive disclosure theory |
| **`context-degradation`** | Lost-in-middle, poisoning, distraction | Debugging session fatigue, log restructuring |
| **`context-compression`** | Handoff summaries, history compression | Selective retention, structured summaries |
| **`context-optimization`** | Token-saving tactics | Masking, partitioning, prefix caching |
| **`multi-agent-patterns`** | Orchestration topology decisions | Supervisor vs swarm, handoff protocols |
| **`memory-systems`** | Cross-session persistence design | Vector RAG, graph memory, hybrid architectures |
| **`tool-design`** | Tool schema/description failures | Consolidation, contextual error messages |
| **`filesystem-context`** | Offloading verbose outputs | Scratch files, plan persistence |
| **`hosted-agents`** | Remote sandbox agent pools | Warm pools, snapshots, multiplayer |
| **`evaluation`** | Regression test frameworks | Assertion-based agent checks |
| **`advanced-evaluation`** | LLM-as-judge systems | Rubrics, pairwise comparison, bias mitigation |
| **`harness-engineering`** | Autonomous agent operating loops | Novelty gates, rollback, HITL boundaries |
| **`project-development`** | New LLM project scoping | Task-model fit, pipeline architecture |

## Validation Gates

```bash
python3 researcher/scripts/validate_repo.py --strict
python3 researcher/scripts/skill_health.py --strict --no-history
python3 researcher/scripts/run_benchmarks.py
python3 researcher/scripts/check_activation_cases.py
```

## Context Window Savings (Measured)

> **These are real measurements**, not theoretical estimates. Each benchmark processes realistic test fixtures and reports actual token counts before and after applying each technique.
>
> **Attribution:** The benchmark harness and fixtures originate from [context-management-for-antigravity](https://github.com/maybeanns/context-management-for-antigravity) by maybeanns. The numbers below were **re-measured against this repository** (28 skills across five platforms) on **2026-06-14**. Progressive Disclosure baseline changed because this collection has a larger skill set than upstream.

```bash
python researcher/benchmarks/context-savings/benchmark_context_savings.py
python researcher/benchmarks/context-savings/benchmark_context_savings.py --markdown
python researcher/benchmarks/context-savings/benchmark_context_savings.py --json
```

| Technique | Before (tokens) | After (tokens) | Saved | Savings % | Skill |
|-----------|----------------:|---------------:|------:|----------:|-------|
| Observation Masking | 2,222 | 95 | 2,127 | 95.7% | `context-optimization` |
| Hierarchical Summarization | 3,777 | 428 | 3,349 | 88.7% | `context-compression` |
| Tool Schema Optimization | 1,571 | 292 | 1,279 | 81.4% | `tool-design` |
| Progressive Disclosure | 58,790 | 3,426 | 55,364 | 94.2% | `context-fundamentals` |
| Format Optimization | 493 | 136 | 357 | 72.4% | `context-optimization` |
| Filesystem Offloading | 1,250 | 203 | 1,047 | 83.8% | `filesystem-context` |
| Context Partitioning + Budget | 3,682 | 435 | 3,247 | 88.2% | `context-optimization` |
| Handoff Summary | 3,777 | 255 | 3,522 | 93.2% | `context-compression` |
| Selective Retention | 904 | 145 | 759 | 84.0% | `context-compression` |
| Combined Pipeline | 2,936 | 234 | 2,702 | 92.0% | all context skills |
| **TOTAL** | **79,402** | **5,649** | **73,753** | **92.9%** | — |

**Key findings:**
- **Progressive Disclosure** delivers the largest absolute saving (55.4K tokens) — 28 skill descriptions cost 3,426 tokens vs. 58,790 for full bodies + references
- **Observation Masking** achieves the highest per-item efficiency (95.7%)
- **Combined Pipeline** achieves 92.0% savings on a full agent session

#### Skill Quality Validation (re-measured 2026-06-14)

| Metric | Result | Details |
|--------|--------|---------|
| Activation Boundary Completeness | 100.0% | 28/28 skills have both "When to Activate" and "Do not activate" |
| Cross-Reference Density | 239 refs | Explicit routing to sibling skills |
| Token Budget Compliance (500-line) | 28/28 | All SKILL.md files under 500 lines |
| Routing Signal Quality | 2.93/5.0 | 5-point rubric on activation descriptions |

Full results: [context-savings-2026-06-14.json](researcher/benchmarks/context-savings/results/context-savings-2026-06-14.json)

## Examples

| Example | Skills Applied |
|---------|---------------|
| [digital-brain-skill](examples/digital-brain-skill/) | context-fundamentals, memory-systems, filesystem-context |
| [llm-as-judge-skills](examples/llm-as-judge-skills/) | evaluation, advanced-evaluation |
| [code-generation-harness](examples/code-generation-harness/) | harness-engineering, tool-design, context-optimization |
| [research-pipeline](examples/research-pipeline/) | multi-agent-patterns, filesystem-context, context-compression |
| [multi-agent-coordination](examples/multi-agent-coordination/) | multi-agent-patterns, memory-systems, filesystem-context |

## Contributing

1. Use `template/SKILL.md` as the starting point for new skills
2. Keep SKILL.md under 500 lines; move details to `references/`
3. Include YAML frontmatter with `name` and `description`
4. Define ownership boundaries with "Do not activate" blocks
5. Add activation cases and update `EXPECTED_SKILLS` in all validation scripts
6. Run all four validation gates before submitting

## Credits & Inspiration

Adapted from:
- **Original:** [Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) by Muratcan Koylan
- **Antigravity fork:** [context-management-for-antigravity](https://github.com/maybeanns/context-management-for-antigravity) by maybeanns
- **Multi-platform expansion:** Adds platform skills for Cursor, Kiro, Antigravity, and Amazon Q Developer; multi-platform installer; rebranded as **context-management-for-agents**

## About the Author

**[Navendu Brajesh](https://navendubrajesh.github.io)** is a Delivery Manager for Digital Enablement Platform Group Tools at [Sopra Steria](https://www.linkedin.com/company/soprasteria), based in Delhi, India. He works at the intersection of platform management, digital enablement, and AI/ML — with certifications spanning cloud architecture, AI foundations, and agile delivery (CSM, PMP).

This collection reflects practical context-engineering patterns for production agent systems across the major agentic coding platforms teams adopt today. More projects and writing at **[navendubrajesh.github.io](https://navendubrajesh.github.io)**.

## Connect & Read More

[![Portfolio](https://img.shields.io/badge/Portfolio-navendubrajesh.github.io-0f766e?style=flat)](https://navendubrajesh.github.io)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Navendu_Brajesh-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://in.linkedin.com/in/navendubrajesh)
[![Medium](https://img.shields.io/badge/Medium-@navendubrajesh-000000?style=flat&logo=medium&logoColor=white)](https://medium.com/@navendubrajesh)

I write about context engineering, AI agents, and platform enablement on [Medium](https://medium.com/@navendubrajesh). If this repository helps your work, the essays there go deeper on the why behind the patterns.

**Related writing:** Context window discipline, agent harness design, and multi-platform steering surfaces are recurring themes in my Medium posts — complementary reading to the skills in this repo.

## License

[MIT](LICENSE)
