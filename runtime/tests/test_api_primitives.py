from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from context_skills.paths import find_repo_root


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return find_repo_root(Path(__file__))


@pytest.fixture(scope="session")
def client(repo_root: Path) -> TestClient:
    import app as api_app

    api_app.app.state.repo_root = str(repo_root)
    return TestClient(api_app.app)


def test_mask_observation_endpoint(client: TestClient) -> None:
    raw = json.loads(
        (
            find_repo_root()
            / "researcher/benchmarks/context-savings/test_fixtures/sample_tool_output.json"
        ).read_text()
    )
    response = client.post(
        "/primitives/mask_observation",
        json={"tool_name": "database_query", "content": raw},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["metrics"]["tokens_saved"] > 0
    assert payload["correlation_id"]
    assert "summarized" in payload["output"]


def test_usage_endpoint(client: TestClient) -> None:
    raw = json.loads(
        (
            find_repo_root()
            / "researcher/benchmarks/context-savings/test_fixtures/sample_tool_output.json"
        ).read_text()
    )
    client.post("/primitives/mask_observation", json={"tool_name": "database_query", "content": raw})
    usage = client.get("/usage?limit=5")
    assert usage.status_code == 200
    records = usage.json()["records"]
    assert records
    assert records[0]["operation"] == "mask_observation"
