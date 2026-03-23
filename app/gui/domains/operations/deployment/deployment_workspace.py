"""R4: Deployment-Workspace unter Operations (Tabs Targets / Releases / Rollouts)."""

from PySide6.QtWidgets import QTabWidget, QVBoxLayout

from app.gui.domains.operations.deployment.panels.releases_panel import ReleasesPanel
from app.gui.domains.operations.deployment.panels.rollouts_panel import RolloutsPanel
from app.gui.domains.operations.deployment.panels.targets_panel import TargetsPanel
from app.gui.shared.base_operations_workspace import BaseOperationsWorkspace


class DeploymentWorkspace(BaseOperationsWorkspace):
    def __init__(self, parent=None):
        super().__init__("deployment", parent)
        self._tabs = QTabWidget()
        self._targets = TargetsPanel(self)
        self._releases = ReleasesPanel(self)
        self._rollouts = RolloutsPanel(self)
        self._tabs.addTab(self._targets, "Ziele")
        self._tabs.addTab(self._releases, "Releases")
        self._tabs.addTab(self._rollouts, "Rollouts")
        self._tabs.currentChanged.connect(self._on_tab)

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.addWidget(self._tabs, 1)
        self._targets.refresh()

    def _on_tab(self, index: int) -> None:
        if index == 0:
            self._targets.refresh()
        elif index == 1:
            self._releases.refresh()
        elif index == 2:
            self._rollouts.refresh()
