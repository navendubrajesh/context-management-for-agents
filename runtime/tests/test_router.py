from __future__ import annotations

import json
from pathlib import Path

import pytest

from context_skills.paths import find_repo_root
from context_skills.router import load_router_index, route, score_skill_match


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return find_repo_root(Path(__file__))


@pytest.fixture(scope="session")
def activation_cases(repo_root: Path) -> list[dict]:
    cases_path = repo_root / "researcher" / "benchmarks" / "activation-cases.jsonl"
    cases: list[dict] = []
    with cases_path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases


@pytest.fixture(scope="session")
def router_index(repo_root: Path):
    return load_router_index(repo_root)


def test_route_handoff_query(repo_root: Path) -> None:
    results = route("How do I compress conversation history for a handoff?", top_k=3, repo_root=repo_root)
    assert results[0]["skill"] == "context-compression"
    assert results[0]["score"] > 0


def test_activation_cases_fixture(activation_cases: list[dict], router_index) -> None:
    assert len(activation_cases) == 29
    for case in activation_cases:
        query = case["query"]
        expected = case["expected_skill"]
        not_expected = case["not_skill"]
        expected_score = score_skill_match(query, router_index[expected])
        not_expected_score = score_skill_match(query, router_index[not_expected])
        assert expected_score > not_expected_score, case["id"]
        assert expected_score > 0, case["id"]
