"""
Icon-System – zentrale Icon-Verwaltung.

IconManager.get("dashboard")
IconManager.get("chat", size=20)
"""

from app.gui.icons.manager import IconManager, get_icon_manager
from app.gui.icons.registry import IconRegistry

__all__ = ["IconManager", "get_icon_manager", "IconRegistry"]
