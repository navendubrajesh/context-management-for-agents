from __future__ import annotations

from pathlib import Path

import pytest

from context_skills.paths import find_repo_root
from context_skills_sdk import SkillsClient


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return find_repo_root(Path(__file__))


def test_local_sdk_route(repo_root: Path) -> None:
    client = SkillsClient(repo_root=repo_root)
    assert client.mode == "local"
    results = client.route("How do I compress conversation history for a handoff?", top_k=1)
    assert results[0]["skill"] == "context-compression"
