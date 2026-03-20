"""
Heuristische Erkennung unvollständiger Chat-Antworten.

Konservativ: Normale kurze Antworten sollen nicht fälschlich markiert werden.
Dokumentiert und testbar.
"""

import re
from typing import Optional

from app.chat.completion_status import CompletionStatus


def _count_code_fence_markers(text: str) -> int:
    """Zählt ```-Marker (Codeblöcke). Ungerade = offener Block."""
    return len(re.findall(r"```", text))


def _ends_mid_word(text: str) -> bool:
    """
    True wenn Text mitten im Wort endet (kein Leerzeichen, Satzzeichen, Newline).
    Mindestlänge 3 Zeichen, um "Ja" oder "Ok" nicht zu triggern.
    """
    t = (text or "").rstrip()
    if len(t) < 3:
        return False
    last = t[-1]
    if last in " \n\t.,;:!?)]}\"'":
        return False
    return True


def _ends_after_numbered_item_without_continuation(text: str) -> bool:
    """
    True wenn Text mit "1." oder "2." etc. endet und keine Fortsetzung hat.
    Nur bei ausreichender Länge (> 80 Zeichen), um kurze Listen nicht zu falsch zu markieren.
    """
    t = (text or "").rstrip()
    if len(t) < 80:
        return False
    if not re.search(r"\d+\.\s*$", t):
        return False
    return True


def _has_unclosed_markdown_constructs(text: str) -> bool:
    """
    Prüft auf offensichtlich ungeschlossene Markdown-Konstrukte.
    Nur Codeblöcke (```) – robust prüfbar. Quotes/Listen zu fehleranfällig.
    """
    return _count_code_fence_markers(text) % 2 == 1


def _ends_after_heading_without_content(text: str) -> bool:
    """
    True wenn Text mit einer Markdown-Überschrift endet und danach nichts kommt.
    Z.B. "## Einleitung\n" oder "### Kapitel 1\n" – typisches Abbruchmuster.
    """
    t = (text or "").rstrip()
    if len(t) < 10:
        return False
    if not re.search(r"#{1,6}\s+.+\s*$", t, re.MULTILINE):
        return False
    return True


def _minimum_length_for_heuristics(text: str) -> bool:
    """Heuristiken nur bei ausreichend langem Text anwenden (außer Codeblock)."""
    if _has_unclosed_markdown_constructs(text):
        return True
    return len((text or "").strip()) >= 50


def assess_completion_heuristic(
    content: str,
    *,
    provider_finished_normally: bool = True,
    had_error: bool = False,
    had_exception: bool = False,
) -> CompletionStatus:
    """
    Bewertet die Vollständigkeit einer Antwort anhand von Signalen und Heuristiken.

    Args:
        content: Der Antworttext
        provider_finished_normally: True wenn Stream mit done=True endete
        had_error: True wenn Provider einen error-Chunk lieferte
        had_exception: True wenn Exception während der Generierung auftrat

    Returns:
        CompletionStatus – complete, possibly_truncated, interrupted oder error
    """
    if had_error:
        return CompletionStatus.ERROR
    if had_exception:
        return CompletionStatus.INTERRUPTED
    if not provider_finished_normally:
        return CompletionStatus.INTERRUPTED

    text = content or ""
    if not _minimum_length_for_heuristics(text):
        return CompletionStatus.COMPLETE

    flags: list[str] = []

    if _has_unclosed_markdown_constructs(text):
        flags.append("open_code_block")
    if _ends_mid_word(text):
        flags.append("ends_mid_word")
    if _ends_after_numbered_item_without_continuation(text):
        flags.append("ends_after_numbered_item")
    if _ends_after_heading_without_content(text):
        flags.append("ends_after_heading")

    if flags:
        return CompletionStatus.POSSIBLY_TRUNCATED

    return CompletionStatus.COMPLETE


def get_heuristic_flags(content: str) -> list[str]:
    """
    Liefert die erkannten Heuristik-Flags für Debug/Tracing.
    Keine Bewertung, nur die rohen Signale.
    """
    text = content or ""
    flags: list[str] = []
    if _count_code_fence_markers(text) % 2 == 1:
        flags.append("open_code_block")
    if _ends_mid_word(text):
        flags.append("ends_mid_word")
    if _ends_after_numbered_item_without_continuation(text):
        flags.append("ends_after_numbered_item")
    if _ends_after_heading_without_content(text):
        flags.append("ends_after_heading")
    return flags
