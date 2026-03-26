"""
QML context object ``shell`` — shell routing only (no services, no domain use-cases).

Welle 1: top areas align with :class:`app.core.navigation.nav_areas.NavArea`;
Operations sub-workspaces align with ``OperationsScreen`` workspace IDs.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot

from app.core.navigation.nav_areas import NavArea
from app.ui_runtime.qml.domain_nav_model import DomainNavModel, WorkspaceNavModel
from app.ui_runtime.qml.presenters.shell_presenter import ShellPresenter
from app.ui_runtime.qml.shell_route_catalog import (
    map_legacy_flat_domain,
    operations_workspace_entries,
    top_area_entries,
)

logger = logging.getLogger(__name__)


class ShellBridgeFacade(QObject):
    activeDomainChanged = Signal()
    activeTopAreaChanged = Signal()
    activeWorkspaceIdChanged = Signal()
    stageUrlChanged = Signal()
    shellReadyChanged = Signal()
    routeDeferReasonChanged = Signal()
    pendingContextJsonChanged = Signal()
    workspaceNavModelChanged = Signal()

    def __init__(self, qml_root: Path, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._qml_root = Path(qml_root)
        self._active_top_area = ""
        self._active_workspace_id = ""
        self._active_domain = ""
        self._stage_url = QUrl()
        self._shell_ready = False
        self._route_defer_reason = ""
        self._pending_context_json = ""
        self._domain_model = DomainNavModel(top_area_entries(), self)
        self._workspace_model = WorkspaceNavModel([], self)
        self._presenter = ShellPresenter(self, self._qml_root)

    def _get_active_domain(self) -> str:
        return self._active_domain

    activeDomain = Property(str, _get_active_domain, notify=activeDomainChanged)

    def _get_active_top_area(self) -> str:
        return self._active_top_area

    activeTopArea = Property(str, _get_active_top_area, notify=activeTopAreaChanged)

    def _get_active_workspace_id(self) -> str:
        return self._active_workspace_id

    activeWorkspaceId = Property(str, _get_active_workspace_id, notify=activeWorkspaceIdChanged)

    def _get_stage_url(self) -> QUrl:
        return self._stage_url

    stageUrl = Property(QUrl, _get_stage_url, notify=stageUrlChanged)

    def _get_shell_ready(self) -> bool:
        return self._shell_ready

    shellReady = Property(bool, _get_shell_ready, notify=shellReadyChanged)

    def _get_route_defer_reason(self) -> str:
        return self._route_defer_reason

    routeDeferReason = Property(str, _get_route_defer_reason, notify=routeDeferReasonChanged)

    def _get_pending_context_json(self) -> str:
        return self._pending_context_json

    pendingContextJson = Property(str, _get_pending_context_json, notify=pendingContextJsonChanged)

    def _get_domain_nav_model(self) -> DomainNavModel:
        return self._domain_model

    domainNavModel = Property(QObject, _get_domain_nav_model, constant=True)

    def _get_workspace_nav_model(self) -> WorkspaceNavModel:
        return self._workspace_model

    workspaceNavModel = Property(QObject, _get_workspace_nav_model, notify=workspaceNavModelChanged)

    def apply_shell_state(
        self,
        *,
        active_top_area: str,
        active_workspace_id: str,
        stage_url: QUrl,
        legacy_active_domain: str,
        route_defer_reason: str,
        pending_context_json: str,
    ) -> None:
        dom_changed = self._active_domain != legacy_active_domain
        area_changed = self._active_top_area != active_top_area
        ws_changed = self._active_workspace_id != active_workspace_id
        url_changed = self._stage_url != stage_url
        defer_changed = self._route_defer_reason != route_defer_reason
        pend_changed = self._pending_context_json != pending_context_json

        self._active_top_area = active_top_area
        self._active_workspace_id = active_workspace_id
        self._active_domain = legacy_active_domain
        self._stage_url = stage_url
        self._route_defer_reason = route_defer_reason
        self._pending_context_json = pending_context_json

        if active_top_area == NavArea.OPERATIONS:
            self._workspace_model.set_entries(operations_workspace_entries())
        else:
            self._workspace_model.set_entries([])

        if area_changed:
            self.activeTopAreaChanged.emit()
            self.workspaceNavModelChanged.emit()
        if ws_changed:
            self.activeWorkspaceIdChanged.emit()
        if dom_changed:
            self.activeDomainChanged.emit()
        if url_changed:
            self.stageUrlChanged.emit()
        if defer_changed:
            self.routeDeferReasonChanged.emit()
        if pend_changed:
            self.pendingContextJsonChanged.emit()

        if dom_changed or area_changed or ws_changed or url_changed:
            if not self._shell_ready:
                self._shell_ready = True
                self.shellReadyChanged.emit()

    def initialize(self) -> None:
        self._presenter.navigate_to_default()

    @Slot(str)
    def requestDomainChange(self, domain_id: str) -> None:
        """Backward-compatible flat domain id (pre–Welle 1) or passthrough top area id."""
        if map_legacy_flat_domain(domain_id) is not None:
            self._presenter.navigate_legacy_flat_domain(domain_id)
            return
        if domain_id in {a for a, _ in NavArea.all_areas()}:
            from app.ui_runtime.qml.shell_route_catalog import default_workspace_for_area

            self._presenter.navigate_to_route(domain_id, default_workspace_for_area(domain_id))
            return
        logger.debug("requestDomainChange: unknown id %r", domain_id)

    @Slot(str, str)
    def requestRouteChange(self, area_id: str, workspace_id: str) -> None:
        """Canonical navigation: ``NavArea`` id + workspace id (empty for non-Operations areas)."""
        self._presenter.navigate_to_route(area_id, workspace_id or None, pending_context=None)

    @Slot(str, str, str)
    def requestRouteChangeWithContextJson(self, area_id: str, workspace_id: str, context_json: str) -> None:
        """
        Navigate and attach pending context for the target stage (JSON object string).

        Stages may read ``shell.pendingContextJson`` and call ``clearPendingContext`` when consumed.
        """
        ctx: dict | None = None
        raw = (context_json or "").strip()
        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    ctx = parsed
                else:
                    logger.debug("pending context JSON is not an object; ignoring")
            except json.JSONDecodeError:
                logger.debug("invalid pending context JSON; ignoring")
        self._presenter.navigate_to_route(area_id, workspace_id or None, pending_context=ctx)

    @Slot()
    def clearPendingContext(self) -> None:
        if self._pending_context_json:
            self._pending_context_json = ""
            self.pendingContextJsonChanged.emit()

    @Slot(str)
    def requestTopAreaChange(self, area_id: str) -> None:
        """User picked a primary nav entry — apply area default workspace."""
        from app.ui_runtime.qml.shell_route_catalog import default_workspace_for_area

        self._presenter.navigate_to_route(area_id, default_workspace_for_area(area_id))

    @Slot(str)
    def requestOperationsWorkspaceChange(self, workspace_id: str) -> None:
        """Switch Operations hub workspace without changing top area."""
        self._presenter.navigate_to_route(NavArea.OPERATIONS, workspace_id, pending_context=None)
