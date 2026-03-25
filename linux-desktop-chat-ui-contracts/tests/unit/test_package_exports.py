"""Minimaler Smoke-Test ohne Host-`app.gui`."""

from __future__ import annotations

import app.ui_contracts as uc


def test_root_exports_chat_and_settings_error_info():
    assert uc.ChatWorkspaceState is not None
    assert uc.SettingsErrorInfo is not None
    assert uc.ChatUiEvent is not None
