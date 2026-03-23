"""Cutover: Nav-, Status- und Konflikt-Mappings gegen kanonische Registry."""

from app.gui.icons.icon_registry import (
    get_icon_for_action,
    get_icon_for_nav,
    get_icon_for_status,
)
from app.gui.icons.registry import IconRegistry
from app.gui.navigation.nav_areas import NavArea


def test_nav_area_icons_match_mapping(qapplication):
    assert not get_icon_for_nav(NavArea.COMMAND_CENTER, size=18).isNull()
    assert not get_icon_for_nav(NavArea.SETTINGS, size=18).isNull()
    assert not get_icon_for_nav(NavArea.QA_GOVERNANCE, size=18).isNull()


def test_workspace_deployment_is_deploy_not_data_stores(qapplication):
    ic = get_icon_for_nav("operations_deployment", size=18)
    assert not ic.isNull()
    from app.gui.icons.nav_mapping import get_workspace_icon

    assert get_workspace_icon("operations_deployment") == IconRegistry.DEPLOY


def test_actions_open_and_link_out_distinct(qapplication):
    assert not get_icon_for_action("open", size=16).isNull()
    assert not get_icon_for_action("external_link", size=16).isNull()


def test_status_icons_resolve(qapplication):
    for s in ("success", "warning", "error", "running", "idle", "paused"):
        assert not get_icon_for_status(s, size=16).isNull()


def test_unknown_status_falls_back_to_info(qapplication):
    assert not get_icon_for_status("unknown_xyz", size=16).isNull()
