"""
Prompt-Speicher-Backends – Abstraktion für Datenbank und Verzeichnis.
"""

import json
import os
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from app.prompts.prompt_models import Prompt
from app.utils.datetime_utils import parse_datetime, to_iso_datetime


def _slugify(text: str) -> str:
    """Erzeugt einen sicheren Dateinamen aus dem Titel."""
    text = text.strip() or "untitled"
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "_", text)
    return text[:80] or "untitled"


class PromptStorageBackend(ABC):
    """Abstrakte Basis für Prompt-Speicherung."""

    @abstractmethod
    def create(self, prompt: Prompt) -> int:
        """Erstellt einen neuen Prompt. Gibt die ID zurück."""
        pass

    @abstractmethod
    def update(self, prompt: Prompt) -> bool:
        """Aktualisiert einen bestehenden Prompt."""
        pass

    @abstractmethod
    def delete(self, prompt_id: int) -> bool:
        """Löscht einen Prompt."""
        pass

    @abstractmethod
    def get(self, prompt_id: int) -> Optional[Prompt]:
        """Lädt einen Prompt nach ID."""
        pass

    @abstractmethod
    def list_all(
        self,
        filter_text: str = "",
        category: Optional[str] = None,
        project_id: Optional[int] = None,
        include_global: bool = True,
    ) -> List[Prompt]:
        """Listet Prompts, optional gefiltert."""
        pass

    def create_version(self, prompt_id: int, title: str, content: str) -> int:
        """Erstellt einen Versionseintrag. Default: nicht unterstützt (0)."""
        return 0

    def count_versions(self, prompt_id: int) -> int:
        """Anzahl Versionen. Default: 0."""
        return 0

    def list_versions(self, prompt_id: int) -> List[dict]:
        """Listet Versionen. Default: leere Liste."""
        return []


class DatabasePromptStorage(PromptStorageBackend):
    """SQLite-basierte Speicherung (Standard)."""

    def __init__(self, db_path: str = "chat_history.db"):
        from app.prompts.prompt_repository import PromptRepository
        self._repo = PromptRepository(db_path)

    def create(self, prompt: Prompt) -> int:
        return self._repo.create(prompt)

    def update(self, prompt: Prompt) -> bool:
        return self._repo.update(prompt)

    def delete(self, prompt_id: int) -> bool:
        return self._repo.delete(prompt_id)

    def get(self, prompt_id: int) -> Optional[Prompt]:
        return self._repo.get(prompt_id)

    def list_all(
        self,
        filter_text: str = "",
        category: Optional[str] = None,
        project_id: Optional[int] = None,
        include_global: bool = True,
    ) -> List[Prompt]:
        prompts = self._repo.list_all(filter_text, project_id, include_global)
        if category:
            prompts = [p for p in prompts if p.category == category]
        return prompts

    def list_for_project(self, project_id: int) -> List[Prompt]:
        return self._repo.list_for_project(project_id)

    def list_project_prompts(self, project_id: int, filter_text: str = "") -> List[Prompt]:
        return self._repo.list_project_prompts(project_id, filter_text)

    def list_global_prompts(self, filter_text: str = "") -> List[Prompt]:
        return self._repo.list_global_prompts(filter_text)

    def create_version(self, prompt_id: int, title: str, content: str) -> int:
        return self._repo.create_version(prompt_id, title, content)

    def count_versions(self, prompt_id: int) -> int:
        return self._repo.count_versions(prompt_id)

    def list_versions(self, prompt_id: int) -> List[dict]:
        return self._repo.list_versions(prompt_id)


class DirectoryPromptStorage(PromptStorageBackend):
    """Verzeichnis-basierte Speicherung (JSON-Dateien)."""

    COUNTER_FILE = ".prompt_counter"
    FILE_PATTERN = "*.json"

    def __init__(self, directory: str):
        self.directory = Path(directory)

    def _ensure_directory(self) -> None:
        """Stellt sicher, dass das Verzeichnis existiert und beschreibbar ist."""
        if not self.directory.exists():
            self.directory.mkdir(parents=True, exist_ok=True)
        if not self.directory.is_dir():
            raise ValueError(f"Pfad ist kein Verzeichnis: {self.directory}")
        if not os.access(self.directory, os.W_OK):
            raise PermissionError(f"Verzeichnis nicht beschreibbar: {self.directory}")

    def _counter_path(self) -> Path:
        return self.directory / self.COUNTER_FILE

    def _next_id(self) -> int:
        """Liefert die nächste ID und erhöht den Zähler."""
        self._ensure_directory()
        path = self._counter_path()
        try:
            current = int(path.read_text().strip())
        except (FileNotFoundError, ValueError):
            current = 0
        next_id = current + 1
        path.write_text(str(next_id))
        return next_id

    def _prompt_path(self, prompt_id: int) -> Path:
        """Pfad zur Datei eines Prompts (ohne Prüfung ob existiert)."""
        return self.directory / f"{prompt_id:05d}.json"

    def _find_path_by_id(self, prompt_id: int) -> Optional[Path]:
        """Findet die Datei für eine ID."""
        path = self._prompt_path(prompt_id)
        if path.exists():
            return path
        for p in self.directory.glob(self.FILE_PATTERN):
            if p.name == self.COUNTER_FILE:
                continue
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if data.get("id") == prompt_id:
                    return p
            except (json.JSONDecodeError, KeyError):
                continue
        return None

    def _prompt_to_dict(self, prompt: Prompt, prompt_id: int) -> dict:
        now = to_iso_datetime(datetime.now(timezone.utc)) or ""
        return {
            "id": prompt_id,
            "title": prompt.title,
            "category": prompt.category,
            "description": prompt.description,
            "content": prompt.content,
            "tags": prompt.tags,
            "prompt_type": prompt.prompt_type,
            "scope": getattr(prompt, "scope", "global"),
            "project_id": getattr(prompt, "project_id", None),
            "created_at": now,
            "updated_at": now,
        }

    def _dict_to_prompt(self, d: dict) -> Prompt:
        tags = d.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        return Prompt(
            id=d.get("id"),
            title=d.get("title", ""),
            category=d.get("category", "general"),
            description=d.get("description", ""),
            content=d.get("content", ""),
            tags=tags,
            prompt_type=d.get("prompt_type", "user"),
            scope=d.get("scope", "global"),
            project_id=d.get("project_id"),
            created_at=parse_datetime(d.get("created_at")),
            updated_at=parse_datetime(d.get("updated_at")),
        )

    def create(self, prompt: Prompt) -> int:
        self._ensure_directory()
        prompt_id = self._next_id()
        path = self._prompt_path(prompt_id)
        data = self._prompt_to_dict(prompt, prompt_id)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return prompt_id

    def update(self, prompt: Prompt) -> bool:
        if prompt.id is None:
            return False
        path = self._find_path_by_id(prompt.id)
        if not path:
            return False
        self._ensure_directory()
        data = json.loads(path.read_text(encoding="utf-8"))
        data["title"] = prompt.title
        data["category"] = prompt.category
        data["description"] = prompt.description
        data["content"] = prompt.content
        data["tags"] = prompt.tags
        data["prompt_type"] = prompt.prompt_type
        data["updated_at"] = to_iso_datetime(datetime.now(timezone.utc)) or ""
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return True

    def delete(self, prompt_id: int) -> bool:
        path = self._find_path_by_id(prompt_id)
        if not path:
            return False
        try:
            path.unlink()
            return True
        except OSError:
            return False

    def get(self, prompt_id: int) -> Optional[Prompt]:
        path = self._find_path_by_id(prompt_id)
        if not path:
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return self._dict_to_prompt(data)
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Beschädigte Prompt-Datei: {path}") from e

    def list_all(
        self,
        filter_text: str = "",
        category: Optional[str] = None,
        project_id: Optional[int] = None,
        include_global: bool = True,
    ) -> List[Prompt]:
        self._ensure_directory()
        prompts = []
        for path in sorted(self.directory.glob(self.FILE_PATTERN)):
            if path.name == self.COUNTER_FILE:
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                p = self._dict_to_prompt(data)
                if category and p.category != category:
                    continue
                if filter_text:
                    search = filter_text.lower()
                    if not (
                        search in (p.title or "").lower()
                        or search in (p.description or "").lower()
                        or search in (p.content or "").lower()
                        or any(search in (t or "").lower() for t in p.tags)
                    ):
                        continue
                prompts.append(p)
            except (json.JSONDecodeError, KeyError):
                continue
        prompts.sort(key=lambda x: (x.updated_at or datetime.min) if x.updated_at else datetime.min, reverse=True)
        if project_id is not None and not include_global:
            prompts = [p for p in prompts if getattr(p, "project_id", None) == project_id]
        elif project_id is not None:
            prompts = [p for p in prompts if getattr(p, "project_id", None) is None or getattr(p, "project_id", None) == project_id]
        return prompts

    def list_for_project(self, project_id: int) -> List[Prompt]:
        return self.list_all(project_id=project_id, include_global=True)

    def list_project_prompts(self, project_id: int, filter_text: str = "") -> List[Prompt]:
        prompts = [p for p in self.list_all(project_id=project_id, include_global=False) if getattr(p, "project_id", None) == project_id]
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

    def list_global_prompts(self, filter_text: str = "") -> List[Prompt]:
        prompts = [p for p in self.list_all(project_id=None, include_global=True) if getattr(p, "project_id", None) is None]
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

    def create_version(self, prompt_id: int, title: str, content: str) -> int:
        """Speichert Version als JSON in versions/ Unterverzeichnis."""
        self._ensure_directory()
        versions_dir = self.directory / "versions"
        versions_dir.mkdir(exist_ok=True)
        existing = [p for p in versions_dir.glob("*.json") if p.stem.startswith(f"{prompt_id}_")]
        version = 1
        for p in existing:
            try:
                v = int(p.stem.split("_", 1)[1].split(".")[0])
                version = max(version, v + 1)
            except (ValueError, IndexError):
                pass
        path = versions_dir / f"{prompt_id}_{version:05d}.json"
        data = {
            "prompt_id": prompt_id,
            "version": version,
            "title": title,
            "content": content,
            "created_at": to_iso_datetime(datetime.now(timezone.utc)) or "",
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return version

    def count_versions(self, prompt_id: int) -> int:
        versions_dir = self.directory / "versions"
        if not versions_dir.exists():
            return 0
        try:
            return len([p for p in versions_dir.glob("*.json") if p.stem.startswith(f"{prompt_id}_")])
        except Exception:
            return 0

    def list_versions(self, prompt_id: int) -> List[dict]:
        versions_dir = self.directory / "versions"
        if not versions_dir.exists():
            return []
        result = []
        for path in sorted(versions_dir.glob("*.json"), reverse=True):
            if not path.stem.startswith(f"{prompt_id}_"):
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                created = parse_datetime(data.get("created_at"))
                result.append({
                    "version": data.get("version", 0),
                    "title": data.get("title", ""),
                    "content": data.get("content", ""),
                    "created_at": created,
                })
            except (json.JSONDecodeError, KeyError):
                continue
        result.sort(key=lambda x: x["version"], reverse=True)
        return result
