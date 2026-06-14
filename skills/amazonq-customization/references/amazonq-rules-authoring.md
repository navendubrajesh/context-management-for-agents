# Amazon Q Rules Authoring Reference

Sources: [AWS — Creating project rules](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/context-project-rules.html), [AWS DevOps Blog — Q rules](https://aws.amazon.com/blogs/devops/mastering-amazon-q-developer-with-rules/).

## Minimal rule example

```markdown
# Python Type Hints

All public functions and methods must include type hints for parameters and return values.
Use `from __future__ import annotations` in modules with forward references.
Private helpers (_prefix) may omit return hints if obvious.
```

## Recommended directory layout

```
.amazonq/
  rules/
    00-project-conventions.md
    backend/python.md
    frontend/typescript.md
  cli-agents/          # verify current schema in AWS docs
    reviewer.json
AmazonQ.md             # optional scaffold (CLI glob)
README.md              # often auto-included in CLI context
```

## CLI agent resources pattern

Custom agents reference context files:
```json
{
  "resources": [
    "file://.amazonq/rules/00-project-conventions.md"
  ]
}
```

Verify field names against current Q CLI agent schema — format evolves between releases.

## Priority and organization tips

- Split by domain, not by file size alone
- Keep each rule file under a few hundred lines
- Run `/context show` after adding rules to verify token impact
- Use subdirectories for teams maintaining separate rule sets
