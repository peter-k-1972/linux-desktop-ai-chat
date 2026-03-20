"""
Modell-Rollen für den Desktop-Chat.

Abstrahiert von konkreten Modellen. Jede Rolle hat ein semantisches Profil
und wird auf konkrete Modell-IDs gemappt.
"""

from enum import Enum
from typing import Dict, List, Optional


class ModelRole(str, Enum):
    """Semantische Rollen für Modellauswahl."""

    FAST = "FAST"  # Schnelle Antworten, Brainstorming, leichte Aufgaben
    DEFAULT = "DEFAULT"  # Allround, Standardmodus
    CHAT = "CHAT"  # Natürliches Gespräch, lockerer Stil, Kreativmodus
    THINK = "THINK"  # Analyse, Struktur, anspruchsvollere Aufgaben
    CODE = "CODE"  # Code, Debugging, Refactoring, technischer Fokus
    VISION = "VISION"  # Multimodal, Bildanalyse (vorbereitet)
    OVERKILL = "OVERKILL"  # Cloud-Eskalation, maximale Kapazität
    RESEARCH = "RESEARCH"  # Research Agent (Planner→RAG→LLM→Critic)


# Default-Mapping: Rolle -> bevorzugtes Modell
DEFAULT_ROLE_MODEL_MAP: Dict[ModelRole, str] = {
    ModelRole.FAST: "mistral:latest",
    ModelRole.DEFAULT: "qwen2.5:latest",
    ModelRole.CHAT: "llama3:latest",
    ModelRole.THINK: "gpt-oss:latest",
    ModelRole.CODE: "qwen2.5-coder:7b",
    ModelRole.VISION: "qwen3-vl",  # optional, Cloud
    ModelRole.OVERKILL: "gpt-oss:120b",  # Cloud
    ModelRole.RESEARCH: "gpt-oss:latest",  # Research Agent (intern: Planner qwen2.5, Research gpt-oss, Critic mistral)
}

# Anzeigenamen für UI
ROLE_DISPLAY_NAMES: Dict[ModelRole, str] = {
    ModelRole.FAST: "Schnell",
    ModelRole.DEFAULT: "Standard",
    ModelRole.CHAT: "Chat",
    ModelRole.THINK: "Denken",
    ModelRole.CODE: "Code",
    ModelRole.VISION: "Vision",
    ModelRole.OVERKILL: "Overkill",
    ModelRole.RESEARCH: "Research",
}


def get_role_display_name(role: ModelRole) -> str:
    """Liefert den Anzeigenamen einer Rolle."""
    return ROLE_DISPLAY_NAMES.get(role, role.value)


def get_default_model_for_role(role: ModelRole) -> str:
    """Liefert das Standard-Modell für eine Rolle."""
    return DEFAULT_ROLE_MODEL_MAP.get(role, DEFAULT_ROLE_MODEL_MAP[ModelRole.DEFAULT])


def all_roles() -> List[ModelRole]:
    """Liefert alle definierten Rollen."""
    return list(ModelRole)
