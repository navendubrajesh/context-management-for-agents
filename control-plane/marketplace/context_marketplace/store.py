"""Marketplace registry with submit → approval → tenant install flow."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class MarketplaceEntry:
    id: str
    name: str
    version: str
    description: str
    publisher: str
    tenant_id: str
    status: str = "published"
    approval_id: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "publisher": self.publisher,
            "tenant_id": self.tenant_id,
            "status": self.status,
            "approval_id": self.approval_id,
            "created_at": self.created_at,
        }


class MarketplaceStore:
    def __init__(self) -> None:
        self._entries: dict[str, MarketplaceEntry] = {}
        self._tenant_catalog: dict[str, set[str]] = {}

    def search(self, query: str = "") -> list[dict[str, Any]]:
        q = query.lower().strip()
        rows = [e.to_dict() for e in self._entries.values() if e.status == "published"]
        if not q:
            return rows
        return [
            row
            for row in rows
            if q in row["name"].lower() or q in row["description"].lower()
        ]

    def submit(
        self,
        *,
        name: str,
        version: str,
        description: str,
        publisher: str,
        tenant_id: str,
        approval_id: str | None = None,
    ) -> MarketplaceEntry:
        entry_id = str(uuid.uuid4())
        entry = MarketplaceEntry(
            id=entry_id,
            name=name,
            version=version,
            description=description,
            publisher=publisher,
            tenant_id=tenant_id,
            status="pending" if approval_id else "published",
            approval_id=approval_id,
        )
        self._entries[entry_id] = entry
        return entry

    def approve(self, entry_id: str) -> MarketplaceEntry:
        entry = self._entries[entry_id]
        entry.status = "published"
        return entry

    def get(self, entry_id: str) -> MarketplaceEntry | None:
        return self._entries.get(entry_id)

    def find_by_approval(self, approval_id: str) -> MarketplaceEntry | None:
        for entry in self._entries.values():
            if entry.approval_id == approval_id:
                return entry
        return None

    def install(self, entry_id: str, tenant_id: str) -> dict[str, Any]:
        entry = self._entries[entry_id]
        if entry.status != "published":
            raise ValueError("Entry not published")
        catalog = self._tenant_catalog.setdefault(tenant_id, set())
        catalog.add(entry.name)
        return {"tenant_id": tenant_id, "skill": entry.name, "version": entry.version}

    def tenant_catalog(self, tenant_id: str) -> list[str]:
        return sorted(self._tenant_catalog.get(tenant_id, set()))


_STORE: MarketplaceStore | None = None


def get_marketplace_store() -> MarketplaceStore:
    global _STORE
    if _STORE is None:
        _STORE = MarketplaceStore()
    return _STORE
