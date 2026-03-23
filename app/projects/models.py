"""
Projekt-Modelle – Kontext-Policy und Metadaten.

Projekte können default_context_policy setzen für kontextabhängiges Verhalten.
"""

from typing import Dict, Optional

from app.chat.context_policies import ChatContextPolicy


def format_default_context_policy_caption(project: Optional[Dict]) -> str:
    """
    Kurztext für UI: gespeicherte Standard-Kontextpolicy des Projekts.
    """
    if not project:
        return "—"
    raw = project.get("default_context_policy")
    if raw is not None and isinstance(raw, str) and raw.strip():
        pol = get_default_context_policy(project)
        if pol is not None:
            _names = {
                ChatContextPolicy.DEFAULT: "default (ausgewogen)",
                ChatContextPolicy.ARCHITECTURE: "architecture (ausführlich)",
                ChatContextPolicy.DEBUG: "debug (minimal)",
                ChatContextPolicy.EXPLORATION: "exploration",
            }
            return _names.get(pol, pol.value)
        return f"Gespeichert (unklar): {raw.strip()[:48]}"
    return "App-Standard (keine Projekt-Policy)"


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
