"""Header-Profile (standard / compact / ultra) — Phase-2 Layout-Pilot."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QVBoxLayout

from app.gui.shared.layout_constants import apply_header_profile_margins
from app.gui.theme import design_metrics as dm


@pytest.mark.parametrize(
    ("profile", "expected"),
    [
        ("standard", dm.HEADER_STANDARD_MARGINS),
        ("compact", dm.HEADER_COMPACT_MARGINS),
        ("ultra", dm.HEADER_ULTRA_MARGINS),
    ],
)
def test_apply_header_profile_margins(qapplication, profile, expected):
    lay = QVBoxLayout()
    apply_header_profile_margins(lay, profile)
    m = lay.contentsMargins()
    l, t, r, b = expected
    assert (m.left(), m.top(), m.right(), m.bottom()) == (l, t, r, b)


def test_panel_header_uses_standard_profile(qapplication):
    from app.gui.workbench.ui.panel_header import PanelHeader

    h = PanelHeader("T", "S")
    lay = h.layout()
    m = lay.contentsMargins()
    assert (m.left(), m.top(), m.right(), m.bottom()) == dm.HEADER_STANDARD_MARGINS
    assert lay.spacing() == dm.SPACE_2XS_PX
    h.deleteLater()


def test_context_action_bar_uses_ultra_profile(qapplication):
    from unittest.mock import MagicMock

    from app.gui.workbench.ui.context_action_bar import ContextActionBar

    win = MagicMock()
    win.focus_controller.active_object = MagicMock()
    win.focus_controller.active_object.is_empty = lambda: True
    bar = ContextActionBar(win)
    lay = bar.layout()
    m = lay.contentsMargins()
    assert (m.left(), m.top(), m.right(), m.bottom()) == dm.HEADER_ULTRA_MARGINS
    assert lay.spacing() == dm.SPACE_SM_PX
    bar.deleteLater()


def test_workflow_canvas_header_uses_compact_profile(qapplication):
    from app.gui.workbench.workflows.workflow_header import WorkflowCanvasHeader

    h = WorkflowCanvasHeader("T", None, [])
    lay = h.layout()
    m = lay.contentsMargins()
    assert (m.left(), m.top(), m.right(), m.bottom()) == dm.HEADER_COMPACT_MARGINS
    h.deleteLater()
