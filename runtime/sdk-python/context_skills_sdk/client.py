"""Unified client for local (in-process) and remote (REST) skill access."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import httpx

from context_skills import get_reference as local_get_reference
from context_skills import get_skill as local_get_skill
from context_skills import list_skills as local_list_skills
from context_skills import route as local_route
from context_skills.primitives import (
    budget_context as local_budget_context,
)
from context_skills.primitives import (
    compact_session as local_compact_session,
)
from context_skills.primitives import (
    mask_observation as local_mask_observation,
)
from context_skills.primitives import (
    optimize_format as local_optimize_format,
)
from context_skills.primitives import (
    run_context_pipeline as local_run_context_pipeline,
)
from context_skills.primitives.budgeter import ContextComponent
from context_skills.primitives.service import run_primitive


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

    def _post_primitive(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}{path}",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def mask_observation(
        self,
        *,
        tool_name: str,
        content: str | dict[str, Any],
        query: str | None = None,
    ) -> dict[str, Any]:
        if self.base_url:
            return self._post_primitive(
                "/primitives/mask_observation",
                {"tool_name": tool_name, "content": content, "query": query},
            )
        result = run_primitive(
            local_mask_observation,
            tool_name=tool_name,
            content=content,
            query=query,
        )
        return {"output": result.output, "metrics": result.metrics.to_dict()}

    def compact_session(
        self,
        *,
        messages: list[dict[str, Any]] | None = None,
        text: str | None = None,
        mode: Literal["hierarchical", "handoff_summary", "selective_retention"] = "hierarchical",
    ) -> dict[str, Any]:
        if self.base_url:
            return self._post_primitive(
                "/primitives/compact_session",
                {"messages": messages, "text": text, "mode": mode},
            )
        result = run_primitive(
            local_compact_session,
            messages=messages,
            text=text,
            mode=mode,
        )
        return {"output": result.output, "metrics": result.metrics.to_dict()}

    def budget_context(
        self,
        *,
        components: list[dict[str, Any] | ContextComponent],
        token_budget: int,
    ) -> dict[str, Any]:
        if self.base_url:
            serialized = [
                item if isinstance(item, dict) else {
                    "name": item.name,
                    "content": item.content,
                    "priority": item.priority,
                }
                for item in components
            ]
            return self._post_primitive(
                "/primitives/budget_context",
                {"components": serialized, "token_budget": token_budget},
            )
        parsed = [
            item if isinstance(item, ContextComponent) else ContextComponent(**item)
            for item in components
        ]
        result = run_primitive(
            local_budget_context,
            components=parsed,
            token_budget=token_budget,
        )
        return {"output": result.output, "metrics": result.metrics.to_dict()}

    def optimize_format(
        self,
        *,
        content: str | dict[str, Any] | list[Any],
        kind: Literal["json", "text", "auto"] = "auto",
    ) -> dict[str, Any]:
        if self.base_url:
            return self._post_primitive(
                "/primitives/optimize_format",
                {"content": content, "kind": kind},
            )
        result = run_primitive(local_optimize_format, content=content, kind=kind)
        return {"output": result.output, "metrics": result.metrics.to_dict()}

    def run_context_pipeline(self, session: dict[str, Any]) -> dict[str, Any]:
        if self.base_url:
            return self._post_primitive(
                "/primitives/run_context_pipeline",
                {"session": session},
            )
        result = run_primitive(local_run_context_pipeline, session)
        return {"output": result.output, "metrics": result.metrics.to_dict()}

    def get_usage(self, limit: int = 50) -> dict[str, Any]:
        if not self.base_url:
            from context_skills.metering import get_usage_sink

            return {"records": get_usage_sink().recent(limit=limit)}
        response = httpx.get(f"{self.base_url}/usage", params={"limit": limit}, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
