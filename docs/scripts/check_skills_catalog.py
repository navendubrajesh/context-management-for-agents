#!/usr/bin/env python3
"""Fail if docs skills catalog is missing skills or out of date."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG = REPO_ROOT / "docs" / "skills" / "index.md"
GENERATOR = REPO_ROOT / "docs" / "scripts" / "generate_skills_catalog.py"
CORE_DIR = REPO_ROOT / "runtime" / "core"
sys.path.insert(0, str(CORE_DIR))

from context_skills.constants import EXPECTED_SKILLS  # noqa: E402


def catalog_skill_names(text: str) -> set[str]:
    names: set[str] = set()
    for line in text.splitlines():
        match = re.match(r"\| \[([^\]]+)\]", line)
        if match:
            names.add(match.group(1))
    return names


def main() -> int:
    if not CATALOG.is_file():
        print(f"Missing catalog: {CATALOG}. Run generate_skills_catalog.py", file=sys.stderr)
        return 1

    before = CATALOG.read_text(encoding="utf-8")
    proc = subprocess.run([sys.executable, str(GENERATOR)], cwd=str(REPO_ROOT), check=False)
    if proc.returncode != 0:
        return proc.returncode

    after = CATALOG.read_text(encoding="utf-8")
    if before != after:
        print("Skills catalog is stale. Commit regenerated docs/skills/index.md", file=sys.stderr)
        return 1

    in_catalog = catalog_skill_names(after)
    expected = set(EXPECTED_SKILLS)
    missing = expected - in_catalog
    extra = in_catalog - expected
    if missing:
        print(f"Catalog missing skills: {sorted(missing)}", file=sys.stderr)
        return 1
    if extra:
        print(f"Catalog has unexpected skills: {sorted(extra)}", file=sys.stderr)
        return 1

    print(f"[+] Skills catalog OK ({len(expected)} skills)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
