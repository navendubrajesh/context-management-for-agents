"""SQLAlchemy models for tenants, audit events, and approvals."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TenantRow(Base):
    __tablename__ = "tenants"

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    enabled_skills_json: Mapped[str] = mapped_column(Text, default="[]")
    llm_provider: Mapped[str] = mapped_column(String(64), default="offline")
    pricing_tier: Mapped[str] = mapped_column(String(64), default="default")
    region: Mapped[str] = mapped_column(String(64), default="default")

    def skills(self) -> list[str]:
        return json.loads(self.enabled_skills_json or "[]")

    @staticmethod
    def skills_to_json(skills: list[str]) -> str:
        return json.dumps(skills)


class AuditEventRow(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    timestamp: Mapped[str] = mapped_column(String(64))
    event_type: Mapped[str] = mapped_column(String(128))
    actor: Mapped[str] = mapped_column(String(256))
    tenant_id: Mapped[str] = mapped_column(String(128), index=True)
    correlation_id: Mapped[str] = mapped_column(String(128))
    detail_json: Mapped[str] = mapped_column(Text, default="{}")
    prev_hash: Mapped[str] = mapped_column(String(64))
    event_hash: Mapped[str] = mapped_column(String(64))

    def detail(self) -> dict[str, Any]:
        return json.loads(self.detail_json or "{}")


class ApprovalRow(Base):
    __tablename__ = "approval_requests"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    operation: Mapped[str] = mapped_column(String(128))
    tenant_id: Mapped[str] = mapped_column(String(128), index=True)
    actor: Mapped[str] = mapped_column(String(256))
    status: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[str] = mapped_column(String(64))
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    decided_by: Mapped[str | None] = mapped_column(String(256), nullable=True)
    decided_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    def payload(self) -> dict[str, Any]:
        return json.loads(self.payload_json or "{}")
