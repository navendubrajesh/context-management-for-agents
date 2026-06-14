"""SCIM 2.0 user/group provisioning (in-memory store for Phase 3)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from threading import Lock
from typing import Any


@dataclass
class ScimUser:
    id: str
    user_name: str
    display_name: str
    active: bool = True
    roles: list[str] = field(default_factory=lambda: ["viewer"])
    tenant_id: str = "default"

    def to_scim(self) -> dict[str, Any]:
        return {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
            "id": self.id,
            "userName": self.user_name,
            "displayName": self.display_name,
            "active": self.active,
            "roles": self.roles,
            "tenantId": self.tenant_id,
        }


@dataclass
class ScimGroup:
    id: str
    display_name: str
    members: list[str] = field(default_factory=list)
    tenant_id: str = "default"

    def to_scim(self) -> dict[str, Any]:
        return {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
            "id": self.id,
            "displayName": self.display_name,
            "members": [{"value": m} for m in self.members],
            "tenantId": self.tenant_id,
        }


class ScimStore:
    def __init__(self) -> None:
        self._users: dict[str, ScimUser] = {}
        self._groups: dict[str, ScimGroup] = {}
        self._lock = Lock()

    def list_users(self) -> list[ScimUser]:
        with self._lock:
            return list(self._users.values())

    def create_user(self, payload: dict[str, Any]) -> ScimUser:
        user = ScimUser(
            id=str(uuid.uuid4()),
            user_name=str(payload.get("userName", "")),
            display_name=str(payload.get("displayName", payload.get("userName", ""))),
            active=bool(payload.get("active", True)),
            roles=list(payload.get("roles") or ["viewer"]),
            tenant_id=str(payload.get("tenantId", "default")),
        )
        with self._lock:
            self._users[user.id] = user
        return user

    def list_groups(self) -> list[ScimGroup]:
        with self._lock:
            return list(self._groups.values())

    def create_group(self, payload: dict[str, Any]) -> ScimGroup:
        members = [m.get("value", m) if isinstance(m, dict) else str(m) for m in payload.get("members", [])]
        group = ScimGroup(
            id=str(uuid.uuid4()),
            display_name=str(payload.get("displayName", "")),
            members=members,
            tenant_id=str(payload.get("tenantId", "default")),
        )
        with self._lock:
            self._groups[group.id] = group
        return group

    def clear(self) -> None:
        with self._lock:
            self._users.clear()
            self._groups.clear()


_GLOBAL_SCIM = ScimStore()


def get_scim_store() -> ScimStore:
    return _GLOBAL_SCIM
