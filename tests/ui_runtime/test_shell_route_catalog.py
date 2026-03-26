from __future__ import annotations

from app.core.navigation.nav_areas import NavArea
from app.ui_runtime.qml.shell_route_catalog import (
    DEFER_STAGE_RELATIVE,
    SETTINGS_STAGE_RELATIVE,
    default_route,
    is_valid_operations_workspace,
    is_valid_top_area,
    legacy_surface_key,
    map_legacy_flat_domain,
    normalize_route,
    operations_workspace_entries,
    resolve_stage_relative_path,
    top_area_entries,
)


def test_default_route_is_operations_projects() -> None:
    a, w = default_route()
    assert a == NavArea.OPERATIONS
    assert w == "operations_projects"


def test_top_area_entries_match_nav_area() -> None:
    entries = top_area_entries()
    assert len(entries) == 6
    ids = [e[0] for e in entries]
    assert NavArea.COMMAND_CENTER in ids
    assert NavArea.SETTINGS in ids


def test_operations_workspace_entries_count() -> None:
    assert len(operations_workspace_entries()) == 8


def test_resolve_operations_bound_stages() -> None:
    rel, defer = resolve_stage_relative_path(NavArea.OPERATIONS, "operations_chat")
    assert defer == ""
    assert rel.endswith("ChatStage.qml")


def test_resolve_operations_unbound_stages() -> None:
    rel, defer = resolve_stage_relative_path(NavArea.OPERATIONS, "operations_knowledge")
    assert rel == DEFER_STAGE_RELATIVE
    assert "unbound" in defer


def test_resolve_operations_audit_incidents_stage() -> None:
    rel, defer = resolve_stage_relative_path(NavArea.OPERATIONS, "operations_audit_incidents")
    assert defer == ""
    assert rel.endswith("OperationsReadStage.qml")


def test_resolve_settings() -> None:
    rel, defer = resolve_stage_relative_path(NavArea.SETTINGS, "")
    assert rel == SETTINGS_STAGE_RELATIVE
    assert defer == ""


def test_resolve_non_operations_top_area_defers() -> None:
    rel, defer = resolve_stage_relative_path(NavArea.COMMAND_CENTER, "")
    assert rel == DEFER_STAGE_RELATIVE
    assert "unbound_area" in defer


def test_legacy_flat_mapping_round_trip() -> None:
    assert map_legacy_flat_domain("chat") == (NavArea.OPERATIONS, "operations_chat")
    assert map_legacy_flat_domain("bogus") is None


def test_legacy_surface_key() -> None:
    assert legacy_surface_key(NavArea.OPERATIONS, "operations_chat") == "chat"
    assert legacy_surface_key(NavArea.SETTINGS, "") == "settings"


def test_normalize_route_operations_default_workspace() -> None:
    a, w = normalize_route(NavArea.OPERATIONS, "")
    assert a == NavArea.OPERATIONS
    assert w == "operations_projects"


def test_validators() -> None:
    assert is_valid_top_area(NavArea.OPERATIONS) is True
    assert is_valid_top_area("nope") is False
    assert is_valid_operations_workspace("operations_workflows") is True
    assert is_valid_operations_workspace("x") is False
