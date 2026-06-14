# Context Skills Core

Shared Python library for loading Agent Skills from the repository `skills/` tree, validating runtime manifests, and routing tasks with a deterministic lexical scorer.

## Install

```bash
pip install -e runtime/core
```

## API

```python
from context_skills import list_skills, get_skill, get_reference, route

# Progressive disclosure
index = list_skills()          # name + description only
full = get_skill("context-compression")
ref = get_reference("context-compression", "references/compression-strategies.md")

# Routing
matches = route("How do I compress conversation history for a handoff?", top_k=3)
```

## Manifest schema

Each skill can be materialized as a JSON manifest validated by `runtime/core/skill-manifest.schema.json`. The researcher gate `validate_repo.py` runs this check on every PR.
