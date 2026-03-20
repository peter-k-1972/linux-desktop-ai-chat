"""
Architektur-Guard: GUI Domain Dependency Guards.

Prüft verbotene Cross-Domain-Imports zwischen app/gui/domains/.
Regeln: docs/architecture/GUI_DOMAIN_DEPENDENCY_POLICY.md
Config: tests/architecture/arch_guard_config.py
"""

import ast
import pytest
from pathlib import Path

from tests.architecture.arch_guard_config import (
    APP_ROOT,
    FORBIDDEN_GUI_DOMAIN_PAIRS,
    KNOWN_GUI_DOMAIN_EXCEPTIONS,
)


def _get_source_domain(rel_path: str) -> str | None:
    """
    Ermittelt die Domain aus dem Dateipfad (relativ zu app/gui/).
    domains/settings/panels/foo.py -> settings
    domains/operations/chat/panels/foo.py -> operations.chat
    """
    parts = rel_path.replace("\\", "/").split("/")
    if len(parts) < 2 or parts[0] != "domains":
        return None
    domain = parts[1]
    if domain == "operations" and len(parts) >= 3:
        return f"operations.{parts[2]}"
    return domain


def _get_target_domain(module_path: str) -> str | None:
    """
    Ermittelt die Domain aus dem Modulpfad (app.gui. entfernt).
    domains.settings.panels.foo -> settings
    domains.operations.chat.panels.foo -> operations.chat
    domains.operations.operations_context -> operations (kein Subdomain)
    """
    if not module_path.startswith("app.gui."):
        return None
    rest = module_path[len("app.gui.") :]
    parts = rest.split(".")
    if len(parts) < 2 or parts[0] != "domains":
        return None
    domain = parts[1]
    if domain == "operations" and len(parts) >= 3:
        sub = parts[2]
        if sub in ("chat", "knowledge", "prompt_studio", "agent_tasks", "projects"):
            return f"operations.{sub}"
        return "operations"
    return domain


def _extract_gui_imports(file_path: Path) -> list[str]:
    """Extrahiert alle app.gui.*-Imports aus einer Python-Datei via AST."""
    try:
        source = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("app.gui."):
                    imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("app.gui."):
                imports.append(node.module)
    return imports


def _collect_domain_imports() -> list[tuple[str, str, str]]:
    """
    Sammelt alle (rel_path, source_domain, target_domain) für Cross-Domain-Imports.
    """
    gui_root = APP_ROOT / "gui"
    if not gui_root.exists():
        return []
    results = []
    for py_path in gui_root.rglob("*.py"):
        if "__pycache__" in py_path.parts:
            continue
        rel = py_path.relative_to(gui_root)
        rel_str = str(rel).replace("\\", "/")
        source_domain = _get_source_domain(rel_str)
        if source_domain is None:
            continue
        for mod in _extract_gui_imports(py_path):
            target_domain = _get_target_domain(mod)
            if target_domain is None or source_domain == target_domain:
                continue
            results.append((rel_str, source_domain, target_domain))
    return results


@pytest.mark.architecture
@pytest.mark.contract
def test_no_forbidden_gui_domain_imports():
    """
    Sentinel: Keine verbotenen Cross-Domain-Imports zwischen GUI-Domains.

    Regeln aus docs/architecture/GUI_DOMAIN_DEPENDENCY_POLICY.md.
    Bekannte Ausnahmen in KNOWN_GUI_DOMAIN_EXCEPTIONS.
    """
    gui_root = APP_ROOT / "gui"
    if not gui_root.exists():
        pytest.skip("app/gui/ nicht vorhanden")

    violations = []
    for rel_path, source_domain, target_domain in _collect_domain_imports():
        pair = (source_domain, target_domain)
        if pair not in FORBIDDEN_GUI_DOMAIN_PAIRS:
            continue
        if any(
            pat in rel_path and td == target_domain
            for pat, td in KNOWN_GUI_DOMAIN_EXCEPTIONS
        ):
            continue
        violations.append((rel_path, source_domain, target_domain))

    assert not violations, (
        f"Architekturdrift: {len(violations)} verbotene Domain-Import(s). "
        f"Regel: {source_domain} darf nicht {target_domain} importieren.\n"
        + "\n".join(
            f"  {path}: {src} -> {tgt}"
            for path, src, tgt in violations[:15]
        )
        + ("\n  ..." if len(violations) > 15 else "")
        + "\nSiehe docs/architecture/GUI_DOMAIN_DEPENDENCY_POLICY.md"
    )


@pytest.mark.architecture
def test_known_domain_exceptions_are_valid():
    """
    Stellt sicher, dass dokumentierte Ausnahmen tatsächlich verbotene Paare abdecken.
    Verhindert tote Ausnahme-Einträge.
    """
    for pat, target_domain in KNOWN_GUI_DOMAIN_EXCEPTIONS:
        found = False
        for rel_path, source_domain, target_domain_actual in _collect_domain_imports():
            if pat in rel_path and target_domain_actual == target_domain:
                pair = (source_domain, target_domain)
                if pair in FORBIDDEN_GUI_DOMAIN_PAIRS:
                    found = True
                    break
        assert found, (
            f"Ausnahme ({pat}, {target_domain}) trifft auf keinen aktuellen Import zu. "
            "Entfernen oder korrigieren."
        )
