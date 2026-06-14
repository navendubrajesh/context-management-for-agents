# Context Management for GitHub Copilot

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skills: 16](https://img.shields.io/badge/Skills-16-brightgreen.svg)](#skills-overview)
[![Platform: GitHub Copilot](https://img.shields.io/badge/Platform-GitHub%20Copilot-8957e5.svg)](https://github.com/features/copilot)

A comprehensive, open collection of Agent Skills focused on context engineering and harness engineering principles for building production-grade AI agent systems. These skills teach the art and science of curating context, designing agent operating loops, and evaluating agent behavior across any agent platform — optimized for GitHub Copilot (VS Code, Copilot CLI, and the Copilot coding agent).

## What is Context Engineering?

Context engineering is the discipline of managing the language model's context window. Unlike prompt engineering, which focuses on crafting effective instructions, context engineering addresses the holistic curation of **all information** that enters the model's limited attention budget: system prompts, tool definitions, retrieved documents, message history, and tool outputs.

The fundamental challenge is that context windows are constrained not by raw token capacity but by **attention mechanics**. As context length increases, models exhibit predictable degradation patterns: the "lost-in-the-middle" phenomenon, U-shaped attention curves, and attention scarcity. Effective context engineering means finding the **smallest possible set of high-signal tokens** that maximize the likelihood of desired outcomes.

GitHub Copilot is itself a heavily engineered context system — a client-side prompt crafter that packs a token-budgeted Fill-in-the-Middle prompt from open tabs and Jaccard-ranked snippets, plus a cloud-side RAG pipeline over a custom semantic index. Three skills in this collection (`copilot-context-architecture`, `copilot-session-management`, `copilot-customization`) document that machinery and its steering surface so you can work *with* it instead of against it.

## Skills Overview

### Copilot Platform Skills

Skills specific to GitHub Copilot's context machinery.

| Skill | Description |
|-------|-------------|
| [copilot-context-architecture](skills/copilot-context-architecture/) | How Copilot assembles context: the prompt wishlist, Jaccard snippet ranking, FIM prompts, the semantic RAG index, instruction layering, and enterprise governance |
| [copilot-session-management](skills/copilot-session-management/) | The Copilot CLI context lifecycle: `/context` monitoring, compaction, checkpoints, and long-session hygiene |
| [copilot-customization](skills/copilot-customization/) | Author the files that steer Copilot: `copilot-instructions.md`, path-scoped `.instructions.md` with `applyTo` globs, prompt files, `AGENTS.md`, and MCP configuration |

### Foundational Skills

These skills establish the foundational understanding required for all subsequent context engineering work.

| Skill | Description |
|-------|-------------|
| [context-fundamentals](skills/context-fundamentals/) | Understand what context is, why it matters, and the anatomy of context in agent systems |
| [context-degradation](skills/context-degradation/) | Recognize patterns of context failure: lost-in-middle, poisoning, distraction, and clash |
| [context-compression](skills/context-compression/) | Design and evaluate compression strategies for long-running sessions |

### Architectural Skills

These skills cover the patterns and structures for building effective agent systems.

| Skill | Description |
|-------|-------------|
| [multi-agent-patterns](skills/multi-agent-patterns/) | Master orchestrator, peer-to-peer, and hierarchical multi-agent architectures |
| [memory-systems](skills/memory-systems/) | Design short-term, long-term, and graph-based memory architectures |
| [tool-design](skills/tool-design/) | Build tools that agents can use effectively |
| [filesystem-context](skills/filesystem-context/) | Use filesystems for dynamic context discovery, tool output offloading, and plan persistence |
| [hosted-agents](skills/hosted-agents/) | Build background coding agents with sandboxed VMs, pre-built images, and multiplayer support |

### Operational Skills

These skills address the ongoing operation and optimization of agent systems.

| Skill | Description |
|-------|-------------|
| [context-optimization](skills/context-optimization/) | Apply compaction, masking, and caching strategies |
| [evaluation](skills/evaluation/) | Build evaluation frameworks for agent systems |
| [advanced-evaluation](skills/advanced-evaluation/) | Master LLM-as-a-Judge techniques: direct scoring, pairwise comparison, rubric generation, and bias mitigation |
| [harness-engineering](skills/harness-engineering/) | Design autonomous agent harnesses with locked metrics, durable logs, novelty gates, rollback, and human approval boundaries |

### Development Methodology

| Skill | Description |
|-------|-------------|
| [project-development](skills/project-development/) | Design and build LLM projects from ideation through deployment, including task-model fit analysis, pipeline architecture, and structured output design |

## Design Philosophy

### Progressive Disclosure

Each skill is structured for efficient context use. At startup, agents load only skill names and descriptions. Full content loads only when a skill is activated for relevant tasks. This mirrors human cognition — maintain an index, not a copy. It is also exactly how Copilot's own instruction layering works: keep `copilot-instructions.md` lean, push detail into path-scoped files.

### Platform Agnosticism

These skills focus on transferable principles rather than vendor-specific implementations. Aside from the two Copilot platform skills, the patterns work across GitHub Copilot, Claude Code, Cursor, Google Antigravity IDE, and any agent platform that supports skills or allows custom instructions.

### Conceptual Foundation with Practical Examples

Scripts and examples demonstrate concepts using Python pseudocode that works across environments without requiring specific dependency installations. The goal is understanding, not copy-paste.

### Token Consciousness

Every SKILL.md is kept under 500 lines. Detailed reference material lives in `references/` subdirectories, loaded only when needed. This ensures skills don't bloat the agent's context window during discovery.

## Installation & Setup

GitHub Copilot discovers customization through instruction files. This collection supports three install targets:

### Option 1: CLI Installer (Recommended)

```bash
npm i context-management-for-copilot
```

Or run the installer directly with `npx`:

* **Repository install (VS Code / Copilot coding agent):**
  Copies the skills into `.github/skills/` of the current repository and generates a `.github/copilot-instructions.md` index that teaches Copilot to load skills progressively (names + descriptions up front, full SKILL.md on demand):
  ```bash
  npx context-management-for-copilot
  ```
  If a `.github/copilot-instructions.md` already exists, the index is appended; nothing is overwritten.

* **Global install (Copilot CLI):**
  Copies the skills to `~/.copilot/skills` and generates/extends `~/.copilot/copilot-instructions.md` with the same progressive-disclosure index:
  ```bash
  npx context-management-for-copilot --global
  ```

* **Custom directory:**
  ```bash
  npx context-management-for-copilot --path ./my-skills-folder
  ```

### Option 2: Direct Git Clone

```bash
git clone https://github.com/your-username/context-management-for-copilot.git
```

After cloning, copy `skills/` into `.github/skills/` of your repository and reference it from `.github/copilot-instructions.md`, or point path-scoped `.github/instructions/*.instructions.md` files (with `applyTo` globs) at individual skills.

### Option 3: AGENTS.md

For agent products that read `AGENTS.md` (including the Copilot coding agent), add the skill index from `SKILL.md` to your repository's `AGENTS.md`. Copilot merges instruction layers in priority order: personal → path-scoped `.instructions.md` → repo `copilot-instructions.md` → `AGENTS.md` → org.

## Skill Activation & Detailed Use Cases

This collection consists of 16 specialized skills. The table below outlines exactly when each skill should be activated (the activation trigger) and its primary practical use cases.

| Skill | Activate When (Trigger Scenario) | Primary Use Cases |
| :--- | :--- | :--- |
| **`copilot-context-architecture`** | Tuning what Copilot sees, diagnosing irrelevant completions, configuring `#codebase`/indexing, or making Copilot governance decisions. | • Structuring workspaces/tabs for better completions<br>• Configuring content exclusions and training opt-outs<br>• Budgeting against effective (not advertised) context limits. |
| **`copilot-session-management`** | Copilot CLI sessions grow long, the agent forgets earlier decisions, or planning multi-phase work in one session. | • Proactive `/compact` at phase boundaries<br>• Auditing checkpoints after auto-compaction<br>• Deciding session-continue vs. fresh-start. |
| **`copilot-customization`** | Authoring or fixing Copilot instruction files, instructions being ignored, or instruction bloat degrading responses. | • Writing path-scoped `.instructions.md` with `applyTo`<br>• Keeping `copilot-instructions.md` within budget<br>• Mirroring invariants into `AGENTS.md` for the coding agent. |
| **`context-fundamentals`** | Establishing base context models, designing system prompts, or when analyzing how context structures affect LLM reasoning. | • Setting up startup agent profiles<br>• Designing token-conscious system prompts<br>• Decoupling code instructions from workspace files. |
| **`context-degradation`** | Diagnosing degraded agent performance, "lost-in-middle" attention drops, repeating actions, or context distraction in long sessions. | • Debugging multi-turn session fatigue<br>• Preventing hallucinated tool loops<br>• Restructuring bloated conversation logs. |
| **`context-compression`** | Compressing conversation history or tool trajectories to free up space under strict token limits without losing critical state. | • Compacting long chat histories<br>• Defining token budgets for sub-agents<br>• Generating structured session summaries. |
| **`context-optimization`** | Applying systematic token-saving strategies (masking, partitioning, prefix caching optimization) to make the workspace highly efficient. | • Minimizing overhead of large payload tokens<br>• Restructuring prompts for Prefix Cache hits<br>• Setting up compartmentalized context pools. |
| **`multi-agent-patterns`** | Designing orchestration systems, determining if a task warrants parallel agents, or designing sub-agent communications. | • Building orchestrator-worker swarms<br>• Isolating context between specialist sub-agents<br>• Defining handoff protocols between CLI agents. |
| **`memory-systems`** | Designing short-term, long-term, or graph-based memory structures to persist information across multiple sessions. | • Setting up cross-session knowledge bases<br>• Designing hybrid Vector RAG + Knowledge Graph memory<br>• Minimizing context bloating via filesystem paging. |
| **`tool-design`** | Creating new tools (e.g., custom MCP servers), refining tool descriptions, or diagnosing tool selection/argument generation failures. | • Writing precise OpenAPI/JSON tool schemas<br>• Describing tools as steering prompts<br>• Returning rich contextual help in tool errors. |
| **`filesystem-context`** | Offloading verbose outputs to file systems, persisting long-term plans, or managing sub-agent communication files. | • Offloading grep/git output to scratch files<br>• Creating persistent plan-tracking checklists<br>• Using file read/write for dynamic skill loading. |
| **`hosted-agents`** | Designing background agent sandbox pools, pre-built runtime images, session persistence, or multiplayer collab environments. | • Scaffold VM environments for remote execution<br>• Managing warm pool caches for instant CLI runs<br>• Rebuilding sandbox filesystem snapshots. |
| **`evaluation`** | Designing deterministic regression tests, verification frameworks, and pass/fail metrics for agent task execution. | • Asserting file changes match expected specs<br>• Testing tool sequence execution correctness<br>• Automated repo-health checks. |
| **`advanced-evaluation`** | Implementing LLM-as-a-Judge systems, rubric-based grading, pairwise comparisons, or neutralizing evaluator bias. | • Grading non-deterministic code changes<br>• Conducting automated A/B test analysis<br>• Designing double-blind grading prompts. |
| **`harness-engineering`** | Constructing end-to-end agent harnesses with locked targets, durable history tracking, and rollback capabilities. | • Building automated benchmark systems<br>• Managing loop security policies and permissions<br>• Handling human-in-the-loop approvals. |
| **`project-development`** | Starting new AI-native projects, conducting task-model fit audits, or choosing pipeline architectures. | • Auditing complexity of codebase tasks<br>• Designing structured JSON schema outputs<br>• Deciding between RAG vs. fine-tuning approach. |

## Working With Copilot's Context Machinery

Practical levers this collection teaches, specific to Copilot:

- **Open the right tabs.** Inline completions rank snippets from open/recent same-language files via Jaccard similarity — opening the relevant interface or schema file is the cheapest context win available.
- **Keep `copilot-instructions.md` lean.** It loads into every request. Push path-specific guidance into `.github/instructions/*.instructions.md` with `applyTo` globs — progressive disclosure, natively.
- **Budget against effective limits.** Copilot's routing layer caps usable context below provider maxima and reserves ~30–35% for output.
- **Compact at phase boundaries.** In Copilot CLI, run `/compact` proactively before a new phase instead of letting auto-compaction fire mid-task; verify checkpoints with `/session checkpoints`.
- **Offload to files.** Plans and decisions written to workspace files survive compaction losslessly; conversation history does not.

## Examples

See the [examples/](examples/) directory for complete demonstration projects that apply these skills in practice:

| Example | Skills Applied |
|---------|---------------|
| [digital-brain-skill](examples/digital-brain-skill/) | context-fundamentals, memory-systems, filesystem-context |
| [llm-as-judge-skills](examples/llm-as-judge-skills/) | evaluation, advanced-evaluation |
| [code-generation-harness](examples/code-generation-harness/) | harness-engineering, tool-design, context-optimization |
| [research-pipeline](examples/research-pipeline/) | multi-agent-patterns, filesystem-context, context-compression |
| [multi-agent-coordination](examples/multi-agent-coordination/) | multi-agent-patterns, memory-systems, filesystem-context |

## Researcher Operating System

The `researcher/` directory contains a file-based research operating system for continuous skill improvement:

- **source-registry.md** — Research priorities and source tracking
- **mechanisms/** — Behavior-changing mechanism registry (JSONL)
- **claims/** — Volatile claim provenance tracking
- **corpus/** — Machine-readable skill-to-mechanism map
- **rubrics/** — Deterministic quality rubrics
- **scripts/** — Validation and benchmarking scripts
- **benchmarks/** — Activation case fixtures

### Validation Gates

```bash
python3 researcher/scripts/validate_repo.py --strict
python3 researcher/scripts/skill_health.py --strict --no-history
python3 researcher/scripts/run_benchmarks.py
python3 researcher/scripts/check_activation_cases.py
```

### Context Window Savings (Measured)

> **These are real measurements**, not theoretical estimates. Each benchmark processes realistic test fixtures — 41-row database query results, 20-turn agent conversations with tool outputs, 5-tool JSON schemas, and all 16 skill files in this repository — and reports actual token counts before and after applying each technique.
>
> **Attribution:** The benchmark harness and fixtures originate from [context-management-for-antigravity](https://github.com/maybeanns/context-management-for-antigravity) by maybeanns. The numbers below were **re-measured against this repository** (16 skills, including the three Copilot platform skills) on 2026-06-13. The Progressive Disclosure row differs from the upstream repo's published results because this collection has a different skill set, which changes the "load everything" baseline.

Run the benchmark yourself:

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
| Progressive Disclosure | 40,532 | 1,959 | 38,573 | 95.2% | `context-fundamentals` |
| Format Optimization | 493 | 136 | 357 | 72.4% | `context-optimization` |
| Filesystem Offloading | 1,250 | 203 | 1,047 | 83.8% | `filesystem-context` |
| Context Partitioning + Budget | 3,682 | 435 | 3,247 | 88.2% | `context-optimization` |
| Handoff Summary | 3,777 | 255 | 3,522 | 93.2% | `context-compression` |
| Selective Retention | 904 | 145 | 759 | 84.0% | `context-compression` |
| Combined Pipeline | 2,936 | 234 | 2,702 | 92.0% | `all context skills` |
| **TOTAL** | **61,144** | **4,182** | **56,962** | **93.2%** | — |

**Key findings:**
- **Progressive Disclosure** delivers the single largest saving (38.6K tokens) — loading 16 skill descriptions at startup costs 1,959 tokens vs. 40,532 for loading all skill bodies + references
- **Observation Masking** achieves the highest per-item efficiency (95.7%) — a 41-row database query compresses from 2,222 to 95 tokens
- **Combined Pipeline** (all techniques together) achieves 92.0% savings on a full agent session

#### Skill Quality Validation (re-measured on this repository, 2026-06-13)

| Metric | Result | Details |
|--------|--------|---------|
| Activation Boundary Completeness | 100.0% | 16/16 skills have both "When to Activate" and "Do not activate" |
| Cross-Reference Density | 139 refs | Explicit routing to sibling skills for disambiguation |
| Token Budget Compliance (500-line) | 16/16 | All SKILL.md files under 500 lines |
| Routing Signal Quality | 3.62/5.0 | 5-point rubric: activation phrase, scope, disambiguation, detail, cross-refs |

Full results: [context-savings-2026-06-13.json](researcher/benchmarks/context-savings/results/context-savings-2026-06-13.json)

## Contributing

1. Use `template/SKILL.md` as the starting point for new skills
2. Keep SKILL.md under 500 lines; move details to `references/`
3. Include YAML frontmatter with `name` and `description`
4. Define ownership boundaries in "When to Activate" with "Do not activate" blocks
5. Run all validation gates before submitting

## Credits & Inspiration

This project is adapted from:
* **Original Repository:** [Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) by Muratcan Koylan.
* **Antigravity Adaptation:** [context-management-for-antigravity](https://github.com/maybeanns/context-management-for-antigravity) by maybeanns.
* **GitHub Copilot Adaptation:** Adds `copilot-context-architecture`, `copilot-session-management`, and `copilot-customization` skills documenting Copilot's two-tier context pipeline, CLI session lifecycle, and file-based steering surface; drops the `latent-briefing` and `bdi-mental-states` skills as inapplicable to Copilot's closed runtime; and adds Copilot-native installation via `copilot-instructions.md`, path-scoped `.instructions.md`, and `AGENTS.md`.

## License

[MIT](LICENSE)
