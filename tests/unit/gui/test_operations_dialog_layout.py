"""Operations-Dialoge — Phase-2 (ProjectEditDialog)."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QFormLayout, QVBoxLayout, QWidget

from app.gui.domains.operations.projects.dialogs.project_edit_dialog import ProjectEditDialog
from app.gui.shared.layout_constants import CARD_SPACING, DIALOG_CONTENT_PADDING
from app.gui.theme import design_metrics as dm


@pytest.fixture
def sample_project():
    return {
        "project_id": 1,
        "name": "Test",
        "description": "",
        "customer_name": "",
        "external_reference": "",
        "internal_code": "",
        "lifecycle_status": "active",
        "planned_start_date": "",
        "planned_end_date": "",
        "budget_amount": None,
        "budget_currency": "",
        "estimated_effort_hours": None,
        "status": "active",
        "default_context_policy": None,
    }


def test_project_edit_dialog_instantiates(qapplication, sample_project):
    d = ProjectEditDialog(sample_project)
    assert d.windowTitle() == "Projekt bearbeiten"
    d.deleteLater()


def test_project_edit_dialog_outer_structure(qapplication, sample_project):
    d = ProjectEditDialog(sample_project)
    main = d.layout()
    assert isinstance(main, QVBoxLayout)
    m = main.contentsMargins()
    assert m.bottom() == dm.DIALOG_FOOTER_TOP_GAP_PX
    body = main.itemAt(0).widget()
    assert isinstance(body, QWidget)
    bl = body.layout()
    assert isinstance(bl, QVBoxLayout)
    bm = bl.contentsMargins()
    assert bm.left() == DIALOG_CONTENT_PADDING == 24
    assert bl.spacing() == CARD_SPACING == 16
    form_item = bl.itemAt(0).layout()
    assert isinstance(form_item, QFormLayout)
    assert form_item.verticalSpacing() == dm.FORM_ROW_GAP_PX
    assert form_item.horizontalSpacing() == dm.FORM_LABEL_GAP_PX
    btn_lay = main.itemAt(main.count() - 1).layout()
    m2 = btn_lay.contentsMargins()
    assert m2.left() == dm.DIALOG_PADDING_PX == 24
    d.deleteLater()
