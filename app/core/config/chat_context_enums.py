"""
Chat-Kontext – Enums für Mode und Detail-Level.

Getrennt von AppSettings, damit das Context-Modul keine Settings-Abhängigkeit hat.
Settings liefert Konfiguration; Context erzeugt Fragmente.
"""

from enum import Enum


class ChatContextMode(str, Enum):
    OFF = "off"
    NEUTRAL = "neutral"
    SEMANTIC = "semantic"


class ChatContextDetailLevel(str, Enum):
    MINIMAL = "minimal"
    STANDARD = "standard"
    FULL = "full"
