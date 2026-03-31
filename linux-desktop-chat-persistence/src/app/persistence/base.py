"""SQLAlchemy Declarative Base für alle ORM-Tabellen."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Gemeinsame Basisklasse; Metadata für Alembic ``target_metadata``."""

    pass
