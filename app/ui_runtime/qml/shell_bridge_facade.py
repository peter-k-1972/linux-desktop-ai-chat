"""
Single QML context object for shell routing (Slice 0/1).

Exposed as context property ``shell``. No services, no domain logic.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot

from app.ui_runtime.qml.domain_nav_model import DomainNavModel
from app.ui_runtime.qml.presenters.shell_presenter import ShellPresenter
from app.ui_runtime.qml.shell_navigation_state import domain_entries


class ShellBridgeFacade(QObject):
    activeDomainChanged = Signal()
    stageUrlChanged = Signal()
    shellReadyChanged = Signal()

    def __init__(self, qml_root: Path, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._qml_root = Path(qml_root)
        self._active_domain = ""
        self._stage_url = QUrl()
        self._shell_ready = False
        self._domain_model = DomainNavModel(domain_entries(), self)
        self._presenter = ShellPresenter(self, self._qml_root)

    def _get_active_domain(self) -> str:
        return self._active_domain

    activeDomain = Property(str, _get_active_domain, notify=activeDomainChanged)

    def _get_stage_url(self) -> QUrl:
        return self._stage_url

    stageUrl = Property(QUrl, _get_stage_url, notify=stageUrlChanged)

    def _get_shell_ready(self) -> bool:
        return self._shell_ready

    shellReady = Property(bool, _get_shell_ready, notify=shellReadyChanged)

    def _get_domain_nav_model(self) -> DomainNavModel:
        return self._domain_model

    domainNavModel = Property(QObject, _get_domain_nav_model, constant=True)

    def apply_shell_state(self, domain_id: str, stage_url: QUrl) -> None:
        dom_changed = self._active_domain != domain_id
        url_changed = self._stage_url != stage_url
        if dom_changed:
            self._active_domain = domain_id
            self.activeDomainChanged.emit()
        if url_changed:
            self._stage_url = stage_url
            self.stageUrlChanged.emit()
        if dom_changed or url_changed:
            if not self._shell_ready:
                self._shell_ready = True
                self.shellReadyChanged.emit()

    def initialize(self) -> None:
        self._presenter.navigate_to_default()

    @Slot(str)
    def requestDomainChange(self, domain_id: str) -> None:
        self._presenter.navigate_to(domain_id)
