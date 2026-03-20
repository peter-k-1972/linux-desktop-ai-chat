"""Tests für den Modell-Router."""

import pytest
from app.core.models.router import route_prompt
from app.core.models.roles import ModelRole


def test_route_code():
    assert route_prompt("Wie fixe ich diesen Python Bug?") == ModelRole.CODE
    assert route_prompt("Erkläre die Funktion def foo():") == ModelRole.CODE
    assert route_prompt("Refactoring dieser Klasse") == ModelRole.CODE
    assert route_prompt("SQL Query optimieren") == ModelRole.CODE


def test_route_think():
    assert route_prompt("Analysiere die Vor- und Nachteile von X") == ModelRole.THINK
    assert route_prompt("Vergleiche die Architektur von A und B") == ModelRole.THINK
    assert route_prompt("Bewerte die Strategie") == ModelRole.THINK


def test_route_chat():
    assert route_prompt("Hallo, wie geht es dir?") == ModelRole.CHAT
    assert route_prompt("Erzähl mir einen Witz") == ModelRole.CHAT


def test_route_default():
    assert route_prompt("Was ist die Hauptstadt von Frankreich?") == ModelRole.DEFAULT
    assert route_prompt("Erkläre mir kurz Machine Learning") == ModelRole.DEFAULT


def test_route_force_role():
    assert route_prompt("Code", force_role=ModelRole.THINK) == ModelRole.THINK
    assert route_prompt("Hallo", force_role=ModelRole.OVERKILL) == ModelRole.OVERKILL


def test_route_empty():
    assert route_prompt("") == ModelRole.DEFAULT
    assert route_prompt("   ") == ModelRole.DEFAULT
