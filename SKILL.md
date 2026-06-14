---
name: context-engineering-collection
description: A comprehensive collection of Agent Skills for context engineering, harness engineering, multi-agent architectures, and production agent systems — optimized for GitHub Copilot. Use when building, optimizing, evaluating, or debugging agent systems that require effective context management and reliable operating loops.
version: 1.0.0
author: Navendu Brajesh
---

# Agent Skills for Context Engineering

This collection provides structured guidance for building production-grade AI agent systems through effective context engineering. It is optimized for GitHub Copilot (VS Code, Copilot CLI, and the Copilot coding agent) but works with any agent platform that supports skills or custom instructions.

## When to Activate

Activate these skills when:
- Building new agent systems from scratch
- Optimizing existing agent performance
- Debugging context-related failures
- Designing multi-agent architectures
- Creating or evaluating tools for agents
- Implementing memory and persistence layers
- Designing autonomous research or evaluation harnesses
- Tuning GitHub Copilot's context behavior or managing long Copilot CLI sessions
- Authoring Copilot customization files (instructions, prompt files, AGENTS.md, MCP config)

## Skill Map

### Copilot Platform

**Copilot Context Architecture**
How GitHub Copilot assembles context: the client-side prompt wishlist (BeforeCursor, AfterCursor, SimilarFile, ImportedFile, markers) fulfilled against a token budget, Jaccard-based neighboring-tab snippet ranking, Fill-in-the-Middle prompts, the server-side semantic RAG index with a custom embedding model, instruction-file layering, and enterprise governance (content exclusions, training opt-outs, data residency).

**Copilot Session Management**
The context-window lifecycle in Copilot CLI: monitoring with `/context`, automatic compaction at ~80% capacity, manual `/compact`, checkpoints via `/session checkpoints`, and deciding between long-running sessions and fresh starts.

**Copilot Customization**
The file-based steering surface: repository `copilot-instructions.md`, path-scoped `.instructions.md` with `applyTo` globs, prompt files, `AGENTS.md` for the coding agent, and MCP server configuration. Covers which layer to use for what, how to budget the always-on instruction cost, and the failure modes that make Copilot ignore or misapply instructions.

### Foundational Context Engineering

**Understanding Context Fundamentals**
Context is not just prompt text — it is the complete state available to the language model at inference time, including system instructions, tool definitions, retrieved documents, message history, and tool outputs. Effective context engineering means understanding what information truly matters for the task at hand and curating that information for maximum signal-to-noise ratio.

**Recognizing Context Degradation**
Language models exhibit predictable degradation patterns as context grows: the "lost-in-middle" phenomenon where information in the center of context receives less attention; U-shaped attention curves that prioritize beginning and end; context poisoning when errors compound; and context distraction when irrelevant information overwhelms relevant content.

**Compression Under Pressure**
Long-running agent sessions accumulate history that eventually exceeds useful capacity. Compression strategies — hierarchical summarization, selective retention, token budgeting — preserve task-critical state while shedding noise. The key insight is that compression is not lossless: every strategy trades some fidelity for capacity, and the engineering challenge is choosing what to lose.

### Architectural Patterns

**Multi-Agent Coordination**
Production multi-agent systems converge on three dominant patterns: supervisor/orchestrator architectures with centralized control, peer-to-peer swarm architectures for flexible handoffs, and hierarchical structures for complex task decomposition. The critical insight is that sub-agents exist primarily to isolate context rather than to simulate organizational roles.

**Memory System Design**
Memory architectures range from simple scratchpads to sophisticated temporal knowledge graphs. Vector RAG provides semantic retrieval but loses relationship information. Knowledge graphs preserve structure but require more engineering investment. The file-system-as-memory pattern enables just-in-time context loading without stuffing context windows.

**Tool Design Principles**
Tools are contracts between deterministic systems and non-deterministic agents. Effective tool design follows the consolidation principle (prefer single comprehensive tools over multiple narrow ones), returns contextual information in error messages, and treats descriptions as prompt engineering that directly steers agent behavior.

**Filesystem-Based Context**
The filesystem provides a single interface for storing, retrieving, and updating effectively unlimited context. Key patterns include scratch pads for tool output offloading, plan persistence for long-horizon tasks, sub-agent communication via shared files, and dynamic skill loading. Agents use `ls`, `glob`, `grep`, and `read_file` for targeted context discovery, often outperforming semantic search for structural queries.

**Hosted Agent Infrastructure**
Background coding agents run in remote sandboxed environments rather than on local machines. Key patterns include pre-built environment images refreshed on regular cadence, warm sandbox pools for instant session starts, filesystem snapshots for session persistence, and multiplayer support for collaborative agent sessions.

### Operational Excellence

**Context Optimization**
Token-level efficiency tactics: observation masking removes redundant tool outputs, prefix caching reuses shared context prefixes, partitioning separates static from dynamic content, and budget allocation ensures each context component earns its token cost.

**Evaluation Frameworks**
Deterministic evaluation gates catch regressions before deployment. Production evaluation stacks combine assertion-based checks (format, structure, constraint compliance) with statistical sampling and LLM-as-judge techniques for subjective quality dimensions.

**Harness Engineering**
Autonomous agent harnesses manage the operating loop: locked evaluation metrics prevent gaming, durable logs enable post-hoc analysis, novelty gates prevent repetitive exploration, rollback mechanisms recover from failures, and human approval boundaries enforce safety constraints.

### Development Methodology

**Project Development**
LLM project lifecycle from ideation through deployment. Task-model fit analysis determines whether LLMs are appropriate. Pipeline architecture designs the flow of information. Structured output design ensures reliable parsing. Batch processing optimizes throughput and cost.
