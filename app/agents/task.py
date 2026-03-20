"""
Task – Modell für delegierbare Aufgaben in der Agenten-Orchestrierung.

Tasks werden vom Task Planner erzeugt, vom Agent Router zugewiesen
und von der Execution Engine ausgeführt.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskStatus(str, Enum):
    """Status eines Tasks."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """
    Vollständige Task-Struktur für die Agenten-Farm.

    Attributes:
        id: Eindeutige Task-ID
        description: Kurzbeschreibung der Aufgabe
        assigned_agent: Agent-ID oder Slug des zugewiesenen Agenten
        status: Aktueller Status
        input: Eingabedaten (z.B. User-Prompt, Kontext)
        output: Ergebnis nach Ausführung
        dependencies: IDs von Tasks, die vor diesem abgeschlossen sein müssen
        priority: Höhere Zahl = höhere Priorität
        created_at: Erstellungszeitpunkt
        updated_at: Letzte Aktualisierung
        tool_hint: Optionaler Hinweis auf externes Tool (comfyui_render, audio_pipeline, etc.)
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    assigned_agent: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    input: Dict[str, Any] = field(default_factory=dict)
    output: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    priority: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tool_hint: Optional[str] = None  # comfyui_render, audio_pipeline, video_pipeline, thumbnail_generator
    error: Optional[str] = None  # Fehlermeldung bei status=FAILED

    def __post_init__(self):
        now = datetime.now(timezone.utc)
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now

    def touch(self) -> None:
        """Aktualisiert updated_at."""
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Serialisiert den Task für Persistenz oder Übertragung."""
        return {
            "id": self.id,
            "description": self.description,
            "assigned_agent": self.assigned_agent,
            "status": self.status.value,
            "input": self.input,
            "output": self.output,
            "dependencies": list(self.dependencies),
            "priority": self.priority,
            "created_at": self._dt_to_iso(self.created_at),
            "updated_at": self._dt_to_iso(self.updated_at),
            "tool_hint": self.tool_hint,
            "error": self.error,
        }

    @staticmethod
    def _dt_to_iso(dt: Optional[datetime]) -> Optional[str]:
        if dt is None:
            return None
        return dt.isoformat()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Deserialisiert aus einem Dict."""
        status_val = data.get("status", "pending")
        try:
            status = TaskStatus(status_val)
        except ValueError:
            status = TaskStatus.PENDING

        return cls(
            id=data.get("id") or str(uuid.uuid4()),
            description=data.get("description", ""),
            assigned_agent=data.get("assigned_agent"),
            status=status,
            input=dict(data.get("input") or {}),
            output=data.get("output"),
            dependencies=list(data.get("dependencies") or []),
            priority=int(data.get("priority", 0) or 0),
            created_at=cls._parse_dt(data.get("created_at")),
            updated_at=cls._parse_dt(data.get("updated_at")),
            tool_hint=data.get("tool_hint"),
            error=data.get("error"),
        )

    @staticmethod
    def _parse_dt(val: Any) -> Optional[datetime]:
        if val is None:
            return None
        if isinstance(val, datetime):
            return val
        s = str(val).replace("Z", "+00:00")
        try:
            if "T" in s or "+" in s:
                return datetime.fromisoformat(s)
            return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            return None

    @property
    def is_pending(self) -> bool:
        return self.status == TaskStatus.PENDING

    @property
    def is_running(self) -> bool:
        return self.status == TaskStatus.RUNNING

    @property
    def is_completed(self) -> bool:
        return self.status == TaskStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        return self.status == TaskStatus.FAILED

    @property
    def is_terminal(self) -> bool:
        """True wenn Task abgeschlossen (erfolgreich oder fehlgeschlagen)."""
        return self.status in (TaskStatus.COMPLETED, TaskStatus.FAILED)
