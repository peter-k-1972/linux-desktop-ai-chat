"""
SettingsModelRoutingPresenter — ModelSettingsPanel (Studio), Slice Routing/skalare LLM-Felder.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from app.ui_contracts.workspaces.settings_model_routing import (
    ApplyModelRoutingStudioPatchCommand,
    LoadModelRoutingStudioCommand,
    ModelRoutingStudioCommand,
    ModelRoutingStudioState,
)

if TYPE_CHECKING:
    from app.ui_application.ports.settings_operations_port import SettingsOperationsPort


class SettingsModelRoutingStudioSinkPort(Protocol):
    def apply_full_state(self, state: ModelRoutingStudioState) -> None: ...


class SettingsModelRoutingPresenter:
    def __init__(self, sink: SettingsModelRoutingStudioSinkPort, port: SettingsOperationsPort) -> None:
        self._sink = sink
        self._port = port

    def handle_command(self, command: ModelRoutingStudioCommand) -> None:
        if isinstance(command, LoadModelRoutingStudioCommand):
            st = self._port.load_model_routing_studio_state()
            self._sink.apply_full_state(st)
            return
        if isinstance(command, ApplyModelRoutingStudioPatchCommand):
            self._port.persist_model_routing_studio(command.patch)
            st = self._port.load_model_routing_studio_state()
            self._sink.apply_full_state(st)
