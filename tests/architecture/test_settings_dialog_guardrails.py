"""
Guardrail: SettingsDialog ohne direkte Provider-/Unified-Catalog-Service-Getter.

POST-CORRECTION: API-Key-Validierung nicht per ``validate_cloud_api_key`` im Widget — Presenter-Pfad.
"""

from __future__ import annotations

import ast

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

DIALOG = APP_ROOT / "gui" / "domains" / "settings" / "settings_dialog.py"


@pytest.mark.architecture
def test_settings_dialog_no_get_provider_service() -> None:
    text = DIALOG.read_text(encoding="utf-8")
    assert "get_provider_service" not in text


@pytest.mark.architecture
def test_settings_dialog_no_unified_catalog_service() -> None:
    text = DIALOG.read_text(encoding="utf-8")
    assert "get_unified_model_catalog_service" not in text


@pytest.mark.architecture
def test_settings_dialog_no_get_infrastructure() -> None:
    text = DIALOG.read_text(encoding="utf-8")
    assert "get_infrastructure(" not in text


@pytest.mark.architecture
def test_settings_dialog_save_uses_settings_port_not_direct_save() -> None:
    text = DIALOG.read_text(encoding="utf-8")
    assert "persist_from_ui" in text
    assert "self.settings.save()" not in text


@pytest.mark.architecture
def test_settings_dialog_widget_does_not_construct_legacy_commit_dto() -> None:
    text = DIALOG.read_text(encoding="utf-8")
    assert "SettingsLegacyModalCommit" not in text


@pytest.mark.architecture
def test_settings_dialog_widget_does_not_call_catalog_presenter_static() -> None:
    text = DIALOG.read_text(encoding="utf-8")
    assert "SettingsAiModelCatalogPresenter" not in text


def _function_def(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "SettingsDialog":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == name:
                    return item
    return None


def _calls_validate_cloud_api_key(func: ast.FunctionDef) -> bool:
    for sub in ast.walk(func):
        if not isinstance(sub, ast.Call):
            continue
        f = sub.func
        if isinstance(f, ast.Attribute) and f.attr == "validate_cloud_api_key":
            return True
    return False


@pytest.mark.architecture
def test_settings_dialog_on_check_api_key_avoids_direct_port_validate() -> None:
    tree = ast.parse(DIALOG.read_text(encoding="utf-8"))
    fn = _function_def(tree, "_on_check_api_key_status")
    assert fn is not None
    assert not _calls_validate_cloud_api_key(fn), (
        "_on_check_api_key_status must schedule presenter validation, not call validate_cloud_api_key on the port."
    )
