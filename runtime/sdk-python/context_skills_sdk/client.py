"""Unified client for local (in-process) and remote (REST) skill access."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from context_skills import get_reference as local_get_reference
from context_skills import get_skill as local_get_skill
from context_skills import list_skills as local_list_skills
from context_skills import route as local_route


class SkillsClient:
    """Thin wrapper over context-skills-core (local) or the REST API (remote)."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        repo_root: Path | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/") if base_url else None
        self.repo_root = repo_root
        self.timeout = timeout

    @property
    def mode(self) -> str:
        return "remote" if self.base_url else "local"

    def list_skills(self) -> list[dict[str, str]]:
        if self.base_url:
            response = httpx.get(f"{self.base_url}/skills", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        return local_list_skills(self.repo_root)

    def get_skill(self, name: str) -> dict[str, Any]:
        if self.base_url:
            response = httpx.get(f"{self.base_url}/skills/{name}", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        return local_get_skill(name, self.repo_root)

    def route(self, task: str, top_k: int = 5) -> list[dict[str, Any]]:
        if self.base_url:
            response = httpx.post(
                f"{self.base_url}/route",
                json={"task": task, "top_k": top_k},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            return payload["results"]
        return local_route(task, top_k, self.repo_root)

    def get_reference(self, name: str, path: str) -> str:
        if self.base_url:
            response = httpx.get(
                f"{self.base_url}/skills/{name}/references/{path}",
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()["content"]
        return local_get_reference(name, path, self.repo_root)
