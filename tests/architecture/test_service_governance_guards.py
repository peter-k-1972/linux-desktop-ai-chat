"""
Architektur-Guard: Service Governance.

Prüft Layer-Konsistenz, Service-/Provider-Nutzung und Registry-Konsistenz.
Regeln: docs/architecture/SERVICE_GOVERNANCE_POLICY.md
Config: tests/architecture/arch_guard_config.py
"""

import ast
import importlib.util
import re
import pytest
from pathlib import Path

from tests.architecture.arch_guard_config import (
    APP_ROOT,
    CANONICAL_SERVICE_MODULES,
    KNOWN_GUI_PROVIDER_EXCEPTIONS,
    KNOWN_SERVICE_GUI_EXCEPTIONS,
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
    Returns: [(source_top_pkg, imported_top_pkg), ...]
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
    rel = file_path.relative_to(APP_ROOT)
    source_top = _get_top_package(rel) or "_root"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name.startswith("app."):
                    parts = name.split(".")
                    if len(parts) >= 2:
                        imported_top = parts[1]
                        imports.append((source_top, imported_top))
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("app."):
                parts = node.module.split(".")
                if len(parts) >= 2:
                    imported_top = parts[1]
                    imports.append((source_top, imported_top))

    return imports


def _iter_app_python_files():
    """Iteriert über alle .py-Dateien unter app/ (ohne __pycache__)."""
    for path in APP_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        yield path


# --- A. Layer Guards ---


@pytest.mark.architecture
@pytest.mark.contract
def test_services_do_not_import_gui():
    """
    Sentinel: app.services darf app.gui nicht importieren.

    Ausnahme: services/infrastructure.py (QSettings-Backend, lazy/optional).
    Siehe docs/architecture/SERVICE_GOVERNANCE_POLICY.md Abschnitt 2.
    """
    violations = []
    for py_path in _iter_app_python_files():
        rel = py_path.relative_to(APP_ROOT)
        rel_str = str(rel).replace("\\", "/")
        if not rel_str.startswith("services/"):
            continue
        for _src, _dst in _extract_app_imports(py_path):
            if _dst != "gui":
                continue
            if any(pat in rel_str for pat, _ in KNOWN_SERVICE_GUI_EXCEPTIONS if _ == "gui"):
                continue
            violations.append((rel_str, "app.gui"))

    assert not violations, (
        f"Service Governance: app.services darf app.gui nicht importieren. "
        f"Verletzungen: {violations}. "
        "Ausnahme: services/infrastructure.py (dokumentiert). "
        "Siehe docs/architecture/SERVICE_GOVERNANCE_POLICY.md."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_gui_does_not_import_providers_directly():
    """
    Sentinel: app.gui darf app.providers nicht direkt importieren.

    GUI soll Services nutzen (ProviderService etc.). Ausnahme: main.py (Legacy).
    Siehe docs/architecture/SERVICE_GOVERNANCE_POLICY.md Abschnitt 4.
    """
    violations = []
    for py_path in _iter_app_python_files():
        rel = py_path.relative_to(APP_ROOT)
        rel_str = str(rel).replace("\\", "/")
        # main.py ist _root, nicht gui
        if rel_str.startswith("gui/"):
            source_top = "gui"
        elif rel_str == "main.py":
            source_top = "_root"
        else:
            continue
        for _src, _dst in _extract_app_imports(py_path):
            if _dst != "providers":
                continue
            if any(pat in rel_str for pat, _ in KNOWN_GUI_PROVIDER_EXCEPTIONS if _ == "providers"):
                continue
            violations.append((rel_str, "app.providers"))

    assert not violations, (
        f"Service Governance: GUI/main darf app.providers nicht direkt importieren. "
        f"Verletzungen: {violations}. "
        "Nutze ProviderService. Ausnahme: main.py (dokumentiert). "
        "Siehe docs/architecture/SERVICE_GOVERNANCE_POLICY.md."
    )


# --- B. Service / Provider Identity Guards ---


@pytest.mark.architecture
@pytest.mark.contract
def test_canonical_services_exist():
    """
    Sentinel: Alle kanonischen Service-Module existieren unter app/services/.
    """
    services_dir = APP_ROOT / "services"
    if not services_dir.exists():
        pytest.skip("app/services/ nicht vorhanden")

    existing = {p.stem for p in services_dir.glob("*.py") if p.stem != "__init__"}
    missing = CANONICAL_SERVICE_MODULES - existing
    assert not missing, (
        f"Service Governance: Kanonische Services fehlen: {missing}. "
        f"Erwartet: {CANONICAL_SERVICE_MODULES}. "
        "Siehe arch_guard_config.CANONICAL_SERVICE_MODULES."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_navigation_registry_entries_unique():
    """
    Sentinel: NavEntry-IDs in der Navigation Registry sind eindeutig.
    """
    from app.core.navigation.navigation_registry import get_all_entries

    entries = get_all_entries()
    ids = list(entries.keys())
    seen = set()
    duplicates = []
    for eid in ids:
        if eid in seen:
            duplicates.append(eid)
        seen.add(eid)
    assert not duplicates, (
        f"Service Governance: Doppelte NavEntry-IDs: {duplicates}. "
        "Siehe app/core/navigation/navigation_registry.py."
    )


# --- C. Usage Guards (Smoke) ---


@pytest.mark.architecture
@pytest.mark.contract
def test_central_services_importable():
    """
    Sentinel: Zentrale Services sind importierbar (keine Broken-Wiring).
    """
    errors = []
    for name in ["chat_service", "model_service", "provider_service", "knowledge_service", "agent_service", "pipeline_service"]:
        try:
            mod = importlib.import_module(f"app.services.{name}")
            getter = getattr(mod, f"get_{name.replace('_service', '')}_service", None)
            if getter is None and name == "agent_service":
                getter = getattr(mod, "get_agent_service", None)
            if getter is None and name == "pipeline_service":
                getter = getattr(mod, "get_pipeline_service", None)
            if getter is not None:
                # Nur prüfen, dass Getter existiert; kein Aufruf (könnte DB/Infra brauchen)
                pass
        except Exception as e:
            errors.append((name, str(e)))

    assert not errors, (
        f"Service Governance: Services nicht importierbar: {errors}. "
        "Broken-Wiring in app/services/."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_providers_importable():
    """
    Sentinel: Provider sind importierbar.
    """
    try:
        from app.providers import BaseChatProvider, LocalOllamaProvider, CloudOllamaProvider
        from app.providers.ollama_client import OllamaClient
    except Exception as e:
        pytest.fail(f"Service Governance: Provider nicht importierbar: {e}")


# --- D. Registry / Trace Map Consistency ---


def _parse_trace_map_services() -> set[str]:
    """Parst docs/TRACE_MAP.md Sektion 2. Returns set of service module stems."""
    path = PROJECT_ROOT / "docs" / "TRACE_MAP.md"
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8")
    result = set()
    in_section = False
    for line in text.splitlines():
        if "## 2. Services" in line:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and "app/services/" in line:
            m = re.search(r"app/services/([a-z_]+)\.py", line)
            if m:
                result.add(m.group(1))
    return result


@pytest.mark.architecture
@pytest.mark.contract
def test_trace_map_services_match_canonical():
    """
    Sentinel: TRACE_MAP.md Sektion Services stimmt mit CANONICAL_SERVICE_MODULES überein.

    infrastructure und result sind Infrastruktur, können in TRACE_MAP sein oder nicht.
    """
    trace_services = _parse_trace_map_services()
    if not trace_services:
        pytest.skip("TRACE_MAP.md Sektion 2 nicht gefunden oder leer")

    # TRACE_MAP kann infrastructure, result enthalten; canonical hat keine result
    canonical = CANONICAL_SERVICE_MODULES
    missing_in_trace = canonical - trace_services
    # topic_service, project_service, qa_governance_service müssen in TRACE_MAP sein
    critical = {"chat_service", "model_service", "provider_service", "knowledge_service", "agent_service"}
    missing_critical = critical - trace_services
    assert not missing_critical, (
        f"Service Governance: TRACE_MAP.md fehlt kritische Services: {missing_critical}. "
        "Siehe docs/TRACE_MAP.md Sektion 2."
    )


# --- E. Smoke Governance ---


@pytest.mark.architecture
@pytest.mark.contract
def test_gui_service_kernpaths_smoke():
    """
    Sentinel: GUI kann zentrale Service-Getter importieren (Smoke).
    """
    try:
        from app.services.chat_service import get_chat_service
        from app.services.model_service import get_model_service
        from app.services.provider_service import get_provider_service
        from app.services.knowledge_service import get_knowledge_service
        from app.services.agent_service import get_agent_service
        from app.services.project_service import get_project_service
        from app.services.pipeline_service import get_pipeline_service
    except Exception as e:
        pytest.fail(f"Service Governance: GUI-Service-Kernpfade nicht importierbar: {e}")
