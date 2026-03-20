"""Tests für Self-Improving Knowledge."""

import pytest

from app.rag.knowledge_models import KnowledgeEntry
from app.rag.knowledge_validator import KnowledgeValidator


def test_knowledge_entry():
    """KnowledgeEntry Struktur."""
    e = KnowledgeEntry(title="Test", content="Inhalt", source="test", confidence=0.9)
    assert e.title == "Test"
    assert e.confidence == 0.9
    assert e.timestamp is not None


def test_validator_accepts_good():
    """Validator akzeptiert gültige Einträge."""
    v = KnowledgeValidator(min_confidence=0.5)
    e = KnowledgeEntry(
        title="Python",
        content="Python ist eine interpretierte Programmiersprache mit dynamischer Typisierung.",
        source="test",
        confidence=0.8,
    )
    assert v.validate(e) is True


def test_validator_rejects_low_confidence():
    """Validator lehnt niedrige Konfidenz ab."""
    v = KnowledgeValidator(min_confidence=0.8)
    e = KnowledgeEntry(title="X", content="Langer Inhalt hier.", source="test", confidence=0.5)
    assert v.validate(e) is False


def test_validator_rejects_short_content():
    """Validator lehnt zu kurzen Inhalt ab."""
    v = KnowledgeValidator(min_content_length=30)
    e = KnowledgeEntry(title="X", content="Kurz.", source="test", confidence=0.9)
    assert v.validate(e) is False


def test_validator_filter_valid():
    """filter_valid filtert korrekt."""
    v = KnowledgeValidator(min_confidence=0.7, min_content_length=20)
    entries = [
        KnowledgeEntry("Python", "Guter langer Inhalt mit genug Zeichen.", "s", 0.9),
        KnowledgeEntry("Kurz", "Kurz.", "s", 0.9),
        KnowledgeEntry("Niedrig", "Auch gut genug Inhalt hier.", "s", 0.5),
    ]
    valid = v.filter_valid(entries)
    assert len(valid) == 1
    assert valid[0].title == "Python"
