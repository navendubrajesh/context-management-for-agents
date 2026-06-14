# Roadmap

Four-phase plan from skills collection to enterprise platform and ecosystem scale.

| Phase | Status | Goal |
|-------|--------|------|
| **0** | Done | Skills collection + validation OS |
| **1** | Done | MCP, REST, SDKs, Skill Router |
| **2** | Done | Context primitives, metering, telemetry |
| **3** | Done | Enterprise IAM, tenancy, policy, audit, deploy |
| **4** | Planned | Orchestrator adapters, eval-as-a-service, drift detection, marketplace |

## Phase 4 (not yet implemented)

- LangGraph / CrewAI / Temporal adapter packs
- Eval-as-a-service productization
- Automated claim/drift detection
- Governed public skill marketplace

Interfaces and hooks exist from Phase 3; implementations are deferred.

## Build runbook

Phases are designed as sequential Cursor prompts with:

- Checkpoint commits per workstream
- Four validation gates before every commit
- No skill content changes to make code pass

Internal runbook: maintain phase prompts and guardrails alongside this repo.

## Contributing to the roadmap

Open a [feature request](https://github.com/navendubrajesh/context-management-for-agents/issues/new?template=feature_request.md) describing the use case. Phase 4 items should explain which adapter or operator workflow they unblock.
