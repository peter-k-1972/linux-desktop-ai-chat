"""
ModelUsageSidebarHintPresenter — ein Befehl, ein String, ein Sink.
"""

from __future__ import annotations

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.ports.model_usage_gui_port import ModelUsageGuiReadPort
from app.ui_application.view_models.protocols import ModelUsageSidebarUiSink
from app.ui_contracts.workspaces.model_usage_sidebar import (
    ModelUsageSidebarCommand,
    ModelUsageSidebarHintState,
    RefreshModelUsageSidebarHintCommand,
)


class ModelUsageSidebarHintPresenter(BasePresenter):
    def __init__(
        self,
        sink: ModelUsageSidebarUiSink,
        port: ModelUsageGuiReadPort,
    ) -> None:
        super().__init__()
        self._sink = sink
        self._port = port

    def handle_command(self, command: ModelUsageSidebarCommand) -> None:
        if isinstance(command, RefreshModelUsageSidebarHintCommand):
            try:
                text = self._port.quick_sidebar_hint()
            except Exception:
                text = ""
            self._sink.apply_full_state(ModelUsageSidebarHintState(hint_text=text))
