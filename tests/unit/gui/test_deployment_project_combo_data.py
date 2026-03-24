"""deployment_project_combo_data — Delegation zu project_service."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.gui.domains.operations.deployment.deployment_project_combo_data import list_project_label_id_pairs


def test_list_project_label_id_pairs_maps_rows(monkeypatch) -> None:
    svc = MagicMock()
    svc.list_projects.return_value = [
        {"project_id": 1, "name": "Alpha"},
        {"project_id": 2, "name": ""},
    ]

    monkeypatch.setattr(
        "app.services.project_service.get_project_service",
        lambda: svc,
    )
    rows = list_project_label_id_pairs()
    assert rows == [("Alpha", 1), ("Projekt 2", 2)]
