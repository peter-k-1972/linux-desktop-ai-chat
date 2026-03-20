"""
Projekt-Modelle – Kontext-Policy und Metadaten.

Projekte können default_context_policy setzen für kontextabhängiges Verhalten.
"""

from typing import Dict, Optional

from app.chat.context_policies import ChatContextPolicy


def get_default_context_policy(project: Optional[Dict]) -> Optional[ChatContextPolicy]:
    """
    Liefert die Kontext-Policy eines Projekts oder None.

    project: Dict von get_project() (project_id, name, default_context_policy, ...)
    """
    if not project:
        return None
    raw = project.get("default_context_policy")
    if not raw or not isinstance(raw, str) or not raw.strip():
        return None
    try:
        return ChatContextPolicy(raw.strip().lower())
    except ValueError:
        return None
