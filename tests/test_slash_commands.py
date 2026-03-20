"""Tests für Slash-Commands."""

import pytest
from app.core.commands.chat_commands import parse_slash_command
from app.core.models.roles import ModelRole


def test_parse_role_commands():
    r = parse_slash_command("/fast")
    assert r.consumed is True
    assert r.role == ModelRole.FAST

    r = parse_slash_command("/think Erkläre Quantenphysik")
    assert r.consumed is False
    assert r.role == ModelRole.THINK
    assert r.remaining_text == "Erkläre Quantenphysik"

    r = parse_slash_command("/code")
    assert r.consumed is True
    assert r.role == ModelRole.CODE


def test_parse_auto_commands():
    r = parse_slash_command("/auto on")
    assert r.consumed is True
    assert r.auto_routing is True

    r = parse_slash_command("/auto off")
    assert r.consumed is True
    assert r.auto_routing is False


def test_parse_cloud_commands():
    r = parse_slash_command("/cloud on")
    assert r.consumed is True
    assert r.cloud_escalation is True


def test_parse_no_command():
    r = parse_slash_command("Normale Nachricht")
    assert r.consumed is False
    assert r.remaining_text == "Normale Nachricht"
