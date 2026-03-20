"""
Intent-Beispielset für ML-/Embedding-basierte Klassifikation.

Kleines, versionierbares Set. Kein großes Training.
"""

from app.core.chat_guard.intent_model import ChatIntent

# (text, intent) – repräsentative Beispiele pro Intent
INTENT_EXAMPLES: list[tuple[str, ChatIntent]] = [
    # command
    ("/think Erkläre mir das", ChatIntent.COMMAND),
    ("/agent führe Recherche durch", ChatIntent.COMMAND),
    ("/tool berechne", ChatIntent.COMMAND),
    ("/rag suche in Dokumenten", ChatIntent.COMMAND),
    ("/code schreibe eine Funktion", ChatIntent.COMMAND),
    ("/help was kannst du", ChatIntent.COMMAND),
    # formal_reasoning
    ("Beweise dass 2+2=4 ist", ChatIntent.FORMAL_REASONING),
    ("Was ist das Axiom der Vollständigkeit", ChatIntent.FORMAL_REASONING),
    ("Formale Definition von Stetigkeit", ChatIntent.FORMAL_REASONING),
    ("Beweise den Satz des Pythagoras", ChatIntent.FORMAL_REASONING),
    ("Logische Herleitung aus den Axiomen", ChatIntent.FORMAL_REASONING),
    ("Theorem und Lemma ableiten", ChatIntent.FORMAL_REASONING),
    # coding
    ("Schreibe eine Python-Funktion für", ChatIntent.CODING),
    ("Wie debugge ich einen Stacktrace", ChatIntent.CODING),
    ("Refaktorisiere diese Klasse", ChatIntent.CODING),
    ("API-Aufruf in Python", ChatIntent.CODING),
    ("Exception Handling Best Practices", ChatIntent.CODING),
    ("Bug im Code finden", ChatIntent.CODING),
    # knowledge_query
    ("Wer schrieb Faust", ChatIntent.KNOWLEDGE_QUERY),
    ("Von wem stammt die Ballade Erlkönig", ChatIntent.KNOWLEDGE_QUERY),
    ("Autor des Romans Die Leiden des jungen Werther", ChatIntent.KNOWLEDGE_QUERY),
    ("Wer hat das Gedicht geschrieben", ChatIntent.KNOWLEDGE_QUERY),
    ("Komponist der 9. Sinfonie", ChatIntent.KNOWLEDGE_QUERY),
    ("Verfasser von Hamlet", ChatIntent.KNOWLEDGE_QUERY),
    # possibly_ambiguous
    ("Die Glocke von Goethe", ChatIntent.POSSIBLY_AMBIGUOUS),
    ("Wer schrieb das Werk von Schiller über Maria Stuart", ChatIntent.POSSIBLY_AMBIGUOUS),
    ("Das Gedicht von Heine zugeschrieben", ChatIntent.POSSIBLY_AMBIGUOUS),
    # chat
    ("Hallo wie geht es dir", ChatIntent.CHAT),
    ("Erzähl mir einen Witz", ChatIntent.CHAT),
    ("Was denkst du darüber", ChatIntent.CHAT),
    ("Danke für die Hilfe", ChatIntent.CHAT),
    ("Kannst du das anders formulieren", ChatIntent.CHAT),
]


def get_example_texts_by_intent() -> dict[ChatIntent, list[str]]:
    """Gruppiert Beispiele nach Intent."""
    by_intent: dict[ChatIntent, list[str]] = {}
    for text, intent in INTENT_EXAMPLES:
        by_intent.setdefault(intent, []).append(text)
    return by_intent
