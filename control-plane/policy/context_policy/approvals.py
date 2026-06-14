"""Human-in-the-loop approval workflow."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Literal

ApprovalStatus = Literal["pending", "approved", "rejected"]


@dataclass
class ApprovalRequest:
    id: str
    operation: str
    tenant_id: str
    actor: str
    status: ApprovalStatus
    created_at: str
    payload: dict[str, Any] = field(default_factory=dict)
    decided_by: str | None = None
    decided_at: str | None = None
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "operation": self.operation,
            "tenant_id": self.tenant_id,
            "actor": self.actor,
            "status": self.status,
            "created_at": self.created_at,
            "payload": self.payload,
            "decided_by": self.decided_by,
            "decided_at": self.decided_at,
            "reason": self.reason,
        }


class ApprovalStore:
    def __init__(self) -> None:
        self._items: dict[str, ApprovalRequest] = {}
        self._lock = Lock()

    def create(self, operation: str, tenant_id: str, actor: str, payload: dict[str, Any] | None = None) -> ApprovalRequest:
        req = ApprovalRequest(
            id=str(uuid.uuid4()),
            operation=operation,
            tenant_id=tenant_id,
            actor=actor,
            status="pending",
            created_at=datetime.now(timezone.utc).isoformat(),
            payload=payload or {},
        )
        with self._lock:
            self._items[req.id] = req
        return req

    def list_pending(self, tenant_id: str | None = None) -> list[ApprovalRequest]:
        with self._lock:
            items = list(self._items.values())
        if tenant_id:
            items = [i for i in items if i.tenant_id == tenant_id]
        return [i for i in items if i.status == "pending"]

    def decide(self, approval_id: str, *, approver: str, approve: bool, reason: str = "") -> ApprovalRequest:
        with self._lock:
            req = self._items.get(approval_id)
            if req is None:
                raise KeyError(f"Unknown approval: {approval_id}")
            if req.status != "pending":
                raise ValueError(f"Approval already {req.status}")
            req.status = "approved" if approve else "rejected"
            req.decided_by = approver
            req.decided_at = datetime.now(timezone.utc).isoformat()
            req.reason = reason or None
            return req

    def get(self, approval_id: str) -> ApprovalRequest | None:
        with self._lock:
            return self._items.get(approval_id)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()


_GLOBAL = ApprovalStore()


def get_approval_store() -> ApprovalStore:
    return _GLOBAL
