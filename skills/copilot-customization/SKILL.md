---
name: copilot-customization
description: Author the files that steer GitHub Copilot — repository copilot-instructions.md, path-scoped .instructions.md with applyTo globs, prompt files, AGENTS.md, and MCP server configuration. Use when writing or restructuring Copilot customization files, when instructions are being ignored, or when instruction bloat degrades responses. Do not activate for how Copilot internally assembles context (copilot-context-architecture) or general system-prompt theory (context-fundamentals).
---

# Copilot Customization

GitHub Copilot exposes a layered, file-based steering surface. These files are the only context channel the user fully controls — everything else (tab scanning, snippet ranking, retrieval) is automatic. This skill covers authoring them well: which layer to use for what, how to budget their token cost, and the failure modes that make Copilot ignore or misapply instructions.

## When to Activate

Activate this skill when:
- Creating or restructuring `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, or `AGENTS.md`
- Copilot ignores stated conventions, or applies rules from one part of the codebase to another
- Responses degrade after instructions grow ("instruction bloat")
- Building reusable prompt files for recurring tasks
- Configuring MCP servers for Copilot agent mode and deciding which to enable

Do not activate this skill for adjacent work owned by other skills:
- Do not activate for Copilot's internal prompt assembly, retrieval, or governance: `copilot-context-architecture`.
- Do not activate for CLI session compaction and checkpoints: `copilot-session-management`.
- Do not activate for platform-agnostic instruction-design theory: `context-fundamentals`.
- Do not activate for designing MCP tool schemas themselves: `tool-design`.

## Core Concepts

### The instruction layer stack

Copilot merges instruction sources in priority order:

1. **Personal instructions** (user-level, follow the user everywhere)
2. **Path-scoped instructions** — `.github/instructions/<name>.instructions.md` with an `applyTo` glob in YAML frontmatter; loaded only when the working file matches
3. **Repository instructions** — `.github/copilot-instructions.md`; loaded into every Copilot request in the repo
4. **`AGENTS.md`** — read by the Copilot coding agent and other AGENTS.md-conformant agent products
5. **Organization instructions** (Enterprise; apply to all org seats)

The architectural rule: **put content at the narrowest layer that still covers its audience.** Repo-wide invariants (build commands, naming conventions, "never edit generated files") go in `copilot-instructions.md`. Anything language-, directory-, or framework-specific goes in a path-scoped file so it costs zero tokens when irrelevant. This is progressive disclosure implemented with Copilot's native machinery.

### Token budgeting the always-on layer

`copilot-instructions.md` is injected into **every** chat/agent request — its token cost is paid on every interaction, competing with code context for the model's attention. Practical budget: keep it under ~50 lines of dense, behavior-changing content. Each line should pass the test: "would Copilot do something wrong without this?" Background prose, project history, and aspirational style guides fail that test; move them out or delete them.

### Path-scoped instructions (`applyTo`)

```markdown
---
applyTo: "src/api/**/*.ts"
---
All API handlers must validate input with zod schemas from src/schemas.
Return errors via the ApiError class — never throw raw exceptions.
```

Rules:
- Globs match against workspace-relative paths. `**` patterns are supported (`fnmatch`-style).
- Multiple files can match simultaneously; all matching layers merge. Avoid contradictions between layers — Copilot resolves conflicts unpredictably (see Gotchas).
- Scope files by *concern*, not by size: one file per framework/domain (`api.instructions.md`, `tests.instructions.md`), not a grab-bag.

### Prompt files

Prompt files (reusable task prompts, e.g. `.github/prompts/*.prompt.md` in VS Code) capture recurring multi-step tasks — "generate a migration," "write release notes" — as invokable templates. Treat them as the Copilot analog of skills: a name, a description, and a body that loads only on invocation. Keep variables explicit (placeholders the user fills) rather than relying on Copilot inferring intent from a terse prompt.

### AGENTS.md for the coding agent

The Copilot coding agent (cloud, asynchronous) reads `AGENTS.md` at the repo root. Content priorities differ from IDE instructions: the agent has no human in the loop mid-task, so emphasize **verification** — how to build, how to run tests, what "done" means, what it must never touch. A coding agent with build/test commands in `AGENTS.md` self-corrects; one without ships untested diffs.

### MCP servers

Agent mode loads tool definitions from every enabled MCP server into the context of each request. Tool schemas are token-expensive (JSON Schema inflates ~5x over compact representations — see `tool-design`). Enable only the servers the current work needs; an unused MCP server is pure context tax and a distraction risk for tool selection.

### Co-installation with workflow skill packs

If the team uses GStack or similar workflow harnesses alongside context engineering skills, namespace installs: context skills under `.github/skills/context-engineering/` (this collection's installer). Keep workflow skills in their own directory. Reference both in `copilot-instructions.md` with clear ownership — workflow for ship/QA, context for compression/masking — but do not paste full skill bodies into instructions.

## Authoring Playbook

1. **Start from failures, not aspirations.** Add an instruction only after observing Copilot do the wrong thing without it. Speculative instructions accumulate into bloat that buries the rules that matter.
2. **State rules as behavior, not philosophy.** "Use `Result<T, E>` returns in src/core; never throw" beats "We value robust error handling."
3. **One concern per path-scoped file**, named for the concern. Review the set quarterly; delete rules the codebase now enforces by other means (linters, types).
4. **Mirror critical invariants into `AGENTS.md`** if the coding agent is used — it does not read VS Code-specific layers the same way, and a rule that only exists in a chat mode is invisible to it.
5. **Test instructions empirically.** Ask Copilot to do the thing the instruction governs, in a matching and a non-matching file. Verify the rule fires where intended and stays silent elsewhere.
6. **Version instructions like code.** They steer every AI-generated diff in the repo; review changes to them with the same rigor as CI config.

## Gotchas

- **Always-on cost is invisible.** Nothing warns you that a 400-line `copilot-instructions.md` is consuming budget on every request and pushing actual code out of context. Audit length whenever response quality drops repo-wide.
- **Conflicting layers resolve unpredictably.** When a personal instruction says "verbose comments" and the repo file says "minimal comments," the outcome is not a documented precedence at the content level — the model sees both. Keep layers complementary, not overlapping.
- **`applyTo` matches the file being worked on, not files being read.** A rule scoped to `src/api/**` does not fire when Copilot edits a test that *calls* the API. Put cross-cutting rules one layer up.
- **Instructions are context, not constraints.** Copilot can still violate them under pressure from conflicting code patterns in context — high-signal phrasing ("never X; instead Y") outperforms soft guidance, but no instruction is a guarantee. Enforce hard invariants with linters and CI, not prose.
- **Instruction files don't reach inline completions the same way.** The instruction stack primarily steers chat/agent modes; ghost-text completions are driven by the prefix/suffix and neighboring tabs (see `copilot-context-architecture`). Don't expect a style rule in `copilot-instructions.md` to reshape tab completions.
- **Excluded files can't be referenced by instructions.** If content exclusions block a path, instructions pointing Copilot at it produce nothing — the policy wins.

## Integration

- `copilot-context-architecture` explains where each instruction layer enters the prompt and what else competes for the budget.
- `copilot-session-management` covers keeping long agent sessions coherent once instructions are in place.
- `context-fundamentals` provides the attention-budget reasoning behind the "narrowest layer" rule.
- `tool-design` owns the design of MCP tool schemas this skill decides to enable.
- `filesystem-context` covers workspace files as dynamic context, complementing static instruction files.

## References

- `claim-copilot-customization-layers`: The instruction layer set and merge order (personal → path-scoped → repo → AGENTS.md → org) follows GitHub's 2025–2026 documentation and may change as Copilot's customization surface evolves.
