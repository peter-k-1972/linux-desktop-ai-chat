"""PromptTestLab — Run-Pfad delegiert an Presenter (Batch 6)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.prompt_studio.panels.prompt_test_lab import PromptTestLab
from app.ui_contracts.workspaces.prompt_studio_test_lab import RunPromptTestLabCommand


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


async def test_run_via_presenter_awaits_handle_run_async(qapp: QApplication) -> None:
    lab = PromptTestLab()
    pr = MagicMock()
    pr.handle_run_async = AsyncMock()
    lab.attach_test_lab_presenter(pr)

    cmd = RunPromptTestLabCommand("m", "s", "u", 0.1, 8)
    await lab._run_via_presenter(cmd)
    pr.handle_run_async.assert_awaited_once_with(cmd)
