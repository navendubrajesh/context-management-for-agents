"""Generate CycloneDX SBOM for runtime and control-plane packages."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _discover_python_packages(root: Path) -> list[dict[str, Any]]:
    """Collect installable Python packages from pyproject.toml files."""
    components: list[dict[str, Any]] = []
    seen: set[str] = set()

    for pyproject in sorted(root.rglob("pyproject.toml")):
        if ".egg-info" in str(pyproject) or "node_modules" in str(pyproject):
            continue
        text = pyproject.read_text(encoding="utf-8")
        name_match = re.search(r'name\s*=\s*"([^"]+)"', text)
        version_match = re.search(r'version\s*=\s*"([^"]+)"', text)
        if not name_match:
            continue
        name = name_match.group(1)
        if name in seen:
            continue
        seen.add(name)
        version = version_match.group(1) if version_match else "0.0.0"
        rel = pyproject.parent.relative_to(root).as_posix()
        components.append(
            {
                "type": "library",
                "name": name,
                "version": version,
                "purl": f"pkg:pypi/{name}@{version}",
                "properties": [{"name": "source-path", "value": rel}],
            }
        )
    return components


def _discover_runtime_modules(root: Path) -> list[dict[str, Any]]:
    """Add top-level runtime/control-plane modules not declared as separate packages."""
    extras: list[dict[str, Any]] = []
    for label, rel in (
        ("context-skills-runtime", "runtime"),
        ("context-skills-mcp", "runtime/mcp"),
        ("context-skills-api", "runtime/api"),
        ("context-skills-sdk-python", "runtime/sdk-python"),
        ("context-skills-sdk-ts", "runtime/sdk-ts"),
        ("context-iam", "control-plane/iam"),
        ("context-tenancy", "control-plane/tenancy"),
        ("context-policy", "control-plane/policy"),
        ("context-audit", "control-plane/audit"),
        ("context-finops", "control-plane/finops"),
    ):
        path = root / rel
        if path.is_dir():
            extras.append(
                {
                    "type": "application",
                    "name": label,
                    "version": "3.0.0",
                    "properties": [{"name": "source-path", "value": rel}],
                }
            )
    return extras


def generate_sbom(root: Path | None = None) -> dict[str, Any]:
    root = root or _repo_root()
    components = _discover_python_packages(root) + _discover_runtime_modules(root)
    # De-duplicate by name
    unique: dict[str, dict[str, Any]] = {}
    for component in components:
        unique[component["name"]] = component
    ordered = [unique[key] for key in sorted(unique.keys())]

    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "component": {
                "type": "application",
                "name": "context-skills-platform",
                "version": "3.0.0",
            },
            "tools": [{"name": "context-skills-sbom-generator", "version": "1.0.0"}],
        },
        "components": ordered,
    }


def write_sbom(out_path: Path, root: Path | None = None, strict: bool = False) -> int:
    sbom = generate_sbom(root)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(sbom, indent=2) + "\n", encoding="utf-8")
    count = len(sbom["components"])
    print(f"SBOM written to {out_path} ({count} components)")
    if strict and count == 0:
        print("ERROR: strict mode requires at least one SBOM component", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Generate CycloneDX SBOM")
    parser.add_argument(
        "--out",
        default=str(_repo_root() / "security" / "sbom" / "runtime.cdx.json"),
        help="Output path for CycloneDX JSON",
    )
    parser.add_argument("--strict", action="store_true", help="Fail when no components found")
    args = parser.parse_args()
    return write_sbom(Path(args.out), strict=args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
