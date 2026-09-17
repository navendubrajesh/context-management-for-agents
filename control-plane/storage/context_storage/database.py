"""Database engine — Postgres when DATABASE_URL set, otherwise disabled (in-memory stores)."""

from __future__ import annotations

import os
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from context_storage.models import Base

_ENGINE: Engine | None = None
_SESSION_FACTORY: sessionmaker[Session] | None = None


def database_url() -> str | None:
    return os.environ.get("CONTEXT_SKILLS_DATABASE_URL") or os.environ.get("DATABASE_URL")


def is_database_enabled() -> bool:
    return bool(database_url())


@lru_cache(maxsize=1)
def get_engine() -> Engine | None:
    url = database_url()
    if not url:
        return None
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(url, future=True, connect_args=connect_args)


def get_session_factory() -> sessionmaker[Session] | None:
    global _SESSION_FACTORY
    engine = get_engine()
    if engine is None:
        return None
    if _SESSION_FACTORY is None:
        _SESSION_FACTORY = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return _SESSION_FACTORY


def init_database() -> None:
    engine = get_engine()
    if engine is None:
        return
    Base.metadata.create_all(engine)
