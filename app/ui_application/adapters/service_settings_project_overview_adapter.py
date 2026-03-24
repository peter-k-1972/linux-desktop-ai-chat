"""
Adapter: aktives Projekt für Settings → ProjectService + ProjectContextManager.
"""

from __future__ import annotations

from app.ui_contracts.workspaces.settings_project_overview import (
    ActiveProjectSummaryDto,
    SettingsActiveProjectViewState,
)


class ServiceSettingsProjectOverviewAdapter:
    """Parität zum früheren ProjectCategory._refresh (ohne Qt)."""

    def load_active_project_view_state(self) -> SettingsActiveProjectViewState:
        try:
            from app.core.context.project_context_manager import get_project_context_manager
            from app.services.project_service import get_project_service

            pid = get_project_context_manager().get_active_project_id()
            if pid is None:
                return SettingsActiveProjectViewState(mode="no_active")

            svc = get_project_service()
            proj = svc.get_project(pid)
            if not proj:
                return SettingsActiveProjectViewState(mode="not_found")

            n_chats = svc.count_chats_of_project(pid)
            desc = (proj.get("description") or "").strip() or "—"
            pol = proj.get("default_context_policy")
            pol_disp = "—"
            if pol is not None and str(pol).strip():
                s = str(pol).strip()
                pol_disp = s if len(s) <= 240 else s[:237] + "…"

            summary = ActiveProjectSummaryDto(
                project_id=int(pid),
                name=str(proj.get("name", "?")),
                status=str(proj.get("status", "—")),
                description_display=desc,
                chat_count=int(n_chats),
                default_context_policy_display=pol_disp,
                updated_at_display=str(proj.get("updated_at", "—")),
            )
            return SettingsActiveProjectViewState(mode="ok", summary=summary)
        except Exception as exc:
            return SettingsActiveProjectViewState(mode="error", error_message=str(exc))
