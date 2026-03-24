"""
Guardrail: ProjectCategory ohne direkten Projekt-Service / get_infrastructure.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

CAT = APP_ROOT / "gui" / "domains" / "settings" / "categories" / "project_category.py"


@pytest.mark.architecture
def test_project_category_no_get_project_service() -> None:
    text = CAT.read_text(encoding="utf-8")
    assert "get_project_service" not in text


@pytest.mark.architecture
def test_project_category_no_get_infrastructure() -> None:
    text = CAT.read_text(encoding="utf-8")
    assert "get_infrastructure(" not in text


@pytest.mark.architecture
def test_project_category_no_get_service_pattern() -> None:
    text = CAT.read_text(encoding="utf-8")
    assert re.search(r"get_\w+_service\s*\(", text) is None
