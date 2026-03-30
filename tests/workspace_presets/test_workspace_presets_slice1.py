"""Slice 1: Workspace Presets — Modell, Registry, Validierung."""

from __future__ import annotations

import pytest

from app.core.startup_contract import GUI_ID_DEFAULT_WIDGET, list_registered_gui_ids
from app.workspace_presets.preset_models import (
    DEFAULT_CONTEXT_PROFILE,
    DEFAULT_LAYOUT_MODE,
    PresetReleaseStatus,
    WorkspacePreset,
)
from app.workspace_presets.preset_registry import (
    REGISTERED_PRESETS_BY_ID,
    PRESET_ID_CHAT_FOCUS,
    canonical_workspace_preset_ids,
    get_default_workspace_preset_id,
    get_workspace_preset,
    list_approved_workspace_presets,
    list_workspace_preset_ids,
    list_workspace_presets,
)
from app.workspace_presets.preset_validation import (
    collect_all_validation_errors,
    validate_workspace_preset,
)


def test_workspace_preset_defaults_and_strip_preset_id():
    p = WorkspacePreset(
        preset_id="  test_id  ",
        display_name="T",
        description="D",
        gui_id=GUI_ID_DEFAULT_WIDGET,
        theme_id="light_default",
        start_domain="operations_chat",
        requires_restart=False,
        release_status=PresetReleaseStatus.DRAFT,
        compatible_app_versions=("0.9.1",),
    )
    assert p.preset_id == "test_id"
    assert p.layout_mode == DEFAULT_LAYOUT_MODE
    assert p.context_profile == DEFAULT_CONTEXT_PROFILE


def test_workspace_preset_rejects_empty_preset_id():
    with pytest.raises(ValueError, match="preset_id"):
        WorkspacePreset(
            preset_id="",
            display_name="T",
            description="D",
            gui_id=GUI_ID_DEFAULT_WIDGET,
            theme_id="light_default",
            start_domain="operations_chat",
            requires_restart=False,
            release_status=PresetReleaseStatus.APPROVED,
            compatible_app_versions=("0.9.1",),
        )


def test_preset_release_status_values():
    assert PresetReleaseStatus.DRAFT.value == "draft"
    assert PresetReleaseStatus.CANDIDATE.value == "candidate"
    assert PresetReleaseStatus.APPROVED.value == "approved"
    assert PresetReleaseStatus.DEPRECATED.value == "deprecated"


def test_registry_lookup_and_unique_ids():
    ids = list_workspace_preset_ids()
    assert len(ids) == len(set(ids))
    p = get_workspace_preset(PRESET_ID_CHAT_FOCUS)
    assert p.preset_id == PRESET_ID_CHAT_FOCUS
    assert p in list_workspace_presets()


def test_canonical_presets_all_present():
    canon = canonical_workspace_preset_ids()
    for pid in canon:
        assert pid in REGISTERED_PRESETS_BY_ID


def test_list_approved_includes_slice1_presets():
    approved = list_approved_workspace_presets()
    assert all(p.release_status == PresetReleaseStatus.APPROVED for p in approved)
    assert len(approved) == len(REGISTERED_PRESETS_BY_ID)


def test_default_workspace_preset_id():
    assert get_default_workspace_preset_id() == PRESET_ID_CHAT_FOCUS


def test_validation_unknown_gui():
    bad = WorkspacePreset(
        preset_id="bad_gui",
        display_name="X",
        description="Y",
        gui_id="nonexistent_gui_xyz",
        theme_id="light_default",
        start_domain="operations_chat",
        requires_restart=True,
        release_status=PresetReleaseStatus.DRAFT,
        compatible_app_versions=("0.9.1",),
    )
    errs = validate_workspace_preset(bad)
    assert any("unknown gui_id" in e for e in errs)


def test_validation_unknown_start_domain():
    bad = WorkspacePreset(
        preset_id="bad_domain",
        display_name="X",
        description="Y",
        gui_id=GUI_ID_DEFAULT_WIDGET,
        theme_id="light_default",
        start_domain="not_a_real_nav_entry_ever",
        requires_restart=False,
        release_status=PresetReleaseStatus.APPROVED,
        compatible_app_versions=("0.9.1",),
    )
    errs = validate_workspace_preset(bad)
    assert any("unknown start_domain" in e for e in errs)


def test_validation_unknown_theme():
    bad = WorkspacePreset(
        preset_id="bad_theme",
        display_name="X",
        description="Y",
        gui_id=GUI_ID_DEFAULT_WIDGET,
        theme_id="fantasy_theme_9000",
        start_domain="settings",
        requires_restart=False,
        release_status=PresetReleaseStatus.APPROVED,
        compatible_app_versions=("0.9.1",),
    )
    errs = validate_workspace_preset(bad)
    assert any("registered product theme" in e or "fantasy_theme_9000" in e for e in errs)


def test_validation_empty_compatible_versions():
    bad = WorkspacePreset(
        preset_id="no_compat",
        display_name="X",
        description="Y",
        gui_id=GUI_ID_DEFAULT_WIDGET,
        theme_id="light_default",
        start_domain="settings",
        requires_restart=False,
        release_status=PresetReleaseStatus.APPROVED,
        compatible_app_versions=(),
    )
    errs = validate_workspace_preset(bad)
    assert any("compatible_app_versions" in e for e in errs)


def test_validation_invalid_layout_mode():
    bad = WorkspacePreset(
        preset_id="bad_layout",
        display_name="X",
        description="Y",
        gui_id=GUI_ID_DEFAULT_WIDGET,
        theme_id="light_default",
        start_domain="operations_chat",
        layout_mode="mega_layout_ultra",
        requires_restart=False,
        release_status=PresetReleaseStatus.APPROVED,
        compatible_app_versions=("0.9.1",),
    )
    errs = validate_workspace_preset(bad)
    assert any("layout_mode" in e for e in errs)


def test_validation_invalid_release_status_string():
    # Dataclass erzwingt keinen Enum-Typ zur Laufzeit — Validator muss fangen.
    bad = WorkspacePreset(
        preset_id="bad_status",
        display_name="X",
        description="Y",
        gui_id=GUI_ID_DEFAULT_WIDGET,
        theme_id="light_default",
        start_domain="operations_chat",
        requires_restart=False,
        release_status="not_a_status",  # type: ignore[arg-type]
        compatible_app_versions=("0.9.1",),
    )
    errs = validate_workspace_preset(bad)
    assert any("release_status" in e for e in errs)


def test_collect_all_validation_errors_registry_mismatch():
    p = WorkspacePreset(
        preset_id="key_mismatch",
        display_name="X",
        description="Y",
        gui_id=GUI_ID_DEFAULT_WIDGET,
        theme_id="light_default",
        start_domain="operations_chat",
        requires_restart=False,
        release_status=PresetReleaseStatus.APPROVED,
        compatible_app_versions=("0.9.1",),
    )
    fake_reg = {"wrong_key": p}
    errs = collect_all_validation_errors(fake_reg)
    assert any("registry keys" in e for e in errs)


def test_known_gui_ids_cover_registry_presets():
    registered = list_registered_gui_ids()
    for p in REGISTERED_PRESETS_BY_ID.values():
        assert p.gui_id in registered
