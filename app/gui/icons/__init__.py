"""
Icon-System – zentrale Icon-Verwaltung.

IconManager.get("dashboard")
get_icon, get_icon_for_nav, get_icon_for_status, get_icon_for_object, get_icon_for_action — :mod:`icon_registry`
"""

from app.gui.icons.icon_registry import (
    get_icon,
    get_icon_for_action,
    get_icon_for_nav,
    get_icon_for_object,
    get_icon_for_status,
    get_resource_svg_path,
    list_resource_backed_names,
)
from app.gui.icons.manager import IconManager, get_icon_manager
from app.gui.icons.registry import IconRegistry

__all__ = [
    "IconManager",
    "get_icon",
    "get_icon_for_action",
    "get_icon_for_nav",
    "get_icon_for_object",
    "get_icon_for_status",
    "get_icon_manager",
    "get_resource_svg_path",
    "IconRegistry",
    "list_resource_backed_names",
]
