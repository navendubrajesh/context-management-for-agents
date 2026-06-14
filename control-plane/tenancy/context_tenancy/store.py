"""Tenant registry with per-tenant configuration."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from typing import Any


@dataclass
class TenantConfig:
    tenant_id: str
    name: str
    enabled_skills: list[str] = field(default_factory=list)
    llm_provider: str = "offline"
    pricing_tier: str = "default"
    region: str = "default"

    def allows_skill(self, skill_name: str) -> bool:
        if not self.enabled_skills:
            return True
        return skill_name in self.enabled_skills

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "name": self.name,
            "enabled_skills": list(self.enabled_skills),
            "llm_provider": self.llm_provider,
            "pricing_tier": self.pricing_tier,
            "region": self.region,
        }


class TenantStore:
    def __init__(self) -> None:
        self._tenants: dict[str, TenantConfig] = {}
        self._lock = Lock()
        self._seed_defaults()

    def _seed_defaults(self) -> None:
        self._tenants["default"] = TenantConfig(tenant_id="default", name="Default")
        self._tenants["tenant-a"] = TenantConfig(
            tenant_id="tenant-a",
            name="Tenant A",
            enabled_skills=["context-fundamentals", "context-compression", "evaluation"],
        )
        self._tenants["tenant-b"] = TenantConfig(
            tenant_id="tenant-b",
            name="Tenant B",
            enabled_skills=["tool-design", "memory-systems"],
            llm_provider="offline",
        )
        self._tenants["tenant-c"] = TenantConfig(
            tenant_id="tenant-c",
            name="Tenant C",
            enabled_skills=["advanced-evaluation", "evaluation"],
        )

    def load_from_file(self, path: Path | str) -> None:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        with self._lock:
            for item in data.get("tenants", []):
                cfg = TenantConfig(**item)
                self._tenants[cfg.tenant_id] = cfg

    def get(self, tenant_id: str) -> TenantConfig | None:
        with self._lock:
            return self._tenants.get(tenant_id)

    def require(self, tenant_id: str) -> TenantConfig:
        cfg = self.get(tenant_id)
        if cfg is None:
            raise KeyError(f"Unknown tenant: {tenant_id}")
        return cfg

    def list_tenants(self) -> list[TenantConfig]:
        with self._lock:
            return list(self._tenants.values())

    def upsert(self, config: TenantConfig) -> TenantConfig:
        with self._lock:
            self._tenants[config.tenant_id] = config
        return config

    def filter_skills(self, tenant_id: str, skills: list[dict[str, str]]) -> list[dict[str, str]]:
        cfg = self.get(tenant_id)
        if cfg is None or not cfg.enabled_skills:
            return skills
        allowed = set(cfg.enabled_skills)
        return [s for s in skills if s["name"] in allowed]


_GLOBAL_STORE = TenantStore()
_LOADED_FILE: str | None = None


def get_tenant_store() -> TenantStore:
    global _LOADED_FILE
    path = os.environ.get("CONTEXT_SKILLS_TENANTS_FILE")
    if path and Path(path).is_file() and path != _LOADED_FILE:
        _GLOBAL_STORE.load_from_file(path)
        _LOADED_FILE = path
    return _GLOBAL_STORE
