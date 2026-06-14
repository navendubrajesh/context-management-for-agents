# Good first issues (stubs)

Copy any item below into a new GitHub issue, or use as a starting branch name.

---

## 1. Add platform activation case

**Labels:** `good first issue`, `researcher`

Add one activation case to `researcher/data/activation_cases.json` for a platform skill (Cursor, Kiro, etc.) with expected routing winner/loser. Run `check_activation_cases.py` to verify.

**Acceptance:** Gate passes; case documents a realistic user query.

---

## 2. Improve docs quickstart for Windows

**Labels:** `good first issue`, `documentation`

Update `docs/quickstart.md` with PowerShell equivalents for install/demo commands and note path separators for MCP `cwd`.

**Acceptance:** `mkdocs build --strict` passes.

---

## 3. Extend demo with REST one-liner script

**Labels:** `good first issue`, `runtime`

Add `examples/demo/run_rest_demo.py` that starts nothing (assumes API running) and curls `/route` + one primitive via `httpx`, printing token metrics.

**Acceptance:** Works offline against local API; documented in `examples/demo/README.md`.
