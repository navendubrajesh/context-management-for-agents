---
name: copilot-context-architecture
description: Understand how GitHub Copilot assembles, budgets, and governs context — the client-side prompt wishlist, Jaccard snippet ranking, FIM prompts, server-side semantic RAG index, and enterprise privacy controls. Use when tuning Copilot context behavior, deciding what Copilot can and cannot see, diagnosing irrelevant completions, or making governance decisions about Copilot deployments. Do not activate for general context theory (context-fundamentals) or Copilot CLI session compaction (copilot-session-management).
---

# Copilot Context Architecture

GitHub Copilot's context system is a **two-tier pipeline**: a client-side "prompt crafter" in the IDE extension that assembles a token-budgeted Fill-in-the-Middle (FIM) prompt, and a cloud-side GitHub proxy (hosted in Azure) that performs RAG retrieval against a server-side semantic index, applies safety/IP filters, and routes to the model. Understanding this pipeline tells you exactly which levers exist for improving Copilot's context — and which internals are black boxes you should not build on.

## When to Activate

Activate this skill when:
- Diagnosing why Copilot inline completions are irrelevant or ignore nearby code
- Deciding how to structure a workspace so Copilot sees the right context (open tabs, file layout, instruction files)
- Configuring `#codebase` / semantic search, repository indexing, or knowledge bases
- Making enterprise governance decisions: content exclusions, training opt-outs, data residency, plan selection
- Evaluating Copilot's effective vs. advertised context window for a model

Do not activate this skill for adjacent work owned by other skills:
- Do not activate for platform-agnostic attention mechanics: `context-fundamentals`.
- Do not activate for Copilot CLI compaction, checkpoints, and `/context`: `copilot-session-management`.
- Do not activate for designing your own RAG pipelines: `memory-systems`.

## Core Concepts

### Client vs. cloud division of labor

Copilot runs as a language server (Node.js/TypeScript, JSON-RPC) embedded in the IDE. For **inline completions**, the extension collects context and constructs the prompt locally, then ships it through the GitHub proxy. For **Chat, agent, and `#codebase`** flows, the cloud service additionally performs semantic retrieval (RAG) and intent detection. The latency-critical work — scanning open tabs, scoring snippets, packing a token budget — is all client-side.

### What the extension scans

On each keystroke (after a ~75 ms debounce), Copilot extracts the **prefix** (code before cursor) and **suffix** (code after cursor), then scans:
- All open editor tabs ("neighboring tabs")
- Recently edited/accessed files (~20 most recent of the **same language**)
- Files in the same directory and the import graph

Practical lever: **what you have open in tabs directly shapes completions.** Opening the relevant interface, schema, or sibling implementation file is the single cheapest way to improve inline suggestion quality. Per GitHub's A/B testing, neighboring tabs raised suggestion acceptance ~5%, and a very low inclusion threshold proved optimal — "picking the best match we found and including that as context for the model was better than including nothing at all."

### Snippet ranking: Jaccard, not embeddings

The inline-completion relevance mechanism is the **Fixed Window Jaccard Matcher**:
1. Slice each candidate file into fixed-size sliding windows (default 60 lines).
2. Tokenize each window and the window around the cursor into sets.
3. Score Jaccard similarity: J(A,B) = |A ∩ B| / |A ∪ B|.
4. Keep the single best window per candidate file.

There is **no local neural embedding model** in the inline path — it's pure token-set overlap, chosen for speed (no index required). Implication: lexical similarity drives snippet selection. Consistent naming conventions across files materially improve which snippets get pulled in.

### The Prompt Wishlist and token budget

The prompt is a priority-ordered "wishlist" of typed elements — `BeforeCursor`, `AfterCursor`, `SimilarFile`, `ImportedFile`, `LanguageMarker`, `PathMarker` — fulfilled against a token budget (`getPrompt(...)` → `PromptWishlist.fulfill(tokenBudget)`). Elements are added by priority until budget exhausts; lower-priority elements get trimmed. The prefix carries the highest weight; the suffix gets ~15% of the budget by default (`suffixPercent`), enabling Fill-in-the-Middle.

FIM matters: when the suffix is non-empty, the model is invoked in insert mode (`<PRE> prefix <SUF> suffix <MID>`). A/B testing showed FIM gave a 10% relative boost in acceptance.

### Request gating: the contextual filter

Before any model call, the inline path computes a **contextual filter score** via a logistic-regression model over ~11 features (language, previous accept/reject, time since last accept/reject, last line length, character before cursor, etc.). Below threshold (~15%), no request is made. Two hard rules also block requests: prompts under 10 characters, and mid-line cursors not followed by whitespace/closing characters. If Copilot "isn't suggesting anything," this gate is a likely cause — not a context failure.

### Repository-level RAG

For `#codebase` and chat/agent flows, Copilot uses a genuine RAG system:
- **Custom contrastively-trained "Copilot embedding model"** (disclosed Sept 2025): 37.6% lift in retrieval quality, ~2x throughput, 8x smaller index. Trained with InfoNCE loss, Matryoshka Representation Learning, and hard-negative mining.
- **Hybrid index**: parts local, parts remote. GitHub-hosted repos get a server-side per-repo index built from the default branch, shared across everyone with repo access, never used for training. Instant indexing completes in seconds.
- **Agentic retrieval loop**: the agent selects tools (semantic search, grep, symbol lookup), reviews results, and iterates — not a single-shot retrieval.
- **Undisclosed internals**: ANN index type, embedding dimensionality, chunking algorithm, and reranker are all black boxes. Do not build architecture decisions on third-party guesses about them.

### Instruction layering

Retrieved and local context merges with instruction files in priority order:
personal instructions → path-scoped `.instructions.md` (via `applyTo` globs) → repo `.github/copilot-instructions.md` → `AGENTS.md` → org instructions.

This is the primary user-controlled context channel. Keep `copilot-instructions.md` short and high-signal (it is loaded into every request); push path-specific guidance into scoped `.instructions.md` files so it loads only when relevant — progressive disclosure applied to Copilot.

### Effective vs. advertised context windows

Copilot's routing layer (`max_prompt_tokens` / `capabilities.limits`) caps usable context **below provider maxima** — e.g., 128k enforced even when the model API reports 400k. A reserved-output buffer (~30–35%) is held back for generation, further reducing usable input. Plan context budgets against effective limits, not marketing numbers.

## Governance Essentials

- **Business/Enterprise plans contractually exclude prompts/suggestions from training** and do not retain IDE prompts. Individual (Free/Pro/Pro+) plans default interaction data **into** training unless opted out (as of April 24, 2026) — a personal account used on corporate code is the highest-exposure governance gap.
- **Content exclusions** (repo/org/enterprise glob rules + client-side `.copilotignore`) stop files from informing completions — but do not cover symlinks, remote filesystems, Copilot CLI, the cloud agent, or Agent mode. Treat them as defense-in-depth; keep real secrets in vaults.
- **Filters in the proxy**: duplication/public-code filter (blocks matches of ≥65 lexemes against public code), vulnerability filter (hardcoded credentials, SQL injection), pre-inference toxicity/jailbreak screening.
- **Enterprise tier** adds repo indexing/knowledge bases, EMU/SSO, FedRAMP, and (2026) EU/US data residency.

## Gotchas

- **Closed tabs are invisible to inline completions.** Copilot ranks only open/recent same-language files. If a critical definition lives in a closed file of a different language, it will not appear in the prompt.
- **Jaccard is lexical.** Renaming-heavy refactors or inconsistent vocabulary across files defeats snippet matching even when the code is semantically related.
- **The contextual filter suppresses requests silently.** Short prompts (<10 chars) and mid-line cursors produce no completion at all — this is gating, not model failure.
- **Content exclusions leak via IDE semantics.** Type info, hover definitions, and build config from excluded files can still indirectly inform suggestions.
- **Remote indexing requires GitHub.com or GHE Cloud** — not Enterprise Server. Non-GitHub workspaces fall back to a local index that is policy-gated off by default for orgs.
- **Effective context ≠ advertised context.** Budget against the routing-layer cap minus the reserved-output buffer.

## Integration

- `context-fundamentals` provides the attention-budget theory that explains *why* Copilot's wishlist prioritization works.
- `copilot-session-management` covers the CLI-side context lifecycle (compaction, checkpoints).
- `tool-design` informs custom MCP server design for Copilot agent mode.
- `memory-systems` covers building external RAG layers when you need auditable retrieval Copilot's opaque index cannot provide.

## References

- `references/copilot-internals.md` — Full pipeline breakdown: prompt element types, captured prompt structure, embedding model training details, index lifecycle, privacy/retention tables, and the data-flow diagram.
- `claim-copilot-context-architecture-internals`: Granular mechanics (Jaccard windowing, wishlist types, filter weights) derive from reverse engineering of the v1.57 (June 2022) extension and may be version-specific.
- `claim-copilot-context-architecture-limits`: Context-window figures and routing caps change rapidly; verify against current Copilot documentation.
