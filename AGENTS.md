# AGENTS.md

This file provides guidance to AI coding agents (GitHub Copilot, Cursor, Amazon Kiro, Google Antigravity, Amazon Q Developer, and other AGENTS.md-conformant tools) when working with code in this repository.

## Project Overview

**Context Management for Agents**: an open collection of **28 Agent Skills** teaching context engineering and harness engineering for production AI agent systems. **13 skills are platform-agnostic**; **15 platform skills** cover five agentic coding tools (3 skills each for Copilot, Cursor, Kiro, Antigravity, and Amazon Q Developer).

Context engineering is the discipline of curating everything that enters a model's context window (system prompts, tool definitions, retrieved documents, message history, tool outputs) to maximize signal within limited attention budget.

## Repository Structure

- `skills/` — 28 skill directories, each with `SKILL.md` (YAML frontmatter: `name`, `description`) and optional `references/`
- `examples/` — 5 demonstration projects
- `researcher/` — File-based research OS: rubrics, mechanism registry, claim provenance, corpus index, benchmarks, validation scripts
- `template/SKILL.md` — Canonical skill template
- `SKILL.md` (root) — Collection-level skill map
- `.plugin/plugin.json` — Open Plugins manifest
- `bin/cli.js` — Multi-platform installer (`--platform copilot|cursor|kiro|antigravity|amazonq`)

## Build & Test Commands

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
cd examples/llm-as-judge-skills && npm install && npm run build && npm test
```

#### examples/code-generation-harness (Python >= 3.10)
```bash
cd examples/code-generation-harness && pip install -e ".[dev]" && pytest
```

## Skill Authoring Rules

1. **Use the template**: Start from `template/SKILL.md`. YAML frontmatter must have `name` + `description`.
2. **500-line budget**: Keep SKILL.md under 500 lines; move depth to `references/`.
3. **Ownership boundaries**: "When to Activate" + explicit "Do not activate" blocks routing to sibling skills.
4. **Third-person descriptions**: Injected into system prompts — no first/second person.
5. **Token consciousness**: Every paragraph must change agent behavior.
6. **Cross-references**: Backtick-quoted skill names: `context-fundamentals`, `tool-design`.
7. **Claim system**: Volatile facts use `claim-<skill>-<topic>` in `researcher/claims/index.jsonl`.
8. **Mechanism registry**: Reusable concepts in `researcher/mechanisms/registry.jsonl`.
9. **Activation cases**: Add boundary tests to `researcher/benchmarks/activation-cases.jsonl` for every new skill.
10. **Validation**: Run all four gates before committing. Update `EXPECTED_SKILLS` in all scripts when adding/removing skills.

## Platform Conventions

### GitHub Copilot
- Install: `npx context-management-for-agents --platform copilot` → `.github/skills/` + `.github/copilot-instructions.md`
- Layering: personal → path-scoped `.instructions.md` (`applyTo`) → repo `copilot-instructions.md` → `AGENTS.md` → org
- Session: `/context`, `/compact`, `/session checkpoints` in Copilot CLI

### Cursor
- Install: `--platform cursor` → `.cursor/skills/` + `.cursor/rules/*.mdc` index
- Rules: `.cursor/rules/*.mdc` with `description`, `globs`, `alwaysApply`; nested `AGENTS.md` supported
- Session: context ring monitoring, `/compress` in CLI, automatic conversation summarization

### Amazon Kiro
- Install: `--platform kiro` → `.kiro/skills/` + `.kiro/steering/` index
- Steering: `.kiro/steering/` with `inclusion: always|fileMatch|manual|auto`; specs as durable context
- Session: requirements/design/tasks artifacts — not CLI compaction

### Google Antigravity
- Install: `--platform antigravity` → `.agents/skills/` + root `AGENTS.md` index
- Context: AGENTS.md, Knowledge Items, Artifacts, `.agents/skills/`; Editor vs Manager surfaces
- Session: Artifact review cycles, KI hygiene, Manager Surface handoffs

### Amazon Q Developer
- Install: `--platform amazonq` → `.amazonq/skills/` + `.amazonq/rules/` index
- Rules: `.amazonq/rules/**/*.md`; CLI `/context show`, custom agents
- Session: `/compact`, ~80% auto-nudge, `/clear`; monitor rule token cost

## Key Design Decisions

- **Platform agnosticism**: Never vendor-lock the 13 core skills. Platform knowledge lives only in platform-prefixed skills.
- **Progressive disclosure**: Agents load skill names/descriptions first; full SKILL.md on activation.
- **Gotchas first**: Experience-derived failures are highest-signal content.
- **Explicit boundaries**: Every skill defines its edges against siblings.
- **Deterministic gates**: Every PR must pass all four validation scripts.
