"""
Prompt-Datenmodell für die Promptverwaltung.
Erweiterbar für spätere Backend-Integration.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Prompt:
    """Ein gespeicherter Prompt mit Metadaten."""

    id: Optional[int]
    title: str
    category: str
    description: str
    content: str
    tags: List[str]
    prompt_type: str  # system | user | developer | template
    scope: str  # global | project
    project_id: Optional[int]  # bei scope=project
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not isinstance(self.tags, list):
            self.tags = list(self.tags) if self.tags else []
        if not hasattr(self, "scope") or self.scope is None:
            object.__setattr__(self, "scope", "global")
        if not hasattr(self, "project_id"):
            object.__setattr__(self, "project_id", None)

    @classmethod
    def empty(cls) -> "Prompt":
        """Leerer Prompt für Neu-Erstellung."""
        return cls(
            id=None,
            title="",
            category="general",
            description="",
            content="",
            tags=[],
            prompt_type="user",
            scope="global",
            project_id=None,
            created_at=None,
            updated_at=None,
        )

    def to_dict(self) -> dict:
        """Für JSON-Serialisierung."""
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "content": self.content,
            "tags": self.tags,
            "prompt_type": self.prompt_type,
            "scope": getattr(self, "scope", "global"),
            "project_id": getattr(self, "project_id", None),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Prompt":
        """Aus Dictionary (z.B. aus DB/JSON)."""
        created = d.get("created_at")
        updated = d.get("updated_at")
        if isinstance(created, str):
            try:
                created = datetime.fromisoformat(created.replace("Z", "+00:00"))
            except ValueError:
                created = None
        if isinstance(updated, str):
            try:
                updated = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            except ValueError:
                updated = None
        tags = d.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        return cls(
            id=d.get("id"),
            title=d.get("title", ""),
            category=d.get("category", "general"),
            description=d.get("description", ""),
            content=d.get("content", ""),
            tags=tags,
            prompt_type=d.get("prompt_type", "user"),
            scope=d.get("scope", "global"),
            project_id=d.get("project_id"),
            created_at=created,
            updated_at=updated,
        )


PROMPT_TYPES = ["user", "system", "developer", "template"]
PROMPT_CATEGORIES = ["general", "code", "analysis", "creative", "instruction", "other"]
