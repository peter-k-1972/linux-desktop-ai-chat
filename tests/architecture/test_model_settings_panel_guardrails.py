"""
Guardrail: ModelSettingsPanel ohne direkten get_*_service / get_infrastructure.

Hinweis-Pfad: Port injiziert (ChatSidePanel) oder Legacy-Adapter.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

PANEL = APP_ROOT / "gui" / "domains" / "settings" / "panels" / "model_settings_panel.py"

_ROUTING_HANDLER_NAMES = frozenset(
    {
        "_on_model_changed",
        "_on_routing_changed",
        "_on_cloud_changed",
        "_on_cloud_via_local_changed",
        "_on_web_search_changed",
        "_on_overkill_changed",
        "_on_default_role_changed",
        "_on_temp_changed",
        "_on_top_p_changed",
        "_on_max_tokens_changed",
        "_on_timeout_changed",
        "_on_retry_changed",
        "_on_stream_changed",
    },
)


@pytest.mark.architecture
def test_model_settings_panel_no_get_infrastructure() -> None:
    text = PANEL.read_text(encoding="utf-8")
    assert "get_infrastructure(" not in text


@pytest.mark.architecture
def test_model_settings_panel_no_get_service_pattern() -> None:
    text = PANEL.read_text(encoding="utf-8")
    assert re.search(r"get_\w+_service\s*\(", text) is None


@pytest.mark.architecture
def test_model_settings_panel_no_direct_settings_save() -> None:
    text = PANEL.read_text(encoding="utf-8")
    assert "self.settings.save()" not in text


def _class_method_defs(tree: ast.Module, class_name: str) -> list[ast.FunctionDef]:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return [item for item in node.body if isinstance(item, ast.FunctionDef)]
    return []


def _uses_self_settings(node: ast.AST) -> bool:
    for sub in ast.walk(node):
        if isinstance(sub, ast.Attribute) and sub.attr == "settings":
            if isinstance(sub.value, ast.Name) and sub.value.id == "self":
                return True
    return False


@pytest.mark.architecture
def test_model_settings_routing_handlers_no_direct_self_settings() -> None:
    """Port-/Adapter-Persistenz: Routing-Skalare nicht über self.settings mutieren."""
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    for fn in _class_method_defs(tree, "ModelSettingsPanel"):
        if fn.name not in _ROUTING_HANDLER_NAMES:
            continue
        if _uses_self_settings(fn):
            pytest.fail(
                f"ModelSettingsPanel.{fn.name} must not reference self.settings "
                "(use port path or legacy ServiceSettingsAdapter).",
            )
