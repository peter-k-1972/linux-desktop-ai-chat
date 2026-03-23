"""
Engine und Session-Factory.

Standard-URL: sqlite:///chat_history.db (Projektroot), konsistent mit ``DatabaseManager``.
Override: Umgebungsvariable ``LINUX_DESKTOP_CHAT_DATABASE_URL``.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Iterator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

_default_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker[Session]] = None


def get_database_url() -> str:
    env = (os.environ.get("LINUX_DESKTOP_CHAT_DATABASE_URL") or "").strip()
    if env:
        return env
    root = Path(__file__).resolve().parents[2]
    db_path = root / "chat_history.db"
    return f"sqlite:///{db_path}"


def get_engine(*, echo: bool = False) -> Engine:
    global _default_engine
    if _default_engine is None:
        _default_engine = create_engine(
            get_database_url(),
            echo=echo,
            future=True,
            connect_args={"check_same_thread": False} if get_database_url().startswith("sqlite") else {},
        )
    return _default_engine


def reset_engine() -> None:
    """Tests: Engine zurücksetzen."""
    global _default_engine, _session_factory
    if _default_engine is not None:
        _default_engine.dispose()
    _default_engine = None
    _session_factory = None


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            future=True,
        )
    return _session_factory


@contextmanager
def session_scope() -> Iterator[Session]:
    fac = get_session_factory()
    session = fac()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
