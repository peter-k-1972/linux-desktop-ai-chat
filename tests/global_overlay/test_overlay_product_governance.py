"""Product governance: capabilities, overlay shortcuts, canonical launcher, host gui sync."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QWidget

from app.global_overlay import detach_global_overlay_host
from app.global_overlay.overlay_host import install_global_overlay_host, shortcut_sequences
from app.global_overlay.overlay_product_shortcuts import (
    OVERLAY_TOGGLE_EMERGENCY_SHORTCUT,
    OVERLAY_TOGGLE_NORMAL_SHORTCUT,
    all_reserved_overlay_sequence_strings,
    assert_reserved_overlay_sequences_are_unique,
    shortcut_sequences_for_host,
)
from app.global_overlay.product_launcher import (
    CANONICAL_GUI_LAUNCHER_SCRIPT,
    canonical_gui_launcher_is_present,
    resolve_canonical_gui_launcher_path,
)
from app.gui_capabilities import KNOWN_GUI_CAPABILITY_NAMES
from app.gui_registry import GUI_ID_DEFAULT_WIDGET, GUI_ID_LIBRARY_QML


@pytest.fixture(autouse=True)
def _detach_host(qapplication):
    yield
    detach_global_overlay_host(qapplication)
    QApplication.processEvents()


def test_no_supports_global_overlay_capability_name():
    assert "supports_global_overlay" not in KNOWN_GUI_CAPABILITY_NAMES


def test_reserved_overlay_shortcuts_unique_and_stable():
    assert_reserved_overlay_sequences_are_unique()
    seqs = all_reserved_overlay_sequence_strings()
    assert OVERLAY_TOGGLE_NORMAL_SHORTCUT in seqs
    assert OVERLAY_TOGGLE_EMERGENCY_SHORTCUT in seqs
    assert shortcut_sequences() == shortcut_sequences_for_host()


def test_canonical_gui_launcher_path_matches_repo_layout():
    p = resolve_canonical_gui_launcher_path()
    assert p.name == CANONICAL_GUI_LAUNCHER_SCRIPT
    assert canonical_gui_launcher_is_present()


def test_overlay_host_syncs_active_gui_on_repeat_install(qapplication):
    w = QWidget()
    h = install_global_overlay_host(
        qapplication, active_gui_id=GUI_ID_DEFAULT_WIDGET, primary_window=w
    )
    assert h.active_gui_id == GUI_ID_DEFAULT_WIDGET
    install_global_overlay_host(qapplication, active_gui_id=GUI_ID_LIBRARY_QML, primary_window=w)
    assert h.active_gui_id == GUI_ID_LIBRARY_QML
