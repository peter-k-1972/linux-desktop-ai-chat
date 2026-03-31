"""
Persistenzschicht: SQLAlchemy ORM, Session-Factory, gemeinsame DB-URL mit chat_history.db.

Roh-SQL über ``DatabaseManager`` bleibt für Legacy-Tabellen bestehen; neue Domänen
(Model-Usage, Quotas, lokale Artefakte) liegen ausschließlich über dieses Paket.
"""

from app.persistence.base import Base
from app.persistence.session import (
    get_database_url,
    get_engine,
    get_session_factory,
    session_scope,
)

__all__ = [
    "Base",
    "get_database_url",
    "get_engine",
    "get_session_factory",
    "session_scope",
]
