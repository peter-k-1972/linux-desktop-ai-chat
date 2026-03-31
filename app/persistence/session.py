"""
Engine und Session-Factory.

Standard-URL: sqlite:///…/chat_history.db (Monorepo-Root mit Anker ``pyproject.toml``),
konsistent mit ``DatabaseManager``.
Override: Umgebungsvariable ``LINUX_DESKTOP_CHAT_DATABASE_URL``.

Siehe ``docs/architecture/ADR_PERSISTENCE_DB_ROOT_RESOLUTION.md``.
"""

from __future__ import annotations

import os
import re
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Iterator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

_ANCHOR_PROJECT_NAME = "linux-desktop-chat"
_MAX_REPO_ROOT_WALK = 64

_default_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker[Session]] = None


class DatabaseUrlResolutionError(RuntimeError):
    """Kein Monorepo-Anker gefunden und keine URL per Umgebung gesetzt."""

    pass


def _read_project_name_from_pyproject_bytes(raw: bytes) -> Optional[str]:
    """Liest [project].name defensiv; bei Fehlern None."""
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    try:
        import tomllib
    except ImportError:
        return _read_project_name_from_pyproject_text_fallback(text)
    try:
        data = tomllib.loads(text)
    except Exception:
        return None
    project = data.get("project")
    if not isinstance(project, dict):
        return None
    name = project.get("name")
    return name if isinstance(name, str) else None


def _read_project_name_from_pyproject_text_fallback(text: str) -> Optional[str]:
    """Minimaler Parser für [project].name (Python <3.11 ohne tomllib)."""
    in_project = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "[project]":
            in_project = True
            continue
        if not in_project:
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            inner = stripped[1:-1].strip()
            if inner == "project" or inner.startswith("project."):
                continue
            break
        if not stripped or stripped.startswith("#"):
            continue
        m = re.match(r'^name\s*=\s*"([^"\\]*)"', stripped)
        if m:
            return m.group(1)
        m = re.match(r"^name\s*=\s*'([^'\\]*)'", stripped)
        if m:
            return m.group(1)
    return None


def _find_monorepo_root(start_dir: Path) -> Optional[Path]:
    """
    Sucht aufwärts nach einem Verzeichnis mit pyproject.toml und
    [project].name == ANCHOR_PROJECT_NAME.
    """
    current = start_dir.resolve()
    for _ in range(_MAX_REPO_ROOT_WALK):
        candidate = current / "pyproject.toml"
        if candidate.is_file():
            try:
                raw = candidate.read_bytes()
            except OSError:
                raw = b""
            if raw:
                name = _read_project_name_from_pyproject_bytes(raw)
                if name == _ANCHOR_PROJECT_NAME:
                    return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def get_database_url() -> str:
    env = (os.environ.get("LINUX_DESKTOP_CHAT_DATABASE_URL") or "").strip()
    if env:
        return env
    root = _find_monorepo_root(Path(__file__).resolve().parent)
    if root is None:
        raise DatabaseUrlResolutionError(
            "Konnte Monorepo-Root für die Default-SQLite-URL nicht ermitteln "
            "(kein passendes pyproject.toml mit [project].name = "
            f'"{_ANCHOR_PROJECT_NAME}" gefunden). '
            "Bitte LINUX_DESKTOP_CHAT_DATABASE_URL setzen."
        )
    db_path = (root / "chat_history.db").resolve()
    return f"sqlite:///{db_path.as_posix()}"


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
