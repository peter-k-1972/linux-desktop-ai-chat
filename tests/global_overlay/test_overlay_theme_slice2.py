"""Slice 2: Overlay Theme — Adapter, Capabilities, Apply fail-closed."""

from __future__ import annotations

import pytest

from app.global_overlay.overlay_dialogs import StandardOverlayDialog
from app.global_overlay.overlay_theme_port import (
    ThemeApplyEffect,
    apply_theme_via_product,
    build_theme_overlay_snapshot,
)
from app.core.startup_contract import GUI_ID_DEFAULT_WIDGET, GUI_ID_LIBRARY_QML
from app.ui_application.adapters.service_settings_adapter import ServiceSettingsAdapter
from app.ui_contracts.workspaces.settings_appearance import SettingsAppearancePortError


@pytest.fixture
def infra_memory():
    from app.core.config.settings_backend import InMemoryBackend
    from app.services.infrastructure import get_infrastructure, init_infrastructure, set_infrastructure

    set_infrastructure(None)
    init_infrastructure(InMemoryBackend())
    yield get_infrastructure()
    set_infrastructure(None)


def test_theme_snapshot_widget_supports_switching(qapplication):
    snap = build_theme_overlay_snapshot(GUI_ID_DEFAULT_WIDGET)
    assert snap.switching_supported is True
    assert snap.active_gui_id == GUI_ID_DEFAULT_WIDGET
    assert snap.apply_effect == ThemeApplyEffect.IMMEDIATE
    assert snap.current_theme_id != ""
    assert len(snap.allowed_themes) >= 1


def test_theme_snapshot_qml_blocks_switching(qapplication):
    snap = build_theme_overlay_snapshot(GUI_ID_LIBRARY_QML)
    assert snap.switching_supported is False
    assert snap.allowed_themes == ()
    assert snap.switching_block_reason
    assert snap.apply_effect == ThemeApplyEffect.NOT_AVAILABLE


def test_apply_blocked_for_qml(qapplication):
    r = apply_theme_via_product(GUI_ID_LIBRARY_QML, "light_default")
    assert r.ok is False
    assert "not" in r.message.lower() or "GUI" in r.message


def test_apply_rejects_unknown_theme(qapplication, infra_memory):
    r = apply_theme_via_product(GUI_ID_DEFAULT_WIDGET, "totally_unknown_theme_id_xyz")
    assert r.ok is False
    assert "unknown" in r.message.lower() or "unregistered" in r.message.lower()


def test_apply_rejects_empty_selection(qapplication, infra_memory):
    r = apply_theme_via_product(GUI_ID_DEFAULT_WIDGET, "   ")
    assert r.ok is False


def test_apply_success_and_persist(qapplication, infra_memory):
    from app.gui.themes import get_theme_manager

    mgr = get_theme_manager()
    snap = build_theme_overlay_snapshot(GUI_ID_DEFAULT_WIDGET)
    assert len(snap.allowed_themes) >= 2
    a, b = snap.allowed_themes[0][0], snap.allowed_themes[1][0]
    target = b if mgr.get_current_id() == a else a
    before = mgr.get_current_id()
    res = apply_theme_via_product(GUI_ID_DEFAULT_WIDGET, target)
    assert res.ok, res.message
    assert mgr.get_current_id() == target
    assert infra_memory.settings.theme_id == target
    # restore
    apply_theme_via_product(GUI_ID_DEFAULT_WIDGET, before)
    assert mgr.get_current_id() == before


def test_apply_persist_failure_reverts_visual(qapplication, infra_memory, monkeypatch):
    from app.gui.themes import get_theme_manager

    mgr = get_theme_manager()
    before = mgr.get_current_id()
    snap = build_theme_overlay_snapshot(GUI_ID_DEFAULT_WIDGET)
    other = next(tid for tid, _ in snap.allowed_themes if tid != before)

    def _boom(self, theme_id: str) -> None:
        raise SettingsAppearancePortError("persist_failed", "disk full (test)")

    monkeypatch.setattr(ServiceSettingsAdapter, "persist_theme_choice", _boom)
    res = apply_theme_via_product(GUI_ID_DEFAULT_WIDGET, other)
    assert res.ok is False
    assert mgr.get_current_id() == before


def test_standard_overlay_theme_widgets_exist(qapplication):
    dlg = StandardOverlayDialog(None, active_gui_id=GUI_ID_DEFAULT_WIDGET)
    dlg.refresh_content()
    assert dlg._theme_group.title() == "Theme"
    assert dlg._theme_combo.count() >= 1
    dlg.close()
