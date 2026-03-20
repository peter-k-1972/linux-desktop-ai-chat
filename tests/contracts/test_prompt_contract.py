"""
Contract Tests: Prompt-Objekt Roundtrip.

Sichert den Vertrag zwischen Prompt und allen Konsumenten
(PromptService, PromptRepository, UI-Panels, Chat Side-Panel).
"""

from datetime import datetime, timezone

import pytest

from app.prompts.prompt_models import Prompt, PROMPT_TYPES, PROMPT_CATEGORIES


REQUIRED_PROMPT_FIELDS = [
    "id",
    "title",
    "category",
    "description",
    "content",
    "tags",
    "prompt_type",
    "created_at",
    "updated_at",
]


@pytest.mark.contract
def test_prompt_to_dict_contains_required_fields(test_prompt):
    """Prompt.to_dict() liefert alle Pflichtfelder."""
    d = test_prompt.to_dict()
    for field in REQUIRED_PROMPT_FIELDS:
        assert field in d, f"Pflichtfeld '{field}' fehlt in to_dict()"


@pytest.mark.contract
def test_prompt_roundtrip_to_dict_from_dict(test_prompt):
    """Prompt: to_dict → from_dict erhält alle relevanten Daten."""
    d = test_prompt.to_dict()
    restored = Prompt.from_dict(d)
    assert restored.id == test_prompt.id
    assert restored.title == test_prompt.title
    assert restored.category == test_prompt.category
    assert restored.description == test_prompt.description
    assert restored.content == test_prompt.content
    assert restored.tags == test_prompt.tags
    assert restored.prompt_type == test_prompt.prompt_type


@pytest.mark.contract
def test_prompt_empty_creates_valid_prompt():
    """Prompt.empty() erzeugt gültigen Prompt für Neu-Erstellung."""
    p = Prompt.empty()
    assert p.id is None
    assert p.title == ""
    assert p.category == "general"
    assert p.prompt_type == "user"
    assert p.tags == []


@pytest.mark.contract
def test_prompt_from_dict_handles_tags_as_string():
    """Prompt.from_dict() akzeptiert tags als kommagetrennten String."""
    d = {
        "id": 1,
        "title": "Test",
        "category": "code",
        "description": "",
        "content": "x",
        "tags": "a, b, c",
        "prompt_type": "user",
        "created_at": None,
        "updated_at": None,
    }
    p = Prompt.from_dict(d)
    assert p.tags == ["a", "b", "c"]


@pytest.mark.contract
def test_prompt_types_are_stable():
    """PROMPT_TYPES enthält erwartete Werte."""
    assert "user" in PROMPT_TYPES
    assert "system" in PROMPT_TYPES


@pytest.mark.contract
def test_prompt_categories_are_stable():
    """PROMPT_CATEGORIES enthält erwartete Werte."""
    assert "general" in PROMPT_CATEGORIES
    assert "code" in PROMPT_CATEGORIES
