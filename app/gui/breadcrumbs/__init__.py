"""
Breadcrumb-System – BreadcrumbManager, BreadcrumbBar.
"""

from app.gui.breadcrumbs.manager import BreadcrumbManager, get_breadcrumb_manager, set_breadcrumb_manager
from app.gui.breadcrumbs.model import BreadcrumbItem
from app.gui.breadcrumbs.bar import BreadcrumbBar

__all__ = ["BreadcrumbManager", "get_breadcrumb_manager", "set_breadcrumb_manager", "BreadcrumbItem", "BreadcrumbBar"]
