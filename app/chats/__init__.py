"""Chat-Entitäten und Hilfsfunktionen (dünne Schicht über ``app.chat``-Verträgen).

Root-Public-Surface ist absichtlich minimal; siehe ``__all__``.
"""

from app.chats.models import get_chat_context_policy

__all__ = ["get_chat_context_policy"]
