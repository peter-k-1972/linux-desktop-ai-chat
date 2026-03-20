"""
Unit Tests: Model Router.

Testet Modellwahl und Rollenlogik.
"""

import pytest

from app.core.models.router import route_prompt
from app.core.models.roles import (
    ModelRole,
    get_default_model_for_role,
    get_role_display_name,
    all_roles,
    DEFAULT_ROLE_MODEL_MAP,
)


# --- route_prompt ---

def test_route_code():
    """Code-Keywords werden erkannt."""
    assert route_prompt("Wie fixe ich diesen Python Bug?") == ModelRole.CODE
    assert route_prompt("Erkläre die Funktion def foo():") == ModelRole.CODE
    assert route_prompt("Refactoring dieser Klasse") == ModelRole.CODE
    assert route_prompt("SQL Query optimieren") == ModelRole.CODE


def test_route_think():
    """Think-Keywords werden erkannt."""
    assert route_prompt("Analysiere die Vor- und Nachteile von X") == ModelRole.THINK
    assert route_prompt("Vergleiche die Architektur von A und B") == ModelRole.THINK
    assert route_prompt("Bewerte die Strategie") == ModelRole.THINK


def test_route_chat():
    """Chat-Keywords werden erkannt."""
    assert route_prompt("Hallo, wie geht es dir?") == ModelRole.CHAT
    assert route_prompt("Erzähl mir einen Witz") == ModelRole.CHAT


def test_route_default():
    """Sachliche Fragen → DEFAULT."""
    assert route_prompt("Was ist die Hauptstadt von Frankreich?") == ModelRole.DEFAULT
    assert route_prompt("Erkläre mir kurz Machine Learning") == ModelRole.DEFAULT


def test_route_force_role():
    """force_role überschreibt Heuristik."""
    assert route_prompt("Code", force_role=ModelRole.THINK) == ModelRole.THINK
    assert route_prompt("Hallo", force_role=ModelRole.OVERKILL) == ModelRole.OVERKILL


def test_route_empty():
    """Leerer Prompt → DEFAULT."""
    assert route_prompt("") == ModelRole.DEFAULT
    assert route_prompt("   ") == ModelRole.DEFAULT


def test_route_slash_command():
    """Slash-Commands → DEFAULT."""
    assert route_prompt("/help") == ModelRole.DEFAULT


def test_route_available_roles_filter():
    """available_roles filtert Ergebnis."""
    result = route_prompt(
        "Python Bug fixen",
        available_roles={ModelRole.DEFAULT, ModelRole.THINK},
    )
    assert result in (ModelRole.DEFAULT, ModelRole.THINK)
    # CODE nicht verfügbar → Fallback auf DEFAULT
    assert result != ModelRole.CODE or ModelRole.CODE in {ModelRole.DEFAULT, ModelRole.THINK}


# --- Model Roles ---

def test_get_default_model_for_role():
    """Jede Rolle hat ein Standard-Modell."""
    for role in ModelRole:
        model = get_default_model_for_role(role)
        assert model
        assert isinstance(model, str)


def test_get_role_display_name():
    """Display-Namen sind lesbar."""
    assert get_role_display_name(ModelRole.CODE) == "Code"
    assert get_role_display_name(ModelRole.THINK) == "Denken"
    assert get_role_display_name(ModelRole.DEFAULT) == "Standard"


def test_all_roles():
    """all_roles() liefert alle Rollen."""
    roles = all_roles()
    assert ModelRole.CODE in roles
    assert ModelRole.THINK in roles
    assert ModelRole.DEFAULT in roles
    assert len(roles) >= 5


def test_default_role_model_map_complete():
    """DEFAULT_ROLE_MODEL_MAP enthält alle Rollen."""
    for role in ModelRole:
        assert role in DEFAULT_ROLE_MODEL_MAP
        assert DEFAULT_ROLE_MODEL_MAP[role]
