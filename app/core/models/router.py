"""
Modell-Router für automatische Rollenwahl.

Heuristik-basierte Auswahl der passenden Modell-Rolle anhand der User-Nachricht.
Später erweiterbar durch LLM-Klassifikation.
"""

import re
from typing import Optional, Set

from app.core.models.roles import ModelRole


# Heuristik-Keywords für Rollen
CODE_KEYWORDS = [
    "code", "python", "bug", "error", "traceback", "refactor", "function", "class",
    "api", "json", "sql", "regex", "stacktrace", "debug", "implement", "fix",
    "syntax", "import", "def ", "async", "type hint", "test", "unittest",
    "pip", "venv", "dependency", "modul", "paket",
]
CODE_PATTERNS = [r"```[\w]*", r"def\s+\w+\s*\(", r"class\s+\w+", r"import\s+\w+", r"from\s+\w+\s+import"]

THINK_KEYWORDS = [
    "analysiere", "analysieren", "vergleiche", "vergleichen", "plane", "planen",
    "bewerte", "bewerten", "strukturiere", "strukturieren", "begründe", "begründen",
    "architektur", "vor- und nachteile", "vorteile", "nachteile", "strategie",
    "untersuchung", "zusammenfass", "zusammenfassen", "erkläre detailliert",
    "erklären sie", "warum genau", "was sind die gründe",
]
THINK_PATTERNS = [r"\b(pro|contra|vor-?\s*und\s*nach)\b", r"\b(1\.|2\.|3\.)\s+\w+"]  # Aufzählungen

CHAT_KEYWORDS = [
    "hallo", "hey", "wie geht", "was machst", "erzähl", "unterhalte",
    "kreativ", "geschichte", "witz", "witzig", "locker", "smalltalk",
    "philosoph", "gedanken", "meinung", "fühle", "empfinde",
]
CHAT_PATTERNS = [r"\bhi\b", r"\bhey\b"]  # Word boundaries to avoid "machine" matching "hi"

# Factual/sachliche Fragen → DEFAULT (vor CHAT/FAST)
FACTUAL_DEFAULT_KEYWORDS = [
    "erkläre", "erklären", "was ist", "hauptstadt", "definition",
    "bedeutet", "bedeutung", "wie funktioniert",
]

FAST_INDICATORS = [
    "ja oder nein", "kurz", "kurz und knapp", "ein wort", "schnell",
    "nur ", "bloß ", "einfach nur", "nur kurz",
]


def _normalize(text: str) -> str:
    """Normalisiert Text für Heuristik."""
    return text.lower().strip()


def _contains_any(text: str, keywords: list) -> bool:
    """Prüft, ob der Text eines der Keywords enthält."""
    norm = _normalize(text)
    return any(kw in norm for kw in keywords)


def _matches_any(text: str, patterns: list) -> bool:
    """Prüft, ob der Text eines der Regex-Patterns matcht."""
    norm = _normalize(text)
    return any(re.search(p, norm, re.IGNORECASE) for p in patterns)


def route_prompt(
    prompt: str,
    *,
    force_role: Optional[ModelRole] = None,
    available_roles: Optional[Set[ModelRole]] = None,
) -> ModelRole:
    """
    Bestimmt die passende Modell-Rolle für einen Prompt.

    Args:
        prompt: Die User-Nachricht
        force_role: Wenn gesetzt, wird diese Rolle zurückgegeben (manuelle Auswahl)
        available_roles: Optional: nur diese Rollen berücksichtigen

    Returns:
        Die gewählte ModelRole
    """
    if force_role is not None:
        return force_role

    norm = _normalize(prompt)
    if not norm:
        return ModelRole.DEFAULT

    # Slash-Commands werden separat behandelt (in chat_commands)
    if norm.startswith("/"):
        return ModelRole.DEFAULT

    # CODE: technischer Fokus
    if _contains_any(norm, CODE_KEYWORDS) or _matches_any(norm, CODE_PATTERNS):
        role = ModelRole.CODE
        if available_roles and role not in available_roles:
            role = ModelRole.DEFAULT
        return role

    # THINK: komplexe Analyse
    if _contains_any(norm, THINK_KEYWORDS) or _matches_any(norm, THINK_PATTERNS):
        role = ModelRole.THINK
        if available_roles and role not in available_roles:
            role = ModelRole.DEFAULT
        return role

    # Lange Nachricht oder mehrere Sätze -> eher THINK
    if len(norm) > 400 or norm.count(".") >= 3 or norm.count("?") >= 2:
        role = ModelRole.THINK
        if available_roles and role not in available_roles:
            role = ModelRole.DEFAULT
        return role

    # DEFAULT: sachliche/faktische Fragen (vor CHAT/FAST)
    if _contains_any(norm, FACTUAL_DEFAULT_KEYWORDS):
        return ModelRole.DEFAULT

    # CHAT: lockerer Smalltalk (mit Word-Boundaries für hi/hey)
    chat_match = _contains_any(norm, CHAT_KEYWORDS) or _matches_any(norm, CHAT_PATTERNS)
    if chat_match and len(norm) < 150:
        role = ModelRole.CHAT
        if available_roles and role not in available_roles:
            role = ModelRole.DEFAULT
        return role

    # FAST: sehr kurze, einfache Frage
    if len(norm) < 80 and _contains_any(norm, FAST_INDICATORS):
        role = ModelRole.FAST
        if available_roles and role not in available_roles:
            role = ModelRole.DEFAULT
        return role

    # DEFAULT: normaler Alltag
    return ModelRole.DEFAULT
