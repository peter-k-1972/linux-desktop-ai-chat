"""
Split-Readiness-Guards fuer ``app.workflows``.

- ``app.workflows`` bleibt frei von ``app.gui``, ``app.ui_application`` und Qt.
- Die Root-Public-Surface ``app.workflows`` bleibt bewusst leichtgewichtig.
- Nicht-lokale ``app.*``-Kanten im Paket bleiben auf die dokumentierten
  Adapter-/Vertragsstellen begrenzt.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

_EXPECTED_ROOT_EXPORTS: tuple[str, ...] = (
    "WorkflowDefinition",
    "WorkflowNode",
    "WorkflowEdge",
    "WorkflowRun",
    "NodeRun",
    "WorkflowDefinitionStatus",
    "WorkflowRunStatus",
    "NodeRunStatus",
    "GraphValidator",
    "ValidationResult",
    "NodeRegistry",
    "build_default_node_registry",
)

_DOCUMENTED_EXTERNAL_IMPORTS: frozenset[str] = frozenset(
    {
        "app.services.workflow_context_adapter",
        "app.services.workflow_orchestration_adapter",
        "app.services.workflow_agent_adapter",
        "app.pipelines",
        "app.pipelines.executors",
        "app.prompts.prompt_service",
        "app.agents.agent_service",
        "app.chat.context_policies",
        "app.chat.request_context_hints",
    }
)

# registry/node_registry.py: nur diese drei Module (lazy in Validatoren) — siehe Moduldocstring.
_NODE_REGISTRY_DOCUMENTED_EXTERNAL_IMPORTS: frozenset[str] = frozenset(
    {
        "app.pipelines.executors",
        "app.chat.context_policies",
        "app.chat.request_context_hints",
    }
)


def _iter_workflows_python_files() -> list[Path]:
    return sorted((APP_ROOT / "workflows").rglob("*.py"))


def _parse_tree(path: Path) -> ast.AST | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return None


def _external_app_imports(path: Path) -> set[str]:
    tree = _parse_tree(path)
    if tree is None:
        return set()

    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name.startswith("app.") and not name.startswith("app.workflows"):
                    imports.add(name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod.startswith("app.") and not mod.startswith("app.workflows"):
                imports.add(mod)
    return imports


@pytest.mark.architecture
@pytest.mark.contract
def test_workflows_domain_does_not_import_gui_ui_application_or_qt() -> None:
    violations: list[tuple[str, list[str]]] = []
    for py_path in _iter_workflows_python_files():
        tree = _parse_tree(py_path)
        if tree is None:
            continue
        hits: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    if name.startswith("app.gui") or name.startswith("app.ui_application"):
                        hits.append(name)
                    if name.split(".", 1)[0] in ("PySide6", "PySide2", "PySide"):
                        hits.append(name)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if mod.startswith("app.gui") or mod.startswith("app.ui_application"):
                    hits.append(mod)
                if mod.split(".", 1)[0] in ("PySide6", "PySide2", "PySide"):
                    hits.append(mod)
        if hits:
            rel = py_path.relative_to(APP_ROOT)
            violations.append((str(rel).replace("\\", "/"), hits))

    assert not violations, (
        "app.workflows darf app.gui, app.ui_application oder PySide* nicht importieren. "
        f"Verletzungen: {violations}"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_workflows_root_public_surface_matches_documented_exports() -> None:
    init_path = APP_ROOT / "workflows" / "__init__.py"
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

    assert exports == _EXPECTED_ROOT_EXPORTS, (
        "app.workflows.__all__ soll die dokumentierte Root-Public-Surface tragen. "
        f"Gefunden: {exports}"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_workflows_external_app_imports_match_documented_adapter_contracts() -> None:
    found: set[str] = set()
    for py_path in _iter_workflows_python_files():
        found.update(_external_app_imports(py_path))

    assert found == _DOCUMENTED_EXTERNAL_IMPORTS, (
        "app.workflows soll aktuell nur die dokumentierten externen Adapter-/Vertragsimporte "
        "halten. Gefunden: "
        f"{sorted(found)}"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_workflows_node_registry_external_imports_match_boundary_contract() -> None:
    path = APP_ROOT / "workflows" / "registry" / "node_registry.py"
    found = _external_app_imports(path)
    assert found == _NODE_REGISTRY_DOCUMENTED_EXTERNAL_IMPORTS, (
        "registry/node_registry.py darf nur die dokumentierten Grenz-Importe "
        "(tool_call/cursor_light vs. pipelines; context_load vs. chat-Enums) nutzen. "
        f"Gefunden: {sorted(found)}"
    )
