"""Smoke-Tests für Theme-Manifest-Validierung und Registry (ui_runtime)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.ui_runtime.manifest_models import SUPPORTED_MANIFEST_SCHEMA_MAJOR, theme_manifest_from_dict
from app.ui_runtime.theme_loader import load_theme_manifest_from_path
from app.ui_runtime.theme_registry import default_builtin_registry
from app.ui_runtime.widgets.widgets_runtime import WidgetsRuntime
from tests.architecture.app_ui_themes_source_root import app_ui_themes_source_root


def _builtin_manifest_path() -> Path:
    return (
        app_ui_themes_source_root()
        / "builtins"
        / "light_default"
        / "manifest.json"
    )


def test_load_builtin_manifest_file():
    path = _builtin_manifest_path()
    assert path.is_file()
    m = load_theme_manifest_from_path(path)
    assert m.theme_id == "manifest_light_default"
    assert m.runtime_primary == "pyside6_widgets"
    assert "operations_chat" in m.supported_workspaces


def test_default_builtin_registry_contains_starter_theme():
    reg = default_builtin_registry()
    m = reg.get("manifest_light_default")
    assert m is not None
    assert m.display_name


def test_reject_unsupported_schema_major():
    path = _builtin_manifest_path()
    data = json.loads(path.read_text(encoding="utf-8"))
    data["schema_version"] = f"{SUPPORTED_MANIFEST_SCHEMA_MAJOR + 1}.0"
    with pytest.raises(ValueError, match="schema major"):
        theme_manifest_from_dict(data, source_path=path)


def test_widgets_runtime_merge_qss_invokes_hook():
    path = _builtin_manifest_path()
    m = load_theme_manifest_from_path(path)
    merged: list[str] = []

    def hook(qss: str) -> None:
        merged.append(qss)

    rt = WidgetsRuntime(m, stylesheet_hook=hook)
    rt.activate()
    assert merged and "Starter-Fragment" in merged[0]
    rt.deactivate()


def test_qml_runtime_activate_missing_qml_root(qapplication, monkeypatch, tmp_path):
    from app.ui_runtime.qml.qml_runtime import QmlRuntime

    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    import app.ui_runtime.qml.qml_runtime as qml_rt

    monkeypatch.setattr(qml_rt, "_repository_root", lambda: tmp_path)
    m = load_theme_manifest_from_path(_builtin_manifest_path())
    rt = QmlRuntime(m)
    with pytest.raises(FileNotFoundError, match="QML root"):
        rt.activate()
