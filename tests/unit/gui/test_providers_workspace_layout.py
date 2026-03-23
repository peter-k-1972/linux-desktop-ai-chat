"""
Layout-/Spacing-Regression für ProvidersWorkspace (Pilot-Refactor).
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.gui.domains.control_center.workspaces.providers_workspace import (
    ProvidersWorkspace,
)
from app.gui.shared.layout_constants import CARD_SPACING, SCREEN_PADDING
from app.gui.theme import design_metrics as dm


@pytest.fixture
def providers_workspace(qapplication):
    with patch(
        "app.gui.domains.control_center.workspaces.providers_workspace.QTimer.singleShot",
    ):
        w = ProvidersWorkspace()
    yield w
    w.deleteLater()


def test_providers_workspace_instantiates(providers_workspace):
    assert providers_workspace.objectName() == "providersWorkspaceRoot"


def test_providers_workspace_outer_layout(providers_workspace):
    lay = providers_workspace.layout()
    assert lay is not None
    m = lay.contentsMargins()
    assert m.left() == SCREEN_PADDING == dm.DIALOG_PADDING_PX == 24
    assert lay.spacing() == CARD_SPACING == dm.SPACE_LG_PX == 16


def test_provider_panels_card_inner_padding(providers_workspace):
    from app.gui.domains.control_center.panels.providers_panels import ProviderListPanel

    panel = providers_workspace.findChild(ProviderListPanel)
    assert panel is not None
    inner = panel.layout()
    assert inner is not None
    m = inner.contentsMargins()
    assert m.left() == dm.CARD_PADDING_PX == 16
    assert inner.spacing() == dm.SPACE_MD_PX == 12


def test_cc_panel_frame_has_no_qss_padding():
    from app.gui.themes.control_center_styles import cc_panel_frame_style

    style = cc_panel_frame_style()
    assert "padding: 0px" in style or "padding:0px" in style.replace(" ", "")
