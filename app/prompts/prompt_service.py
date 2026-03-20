"""
Prompt-Service – Geschäftslogik für die Promptverwaltung.
Unterstützt Datenbank- und Verzeichnis-Backend.
"""

from typing import List, Optional

from app.prompts.prompt_models import Prompt

_prompt_service: Optional["PromptService"] = None


def get_prompt_service() -> "PromptService":
    """Liefert den globalen PromptService (Singleton)."""
    global _prompt_service
    if _prompt_service is None:
        try:
            from app.services.infrastructure import get_infrastructure
            db_path = get_infrastructure().database.db_path
        except Exception:
            db_path = "chat_history.db"
        _prompt_service = PromptService(db_path=db_path)
    return _prompt_service


def set_prompt_service(service: Optional["PromptService"]) -> None:
    """Setzt den PromptService (für Tests)."""
    global _prompt_service
    _prompt_service = service
from app.prompts.storage_backend import (
    PromptStorageBackend,
    DatabasePromptStorage,
    DirectoryPromptStorage,
)


def create_storage_backend(
    storage_type: str = "database",
    db_path: str = "chat_history.db",
    directory: str = "",
) -> PromptStorageBackend:
    """Erstellt das passende Storage-Backend."""
    if storage_type == "directory" and directory:
        return DirectoryPromptStorage(directory)
    return DatabasePromptStorage(db_path)


class PromptService:
    """Service-Schicht für Prompt-CRUD und Validierung."""

    def __init__(
        self,
        backend: Optional[PromptStorageBackend] = None,
        db_path: str = "chat_history.db",
        storage_type: str = "database",
        directory: str = "",
    ):
        if backend is not None:
            self._backend = backend
        else:
            self._backend = create_storage_backend(storage_type, db_path, directory)

    def set_backend(self, backend: PromptStorageBackend) -> None:
        """Wechselt das Storage-Backend (z.B. nach Einstellungsänderung)."""
        self._backend = backend

    def refresh_backend(
        self,
        storage_type: str = "database",
        db_path: str = "chat_history.db",
        directory: str = "",
    ) -> None:
        """Aktualisiert das Backend (z.B. nach Einstellungsänderung)."""
        self._backend = create_storage_backend(storage_type, db_path, directory)

    def create(self, prompt: Prompt) -> Optional[Prompt]:
        """Erstellt einen neuen Prompt und eine erste Version."""
        if not (prompt.title or "").strip():
            return None
        try:
            pid = self._backend.create(prompt)
            created = self._backend.get(pid)
            if created and hasattr(self._backend, "create_version"):
                self._backend.create_version(pid, created.title, created.content or "")
            return created
        except Exception:
            return None

    def update(self, prompt: Prompt) -> bool:
        """Aktualisiert einen Prompt."""
        if prompt.id is None or not (prompt.title or "").strip():
            return False
        try:
            return self._backend.update(prompt)
        except Exception:
            return False

    def save_version(self, prompt: Prompt, title: str, content: str) -> Optional[Prompt]:
        """
        Speichert eine neue Version und aktualisiert den Prompt.
        Jeder Aufruf erstellt einen neuen Versionseintrag.
        """
        if prompt.id is None or not (title or "").strip():
            return None
        try:
            self._backend.create_version(prompt.id, title, content)
            updated = Prompt(
                id=prompt.id,
                title=title,
                category=prompt.category,
                description=prompt.description,
                content=content,
                tags=getattr(prompt, "tags", []) or [],
                prompt_type=getattr(prompt, "prompt_type", "user"),
                scope=getattr(prompt, "scope", "global"),
                project_id=getattr(prompt, "project_id", None),
                created_at=prompt.created_at,
                updated_at=None,
            )
            if self._backend.update(updated):
                return self._backend.get(prompt.id)
        except Exception:
            pass
        return None

    def count_versions(self, prompt_id: int) -> int:
        """Anzahl Versionen eines Prompts."""
        try:
            if hasattr(self._backend, "count_versions"):
                return self._backend.count_versions(prompt_id)
        except Exception:
            pass
        return 0

    def list_versions(self, prompt_id: int) -> List[dict]:
        """Listet alle Versionen eines Prompts."""
        try:
            if hasattr(self._backend, "list_versions"):
                return self._backend.list_versions(prompt_id)
        except Exception:
            pass
        return []

    def delete(self, prompt_id: int) -> bool:
        """Löscht einen Prompt."""
        try:
            return self._backend.delete(prompt_id)
        except Exception:
            return False

    def get(self, prompt_id: int) -> Optional[Prompt]:
        """Lädt einen Prompt."""
        try:
            return self._backend.get(prompt_id)
        except Exception:
            return None

    def list_all(
        self,
        filter_text: str = "",
        category: Optional[str] = None,
        project_id: Optional[int] = None,
        include_global: bool = True,
    ) -> List[Prompt]:
        """Listet Prompts. project_id: Filter; include_global: globale mit anzeigen."""
        try:
            return self._backend.list_all(filter_text, category, project_id, include_global)
        except TypeError:
            return self._backend.list_all(filter_text, category)
        except Exception:
            return []

    def list_for_project(self, project_id: int) -> List[Prompt]:
        """Listet Prompts eines Projekts (inkl. globale)."""
        try:
            if hasattr(self._backend, "list_for_project"):
                return self._backend.list_for_project(project_id)
            return self.list_all(project_id=project_id, include_global=True)
        except Exception:
            return []

    def list_project_prompts(self, project_id: int, filter_text: str = "") -> List[Prompt]:
        """Listet nur projektbezogene Prompts."""
        try:
            if hasattr(self._backend, "list_project_prompts"):
                return self._backend.list_project_prompts(project_id, filter_text)
            prompts = self.list_all(project_id=project_id, include_global=False)
            if filter_text:
                search = filter_text.lower()
                prompts = [
                    p
                    for p in prompts
                    if search in (p.title or "").lower()
                    or search in (p.description or "").lower()
                    or search in (p.content or "").lower()
                ]
            return prompts
        except Exception:
            return []

    def list_global_prompts(self, filter_text: str = "") -> List[Prompt]:
        """Listet nur globale Prompts."""
        try:
            if hasattr(self._backend, "list_global_prompts"):
                return self._backend.list_global_prompts(filter_text)
            prompts = self.list_all(project_id=None, include_global=True)
            prompts = [p for p in prompts if getattr(p, "project_id", None) is None]
            if filter_text:
                search = filter_text.lower()
                prompts = [
                    p
                    for p in prompts
                    if search in (p.title or "").lower()
                    or search in (p.description or "").lower()
                    or search in (p.content or "").lower()
                ]
            return prompts
        except Exception:
            return []

    def list_templates(
        self,
        project_id: Optional[int] = None,
        filter_text: str = "",
    ) -> List[Prompt]:
        """Listet Templates (prompt_type=template). Projekt + globale."""
        try:
            prompts = self.list_all(
                filter_text=filter_text,
                project_id=project_id,
                include_global=True,
            )
            return [p for p in prompts if getattr(p, "prompt_type", "user") == "template"]
        except Exception:
            return []

    def duplicate(self, prompt: Prompt) -> Optional[Prompt]:
        """Erstellt eine Kopie eines Prompts."""
        if prompt.id is None:
            return None
        copy = Prompt(
            id=None,
            title=f"Kopie von {prompt.title}",
            category=prompt.category,
            description=prompt.description,
            content=prompt.content,
            tags=list(prompt.tags),
            prompt_type=prompt.prompt_type,
            scope=getattr(prompt, "scope", "global"),
            project_id=getattr(prompt, "project_id", None),
            created_at=None,
            updated_at=None,
        )
        return self.create(copy)
