"""Workbench Inspector inner margin (Pilot-Refactor)."""

from __future__ import annotations

from app.gui.theme import design_metrics as dm
from app.gui.workbench.ui.design_tokens import INSPECTOR_INNER_MARGIN_PX


def test_inspector_inner_margin_matches_design_metrics():
    assert INSPECTOR_INNER_MARGIN_PX == dm.SPACE_MD_PX == 12
