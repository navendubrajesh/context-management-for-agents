# Copilot Internals Reference

Deep-dive companion to `copilot-context-architecture`. Sources: GitHub engineering blog posts (2023–2025), the Copilot Trust Center, GitHub Docs, and reverse engineering of the Copilot extension (v1.57, June 2022; newer agent builds 2025–2026). Reverse-engineered details may be version-specific.

## 1. Prompt Element Types

Six typed elements compete for the token budget, each with a priority and insertion order:

| Element | Content | Notes |
|---------|---------|-------|
| `BeforeCursor` | Code before the cursor (prefix) | Highest weight; gets ~85% of budget |
| `AfterCursor` | Code after the cursor (suffix) | ~15% via `suffixPercent`; enables FIM |
| `SimilarFile` | Best Jaccard-scored window from a neighboring tab | One window per candidate file |
| `ImportedFile` | Content reachable via the import graph | |
| `LanguageMarker` | Language identifier comment | |
| `PathMarker` | `# Path: <file>` comment | Anchors the model to file identity |

Captured prompt object (real example):

```json
{
  "prefix": "# Path: codeviz\\app.py\n# Compare this snippet from codeviz\\predictions.py:\n...",
  "suffix": "if __name__ == '__main__':\r\n    app.run(debug=True)",
  "isFimEnabled": true,
  "promptElementRanges": [
    {"kind": "PathMarker"}, {"kind": "SimilarFile"}, {"kind": "BeforeCursor"}
  ]
}
```

## 2. Jaccard Matching Details

- Defined in `neighbor-snippet-selector.getNeighbourSnippets`.
- Default "Eager mode": 60-line fixed sliding windows.
- An "Indentation-based Jaccard Matcher" exists in code but appears unused.
- AST/sibling-function extraction (`SiblingOption`) hardcoded to `NoSiblings` in the analyzed version.
- Top-K window selection exists but defaults to top-1 per file.
- Windowing mode is governed by an A/B experimentation framework.

## 3. Contextual Filter

Logistic regression over ~11 features, weights shipped inside the extension:
- Language one-hot encoding
- Whether the previous suggestion was accepted/rejected
- Time since last accept/reject
- Last line length; last character before cursor
- Threshold default ~15% — below it, no model request is made

Hard suppression rules: prompt under 10 characters; mid-line cursor unless followed by whitespace/closing characters. (A 2024 academic study reverse-engineered the exact weights from the v1.57 build.)

## 4. FIM and the Custom Completion Model

FIM training format: `<PRE> ∘ Enc(prefix) ∘ <SUF> ∘ Enc(suffix) ∘ <MID> ∘ Enc(middle)`.

GitHub's custom completion model is synthetically fine-tuned as a strong FIM engine (accurate inserts, no prefix duplication, no suffix trampling). Reported results: "20% more accepted and retained characters, 12% higher acceptance rate, 3x higher token-per-second throughput, and a 35% reduction in latency."

Latency engineering: target ~500 ms before next keystroke; aggressive result caching; suffix caching across calls; 1–3 inline candidates vs. ~10 in the panel.

## 5. Embedding Model & Semantic Index

**Copilot embedding model** (GitHub blog, Sept 24, 2025):
- 37.6% lift in retrieval quality; ~2x throughput; 8x smaller index
- Average benchmark score 0.362 → 0.498; code-acceptance +110.7% (C#), +113.1% (Java)
- Training: contrastive learning with InfoNCE loss, Matryoshka Representation Learning (truncatable embedding sizes), hard-negative mining from public GitHub + internal repos with LLM-surfaced near-misses
- **Undisclosed**: base architecture, parameter count, embedding dimensionality

**Index lifecycle:**
- Hybrid: "parts of the index might be stored on your machine and parts might come from remote sources"
- GitHub-hosted repos: server-side per-repo index from the default branch, shared across all users with repo access, never used for training
- Instant indexing (GA March 2025): first index in seconds (up to 60s), down from ~5 minutes
- Remote indexing supports GitHub.com and GHE Cloud — **not** Enterprise Server
- Non-GitHub workspaces: local VS Code index, off by default for org/enterprise (policy-gated)

**Chunking** (not officially documented): the open-source `vscode-copilot-chat` extension contains a tree-sitter parser and `workspaceChunkSearch` module, implying AST-aware chunking. Third-party claims of ~100–250-token chunks, SQLite caching by content hash, and a TF-IDF "NaiveChunker" fallback are unverified.

**Distinct from Blackbird**: GitHub's Rust keyword/regex code-search engine (trigram index, sharded by blob OID, ~640 qps, ~53B+ files) is complementary to, not part of, the embedding store.

## 6. Context Window Limits by Generation

| Era | Window |
|-----|--------|
| Codex / cushman-ml | ~2,048 tokens (~150 LOC) |
| GPT-4o Chat (Dec 2024) | 64k standard, 128k Insiders |
| 2026 model picker | GPT-4.1/GPT-5/GPT-4o ~128k; o3-mini / Claude Sonnet 3.7 ~200k; Claude Sonnet 4.5 200k (1M beta); Gemini ~1M; agent default 128k (192k option) |

Routing layer (`max_prompt_tokens` / `capabilities.limits`) enforces caps below provider maxima (e.g., 128k enforced when the API reports 400k; Claude Opus 4.6 observed at 144k). Reserved-output buffer ~30–35%.

## 7. Privacy & Governance Tables

**Data retention (Business/Enterprise):**

| Surface | Retention |
|---------|-----------|
| IDE Chat/Completions/CLI prompts | Not retained (abuse investigations excepted) |
| Outside-IDE surfaces (CLI, agent workflows) | ~28 days |
| User engagement data | 2 years |
| Model training | Never (contractual; extends to Anthropic/Google as providers) |

**Individual plans (from April 24, 2026):** interaction data used for training **by default** unless opted out (account-wide setting; no per-repo control). The plan travels with the account, not the repo.

**Filters:**
- Duplication filter: blocks suggestions matching ≥65 lexemes (~150 chars) of public code; "Allow with reference" mode shows matching repos + licenses; does not apply to the coding agent
- Vulnerability filter: real-time blocking of hardcoded credentials, SQL injection, path injection
- Content exclusions: `fnmatch` glob rules at repo/org/enterprise level; gaps — symlinks, remote filesystems, CLI, cloud agent, Agent mode; semantic leakage via IDE type info/hover remains possible

**Plans:** Business $19/user/mo (policies, audit logs, exclusions, IP indemnity, no-training). Enterprise $39/user/mo + GHE Cloud (repo indexing, knowledge bases, EMU/SSO, FedRAMP Moderate, data residency US/EU with ~10% AI-credit surcharge).

## 8. Data-Flow Summary

```
Keystroke → debounce (~75ms) → extract prefix/suffix
  → scan open tabs / recent files / imports
  → Jaccard rank 60-line windows → select best snippet/file
  → build Prompt Wishlist (priority-ordered elements)
  → fulfill(tokenBudget): prefix (≈85%) + suffix (≈15%) + markers
  → contextual filter score ≥ 15%?  ──no──> suppress (no model call)
        │ yes
        ▼
  [Chat/agent only] cloud RAG: embed query → semantic index
        (server+local) → retrieve chunks → inject into prompt
        ▼
  Azure GitHub proxy: pre-inference filters (toxicity, jailbreak)
        ▼
  Model (GPT-4o/GPT-5.x/Claude/Gemini) — FIM completion
        ▼
  proxy post-filters: duplication (≥65 lexemes), vulnerability scan
        ▼
  ghost text in editor (1–3 inline; ~10 panel)
```

## 9. Architectural Recommendations

1. Baseline regulated enterprises on Business; upgrade to Enterprise for repo-level RAG, knowledge bases, EMU, or data residency.
2. Enable content exclusions and the public-code filter enterprise-wide on day one — as defense-in-depth, not an airtight boundary.
3. Block personal Copilot accounts on corporate code (the April 2026 training default is the highest-exposure gap).
4. Right-size context for cost: prefer Tab completions for micro-tasks, scope chats narrowly, start fresh sessions on task switches, disable unused MCP servers.
5. Treat undisclosed internals (ANN type, dimensions, reranker) as black boxes; build an external RAG layer if you need auditable retrieval.
