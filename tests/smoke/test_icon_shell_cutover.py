"""Smoke: Shell-Navigation und Icon-Schicht ohne Exceptions."""

from app.gui.icons.icon_registry import get_icon_for_nav
from app.gui.navigation.nav_areas import NavArea
from app.gui.navigation.sidebar_config import get_sidebar_sections


def test_sidebar_config_icons_resolve(qapplication):
    for sec in get_sidebar_sections():
        for item in sec.items:
            name = (item.icon or "").strip()
            if name:
                from app.gui.icons import IconManager

                assert not IconManager.get(name, size=18).isNull()
            else:
                assert not get_icon_for_nav(item.nav_key, size=18).isNull()


def test_all_nav_areas_have_icons(qapplication):
    for area_id, _title in NavArea.all_areas():
        assert not get_icon_for_nav(area_id, size=18).isNull()
