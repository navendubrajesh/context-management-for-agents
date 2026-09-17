"""SQL repositories backing control-plane stores when DATABASE_URL is configured."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select

from context_storage.database import get_session_factory, init_database
from context_storage.models import ApprovalRow, AuditEventRow, TenantRow


class TenantRepository:
    def __init__(self) -> None:
        init_database()
        self._factory = get_session_factory()
        if self._factory is None:
            raise RuntimeError("Database not configured")

    def upsert(self, tenant_id: str, name: str, enabled_skills: list[str], **kwargs: Any) -> None:
        with self._factory() as session:
            row = session.get(TenantRow, tenant_id)
            if row is None:
                row = TenantRow(tenant_id=tenant_id, name=name)
                session.add(row)
            row.name = name
            row.enabled_skills_json = TenantRow.skills_to_json(enabled_skills)
            row.llm_provider = kwargs.get("llm_provider", row.llm_provider or "offline")
            row.pricing_tier = kwargs.get("pricing_tier", row.pricing_tier or "default")
            row.region = kwargs.get("region", row.region or "default")
            session.commit()

    def get(self, tenant_id: str) -> dict[str, Any] | None:
        with self._factory() as session:
            row = session.get(TenantRow, tenant_id)
            if row is None:
                return None
            return {
                "tenant_id": row.tenant_id,
                "name": row.name,
                "enabled_skills": row.skills(),
                "llm_provider": row.llm_provider,
                "pricing_tier": row.pricing_tier,
                "region": row.region,
            }

    def list_all(self) -> list[dict[str, Any]]:
        with self._factory() as session:
            rows = session.scalars(select(TenantRow)).all()
            return [
                {
                    "tenant_id": row.tenant_id,
                    "name": row.name,
                    "enabled_skills": row.skills(),
                    "llm_provider": row.llm_provider,
                    "pricing_tier": row.pricing_tier,
                    "region": row.region,
                }
                for row in rows
            ]


class AuditRepository:
    def __init__(self) -> None:
        init_database()
        self._factory = get_session_factory()
        if self._factory is None:
            raise RuntimeError("Database not configured")

    def append(self, event: dict[str, Any]) -> None:
        with self._factory() as session:
            session.add(
                AuditEventRow(
                    id=event["id"],
                    timestamp=event["timestamp"],
                    event_type=event["event_type"],
                    actor=event["actor"],
                    tenant_id=event["tenant_id"],
                    correlation_id=event["correlation_id"],
                    detail_json=json.dumps(event.get("detail", {})),
                    prev_hash=event["prev_hash"],
                    event_hash=event["event_hash"],
                )
            )
            session.commit()

    def list_events(self, tenant_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        with self._factory() as session:
            stmt = select(AuditEventRow).order_by(AuditEventRow.timestamp.desc()).limit(limit)
            rows = session.scalars(stmt).all()
            if tenant_id:
                rows = [row for row in rows if row.tenant_id == tenant_id]
            return [
                {
                    "id": row.id,
                    "timestamp": row.timestamp,
                    "event_type": row.event_type,
                    "actor": row.actor,
                    "tenant_id": row.tenant_id,
                    "correlation_id": row.correlation_id,
                    "detail": row.detail(),
                    "prev_hash": row.prev_hash,
                    "event_hash": row.event_hash,
                }
                for row in rows
            ]


class ApprovalRepository:
    def __init__(self) -> None:
        init_database()
        self._factory = get_session_factory()
        if self._factory is None:
            raise RuntimeError("Database not configured")

    def save(self, item: dict[str, Any]) -> None:
        with self._factory() as session:
            row = session.get(ApprovalRow, item["id"])
            if row is None:
                row = ApprovalRow(id=item["id"], operation=item["operation"], tenant_id=item["tenant_id"],
                                  actor=item["actor"], status=item["status"], created_at=item["created_at"])
                session.add(row)
            row.operation = item["operation"]
            row.tenant_id = item["tenant_id"]
            row.actor = item["actor"]
            row.status = item["status"]
            row.created_at = item["created_at"]
            row.payload_json = json.dumps(item.get("payload", {}))
            row.decided_by = item.get("decided_by")
            row.decided_at = item.get("decided_at")
            row.reason = item.get("reason")
            session.commit()

    def get(self, approval_id: str) -> dict[str, Any] | None:
        with self._factory() as session:
            row = session.get(ApprovalRow, approval_id)
            if row is None:
                return None
            return {
                "id": row.id,
                "operation": row.operation,
                "tenant_id": row.tenant_id,
                "actor": row.actor,
                "status": row.status,
                "created_at": row.created_at,
                "payload": row.payload(),
                "decided_by": row.decided_by,
                "decided_at": row.decided_at,
                "reason": row.reason,
            }

    def list_pending(self, tenant_id: str | None = None) -> list[dict[str, Any]]:
        with self._factory() as session:
            rows = session.scalars(select(ApprovalRow).where(ApprovalRow.status == "pending")).all()
            if tenant_id:
                rows = [row for row in rows if row.tenant_id == tenant_id]
            return [
                {
                    "id": row.id,
                    "operation": row.operation,
                    "tenant_id": row.tenant_id,
                    "actor": row.actor,
                    "status": row.status,
                    "created_at": row.created_at,
                    "payload": row.payload(),
                    "decided_by": row.decided_by,
                    "decided_at": row.decided_at,
                    "reason": row.reason,
                }
                for row in rows
            ]
