"""
Split-Readiness-Guards fuer ``app.chat`` und ``app.chats``.

- ``app.chat`` bleibt frei von ``app.gui``, ``app.ui_application`` und Qt
  (siehe ``test_chat_domain_governance_guards``).
- Die Root-Public-Surface ``app.chat`` entspricht ``__all__`` in
  ``app/chat/__init__.py``.
- Nicht-lokale ``app.*``-Kanten in ``app.chat`` sind auf die dokumentierte
  Menge beschraenkt (``core``, ``context``-Typen unter ``TYPE_CHECKING``,
  ``services`` nur in klar definierten Integrationspfaden).
- ``app.chats`` bleibt duenn: eine oeffentliche Hilfs-API und nur die
  dokumentierte Kante zu ``app.chat.context_policies``.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

_EXPECTED_CHAT_ROOT_EXPORTS: tuple[str, ...] = (
    "CompletionStatus",
    "completion_status_from_db",
    "completion_status_to_db",
    "is_incomplete",
    "assess_completion_heuristic",
    "get_heuristic_flags",
    "ChatContext",
    "ChatRequestContext",
    "build_chat_context",
    "inject_chat_context_into_messages",
)

_DOCUMENTED_CHAT_EXTERNAL_IMPORTS: frozenset[str] = frozenset(
    {
        "app.context.explainability.context_explanation",
        "app.core.config.chat_context_enums",
        "app.core.config.settings",
        "app.services.chat_service",
        "app.services.infrastructure",
        "app.services.project_butler_service",
        "app.services.project_service",
        "app.services.workflow_service",
    }
)

_DOCUMENTED_CHATS_EXTERNAL_IMPORTS: frozenset[str] = frozenset({"app.chat.context_policies"})

_EXPECTED_CHATS_ROOT_EXPORTS: tuple[str, ...] = ("get_chat_context_policy",)


def _iter_package_python_files(rel: str) -> list[Path]:
    return sorted((APP_ROOT / rel).rglob("*.py"))


def _parse_tree(path: Path) -> ast.AST | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return None


def _external_app_imports_excluding_own_package(path: Path, own_prefix: str) -> set[str]:
    tree = _parse_tree(path)
    if tree is None:
        return set()
    imports: set[str] = set()
    prefix = own_prefix.rstrip(".") + "."
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name.startswith("app.") and not name.startswith(prefix):
                    imports.add(name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod.startswith("app.") and not mod.startswith(prefix):
                imports.add(mod)
    return imports


def _package_external_imports(rel_dir: str, own_prefix: str) -> set[str]:
    found: set[str] = set()
    for py_path in _iter_package_python_files(rel_dir):
        if "__pycache__" in py_path.parts:
            continue
        found.update(_external_app_imports_excluding_own_package(py_path, own_prefix))
    return found


@pytest.mark.architecture
@pytest.mark.contract
def test_chat_external_app_imports_match_documented_contract() -> None:
    found = _package_external_imports("chat", "app.chat")
    assert found == _DOCUMENTED_CHAT_EXTERNAL_IMPORTS, (
        "app.chat soll aktuell nur die dokumentierten externen app.*-Importe "
        "halten (core/settings/enums, optional context-Typing, services in "
        "Integrationsmodulen). Gefunden: "
        f"{sorted(found)}"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_chat_root_public_surface_matches_documented_exports() -> None:
    init_path = APP_ROOT / "chat" / "__init__.py"
    tree = _parse_tree(init_path)
    assert tree is not None

    exports: tuple[str, ...] | None = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue
        if node.targets[0].id != "__all__":
            continue
        if isinstance(node.value, (ast.List, ast.Tuple)):
            vals: list[str] = []
            for elt in node.value.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    vals.append(elt.value)
            exports = tuple(vals)
            break

    assert exports == _EXPECTED_CHAT_ROOT_EXPORTS, (
        "app.chat.__all__ soll die dokumentierte Root-Public-Surface tragen. "
        f"Gefunden: {exports}"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_chats_external_app_imports_match_documented_contract() -> None:
    found = _package_external_imports("chats", "app.chats")
    assert found == _DOCUMENTED_CHATS_EXTERNAL_IMPORTS, (
        "app.chats soll aktuell nur die dokumentierte Kante zu app.chat halten. "
        f"Gefunden: {sorted(found)}"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_chats_root_public_surface_matches_documented_exports() -> None:
    init_path = APP_ROOT / "chats" / "__init__.py"
    tree = _parse_tree(init_path)
    assert tree is not None

    exports: tuple[str, ...] | None = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue
        if node.targets[0].id != "__all__":
            continue
        if isinstance(node.value, (ast.List, ast.Tuple)):
            vals: list[str] = []
            for elt in node.value.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    vals.append(elt.value)
            exports = tuple(vals)
            break

    assert exports == _EXPECTED_CHATS_ROOT_EXPORTS, (
        "app.chats.__all__ soll die dokumentierte Root-Public-Surface tragen. "
        f"Gefunden: {exports}"
    )
