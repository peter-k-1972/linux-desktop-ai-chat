"""
RAG-Datenmodelle: Document und Chunk.

Zentrale Strukturen für das RAG-Subsystem.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class Document:
    """
    Repräsentiert ein geladenes Dokument mit Metadaten.

    Attributes:
        id: Eindeutige Dokument-ID (z.B. Hash oder UUID)
        path: Dateipfad oder Quell-URI
        content: Roher Textinhalt
        metadata: Zusätzliche Metadaten (source_type, etc.)
        source_type: Typ der Quelle (file, url, etc.)
        created_at: Zeitstempel der Erstellung
    """

    id: str
    path: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_type: str = "file"
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)


@dataclass
class Chunk:
    """
    Ein Text-Chunk aus einem Dokument.

    Attributes:
        id: Eindeutige Chunk-ID
        document_id: Referenz zum Ursprungsdokument
        content: Chunk-Text
        metadata: Chunk-spezifische Metadaten
        position: Position im Dokument (0-basiert)
    """

    id: str
    document_id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    position: int = 0
