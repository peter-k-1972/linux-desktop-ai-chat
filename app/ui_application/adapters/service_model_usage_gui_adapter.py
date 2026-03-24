"""
Adapter: ModelUsageGuiReadPort → model_usage_gui_service.
"""

from __future__ import annotations


class ServiceModelUsageGuiAdapter:
    """Thin wrapper — keine zusätzliche Fachlogik."""

    def quick_sidebar_hint(self) -> str:
        from app.services.model_usage_gui_service import get_model_usage_gui_service

        return get_model_usage_gui_service().quick_sidebar_hint()
