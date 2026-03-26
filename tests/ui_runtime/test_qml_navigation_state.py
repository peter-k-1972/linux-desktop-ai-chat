from __future__ import annotations

from app.ui_runtime.qml.shell_navigation_state import (
    default_domain,
    domain_entries,
    is_valid_domain,
    map_legacy_flat_domain,
    stage_relative_path,
)


def test_default_domain_legacy_key() -> None:
    assert default_domain() == "projects"


def test_domain_entries_legacy_flat() -> None:
    entries = domain_entries()
    ids = [e[0] for e in entries]
    assert "chat" in ids
    assert "settings" in ids


def test_is_valid_domain_legacy() -> None:
    assert is_valid_domain("chat") is True
    assert is_valid_domain("nope") is False


def test_stage_relative_path_legacy_chat() -> None:
    p = stage_relative_path("chat")
    assert p is not None
    assert p.endswith("ChatStage.qml")


def test_map_legacy_flat_domain_reexport() -> None:
    from app.core.navigation.nav_areas import NavArea

    assert map_legacy_flat_domain("workflows") == (NavArea.OPERATIONS, "operations_workflows")
