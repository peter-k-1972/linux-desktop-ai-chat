"""Projects Workspace Panels — Phase-2 Layout-Pilot."""

from __future__ import annotations

import pytest

from app.gui.domains.operations.projects.panels.project_list_panel import ProjectListPanel
from app.gui.domains.operations.projects.panels.project_overview_panel import ProjectOverviewPanel
from app.gui.domains.operations.projects.panels.project_stats_panel import ProjectStatsPanel
from app.gui.shared.layout_constants import CARD_SPACING, PANEL_PADDING, SIDEBAR_PADDING, WIDGET_SPACING
from app.gui.theme import design_metrics as dm


def test_project_list_panel_layout(qapplication):
    p = ProjectListPanel()
    lay = p.layout()
    m = lay.contentsMargins()
    assert m.left() == SIDEBAR_PADDING == 12
    assert lay.spacing() == WIDGET_SPACING == 12
    assert p._table.columnCount() == 3
    p.deleteLater()


def test_project_overview_panel_outer_layout(qapplication):
    o = ProjectOverviewPanel()
    lay = o.layout()
    m = lay.contentsMargins()
    assert m.left() == PANEL_PADDING == 20
    assert lay.spacing() == CARD_SPACING == 16
    o.deleteLater()


def test_project_stats_panel_spacing(qapplication):
    s = ProjectStatsPanel()
    outer = s.layout()
    assert outer.spacing() == WIDGET_SPACING
    card = s._chat_card
    inner = card.layout()
    m = inner.contentsMargins()
    assert m.left() == dm.CARD_PADDING_PX == 16
    assert inner.spacing() == WIDGET_SPACING
    style = card.styleSheet().replace(" ", "")
    assert "padding:0px" in style
    s.deleteLater()
