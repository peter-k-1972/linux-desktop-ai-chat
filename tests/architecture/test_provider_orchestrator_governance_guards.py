"""
Architektur-Guard: Provider-Orchestrator-Governance.

Prüft Konsistenz zwischen ModelRegistry und Provider-Auflösung,
Layer-Trennung, Drift-Vermeidung.
Regeln: docs/architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md
Config: tests/architecture/arch_guard_config.py
"""

import ast
import pytest
from pathlib import Path

from tests.architecture.arch_guard_config import (
    APP_ROOT,
    ALLOWED_PROVIDER_STRING_FILES,
    KNOWN_MODEL_PROVIDER_STRINGS,
    PROJECT_ROOT,
)


def _get_top_package(rel_path: Path) -> str | None:
    """Liefert das Top-Level-Package für einen relativen Pfad unter app/."""
    parts = rel_path.parts
    if len(parts) < 2:
        return None
    return parts[0]


def _extract_app_imports(file_path: Path) -> list[tuple[str, str]]:
    """
    Extrahiert app.*-Imports aus einer Python-Datei via AST.
    Returns: [(source_top_pkg, imported_module), ...]
    """
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
                if alias.name.startswith("app."):
                    imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("app."):
                imports.append(node.module)
    return imports


def _iter_app_python_files():
    """Iteriert über alle .py-Dateien unter app/ (ohne __pycache__)."""
    for path in APP_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        yield path


# --- A. Provider-Konsistenz Guards ---


@pytest.mark.architecture
@pytest.mark.contract
def test_provider_implementations_match_known_strings():
    """
    Sentinel: Alle Provider-Implementierungen haben provider_id in KNOWN_MODEL_PROVIDER_STRINGS.
    """
    from app.providers import LocalOllamaProvider, CloudOllamaProvider

    providers = [
        LocalOllamaProvider(),
        CloudOllamaProvider(),
    ]
    violations = []
    for p in providers:
        pid = p.provider_id
        if pid not in KNOWN_MODEL_PROVIDER_STRINGS:
            violations.append((type(p).__name__, pid))
    assert not violations, (
        f"Provider-Orchestrator Governance: provider_id nicht in KNOWN_MODEL_PROVIDER_STRINGS: "
        f"{violations}. Erlaubt: {KNOWN_MODEL_PROVIDER_STRINGS}. "
        "Siehe docs/architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_all_known_provider_strings_have_implementation():
    """
    Sentinel: Jeder KNOWN_MODEL_PROVIDER_STRINGS-Eintrag hat eine Provider-Implementierung.
    """
    from app.providers import LocalOllamaProvider, CloudOllamaProvider

    provider_ids = {LocalOllamaProvider().provider_id, CloudOllamaProvider().provider_id}
    missing = KNOWN_MODEL_PROVIDER_STRINGS - provider_ids
    assert not missing, (
        f"Provider-Orchestrator Governance: Keine Implementierung für: {missing}. "
        f"Erwartet: {KNOWN_MODEL_PROVIDER_STRINGS}. "
        "Siehe docs/architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md."
    )


# --- B. Erlaubte Provider-Auflösungsorte ---


@pytest.mark.architecture
@pytest.mark.contract
def test_only_orchestrator_in_core_imports_providers():
    """
    Sentinel: Nur core/models/orchestrator.py in core importiert app.providers.
    """
    core_models = APP_ROOT / "core" / "models"
    if not core_models.exists():
        pytest.skip("app/core/models/ nicht vorhanden")

    violations = []
    for py_path in core_models.rglob("*.py"):
        if "__pycache__" in py_path.parts:
            continue
        rel = py_path.relative_to(APP_ROOT)
        rel_str = str(rel).replace("\\", "/")
        if "orchestrator" in rel_str:
            continue
        for imp in _extract_app_imports(py_path):
            parts = imp.split(".") if isinstance(imp, str) else []
            if len(parts) >= 2 and parts[1] == "providers":
                violations.append((rel_str, imp))

    assert not violations, (
        f"Provider-Orchestrator Governance: core/models (außer orchestrator) darf providers nicht importieren. "
        f"Verletzungen: {violations}. "
        "Siehe docs/architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md Abschnitt 2."
    )


# --- C. Provider importieren keine GUI ---


@pytest.mark.architecture
@pytest.mark.contract
def test_providers_do_not_import_gui():
    """
    Sentinel: app.providers importiert nicht app.gui.
    """
    providers_dir = APP_ROOT / "providers"
    if not providers_dir.exists():
        pytest.skip("app/providers/ nicht vorhanden")

    violations = []
    for py_path in providers_dir.rglob("*.py"):
        if "__pycache__" in py_path.parts:
            continue
        rel = py_path.relative_to(APP_ROOT)
        rel_str = str(rel).replace("\\", "/")
        for imp in _extract_app_imports(py_path):
            parts = imp.split(".") if isinstance(imp, str) else []
            if len(parts) >= 2 and parts[1] == "gui":
                violations.append((rel_str, imp))

    assert not violations, (
        f"Provider-Orchestrator Governance: Provider dürfen gui nicht importieren. "
        f"Verletzungen: {violations}. "
        "Siehe docs/architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md Abschnitt 4."
    )


# --- D. Services importieren keine Provider-Klassen ---


@pytest.mark.architecture
@pytest.mark.contract
def test_services_do_not_import_provider_classes():
    """
    Sentinel: app.services importiert nicht LocalOllamaProvider, CloudOllamaProvider.
    Infrastructure darf ollama_client (OllamaClient) nutzen.
    """
    services_dir = APP_ROOT / "services"
    if not services_dir.exists():
        pytest.skip("app/services/ nicht vorhanden")

    forbidden = {"LocalOllamaProvider", "CloudOllamaProvider"}
    violations = []
    for py_path in services_dir.rglob("*.py"):
        if "__pycache__" in py_path.parts:
            continue
        rel = py_path.relative_to(APP_ROOT)
        rel_str = str(rel).replace("\\", "/")
        try:
            source = py_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for name in forbidden:
            if name in source:
                # Prüfen ob es ein Import ist
                try:
                    tree = ast.parse(source)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom):
                            if node.module and "providers" in node.module:
                                for alias in node.names:
                                    if alias.name == name:
                                        violations.append((rel_str, name))
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                if alias.name.endswith(f".{name}") or alias.asname == name:
                                    violations.append((rel_str, name))
                except SyntaxError:
                    continue

    assert not violations, (
        f"Provider-Orchestrator Governance: Services dürfen nicht LocalOllamaProvider/CloudOllamaProvider importieren. "
        f"Verletzungen: {violations}. "
        "Nutze Infrastructure/OllamaClient. Siehe docs/architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md."
    )


# --- E. Unbekannte Modell-IDs: Fallback ---


@pytest.mark.architecture
@pytest.mark.contract
def test_orchestrator_unknown_model_fallback_to_local():
    """
    Sentinel: ModelOrchestrator.get_provider_for_model bei unbekannter model_id liefert LocalOllamaProvider.
    """
    from unittest.mock import MagicMock

    from app.core.models.orchestrator import ModelOrchestrator
    from app.providers import LocalOllamaProvider

    local = LocalOllamaProvider()
    cloud_mock = MagicMock()
    orch = ModelOrchestrator(local_provider=local, cloud_provider=cloud_mock)
    provider = orch.get_provider_for_model("__unknown_model_xyz__")
    assert provider is local, (
        "Provider-Orchestrator Governance: Unbekannte model_id muss LocalOllamaProvider liefern. "
        "Siehe docs/architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md Abschnitt 7."
    )


# --- F. Keine Provider-String-Hardcodings außerhalb definierter Orte ---


def _find_provider_keyword_assignments(file_path: Path) -> list[tuple[int, str]]:
    """
    Findet provider="local" oder provider="ollama_cloud" als Keyword-Argument.
    """
    try:
        source = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword):
            if node.arg == "provider" and isinstance(node.value, ast.Constant):
                if isinstance(node.value.value, str) and node.value.value in ("local", "ollama_cloud"):
                    findings.append((node.lineno, node.value.value))
        elif isinstance(node, ast.Return) and node.value:
            if isinstance(node.value, ast.Constant) and node.value.value in ("local", "ollama_cloud"):
                findings.append((node.lineno, node.value.value))
    return findings


@pytest.mark.architecture
@pytest.mark.contract
def test_no_provider_string_hardcoding_outside_allowed_files():
    """
    Sentinel: provider="local" / provider="ollama_cloud" / return "local" / return "ollama_cloud"
    nur in definierten Orten (Registry, Provider-Impls, arch_guard_config, Tests).
    """
    violations = []
    for py_path in list(APP_ROOT.rglob("*.py")) + list((PROJECT_ROOT / "tests").rglob("*.py")):
        if "__pycache__" in py_path.parts:
            continue
        try:
            rel = py_path.relative_to(PROJECT_ROOT)
        except ValueError:
            continue
        rel_str = str(rel).replace("\\", "/")
        if rel_str in ALLOWED_PROVIDER_STRING_FILES:
            continue
        findings = _find_provider_keyword_assignments(py_path)
        for lineno, val in findings:
            violations.append((rel_str, lineno, val))

    assert not violations, (
        f"Provider-Orchestrator Governance: Provider-Strings außerhalb erlaubter Orte: {violations}. "
        f"Erlaubt (arch_guard_config.ALLOWED_PROVIDER_STRING_FILES): {ALLOWED_PROVIDER_STRING_FILES}. "
        "Siehe docs/architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md Abschnitt 10."
    )


# --- G. Keine zyklischen Abhängigkeiten ---


@pytest.mark.architecture
@pytest.mark.contract
def test_no_cyclic_import_services_providers():
    """
    Sentinel: Keine zyklische Abhängigkeit services ↔ providers.
    providers importiert nicht services.
    """
    providers_dir = APP_ROOT / "providers"
    if not providers_dir.exists():
        pytest.skip("app/providers/ nicht vorhanden")

    violations = []
    for py_path in providers_dir.rglob("*.py"):
        if "__pycache__" in py_path.parts:
            continue
        rel = py_path.relative_to(APP_ROOT)
        rel_str = str(rel).replace("\\", "/")
        for imp in _extract_app_imports(py_path):
            parts = imp.split(".") if isinstance(imp, str) else []
            if len(parts) >= 2 and parts[1] == "services":
                violations.append((rel_str, imp))

    assert not violations, (
        f"Provider-Orchestrator Governance: Provider dürfen services nicht importieren (Zyklus-Vermeidung). "
        f"Verletzungen: {violations}. "
        "Siehe docs/architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md."
    )
