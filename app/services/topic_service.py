"""
TopicService – Themen-Gruppierung für projektbezogene Chats.

Topics sind flache, arbeitsorientierte Container innerhalb eines Projekts.
"""

from typing import Any, Dict, List, Optional

from app.services.infrastructure import get_infrastructure


class TopicService:
    """Service für Topics: CRUD, Zuordnungen."""

    def __init__(self):
        self._infra = get_infrastructure()

    def list_topics_for_project(self, project_id: int) -> List[Dict[str, Any]]:
        """Topics eines Projekts, sortiert nach Name."""
        return self._infra.database.list_topics_for_project(project_id)

    def create_topic(
        self,
        project_id: int,
        name: str,
        description: str = "",
    ) -> int:
        """Erstellt ein Topic. Gibt topic_id zurück."""
        return self._infra.database.create_topic(project_id, name, description)

    def get_topic(self, topic_id: int) -> Optional[Dict[str, Any]]:
        """Liefert ein Topic oder None."""
        return self._infra.database.get_topic(topic_id)

    def update_topic(
        self,
        topic_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """Aktualisiert Topic-Felder."""
        self._infra.database.update_topic(topic_id, name, description)

    def delete_topic(self, topic_id: int) -> None:
        """Löscht Topic; Chats werden ungrouped."""
        self._infra.database.delete_topic(topic_id)

    def move_chat_to_topic(
        self,
        project_id: int,
        chat_id: int,
        topic_id: Optional[int] = None,
    ) -> None:
        """Ordnet Chat einem Topic zu. topic_id=None = Ungrouped."""
        self._infra.database.set_chat_topic(project_id, chat_id, topic_id)

    def get_topic_of_chat(self, project_id: int, chat_id: int) -> Optional[int]:
        """Liefert topic_id des Chats oder None (ungrouped)."""
        return self._infra.database.get_topic_of_chat(project_id, chat_id)


_topic_service: Optional[TopicService] = None


def get_topic_service() -> TopicService:
    """Liefert den globalen TopicService."""
    global _topic_service
    if _topic_service is None:
        _topic_service = TopicService()
    return _topic_service


def set_topic_service(service: Optional[TopicService]) -> None:
    """Setzt den TopicService (für Tests)."""
    global _topic_service
    _topic_service = service
