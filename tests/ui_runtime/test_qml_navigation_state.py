from __future__ import annotations

from app.ui_runtime.qml.shell_navigation_state import (
    DEFAULT_DOMAIN,
    default_domain,
    domain_entries,
    is_valid_domain,
    stage_relative_path,
)


def test_default_domain_is_chat() -> None:
    assert default_domain() == "chat"
    assert DEFAULT_DOMAIN == "chat"


def test_domain_entries_order_and_labels() -> None:
    entries = domain_entries()
    ids = [e[0] for e in entries]
    assert ids[0] == "chat"
    assert "settings" in ids
    assert all(len(t) == 2 for t in entries)


def test_is_valid_domain() -> None:
    assert is_valid_domain("chat") is True
    assert is_valid_domain("nope") is False


def test_stage_relative_path_known() -> None:
    p = stage_relative_path("chat")
    assert p is not None
    assert p.endswith("ChatStage.qml")
