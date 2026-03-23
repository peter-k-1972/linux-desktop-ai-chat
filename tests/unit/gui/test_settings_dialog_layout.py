"""
Layout-/Spacing-Regression für SettingsDialog (Pilot-Refactor).
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def _close_coro_task(coro):
    """Avoid RuntimeWarning when ``asyncio.create_task`` is patched out."""
    try:
        coro.close()
    except Exception:
        pass
    return MagicMock()
from PySide6.QtWidgets import QFormLayout, QWidget

from app.core.config.settings import AppSettings
from app.gui.domains.settings.settings_dialog import SettingsDialog
from app.gui.shared.layout_constants import CARD_SPACING, DIALOG_CONTENT_PADDING
from app.gui.theme import design_metrics as dm


@pytest.fixture
def settings_dialog(qapplication):
    with patch(
        "app.gui.domains.settings.settings_dialog.asyncio.create_task",
        side_effect=_close_coro_task,
    ):
        dlg = SettingsDialog(AppSettings())
    yield dlg
    dlg.deleteLater()


def test_settings_dialog_instantiates(settings_dialog):
    assert settings_dialog.windowTitle() == "Einstellungen"
    assert settings_dialog.minimumWidth() == 420
    assert settings_dialog.minimumHeight() == 400


def test_settings_dialog_scroll_content_layout(settings_dialog):
    content = settings_dialog.findChild(QWidget, "settingsDialogContent")
    assert content is not None
    lay = content.layout()
    assert lay is not None
    m = lay.contentsMargins()
    assert m.left() == DIALOG_CONTENT_PADDING == dm.DIALOG_PADDING_PX == 24
    assert m.top() == 24 and m.right() == 24 and m.bottom() == 24
    assert lay.spacing() == CARD_SPACING == 16


def test_settings_dialog_main_form_policy(settings_dialog):
    content = settings_dialog.findChild(QWidget, "settingsDialogContent")
    lay = content.layout()
    form_item = lay.itemAt(0)
    assert form_item is not None
    form = form_item.layout()
    assert isinstance(form, QFormLayout)
    assert form.verticalSpacing() == dm.FORM_ROW_GAP_PX == 12
    assert form.horizontalSpacing() == dm.FORM_LABEL_GAP_PX == 8


def test_settings_dialog_button_bar_margins(settings_dialog):
    main = settings_dialog.layout()
    assert main is not None
    # Last item: button row layout
    item = main.itemAt(main.count() - 1)
    btn_lay = item.layout()
    assert btn_lay is not None
    m = btn_lay.contentsMargins()
    assert m.left() == dm.DIALOG_PADDING_PX == 24
    assert m.right() == 24
    assert m.top() == 0 and m.bottom() == 0
    assert btn_lay.spacing() == dm.SPACE_MD_PX == 12


def test_settings_dialog_footer_gap(settings_dialog):
    main = settings_dialog.layout()
    m = main.contentsMargins()
    assert m.bottom() == dm.DIALOG_FOOTER_TOP_GAP_PX == 12
