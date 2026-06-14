# COPILOT.md

This file provides guidance to GitHub Copilot agents (VS Code agent mode, Copilot CLI, and the Copilot coding agent) when working with code in this repository. A copy of this guidance belongs in `.github/copilot-instructions.md` when the skills are installed into a consuming repository.

## Project Overview

Agent Skills for Context Engineering: an open collection of 16 Agent Skills teaching context engineering and harness engineering principles for production AI agent systems. Most skills are platform-agnostic (GitHub Copilot, Claude Code, Cursor, Google Antigravity IDE, any Open Plugins-conformant tool), with three Copilot-specific platform skills (`copilot-context-architecture`, `copilot-session-management`, `copilot-customization`).

Context engineering is the discipline of curating everything that enters a model's context window (system prompts, tool definitions, retrieved documents, message history, tool outputs) to maximize signal within limited attention budget.

## Repository Structure

- `skills/` — 16 skill directories, each containing a `SKILL.md` with YAML frontmatter (`name`, `description`) and optional `references/` and `scripts/` subdirectories
- `examples/` — 5 complete demonstration projects applying skills in practice
- `researcher/` — File-based research-to-skill operating system: rubrics, mechanism registry, claim provenance, corpus index, benchmarks, and validation scripts
- `template/SKILL.md` — Canonical skill template (use when creating new skills)
- `SKILL.md` (root) — Collection-level metadata and skill map
- `.plugin/plugin.json` — Open Plugins format manifest
- `bin/cli.js` — npx installer targeting `.github/skills/` (repo), `~/.copilot/skills` (global), or a custom path

## Build & Test Commands

No top-level build system. Repo-level gates and per-project tooling below.

### Top-level deterministic gates (run on every PR)

```bash
python3 researcher/scripts/validate_repo.py --strict
python3 researcher/scripts/skill_health.py --strict --no-history
python3 researcher/scripts/run_benchmarks.py
python3 researcher/scripts/check_activation_cases.py
```

### Example projects

#### examples/llm-as-judge-skills (TypeScript, Node >= 18)
```bash
cd examples/llm-as-judge-skills
npm install
npm run build        # tsc
npm test             # vitest
```

#### examples/code-generation-harness (Python >= 3.10)
```bash
cd examples/code-generation-harness
pip install -e ".[dev]"
pytest
```

## Skill Authoring Rules

When creating or modifying skills in `skills/`:

1. **Use the template**: Start from `template/SKILL.md`. Every skill must have YAML frontmatter with `name` and `description`.

2. **500-line budget**: Keep SKILL.md under 500 lines. Move detailed content to `references/` subdirectory.

3. **Ownership boundaries**: Every skill must state what it owns and what adjacent skills own. The `description` field and `When to Activate` section must include explicit "Do not activate" blocks.

4. **Third-person descriptions**: Write in third person. Descriptions are injected into system prompts — first-person creates inconsistencies.

5. **Token consciousness**: Challenge every paragraph: "Does this justify its token cost?" Prefer behavior-changing mechanisms over general background.

6. **Cross-references**: Use backtick-quoted skill names for cross-references: `context-fundamentals`, `tool-design`, etc.

7. **Claim system**: Use `claim-<skill-name>-<topic>` identifiers for volatile facts that may change. Track claims in `researcher/claims/index.jsonl`.

8. **Mechanism registry**: If a concept is reusable across skills, add it to `researcher/mechanisms/registry.jsonl`.

9. **Activation cases**: Add boundary test cases to `researcher/benchmarks/activation-cases.jsonl` for every new skill.

10. **Validation**: Run all four deterministic gates before committing changes.

## Copilot-Specific Conventions

- **Instruction layering**: Copilot merges instructions in priority order — personal → path-scoped `.github/instructions/*.instructions.md` (`applyTo` globs) → repo `.github/copilot-instructions.md` → `AGENTS.md` → org. Keep the repo-level file lean; this is the platform's native progressive disclosure.
- **Session hygiene (Copilot CLI)**: check `/context` at phase boundaries, run `/compact` proactively before new phases, audit `/session checkpoints` after auto-compaction, and write durable plans/decisions to workspace files so they survive compaction.
- **Volatile Copilot facts** (compaction thresholds, context-window caps, governance defaults) must use the claim system — they change between Copilot releases.

## Key Design Decisions

- **Platform agnosticism**: Never vendor-lock the 13 core skills. Abstract to principles that transfer across platforms. Copilot-specific knowledge lives only in the three platform skills.
- **Progressive disclosure**: Agents load only skill names initially; full content loads on activation.
- **Gotchas first**: Experience-derived failures are the highest-signal content in any skill.
- **Explicit boundaries**: Overlapping skills create confusion. Every skill must define its edges.
- **Deterministic gates**: Every PR must pass `validate_repo.py --strict` and `skill_health.py --strict`.
