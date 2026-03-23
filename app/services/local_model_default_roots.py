"""
Registrierung projektüblicher Storage-Roots (ohne rechner-spezifische Sonderlogik).

``~/ai`` wird per Home-Expansion und Pfadnormalisierung angelegt, sofern noch nicht vorhanden.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.orm.models import ModelStorageRoot
from app.services.local_model_registry_service import (
    LocalModelRegistryError,
    LocalModelRegistryService,
    get_local_model_registry_service,
)

DEFAULT_USER_AI_ROOT_NAME = "user_ai"
DEFAULT_USER_AI_PATH = "~/ai"


def ensure_user_ai_default_root(
    session: Session, reg: Optional[LocalModelRegistryService] = None
) -> Optional[ModelStorageRoot]:
    """
    Legt einen Root für ``~/ai`` an (scan_enabled, read-only), falls weder Pfad noch Name belegt sind.

    Bei Konflikten (z. B. Name ``user_ai`` bereits mit anderem Pfad) wird nichts überschrieben.
    """
    reg = reg or get_local_model_registry_service()
    path_norm = reg.normalize_absolute_path(DEFAULT_USER_AI_PATH)
    row = session.scalars(select(ModelStorageRoot).where(ModelStorageRoot.path_absolute == path_norm)).first()
    if row:
        return row
    try:
        return reg.register_storage_root(
            session,
            name=DEFAULT_USER_AI_ROOT_NAME,
            path_absolute=DEFAULT_USER_AI_PATH,
            is_enabled=True,
            is_read_only=True,
            scan_enabled=True,
            notes="Phase D: Standard-Ort für lokale Modell-Artefakte (~/ai).",
        )
    except LocalModelRegistryError:
        return session.scalars(
            select(ModelStorageRoot).where(ModelStorageRoot.name == DEFAULT_USER_AI_ROOT_NAME)
        ).first()
