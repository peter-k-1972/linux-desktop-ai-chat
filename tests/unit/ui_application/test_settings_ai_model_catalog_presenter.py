"""SettingsAiModelCatalogPresenter — async Load, Retry, Persist."""

from __future__ import annotations

import pytest

from app.ui_application.presenters.settings_ai_model_catalog_presenter import (
    SettingsAiModelCatalogPresenter,
)
from app.ui_contracts.workspaces.settings_ai_model_catalog import (
    AI_MODEL_CATALOG_PLACEHOLDER_EMPTY_USABLE,
    AI_MODEL_CATALOG_PLACEHOLDER_LOADING,
    AiModelCatalogEntryDto,
    AiModelCatalogPortLoadOutcome,
    AiModelCatalogState,
    LoadAiModelCatalogCommand,
    PersistAiModelSelectionCommand,
    RetryAiModelCatalogCommand,
)


class _Sink:
    def __init__(self) -> None:
        self.states: list[AiModelCatalogState] = []

    def apply_full_catalog_state(self, state: AiModelCatalogState) -> None:
        self.states.append(state)


class _FakePort:
    def __init__(self, outcome: AiModelCatalogPortLoadOutcome) -> None:
        self.outcome = outcome
        self.load_calls = 0
        self.persisted: list[str] = []

    async def load_chat_selectable_catalog_for_settings(self) -> AiModelCatalogPortLoadOutcome:
        self.load_calls += 1
        return self.outcome

    def persist_default_chat_model_id(self, model_id: str) -> None:
        self.persisted.append(model_id)


def _sample_entry(sid: str = "llama3") -> AiModelCatalogEntryDto:
    return AiModelCatalogEntryDto(
        selection_id=sid,
        display_short=sid,
        display_detail="",
        chat_selectable=True,
        asset_type="",
        storage_root_name="",
        path_hint="",
        usage_summary="",
        quota_summary="",
        usage_quality_note="",
    )


@pytest.mark.asyncio
async def test_load_happy_path_shows_entries_then_ready() -> None:
    outcome = AiModelCatalogPortLoadOutcome(
        status="success_entries",
        entries=(_sample_entry(),),
        default_selection_id="llama3",
        placeholder_line="",
    )
    sink = _Sink()
    port = _FakePort(outcome)
    pres = SettingsAiModelCatalogPresenter(sink, port, _NoopScheduler())
    await pres.run_catalog_load_once()
    assert len(sink.states) == 2
    assert sink.states[0].phase == "loading"
    assert sink.states[0].placeholder_line == AI_MODEL_CATALOG_PLACEHOLDER_LOADING
    assert sink.states[1].phase == "ready"
    assert sink.states[1].display_mode == "combo_entries"
    assert len(sink.states[1].entries) == 1
    assert port.load_calls == 1


@pytest.mark.asyncio
async def test_load_empty_usable_placeholder() -> None:
    outcome = AiModelCatalogPortLoadOutcome(
        status="success_empty_usable",
        entries=(),
        default_selection_id="",
        placeholder_line=AI_MODEL_CATALOG_PLACEHOLDER_EMPTY_USABLE,
    )
    sink = _Sink()
    pres = SettingsAiModelCatalogPresenter(sink, _FakePort(outcome), _NoopScheduler())
    await pres.run_catalog_load_once()
    assert sink.states[-1].display_mode == "combo_placeholder"
    assert sink.states[-1].placeholder_line == AI_MODEL_CATALOG_PLACEHOLDER_EMPTY_USABLE


@pytest.mark.asyncio
async def test_load_operational_error_placeholder() -> None:
    outcome = AiModelCatalogPortLoadOutcome(
        status="failure_operational_error",
        entries=(),
        default_selection_id="",
        placeholder_line="(db)",
    )
    sink = _Sink()
    pres = SettingsAiModelCatalogPresenter(sink, _FakePort(outcome), _NoopScheduler())
    await pres.run_catalog_load_once()
    assert sink.states[-1].placeholder_line == "(db)"


@pytest.mark.asyncio
async def test_retry_triggers_scheduled_load() -> None:
    outcome = AiModelCatalogPortLoadOutcome(
        status="success_entries",
        entries=(_sample_entry(),),
        default_selection_id="",
        placeholder_line="",
    )
    sink = _Sink()
    port = _FakePort(outcome)
    sched = _CaptureScheduler()
    pres = SettingsAiModelCatalogPresenter(sink, port, sched)
    pres.handle_command(RetryAiModelCatalogCommand())
    assert len(sched.factories) == 1
    await sched.factories[0]()
    assert port.load_calls == 1


def test_persist_delegates_to_port() -> None:
    outcome = AiModelCatalogPortLoadOutcome(
        status="success_empty_usable",
        entries=(),
        default_selection_id="",
        placeholder_line="x",
    )
    sink = _Sink()
    port = _FakePort(outcome)
    pres = SettingsAiModelCatalogPresenter(sink, port, _NoopScheduler())
    pres.handle_command(PersistAiModelSelectionCommand("my-model"))
    assert port.persisted == ["my-model"]


def test_load_command_schedules() -> None:
    outcome = AiModelCatalogPortLoadOutcome(
        status="success_entries",
        entries=(_sample_entry(),),
        default_selection_id="",
        placeholder_line="",
    )
    sink = _Sink()
    port = _FakePort(outcome)
    sched = _CaptureScheduler()
    pres = SettingsAiModelCatalogPresenter(sink, port, sched)
    pres.handle_command(LoadAiModelCatalogCommand())
    assert len(sched.factories) == 1


class _NoopScheduler:
    def schedule(self, coroutine_factory) -> None:  # noqa: ANN001
        del coroutine_factory


class _CaptureScheduler:
    def __init__(self) -> None:
        self.factories: list = []

    def schedule(self, coroutine_factory) -> None:
        self.factories.append(coroutine_factory)
