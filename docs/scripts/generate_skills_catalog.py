#!/usr/bin/env python3
"""Generate docs/skills/index.md from skills/*/SKILL.md frontmatter."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / "skills"
OUTPUT = REPO_ROOT / "docs" / "skills" / "index.md"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL | re.MULTILINE)

HEADER = """# Skills catalog

Auto-generated from `skills/*/SKILL.md` frontmatter. **Do not edit by hand** — run:

```bash
python docs/scripts/generate_skills_catalog.py
```

Each entry links to the skill in the repository. Full bodies load on activation (progressive disclosure).

| Skill | Description |
|-------|-------------|
"""


def parse_frontmatter(path: Path) -> tuple[str, str]:
    content = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(content)
    if not match:
        return path.parent.name, ""
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    name = meta.get("name", path.parent.name)
    description = meta.get("description", "")
    return name, description


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print(f"Skills directory not found: {SKILLS_DIR}", file=sys.stderr)
        return 1

    rows: list[tuple[str, str, str]] = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_dir.is_dir() or not skill_md.is_file():
            continue
        name, description = parse_frontmatter(skill_md)
        link = f"https://github.com/navendubrajesh/context-management-for-agents/blob/main/skills/{name}/SKILL.md"
        desc = description.replace("|", "\\|")
        rows.append((name, desc, link))

    lines = [HEADER]
    for name, desc, link in rows:
        lines.append(f"| [{name}]({link}) | {desc} |\n")
    lines.append(f"\n_Generated {len(rows)} skills._\n")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(rows)} skills)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
