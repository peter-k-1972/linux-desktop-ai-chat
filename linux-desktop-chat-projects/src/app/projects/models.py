"""
Projekt-Modelle – Kontext-Policy und Metadaten.

Projekte können default_context_policy setzen für kontextabhängiges Verhalten.
Split-Vorbereitung: dieses Modul konsumiert aus ``app.chat.context_policies``
bewusst nur den Enum-Vertrag ``ChatContextPolicy``; Profil-/Budget-Ableitung
bleibt in der Chat-/Kontext-Domäne.
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


def format_context_rules_narrative(project: Optional[Dict]) -> str:
    """
    Kurztext für die Projekt-Inspector-Ansicht: wie Kontextregeln aus Projekt-Policy und Chats zusammenspielen.
    """
    if not project:
        return "—"
    chunks = [
        "Neue Chats in diesem Projekt übernehmen die Standard-Kontextpolicy des Projekts, "
        "sofern im Chat keine abweichende Policy gewählt wird.",
        "Die Policy beeinflusst Umfang und Art der Kontextinformationen (z. B. Architektur- vs. Debug-Fokus).",
    ]
    raw = project.get("default_context_policy")
    if raw is not None and isinstance(raw, str) and raw.strip():
        chunks.append(f"Gespeicherte Rohkonfiguration: {raw.strip()[:160]}")
    else:
        chunks.append(
            "Es ist keine projektspezifische Policy hinterlegt; es gilt der App-Standard, bis ein Wert gesetzt wird."
        )
    return "\n\n".join(chunks)


def get_default_context_policy(project: Optional[Dict]) -> Optional[ChatContextPolicy]:
    """
    Liefert die Kontext-Policy eines Projekts oder None.

    project: Dict von get_project() (project_id, name, default_context_policy, ...)
    Die Projects-Domain wertet hier nur den gemeinsamen Enum-Vertrag aus; weitere
    Kontext-Policy-Logik bleibt außerhalb von ``app.projects``.
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
