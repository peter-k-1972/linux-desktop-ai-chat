"""
Architektur-Guard: Startup Governance.

Prüft definierte Einstiegspunkte, Bootstrap-Reihenfolge und Verdrahtung.
Regeln: docs/architecture/STARTUP_GOVERNANCE_POLICY.md
Config: tests/architecture/arch_guard_config.py
"""

import ast
import pytest
from pathlib import Path

from tests.architecture.arch_guard_config import (
    CANONICAL_GUI_ENTRY_POINTS,
    PROJECT_ROOT,
    REQUIRED_BOOTSTRAP_PATTERNS,
)


def _get_main_function_source(module_path: Path) -> str:
    """
    Liefert den Quelltext der main()-Funktion eines Moduls.
    Für run_gui_shell: main in gleicher Datei.
    Für app.main: main in app/main.py.
    """
    if not module_path.exists():
        return ""
    try:
        source = module_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ""
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "main":
            lines = source.splitlines()
            end_line = getattr(node, "end_lineno", node.lineno) or node.lineno
            if node.lineno:
                return "\n".join(lines[node.lineno - 1 : end_line])
            break
    return ""


def _resolve_entry_point_path(entry: str) -> Path:
    """Resolved Pfad für Einstiegspunkt (relativ zu PROJECT_ROOT)."""
    return PROJECT_ROOT / entry


# --- 1. GUI Entry Points müssen Infrastruktur initialisieren ---


@pytest.mark.architecture
@pytest.mark.contract
def test_canonical_gui_entry_points_exist():
    """
    Sentinel: Alle kanonischen GUI-Einstiegspunkte existieren.
    """
    missing = []
    for entry in CANONICAL_GUI_ENTRY_POINTS:
        path = _resolve_entry_point_path(entry)
        if not path.exists():
            missing.append(entry)
    assert not missing, (
        f"Startup Governance: Kanonische Einstiegspunkte fehlen: {missing}. "
        f"Erwartet: {CANONICAL_GUI_ENTRY_POINTS}. "
        "Siehe arch_guard_config.CANONICAL_GUI_ENTRY_POINTS."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_gui_entry_points_call_init_infrastructure_with_qsettings():
    """
    Sentinel: GUI-Einstiegspunkte rufen init_infrastructure(create_qsettings_backend()) auf.

    Verhindert stille InMemoryBackend-Fallbacks in produktiven GUI-Läufen.
    """
    violations = []
    for entry in CANONICAL_GUI_ENTRY_POINTS:
        path = _resolve_entry_point_path(entry)
        if not path.exists():
            continue
        source = _get_main_function_source(path)
        if not source:
            violations.append((entry, "main()-Funktion nicht gefunden"))
            continue
        for pattern in REQUIRED_BOOTSTRAP_PATTERNS:
            if pattern not in source:
                violations.append((entry, f"Fehlt: '{pattern}' in main()"))
                break

    assert not violations, (
        f"Startup Governance: Bootstrap-Contract verletzt. "
        f"GUI-Einstiegspunkte müssen init_infrastructure(create_qsettings_backend()) aufrufen. "
        f"Verletzungen: {violations}. "
        "Siehe docs/architecture/STARTUP_GOVERNANCE_POLICY.md Abschnitt 3."
    )


# --- 2. Keine inoffiziellen Einstiegspunkte ---


@pytest.mark.architecture
@pytest.mark.contract
def test_app_main_delegates_to_run_gui_shell():
    """
    Sentinel: app.__main__ delegiert an run_gui_shell.main (nicht an Legacy).
    """
    main_py = PROJECT_ROOT / "app" / "__main__.py"
    if not main_py.exists():
        pytest.skip("app/__main__.py nicht vorhanden")
    source = main_py.read_text(encoding="utf-8")
    assert "run_gui_shell" in source, (
        "Startup Governance: app.__main__ muss run_gui_shell importieren. "
        "Siehe docs/architecture/STARTUP_GOVERNANCE_POLICY.md."
    )
    assert "app.main" not in source or "run_gui_shell" in source, (
        "Startup Governance: app.__main__ soll run_gui_shell nutzen, nicht app.main (Legacy)."
    )


# --- 3. Bootstrap-Reihenfolge (init vor get_infrastructure) ---


@pytest.mark.architecture
@pytest.mark.contract
def test_run_gui_shell_init_before_get_infrastructure():
    """
    Sentinel: run_gui_shell ruft init_infrastructure vor get_infrastructure auf.
    """
    path = PROJECT_ROOT / "run_gui_shell.py"
    if not path.exists():
        pytest.skip("run_gui_shell.py nicht vorhanden")
    source = path.read_text(encoding="utf-8")
    init_pos = source.find("init_infrastructure")
    get_pos = source.find("get_infrastructure()")
    assert init_pos >= 0, "run_gui_shell muss init_infrastructure aufrufen"
    assert get_pos >= 0, "run_gui_shell muss get_infrastructure aufrufen"
    assert init_pos < get_pos, (
        "Startup Governance: init_infrastructure muss vor get_infrastructure stehen. "
        "Siehe docs/architecture/STARTUP_GOVERNANCE_POLICY.md Abschnitt 3."
    )


# --- 4. ShellMainWindow nach Bootstrap ---


@pytest.mark.architecture
@pytest.mark.contract
def test_run_gui_shell_window_after_infrastructure():
    """
    Sentinel: ShellMainWindow() wird nach init_infrastructure und get_infrastructure erstellt.
    """
    path = PROJECT_ROOT / "run_gui_shell.py"
    if not path.exists():
        pytest.skip("run_gui_shell.py nicht vorhanden")
    source = path.read_text(encoding="utf-8")
    init_pos = source.find("init_infrastructure")
    win_pos = source.find("ShellMainWindow()")
    assert init_pos >= 0 and win_pos >= 0
    assert init_pos < win_pos, (
        "Startup Governance: ShellMainWindow() muss nach init_infrastructure stehen."
    )


# --- 5. Stille Fallbacks: Produktive GUI nutzt QSettings ---


@pytest.mark.architecture
@pytest.mark.contract
@pytest.mark.ui
def test_bootstrap_with_qsettings_produces_non_inmemory_backend(qapp):
    """
    Sentinel: Nach Bootstrap mit create_qsettings_backend ist das Backend nicht InMemory.

    Verhindert stille Fallbacks: Wenn init_infrastructure(create_qsettings_backend()) aufgerufen
    wurde, muss get_infrastructure().settings ein QSettings-Backend nutzen.
    qapp: pytest-qt fixture für QApplication.
    """
    from app.core.config.settings_backend import InMemoryBackend
    from app.services.infrastructure import (
        init_infrastructure,
        get_infrastructure,
        set_infrastructure,
    )

    # Reset für sauberen Test
    set_infrastructure(None)

    try:
        from app.gui.qsettings_backend import create_qsettings_backend
        init_infrastructure(settings_backend=create_qsettings_backend())
        infra = get_infrastructure()
        backend = infra.settings._backend
        assert not isinstance(backend, InMemoryBackend), (
            "Startup Governance: Nach init_infrastructure(create_qsettings_backend()) "
            "darf das Backend nicht InMemoryBackend sein. Stiller Fallback erkannt."
        )
    finally:
        set_infrastructure(None)
        init_infrastructure(None)


# --- 6. Services importieren nicht von GUI-Bootstrap ---


@pytest.mark.architecture
@pytest.mark.contract
def test_services_do_not_import_entry_points():
    """
    Sentinel: app.services importiert keine GUI-Einstiegspunkte (run_gui_shell, app.main).
    """
    import ast
    services_dir = PROJECT_ROOT / "app" / "services"
    if not services_dir.exists():
        pytest.skip("app/services/ nicht vorhanden")
    violations = []
    for py_path in services_dir.rglob("*.py"):
        if "__pycache__" in py_path.parts:
            continue
        try:
            tree = ast.parse(py_path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and (
                    "run_gui_shell" in node.module or node.module == "app.main"
                ):
                    violations.append((str(py_path.relative_to(PROJECT_ROOT)), node.module))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if "run_gui_shell" in alias.name or alias.name == "app.main":
                        violations.append((str(py_path.relative_to(PROJECT_ROOT)), alias.name))
    assert not violations, (
        f"Startup Governance: services darf keine GUI-Einstiegspunkte importieren. "
        f"Verletzungen: {violations}. "
        "Siehe docs/architecture/STARTUP_GOVERNANCE_POLICY.md Abschnitt 3.1."
    )
