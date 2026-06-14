from __future__ import annotations

from pathlib import Path

import httpx
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


def test_healthz(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_skills_index(client: TestClient) -> None:
    response = client.get("/skills")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 28
    assert set(payload[0].keys()) == {"name", "description"}


def test_route_endpoint(client: TestClient) -> None:
    response = client.post(
        "/route",
        json={"task": "How do I compress conversation history for a handoff?", "top_k": 3},
    )
    assert response.status_code == 200
    results = response.json()["results"]
    assert results[0]["skill"] == "context-compression"


def test_httpx_route(client: TestClient) -> None:
    import asyncio

    async def _request() -> None:
        transport = httpx.ASGITransport(app=client.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
            response = await http_client.post(
                "/route",
                json={"task": "How do I prevent lost-in-middle failures?", "top_k": 2},
            )
            assert response.status_code == 200
            assert response.json()["results"]

    asyncio.run(_request())
