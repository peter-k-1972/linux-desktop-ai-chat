"""
Capabilities – Standard-Fähigkeiten für Agentenprofile.

Erweiterbar für ComfyUI, Multimedia-Pipelines, Tool-Execution, Delegation.
"""

from typing import List

# Standard-Capabilities für Agenten
CAPABILITIES: List[str] = [
    "research",
    "summarize",
    "rag",
    "analysis",
    "code",
    "debug",
    "refactor",
    "documentation",
    "script_generation",
    "image_generation",
    "video_generation",
    "audio_generation",
    "music_generation",
    "workflow_creation",
    "system_monitoring",
    "update_management",
    "recovery",
]


def all_capabilities() -> List[str]:
    """Liefert alle definierten Capabilities."""
    return list(CAPABILITIES)


def capability_display_name(cap: str) -> str:
    """Liefert den Anzeigenamen einer Capability."""
    names = {
        "research": "Recherche",
        "summarize": "Zusammenfassen",
        "rag": "RAG / Knowledge",
        "analysis": "Analyse",
        "code": "Code",
        "debug": "Debugging",
        "refactor": "Refactoring",
        "documentation": "Dokumentation",
        "script_generation": "Skript-Generierung",
        "image_generation": "Bildgenerierung",
        "video_generation": "Videogenerierung",
        "audio_generation": "Audio-Generierung",
        "music_generation": "Musik-Generierung",
        "workflow_creation": "Workflow-Erstellung",
        "system_monitoring": "System-Monitoring",
        "update_management": "Update-Management",
        "recovery": "Recovery",
    }
    return names.get(cap, cap.replace("_", " ").title())
