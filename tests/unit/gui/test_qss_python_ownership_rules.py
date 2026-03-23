"""
Smoke: Ownership-Dokumente vorhanden; ChatInputPanel erzwingt Combo-Höhe nicht in Python.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize(
    "name",
    [
        "QSS_PYTHON_OWNERSHIP_RULES.md",
        "QSS_PYTHON_DOUBLE_SOURCE_AUDIT.md",
        "QSS_PYTHON_CANONICAL_CASES.md",
    ],
)
def test_ownership_docs_exist(name: str):
    p = ROOT / "docs" / "design" / name
    assert p.is_file(), f"missing {p}"
    assert len(p.read_text(encoding="utf-8").strip()) > 200


def test_input_panel_source_has_no_combo_set_minimum_height():
    src = (ROOT / "app" / "gui" / "domains" / "operations" / "chat" / "panels" / "input_panel.py").read_text(
        encoding="utf-8"
    )
    assert "_model_combo.setMinimumHeight" not in src
