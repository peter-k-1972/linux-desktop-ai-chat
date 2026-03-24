"""
SettingsAiModelCatalogPresenter — async Unified Catalog (Slice 4b).

Orchestriert Ladezustand → Port → Sink; Persistenz des Standardmodells synchron über den Port.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.view_models.protocols import SettingsAiModelCatalogUiSink
from app.ui_contracts.workspaces.settings_ai_model_catalog import (
    AI_MODEL_CATALOG_PLACEHOLDER_LOADING,
    AiModelCatalogCommand,
    AiModelCatalogPortLoadOutcome,
    AiModelCatalogState,
    LoadAiModelCatalogCommand,
    PersistAiModelSelectionCommand,
    RetryAiModelCatalogCommand,
)

if TYPE_CHECKING:
    from app.ui_application.ports.ai_model_catalog_port import AiModelCatalogPort, UiCoroutineScheduler


class SettingsAiModelCatalogPresenter(BasePresenter):
    def __init__(
        self,
        sink: SettingsAiModelCatalogUiSink,
        port: AiModelCatalogPort,
        scheduler: UiCoroutineScheduler,
    ) -> None:
        super().__init__()
        self._sink = sink
        self._port = port
        self._scheduler = scheduler

    @staticmethod
    def _loading_state(default_selection_id: str = "") -> AiModelCatalogState:
        return AiModelCatalogState(
            phase="loading",
            entries=(),
            default_selection_id=default_selection_id,
            display_mode="combo_placeholder",
            placeholder_line=AI_MODEL_CATALOG_PLACEHOLDER_LOADING,
        )

    @staticmethod
    def _outcome_to_state(outcome: AiModelCatalogPortLoadOutcome) -> AiModelCatalogState:
        if outcome.status == "success_entries":
            return AiModelCatalogState(
                phase="ready",
                entries=outcome.entries,
                default_selection_id=outcome.default_selection_id,
                display_mode="combo_entries",
                placeholder_line="",
            )
        return AiModelCatalogState(
            phase="ready",
            entries=(),
            default_selection_id=outcome.default_selection_id,
            display_mode="combo_placeholder",
            placeholder_line=outcome.placeholder_line,
        )

    def handle_command(self, command: AiModelCatalogCommand) -> None:
        if isinstance(command, PersistAiModelSelectionCommand):
            self._port.persist_default_chat_model_id(command.model_id)
            return
        if isinstance(command, (LoadAiModelCatalogCommand, RetryAiModelCatalogCommand)):
            self._scheduler.schedule(self.run_catalog_load_once)
            return

    async def run_catalog_load_once(self) -> None:
        """Von :class:`UiCoroutineScheduler` aufgerufen; direkt in Tests await-bar."""
        self._sink.apply_full_catalog_state(self._loading_state())
        outcome = await self._port.load_chat_selectable_catalog_for_settings()
        self._sink.apply_full_catalog_state(self._outcome_to_state(outcome))
