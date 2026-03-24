"""ServiceSettingsAdapter — Persistenz und Registry (gemockte Infrastructure)."""

from __future__ import annotations

from dataclasses import replace
from typing import cast

import pytest

from app.ui_application.adapters.service_settings_adapter import ServiceSettingsAdapter
from app.ui_contracts.workspaces.settings_advanced import AdvancedSettingsWritePatch, SettingsAdvancedPortError
from app.ui_contracts.workspaces.settings_appearance import SettingsAppearancePortError
from app.ui_contracts.workspaces.settings_data import (
    DataSettingsWritePatch,
    PromptStorageType,
    SettingsDataPortError,
)
from app.ui_contracts.workspaces.settings_ai_models import (
    AiModelsScalarWritePatch,
    SettingsAiModelsPortError,
)
from app.ui_contracts.workspaces.settings_legacy_modal import (
    SettingsLegacyModalCommit,
    SettingsLegacyModalPortError,
)
from app.ui_contracts.workspaces.settings_model_routing import (
    ModelRoutingStudioWritePatch,
    SettingsModelRoutingPortError,
)


class _FakeSettings:
    def __init__(self) -> None:
        self.theme_id = "light_default"
        self.theme = "light"
        self.save_calls = 0
        self.fail_save = False

    def save(self) -> None:
        self.save_calls += 1
        if self.fail_save:
            raise OSError("mock io")


def test_validate_theme_id_known() -> None:
    ad = ServiceSettingsAdapter()
    assert ad.validate_theme_id("light_default") is True
    assert ad.validate_theme_id("not_a_real_theme_id_xyz") is False


def test_load_appearance_state_has_builtin_themes(monkeypatch) -> None:
    fake = _FakeSettings()

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    state = ad.load_appearance_state()
    assert len(state.themes) >= 3
    ids = {t.theme_id for t in state.themes}
    assert "light_default" in ids
    assert state.selected_theme_id in ids


def test_persist_theme_choice_updates_settings(monkeypatch) -> None:
    fake = _FakeSettings()

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    ad.persist_theme_choice("dark_default")
    assert fake.theme_id == "dark_default"
    assert fake.save_calls == 1


def test_persist_unknown_raises() -> None:
    ad = ServiceSettingsAdapter()
    with pytest.raises(SettingsAppearancePortError) as ei:
        ad.persist_theme_choice("totally_unknown_theme_12345")
    assert ei.value.code == "unknown_theme"


def test_persist_save_failure_raises(monkeypatch) -> None:
    fake = _FakeSettings()
    fake.fail_save = True

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    with pytest.raises(SettingsAppearancePortError) as ei:
        ad.persist_theme_choice("light_default")
    assert ei.value.code == "persist_failed"


class _FakeSettingsAdvanced:
    def __init__(self) -> None:
        self.debug_panel_enabled = True
        self.context_debug_enabled = False
        self.chat_context_mode = "semantic"
        self.save_calls = 0
        self.fail_save = False

    def save(self) -> None:
        self.save_calls += 1
        if self.fail_save:
            raise OSError("mock io")


def test_load_advanced_settings_state(monkeypatch) -> None:
    fake = _FakeSettingsAdvanced()

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    st = ad.load_advanced_settings_state()
    assert st.debug_panel_enabled is True
    assert st.context_debug_enabled is False
    assert st.chat_context_mode == "semantic"


def test_load_advanced_coerces_invalid_mode(monkeypatch) -> None:
    fake = _FakeSettingsAdvanced()
    fake.chat_context_mode = "not_a_mode"

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    st = ad.load_advanced_settings_state()
    assert st.chat_context_mode == "semantic"


def test_persist_advanced_empty_no_save(monkeypatch) -> None:
    fake = _FakeSettingsAdvanced()

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    ad.persist_advanced_settings(AdvancedSettingsWritePatch())
    assert fake.save_calls == 0


def test_persist_advanced_writes_and_saves(monkeypatch) -> None:
    fake = _FakeSettingsAdvanced()

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    ad.persist_advanced_settings(AdvancedSettingsWritePatch(debug_panel_enabled=False, chat_context_mode="off"))
    assert fake.debug_panel_enabled is False
    assert fake.chat_context_mode == "off"
    assert fake.save_calls == 1


def test_persist_advanced_invalid_mode_raises(monkeypatch) -> None:
    fake = _FakeSettingsAdvanced()

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    with pytest.raises(SettingsAdvancedPortError) as ei:
        ad.persist_advanced_settings(AdvancedSettingsWritePatch(chat_context_mode="invalid"))
    assert ei.value.code == "invalid_context_mode"


def test_persist_advanced_save_failure(monkeypatch) -> None:
    fake = _FakeSettingsAdvanced()
    fake.fail_save = True

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    with pytest.raises(SettingsAdvancedPortError) as ei:
        ad.persist_advanced_settings(AdvancedSettingsWritePatch(context_debug_enabled=True))
    assert ei.value.code == "persist_failed"


class _FakeSettingsData:
    def __init__(self) -> None:
        self.rag_enabled = False
        self.rag_space = "default"
        self.rag_top_k = 5
        self.self_improving_enabled = False
        self.prompt_storage_type = "database"
        self.prompt_directory = ""
        self.prompt_confirm_delete = True
        self.save_calls = 0
        self.fail_save = False

    def save(self) -> None:
        self.save_calls += 1
        if self.fail_save:
            raise OSError("mock io")


def test_load_data_settings_state(monkeypatch) -> None:
    fake = _FakeSettingsData()

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    st = ad.load_data_settings_state()
    assert st.rag_space == "default"
    assert st.rag_top_k == 5
    assert st.prompt_storage_type == "database"


def test_load_data_coerces_unknown_rag_space(monkeypatch) -> None:
    fake = _FakeSettingsData()
    fake.rag_space = "unknown_xyz"

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    st = ad.load_data_settings_state()
    assert st.rag_space == "default"


def test_load_data_clamps_rag_top_k(monkeypatch) -> None:
    fake = _FakeSettingsData()
    fake.rag_top_k = 999

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    st = ad.load_data_settings_state()
    assert st.rag_top_k == 20


def test_persist_data_empty_no_save(monkeypatch) -> None:
    fake = _FakeSettingsData()

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    ad.persist_data_settings(DataSettingsWritePatch())
    assert fake.save_calls == 0


def test_persist_data_directory_only_flag(monkeypatch) -> None:
    fake = _FakeSettingsData()

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    ad.persist_data_settings(
        DataSettingsWritePatch(prompt_directory="/data/prompts", prompt_directory_set=True),
    )
    assert fake.prompt_directory == "/data/prompts"
    assert fake.save_calls == 1


def test_persist_data_invalid_rag_space_raises(monkeypatch) -> None:
    fake = _FakeSettingsData()

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    with pytest.raises(SettingsDataPortError) as ei:
        ad.persist_data_settings(DataSettingsWritePatch(rag_space="bad"))
    assert ei.value.code == "invalid_rag_space"


def test_persist_data_invalid_prompt_storage_raises(monkeypatch) -> None:
    fake = _FakeSettingsData()

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    with pytest.raises(SettingsDataPortError) as ei:
        ad.persist_data_settings(
            DataSettingsWritePatch(prompt_storage_type=cast(PromptStorageType, "filesystem")),
        )
    assert ei.value.code == "invalid_prompt_storage"


def test_persist_data_save_failure(monkeypatch) -> None:
    fake = _FakeSettingsData()
    fake.fail_save = True

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    with pytest.raises(SettingsDataPortError) as ei:
        ad.persist_data_settings(DataSettingsWritePatch(rag_enabled=True))
    assert ei.value.code == "persist_failed"


class _FakeSettingsAiModels:
    def __init__(self) -> None:
        self.temperature = 0.7
        self.max_tokens = 4096
        self.think_mode = "auto"
        self.chat_streaming_enabled = True
        self.save_calls = 0
        self.fail_save = False

    def save(self) -> None:
        self.save_calls += 1
        if self.fail_save:
            raise OSError("mock io")


def test_load_ai_models_scalar_state(monkeypatch) -> None:
    fake = _FakeSettingsAiModels()
    fake.temperature = 1.5
    fake.max_tokens = 1024
    fake.think_mode = "high"
    fake.chat_streaming_enabled = False

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    st = ad.load_ai_models_scalar_state()
    assert st.temperature == 1.5
    assert st.max_tokens == 1024
    assert st.think_mode == "high"
    assert st.chat_streaming_enabled is False


def test_load_ai_models_scalar_coerce_invalid_think_mode(monkeypatch) -> None:
    fake = _FakeSettingsAiModels()
    fake.think_mode = "invalid_xyz"

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    st = ad.load_ai_models_scalar_state()
    assert st.think_mode == "auto"


def test_load_ai_models_scalar_clamp_temperature(monkeypatch) -> None:
    fake = _FakeSettingsAiModels()
    fake.temperature = 99.0

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    st = ad.load_ai_models_scalar_state()
    assert st.temperature == 2.0


def test_persist_ai_models_scalar_empty_no_save(monkeypatch) -> None:
    fake = _FakeSettingsAiModels()

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    ad.persist_ai_models_scalar(AiModelsScalarWritePatch())
    assert fake.save_calls == 0


def test_persist_ai_models_scalar_updates(monkeypatch) -> None:
    fake = _FakeSettingsAiModels()

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    ad.persist_ai_models_scalar(
        AiModelsScalarWritePatch(temperature=0.2, max_tokens=512, think_mode="off", chat_streaming_enabled=True),
    )
    assert fake.temperature == 0.2
    assert fake.max_tokens == 512
    assert fake.think_mode == "off"
    assert fake.chat_streaming_enabled is True
    assert fake.save_calls == 1


def test_persist_ai_models_invalid_think_mode_raises(monkeypatch) -> None:
    fake = _FakeSettingsAiModels()

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    with pytest.raises(SettingsAiModelsPortError) as ei:
        ad.persist_ai_models_scalar(AiModelsScalarWritePatch(think_mode="bogus"))
    assert ei.value.code == "invalid_think_mode"


def test_persist_ai_models_save_failure(monkeypatch) -> None:
    fake = _FakeSettingsAiModels()
    fake.fail_save = True

    class _Infra:
        settings = fake

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: _Infra(),
    )
    ad = ServiceSettingsAdapter()
    with pytest.raises(SettingsAiModelsPortError) as ei:
        ad.persist_ai_models_scalar(AiModelsScalarWritePatch(temperature=0.1))
    assert ei.value.code == "persist_failed"


def _base_legacy_modal_commit() -> SettingsLegacyModalCommit:
    return SettingsLegacyModalCommit(
        model_id="llama2",
        temperature=0.5,
        max_tokens=2048,
        legacy_theme="light",
        think_mode="auto",
        auto_routing=True,
        cloud_escalation=False,
        cloud_via_local=False,
        overkill_mode=False,
        rag_enabled=True,
        rag_space="documentation",
        rag_top_k=7,
        self_improving_enabled=True,
        debug_panel_enabled=False,
        prompt_storage_type="directory",
        prompt_directory="/tmp/p",
        prompt_confirm_delete=False,
        ollama_api_key="secret",
    )


def test_persist_legacy_modal_inmemory_roundtrip() -> None:
    from app.core.config.settings import AppSettings
    from app.core.config.settings_backend import InMemoryBackend

    backend = InMemoryBackend()
    s = AppSettings(backend)
    ad = ServiceSettingsAdapter()
    c = _base_legacy_modal_commit()
    ad.persist_legacy_modal_settings(s, c)
    s2 = AppSettings(backend)
    assert s2.model == "llama2"
    assert s2.temperature == 0.5
    assert s2.max_tokens == 2048
    assert s2.theme == "light"
    assert s2.think_mode == "auto"
    assert s2.auto_routing is True
    assert s2.cloud_escalation is False
    assert s2.cloud_via_local is False
    assert s2.overkill_mode is False
    assert s2.rag_enabled is True
    assert s2.rag_space == "documentation"
    assert s2.rag_top_k == 7
    assert s2.self_improving_enabled is True
    assert s2.debug_panel_enabled is False
    assert s2.prompt_storage_type == "directory"
    assert s2.prompt_directory == "/tmp/p"
    assert s2.prompt_confirm_delete is False
    assert s2.ollama_api_key == "secret"


def test_persist_legacy_modal_invalid_rag_space_raises() -> None:
    from app.core.config.settings import AppSettings

    s = AppSettings()
    ad = ServiceSettingsAdapter()
    c = replace(_base_legacy_modal_commit(), rag_space="unknown_space")
    with pytest.raises(SettingsLegacyModalPortError) as ei:
        ad.persist_legacy_modal_settings(s, c)
    assert ei.value.code == "invalid_rag_space"


def test_persist_legacy_modal_invalid_think_mode_raises() -> None:
    from app.core.config.settings import AppSettings

    s = AppSettings()
    ad = ServiceSettingsAdapter()
    c = replace(_base_legacy_modal_commit(), think_mode="not_a_mode")
    with pytest.raises(SettingsLegacyModalPortError) as ei:
        ad.persist_legacy_modal_settings(s, c)
    assert ei.value.code == "invalid_think_mode"


def test_persist_legacy_modal_clamps_temperature_and_top_k() -> None:
    from app.core.config.settings import AppSettings
    from app.core.config.settings_backend import InMemoryBackend

    backend = InMemoryBackend()
    s = AppSettings(backend)
    ad = ServiceSettingsAdapter()
    c = replace(_base_legacy_modal_commit(), temperature=99.0, rag_top_k=999)
    ad.persist_legacy_modal_settings(s, c)
    s2 = AppSettings(backend)
    assert s2.temperature == 2.0
    assert s2.rag_top_k == 20


def test_load_model_routing_studio_state(monkeypatch) -> None:
    class S:
        model = "m1"
        auto_routing = True
        cloud_escalation = False
        cloud_via_local = False
        web_search = False
        overkill_mode = False
        default_role = "DEFAULT"
        temperature = 0.8
        top_p = 0.88
        max_tokens = 2048
        llm_timeout_seconds = 90
        retry_without_thinking = False
        chat_streaming_enabled = True

    class Inf:
        settings = S()

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: Inf(),
    )
    ad = ServiceSettingsAdapter()
    st = ad.load_model_routing_studio_state()
    assert st.model == "m1"
    assert st.temperature == 0.8
    assert st.default_role == "DEFAULT"
    assert st.top_p == 0.88
    assert st.llm_timeout_seconds == 90
    assert st.retry_without_thinking is False


def test_persist_model_routing_studio_partial(monkeypatch) -> None:
    class S:
        model = "old"
        auto_routing = True
        cloud_escalation = False
        cloud_via_local = False
        web_search = False
        overkill_mode = False
        default_role = "DEFAULT"
        temperature = 0.7
        top_p = 1.0
        max_tokens = 4096
        llm_timeout_seconds = 0
        retry_without_thinking = True
        chat_streaming_enabled = True
        save_calls = 0

        def save(self) -> None:
            self.save_calls += 1

    s = S()

    class Inf:
        settings = s

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: Inf(),
    )
    ad = ServiceSettingsAdapter()
    ad.persist_model_routing_studio(ModelRoutingStudioWritePatch(model="new_id"))
    assert s.model == "new_id"
    assert s.save_calls == 1


def test_persist_model_routing_studio_scalars_top_p_timeout_retry(monkeypatch) -> None:
    class S:
        model = "m"
        auto_routing = True
        cloud_escalation = False
        cloud_via_local = False
        web_search = False
        overkill_mode = False
        default_role = "DEFAULT"
        temperature = 0.7
        top_p = 1.0
        max_tokens = 4096
        llm_timeout_seconds = 0
        retry_without_thinking = True
        chat_streaming_enabled = True
        save_calls = 0

        def save(self) -> None:
            self.save_calls += 1

    s = S()

    class Inf:
        settings = s

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: Inf(),
    )
    ad = ServiceSettingsAdapter()
    ad.persist_model_routing_studio(
        ModelRoutingStudioWritePatch(top_p=0.5, llm_timeout_seconds=45, retry_without_thinking=False),
    )
    assert s.top_p == 0.5
    assert s.llm_timeout_seconds == 45
    assert s.retry_without_thinking is False
    assert s.save_calls == 1


def test_persist_model_routing_invalid_role_raises(monkeypatch) -> None:
    class S:
        def save(self) -> None:
            pass

    class Inf:
        settings = S()

    monkeypatch.setattr(
        "app.ui_application.adapters.service_settings_adapter.get_infrastructure",
        lambda: Inf(),
    )
    ad = ServiceSettingsAdapter()
    with pytest.raises(SettingsModelRoutingPortError) as ei:
        ad.persist_model_routing_studio(ModelRoutingStudioWritePatch(default_role="NOT_A_ROLE"))
    assert ei.value.code == "invalid_default_role"
