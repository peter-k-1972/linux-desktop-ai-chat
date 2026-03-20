"""
AgentEvent – Event-Struktur für Agentenaktivitäten.

Alle Agenten und Engines senden Events an den EventBus,
um die Aktivität im Debug Panel sichtbar zu machen.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class EventType(str, Enum):
    """Typen von Agenten-Events."""

    TASK_CREATED = "task_created"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    AGENT_SELECTED = "agent_selected"
    MODEL_CALL = "model_call"
    TOOL_EXECUTION = "tool_execution"
    RAG_RETRIEVAL_FAILED = "rag_retrieval_failed"


@dataclass
class AgentEvent:
    """
    Einzelnes Event für die Agenten-Aktivitätsüberwachung.

    Attributes:
        timestamp: Zeitpunkt des Events (UTC)
        agent_name: Name oder ID des Agenten
        task_id: ID des zugehörigen Tasks (optional)
        event_type: Art des Events
        message: Kurzbeschreibung
        metadata: Zusätzliche Daten (Modell, Dauer, Tool-Name, etc.)
    """

    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    agent_name: str = ""
    task_id: Optional[str] = None
    event_type: EventType = EventType.TASK_CREATED
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialisiert das Event für Persistenz oder Übertragung."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "agent_name": self.agent_name,
            "task_id": self.task_id,
            "event_type": self.event_type.value,
            "message": self.message,
            "metadata": dict(self.metadata),
        }
