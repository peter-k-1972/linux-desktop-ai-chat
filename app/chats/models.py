"""
Chat-Modelle – Kontext-Policy und Metadaten.

Einzelne Chats können default_context_policy setzen.
"""

from typing import Dict, Optional

from app.chat.context_policies import ChatContextPolicy


def get_chat_context_policy(chat_info: Optional[Dict]) -> Optional[ChatContextPolicy]:
    """
    Liefert die Kontext-Policy eines Chats oder None.

    chat_info: Dict von get_chat_info() (id, title, default_context_policy, ...)
    """
    if not chat_info:
        return None
    raw = chat_info.get("default_context_policy")
    if not raw or not isinstance(raw, str) or not raw.strip():
        return None
    try:
        return ChatContextPolicy(raw.strip().lower())
    except ValueError:
        return None
