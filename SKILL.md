---
name: context-engineering-collection
description: A comprehensive multi-platform collection of Agent Skills for context engineering, harness engineering, multi-agent architectures, and production agent systems. Covers GitHub Copilot, Cursor, Amazon Kiro, Google Antigravity, and Amazon Q Developer. Use when building, optimizing, evaluating, or debugging agent systems that require effective context management.
version: 2.0.0
author: Navendu Brajesh
---

# Context Management for Agents

Structured guidance for building production-grade AI agent systems through effective context engineering. Works across GitHub Copilot, Cursor, Amazon Kiro, Google Antigravity, and Amazon Q Developer — plus any platform that supports skills or custom instructions.

## When to Activate

Activate these skills when:
- Building or optimizing agent systems on any supported platform
- Debugging context-related failures or attention degradation
- Authoring platform-native steering files (rules, steering, AGENTS.md, copilot-instructions)
- Managing long agent sessions, compaction, or durable context artifacts
- Designing multi-agent architectures, memory, tools, or evaluation harnesses

## Skill Map

### Platform Skills — GitHub Copilot

**Copilot Context Architecture** — Client FIM prompt wishlist, Jaccard snippet ranking, semantic RAG index, instruction layering, enterprise governance.

**Copilot Session Management** — CLI `/context`, compaction, checkpoints, long-session hygiene.

**Copilot Customization** — `copilot-instructions.md`, path-scoped `.instructions.md`, prompt files, `AGENTS.md`, MCP.

### Platform Skills — Cursor

**Cursor Context Architecture** — Semantic codebase indexing, @-mentions, rule injection, subagent isolation, context ring.

**Cursor Session Management** — Context ring monitoring, automatic summarization, `/compress`, multi-tab sessions.

**Cursor Customization** — `.cursor/rules/*.mdc`, nested `AGENTS.md`, user/team rules, MCP.

### Platform Skills — Amazon Kiro

**Kiro Context Architecture** — Steering inclusion modes, foundational docs, spec artifacts, file references.

**Kiro Session Management** — Spec-driven durable context (requirements/design/tasks), spec refresh vs fresh chat.

**Kiro Customization** — `.kiro/steering/` frontmatter, global vs workspace scope, hooks, MCP.

### Platform Skills — Google Antigravity

**Antigravity Context Architecture** — AGENTS.md, Knowledge Items, Skills, Artifacts, Editor vs Manager surfaces.

**Antigravity Session Management** — Artifact review cycles, KI hygiene, Manager Surface handoffs.

**Antigravity Customization** — Root/nested AGENTS.md, `.agents/skills/`, workflows, MCP.

### Platform Skills — Amazon Q Developer

**Amazon Q Context Architecture** — `.amazonq/rules/` loading, CLI context profiles, token limits.

**Amazon Q Session Management** — `/compact`, ~80% nudge, `/clear`, CLI auto-compaction.

**Amazon Q Customization** — `.amazonq/rules/`, custom CLI agents, AmazonQ.md scaffolds.

### Foundational Context Engineering

**Context Fundamentals** — What context is, attention mechanics, U-curve, progressive disclosure principles.

**Context Degradation** — Lost-in-middle, poisoning, distraction, clash.

**Context Compression** — Summarization, selective retention, handoff summaries.

### Architectural Patterns

**Multi-Agent Patterns** — Orchestrator, peer-to-peer, hierarchical; context isolation as primary purpose.

**Memory Systems** — Scratchpads, vector RAG, knowledge graphs, filesystem-as-memory.

**Tool Design** — Consolidation principle, descriptions as steering, contextual errors.

**Filesystem Context** — Offloading, plans, sub-agent files, dynamic discovery.

**Hosted Agents** — Sandboxed VMs, warm pools, snapshots, multiplayer.

### Operational Excellence

**Context Optimization** — Masking, partitioning, prefix caching, budgets.

**Evaluation** — Deterministic regression, pass/fail frameworks.

**Advanced Evaluation** — LLM-as-judge, rubrics, pairwise, bias mitigation.

**Harness Engineering** — Locked metrics, logs, novelty gates, rollback, HITL.

### Development Methodology

**Project Development** — Task-model fit, pipeline architecture, structured outputs.
