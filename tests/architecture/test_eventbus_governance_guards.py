"""
Architektur-Guard: EventBus-Governance.

Prüft Event-Erzeugung, Event-Verbrauch, erlaubte Publisher/Subscriber,
Layer-Trennung, Drift-Vermeidung.
Regeln: docs/architecture/EVENTBUS_GOVERNANCE_POLICY.md
Config: tests/architecture/arch_guard_config.py
"""

import ast
import pytest
from pathlib import Path

from tests.architecture.arch_guard_config import (
    APP_ROOT,
    ALLOWED_EMIT_EVENT_IMPORTERS,
    ALLOWED_EVENTBUS_DIRECT_IMPORTERS,
    FORBIDDEN_EVENTBUS_IMPORTER_PACKAGES,
    PROJECT_ROOT,
)


def _rel_path(path: Path) -> str:
    """Relativer Pfad zu PROJECT_ROOT."""
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _matches_any_pattern(rel_str: str, patterns: frozenset) -> bool:
    """Prüft ob rel_str zu einem Pattern passt (Prefix oder exakte Datei)."""
    for p in patterns:
        if rel_str == p or rel_str.startswith(p.rstrip("/") + "/") or (p.endswith("/") and rel_str.startswith(p)):
            return True
    return False


def _extract_imports_from_module(file_path: Path) -> list[str]:
    """Extrahiert importierte Module (app.*) aus einer Python-Datei."""
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
    """Iteriert über produktive .py unter Host-``app/`` und Embedded-``linux-desktop-chat-infra/src/app/``."""
    for path in APP_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        yield path
    infra_app = PROJECT_ROOT / "linux-desktop-chat-infra" / "src" / "app"
    if infra_app.is_dir():
        for path in infra_app.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            yield path


def _rel_is_eventbus_scan_target(rel: str) -> bool:
    return rel.startswith("app/") or rel.startswith("linux-desktop-chat-infra/src/app/")


# --- A. emit_event nur in erlaubten Modulen ---


def _file_imports_debug_emitter(path: Path) -> bool:
    """Prüft ob Datei app.debug.emitter importiert."""
    imports = _extract_imports_from_module(path)
    return any("debug.emitter" in imp for imp in imports)


@pytest.mark.architecture
@pytest.mark.contract
def test_emit_event_only_in_allowed_modules():
    """
    Sentinel: emit_event (app.debug.emitter) nur in erlaubten Modulen importiert.
    """
    violations = []
    for py_path in _iter_app_python_files():
        rel = _rel_path(py_path)
        if not _rel_is_eventbus_scan_target(rel):
            continue
        if not _file_imports_debug_emitter(py_path):
            continue
        if not _matches_any_pattern(rel, ALLOWED_EMIT_EVENT_IMPORTERS):
            violations.append(rel)

    assert not violations, (
        f"EventBus Governance: emit_event nur in erlaubten Modulen. "
        f"Verletzungen: {violations}. "
        f"Erlaubt: {ALLOWED_EMIT_EVENT_IMPORTERS}. "
        "Siehe docs/architecture/EVENTBUS_GOVERNANCE_POLICY.md."
    )


# --- B. EventBus/get_event_bus nur in erlaubten Modulen ---


def _file_imports_debug_event_bus(path: Path) -> bool:
    """Prüft ob Datei app.debug.event_bus importiert."""
    imports = _extract_imports_from_module(path)
    return any("debug.event_bus" in imp for imp in imports)


@pytest.mark.architecture
@pytest.mark.contract
def test_eventbus_only_in_allowed_modules():
    """
    Sentinel: EventBus, get_event_bus (app.debug.event_bus) nur in erlaubten Modulen.
    """
    violations = []
    for py_path in _iter_app_python_files():
        rel = _rel_path(py_path)
        if not _rel_is_eventbus_scan_target(rel):
            continue
        if not _file_imports_debug_event_bus(py_path):
            continue
        if not _matches_any_pattern(rel, ALLOWED_EVENTBUS_DIRECT_IMPORTERS):
            violations.append(rel)

    assert not violations, (
        f"EventBus Governance: EventBus/get_event_bus nur in erlaubten Modulen. "
        f"Verletzungen: {violations}. "
        f"Erlaubt: {ALLOWED_EVENTBUS_DIRECT_IMPORTERS}. "
        "Siehe docs/architecture/EVENTBUS_GOVERNANCE_POLICY.md."
    )


# --- C. Verbotene Packages importieren kein debug (EventBus/emit_event) ---


@pytest.mark.architecture
@pytest.mark.contract
def test_forbidden_packages_do_not_import_debug():
    """
    Sentinel: providers, prompts, tools, utils importieren nicht app.debug.
    """
    violations = []
    for py_path in _iter_app_python_files():
        rel = _rel_path(py_path)
        if not _rel_is_eventbus_scan_target(rel):
            continue
        parts = rel.split("/")
        top_pkg = None
        for i, seg in enumerate(parts):
            if seg == "app" and i + 1 < len(parts):
                top_pkg = parts[i + 1]
                break
        if top_pkg is None or top_pkg not in FORBIDDEN_EVENTBUS_IMPORTER_PACKAGES:
            continue
        imports = _extract_imports_from_module(py_path)
        for imp in imports:
            if "debug" in imp:
                violations.append((rel, imp))

    assert not violations, (
        f"EventBus Governance: {FORBIDDEN_EVENTBUS_IMPORTER_PACKAGES} dürfen app.debug nicht importieren. "
        f"Verletzungen: {violations}. "
        "Siehe docs/architecture/EVENTBUS_GOVERNANCE_POLICY.md Abschnitt 7."
    )


# --- D. EventType nur in agent_event.py definiert ---


@pytest.mark.architecture
@pytest.mark.contract
def test_event_type_only_defined_in_agent_event():
    """
    Sentinel: EventType-Enum nur in app/debug/agent_event.py definiert.
    """
    violations = []
    for py_path in _iter_app_python_files():
        rel = _rel_path(py_path)
        if "agent_event" in rel:
            continue
        try:
            source = py_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == "EventType":
                    # EventType-Klassendefinition außerhalb agent_event
                    has_enum = any(
                        isinstance(b, ast.Name) and b.id == "Enum"
                        for b in node.bases
                    )
                    if has_enum:
                        violations.append((rel, "EventType Enum-Definition"))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue

    assert not violations, (
        f"EventBus Governance: EventType nur in agent_event.py definieren. "
        f"Verletzungen: {violations}. "
        "Siehe docs/architecture/EVENTBUS_GOVERNANCE_POLICY.md Abschnitt 2."
    )


# --- E. debug importiert nicht gui ---


@pytest.mark.architecture
@pytest.mark.contract
def test_debug_does_not_import_gui():
    """
    Sentinel: app.debug importiert nicht app.gui.
    """
    from tests.architecture.app_infra_source_root import app_infra_segment_source_root

    try:
        debug_dir = app_infra_segment_source_root("debug")
    except RuntimeError:
        pytest.skip("app.debug nicht auffindbar (linux-desktop-chat-infra)")

    violations = []
    for py_path in debug_dir.rglob("*.py"):
        if "__pycache__" in py_path.parts:
            continue
        rel = _rel_path(py_path)
        for imp in _extract_imports_from_module(py_path):
            if imp == "app.gui" or imp.startswith("app.gui."):
                violations.append((rel, imp))

    assert not violations, (
        f"EventBus Governance: debug darf gui nicht importieren. "
        f"Verletzungen: {violations}. "
        "Siehe docs/architecture/EVENTBUS_GOVERNANCE_POLICY.md."
    )


# --- F. Project Events nutzen nicht Debug EventBus ---


@pytest.mark.architecture
@pytest.mark.contract
def test_project_events_separate_from_debug_eventbus():
    """
    Sentinel: project_events nutzt eigenes Callback-System, nicht app.debug.event_bus.
    """
    path = APP_ROOT / "gui" / "events" / "project_events.py"
    if not path.exists():
        pytest.skip("project_events.py nicht vorhanden")

    imports = _extract_imports_from_module(path)
    for imp in imports:
        if "debug" in imp or "event_bus" in imp:
            pytest.fail(
                f"EventBus Governance: project_events darf nicht app.debug/event_bus importieren. "
                f"Import: {imp}. Project Events sind separates System."
            )


# --- G. EventType-Werte konsistent ---


@pytest.mark.architecture
@pytest.mark.contract
def test_event_type_enum_has_expected_values():
    """
    Sentinel: EventType enthält die erwarteten Werte (keine stillen Änderungen).
    """
    from app.debug.agent_event import EventType

    expected = {
        "TASK_CREATED", "TASK_STARTED", "TASK_COMPLETED", "TASK_FAILED",
        "AGENT_SELECTED", "MODEL_CALL", "TOOL_EXECUTION", "RAG_RETRIEVAL_FAILED",
    }
    actual = {e.name for e in EventType}
    missing = expected - actual
    assert not missing, (
        f"EventBus Governance: EventType fehlt: {missing}. "
        "Siehe docs/architecture/EVENTBUS_GOVERNANCE_POLICY.md."
    )


# --- H. DebugStore und MetricsCollector sind Subscriber ---


@pytest.mark.architecture
@pytest.mark.contract
def test_debug_store_and_metrics_collector_subscribe():
    """
    Sentinel: DebugStore und MetricsCollector subscriben am EventBus.
    """
    from app.debug.debug_store import DebugStore
    from app.debug.event_bus import EventBus

    bus = EventBus()
    store = DebugStore(bus)
    assert len(bus._listeners) >= 1, "DebugStore muss subscribe aufrufen"
    store._unsubscribe()

    from app.metrics.metrics_collector import MetricsCollector

    bus2 = EventBus()
    collector = MetricsCollector(bus=bus2)
    collector.start()
    assert len(bus2._listeners) >= 1, "MetricsCollector muss subscribe aufrufen"
    collector.stop()
