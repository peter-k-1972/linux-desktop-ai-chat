"""
TooltipHelper – Kontextbezogene Tooltips und Info-Icons.

Zentrale Definition aller Tooltips für konsistente In-App-Hilfe.
"""

from typing import Dict, Optional

# Tooltip-Mapping: Widget-ObjectName oder (parent_id, widget_id) -> Tooltip-Text
TOOLTIPS: Dict[str, str] = {
    # Header
    "headerAgentCombo": "Wählen Sie einen Agenten (Persona) für diesen Chat. Der Agent liefert einen System-Prompt und ein zugewiesenes Modell.",
    "headerModelCombo": "Aktives Sprachmodell für die Konversation. Wird bei Auto-Routing automatisch gewählt.",
    "headerRoleCombo": "Modus: Schnell, Standard, Denken, Code, Research etc. Bestimmt die Modellauswahl.",
    "headerAutoRouting": "Automatische Modellauswahl nach Prompt-Inhalt. Deaktivieren für manuelle Kontrolle.",
    "headerCloud": "Cloud-Eskalation erlauben. Erfordert OLLAMA_API_KEY in den Einstellungen.",
    "overkillButton": "Mit stärkerem Modell (Cloud) erneut versuchen.",
    "headerThinkMode": "Thinking-Modus: auto (Modell entscheidet), off, low, medium, high.",
    "headerWebSearch": "Aktuelle Websuchergebnisse als Kontext nutzen.",
    "headerRAG": "Retrieval Augmented Generation: Kontext aus indexierten Dokumenten nutzen.",
    "headerSelfImproving": "Wissen aus LLM-Antworten extrahieren und in den Knowledge Store aufnehmen.",
    # Composer
    "sendButton": "Nachricht senden. Slash-Commands: /think, /code, /research, /delegate …",
    "chatInput": "Nachricht eingeben. Unterstützt Slash-Commands wie /think oder /delegate.",
    # Side-Panel
    "modelSettingsPanel": "Modell, Temperatur, Max Tokens und Denk-Modus konfigurieren.",
    "promptManagerPanel": "Prompts verwalten, anwenden oder in die Eingabezeile übernehmen.",
    # Allgemein
    "settings": "Einstellungen: Theme, Modelle, RAG, Prompts, Cloud-API.",
    "agents": "Agenten verwalten: Erstellen, bearbeiten, für Chat auswählen.",
}

# Erweiterte Hilfetexte (für Info-Icons oder längere Tooltips)
EXTENDED_HELP: Dict[str, str] = {
    "rag": "RAG nutzt indexierte Dokumente. Indexieren mit: python scripts/index_rag.py --space default ./docs",
    "self_improving": "Antworten werden analysiert; extrahiertes Wissen wird in den Knowledge Store geschrieben.",
    "delegate": "Mit /delegate starten Sie die Agenten-Orchestrierung: Task Planner → Delegation → Execution.",
    "research": "Research-Modus: Planner → RAG → LLM → Critic. Für tiefgehende Recherche.",
    "slash_commands": "Verfügbar: /fast, /smart, /think, /code, /overkill, /research, /delegate, /auto on|off, /cloud on|off",
}


def get_tooltip(widget_object_name: str) -> Optional[str]:
    """Liefert den Tooltip-Text für ein Widget (ObjectName)."""
    return TOOLTIPS.get(widget_object_name)


def get_extended_help(key: str) -> Optional[str]:
    """Liefert erweiterten Hilfetext."""
    return EXTENDED_HELP.get(key)


def set_tooltip_if_defined(widget, object_name: Optional[str] = None):
    """
    Setzt den Tooltip für ein Widget, falls definiert.
    object_name: Falls None, wird widget.objectName() verwendet.
    """
    name = object_name or (widget.objectName() if hasattr(widget, "objectName") else None)
    if name:
        tip = get_tooltip(name)
        if tip and hasattr(widget, "setToolTip"):
            widget.setToolTip(tip)
