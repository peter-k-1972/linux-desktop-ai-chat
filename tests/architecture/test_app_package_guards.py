"""
Architektur-Guard-Tests für app/ Package-Struktur.

Prüft:
1. App-Root nur erlaubte Dateien (neue Root-Dateien werden erkannt)
2. Keine verbotenen Parallelstrukturen (ui/ neben gui/)
3. Verbotene Import-Richtungen
4. Navigation zentral unter gui/navigation/ (global vs. domain getrennt)
5. Feature-Packages importieren weder gui noch Root-Legacy
6. app.core importiert keine app.gui
7. app.utils importiert keine Feature- oder UI-Module
8. app.ui nur von erlaubten Übergangsmodulen importiert

Referenz: docs/04_architecture/APP_TARGET_PACKAGE_ARCHITECTURE.md
          docs/architecture/PACKAGE_MAP.md
          docs/architecture/ARCHITECTURE_GUARD_RULES.md
"""

import ast
import pytest
from pathlib import Path

from tests.architecture.app_utils_source_root import app_utils_source_root
from tests.architecture.arch_guard_config import (
    ALLOWED_APP_ROOT_FILES,
    ALLOWED_UI_IMPORTER_PATTERNS,
    ALLOWED_IN_GUI_NAVIGATION,
    APP_ROOT,
    CENTRAL_NAVIGATION_PATH,
    FORBIDDEN_IMPORT_RULES,
    FORBIDDEN_PARALLEL_PACKAGES,
    GLOBAL_NAVIGATION_CLASSES,
    KNOWN_IMPORT_EXCEPTIONS,
    ROOT_LEGACY_MODULES,
    TARGET_PACKAGES,
    TEMPORARILY_ALLOWED_ROOT_FILES,
)


def _iter_app_python_files():
    """Iteriert über alle .py-Dateien unter app/ (ohne __pycache__)."""
    for path in APP_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        yield path


def _iter_topology_py_for_package_guards():
    """
    Host-``app/*`` plus Embedded-``linux-desktop-chat-infra`` (debug/metrics/tools)
    und Embedded-``linux-desktop-chat-runtime`` (runtime/extensions).

    Yields ``(path, rel_str_for_exceptions, source_top | None)`` — ``source_top`` gesetzt
    für Infra-Dateien (``debug``/``metrics``/``tools``) und Runtime-Dateien (``runtime``/``extensions``).
    """
    for py_path in APP_ROOT.rglob("*.py"):
        if "__pycache__" in py_path.parts:
            continue
        rel = py_path.relative_to(APP_ROOT)
        yield py_path, str(rel).replace("\\", "/"), None
    from tests.architecture.app_infra_source_root import iter_infra_topology_py_files
    from tests.architecture.app_runtime_source_root import iter_product_runtime_topology_py_files

    for py_path, seg, rel_suffix in iter_infra_topology_py_files():
        yield py_path, f"{seg}/{rel_suffix}", seg
    for py_path, seg, rel_suffix in iter_product_runtime_topology_py_files():
        yield py_path, f"{seg}/{rel_suffix}", seg


def _get_top_package(rel_path: Path) -> str | None:
    """Liefert das Top-Level-Package für einen relativen Pfad unter app/."""
    parts = rel_path.parts
    if len(parts) < 2:
        return None  # app/__init__.py etc. -> Root
    return parts[0]  # app/core/... -> "core"


def _extract_app_imports(
    file_path: Path, *, source_top: str | None = None
) -> list[tuple[str, str]]:
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
    if source_top is not None:
        resolved_source_top = source_top
    else:
        try:
            rel = file_path.relative_to(APP_ROOT)
        except ValueError:
            return []
        resolved_source_top = _get_top_package(rel) or "_root"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name.startswith("app."):
                    parts = name.split(".")
                    if len(parts) >= 2:
                        imported_top = parts[1]
                        imports.append((resolved_source_top, imported_top))
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("app."):
                parts = node.module.split(".")
                if len(parts) >= 2:
                    imported_top = parts[1]
                    imports.append((resolved_source_top, imported_top))

    return imports


def _extract_app_imports_with_source_top(
    file_path: Path, source_top: str
) -> list[tuple[str, str]]:
    """Wie :func:`_extract_app_imports`, aber fester Quell-Top-Segmentname (z. B. ``utils``)."""
    try:
        source = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    imports: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name.startswith("app."):
                    parts = name.split(".")
                    if len(parts) >= 2:
                        imports.append((source_top, parts[1]))
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("app."):
                parts = node.module.split(".")
                if len(parts) >= 2:
                    imports.append((source_top, parts[1]))
    return imports


def _is_allowed_ui_importer(rel_path_str: str) -> bool:
    """Prüft, ob Modul app.ui importieren darf (Übergangsphase)."""
    if rel_path_str.startswith("ui/"):
        return True  # ui-intern
    for pattern in ALLOWED_UI_IMPORTER_PATTERNS:
        if pattern.endswith("/"):
            if rel_path_str.startswith(pattern):
                return True
        elif rel_path_str == pattern or rel_path_str.endswith("/" + pattern):
            return True
    return False


def _utils_forbidden_targets() -> frozenset[str]:
    """Packages, die utils nicht importieren darf (Feature + UI)."""
    return frozenset({
        "core", "gui", "agents", "rag", "prompts", "providers",
        "services", "debug", "metrics", "tools", "ui",
    })


# --- Test 1: App-Root nur erlaubte Dateien ---


@pytest.mark.architecture
@pytest.mark.contract
def test_app_root_only_allowed_files():
    """
    Sentinel: Im app/ Root dürfen nur erlaubte Dateien liegen.

    Erlaubt: __init__.py, __main__.py, main.py, resources.qrc, resources_rc.py
    Zusätzlich: Verzeichnisse (Subpackages).

    Bei Verletzung: Datei in Subpackage verschieben oder in ALLOWED_APP_ROOT_FILES
    ergänzen (nach Architektur-Review).
    Neue Root-Dateien werden erkannt und führen zum Testfehler.
    """
    root_files = {f.name for f in APP_ROOT.iterdir() if f.is_file()}
    allowed = ALLOWED_APP_ROOT_FILES | TEMPORARILY_ALLOWED_ROOT_FILES
    disallowed = root_files - allowed
    assert not disallowed, (
        f"Architekturdrift: Ungültige Dateien im app/ Root: {sorted(disallowed)}. "
        f"Erlaubt: {sorted(allowed)}. "
        "Neue Root-Dateien nach docs/architecture/APP_MOVE_MATRIX.md verschieben."
    )


# --- Test 2: Keine verbotenen Parallelstrukturen ---


@pytest.mark.architecture
@pytest.mark.contract
def test_forbidden_parallel_packages_have_import_rules():
    """
    Sentinel: Für jede verbotene Parallelstruktur (z.B. ui/) müssen Import-Regeln existieren.

    ui/ neben gui/ ist verboten; Feature-Packages dürfen ui nicht importieren.
    Prüft, dass FORBIDDEN_IMPORT_RULES alle relevanten (source, ui)-Kombinationen abdeckt.
    """
    for pkg in FORBIDDEN_PARALLEL_PACKAGES:
        pkg_path = APP_ROOT / pkg
        if not pkg_path.is_dir():
            continue
        # Mindestens eine Regel muss (source, pkg) für ein Feature-Package verbieten
        feature_sources = {"core", "agents", "rag", "prompts", "providers", "tools", "metrics", "debug", "utils"}
        rules_for_pkg = {(s, d) for s, d in FORBIDDEN_IMPORT_RULES if d == pkg}
        covered = {s for s, _ in rules_for_pkg}
        missing = feature_sources - covered
        assert not missing, (
            f"Für verbotene Parallelstruktur {pkg}/ fehlen Import-Regeln: {missing}. "
            f"FORBIDDEN_IMPORT_RULES um (source, '{pkg}') für diese Packages ergänzen."
        )


# --- Test 3: Verbotene Import-Richtungen ---


@pytest.mark.architecture
@pytest.mark.contract
def test_no_forbidden_import_directions():
    """
    Sentinel: Keine verbotenen Import-Richtungen zwischen Packages.

    Regeln aus docs/architecture/APP_TARGET_PACKAGE_ARCHITECTURE.md Abschnitt 3.
    z.B. core -> gui verboten, utils -> core verboten.
    """
    violations = []
    for py_path, rel_str, source_top_override in _iter_topology_py_for_package_guards():
        source_top = (
            source_top_override
            if source_top_override is not None
            else (_get_top_package(Path(rel_str)) or "_root")
        )
        for _src, _dst in _extract_app_imports(py_path, source_top=source_top):
            if (_src, _dst) not in FORBIDDEN_IMPORT_RULES:
                continue
            if any(pat in rel_str for pat, _ in KNOWN_IMPORT_EXCEPTIONS if _ == _dst):
                continue
            violations.append((rel_str, _src, _dst))

    assert not violations, (
        f"Architekturdrift: {len(violations)} verbotene Import-Richtung(en). "
        f"Beispiel: app.{violations[0][1]} darf nicht app.{violations[0][2]} importieren. "
        f"Verletzungen: {violations[:10]}{'...' if len(violations) > 10 else ''}. "
        "Siehe docs/architecture/APP_TARGET_PACKAGE_ARCHITECTURE.md Abschnitt 3."
    )


# --- Test 4: Navigation zentral ---


@pytest.mark.architecture
@pytest.mark.contract
def test_central_navigation_exists():
    """
    Sentinel: Zentrale Navigation muss unter app/gui/navigation/ existieren.

    Erwartete Dateien: sidebar.py, command_palette.py, nav_areas.py, sidebar_config.py
    """
    assert CENTRAL_NAVIGATION_PATH.exists(), (
        f"Architekturdrift: Zentrale Navigation fehlt unter {CENTRAL_NAVIGATION_PATH.relative_to(APP_ROOT)}. "
        "Siehe docs/architecture/APP_TARGET_PACKAGE_ARCHITECTURE.md Abschnitt 4."
    )
    expected = {"sidebar.py", "command_palette.py", "nav_areas.py", "sidebar_config.py"}
    present = {f.name for f in CENTRAL_NAVIGATION_PATH.iterdir() if f.is_file()}
    missing = expected - present
    assert not missing, (
        f"Architekturdrift: Zentrale Navigation unvollständig. Fehlend: {missing}. "
        f"Vorhanden: {present}. "
        "Siehe docs/architecture/APP_TARGET_PACKAGE_ARCHITECTURE.md Abschnitt 4."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_no_duplicate_global_navigation_outside_gui():
    """
    Sentinel: Keine zweite globale Navigation außerhalb gui/navigation/.

    NavigationSidebar und CommandPalette (Haupt-Sidebar, Befehlspalette) dürfen
    nur in app/gui/navigation/ definiert werden.
    Domain-spezifische Nav-Panels (chat_navigation_panel etc.) sind erlaubt.
    """
    gui_nav_dir = APP_ROOT / "gui" / "navigation"
    canonical_classes = {"NavigationSidebar", "CommandPalette"}
    violations = []
    for py_path in _iter_app_python_files():
        try:
            tree = ast.parse(py_path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        in_gui_nav = gui_nav_dir in py_path.parents or py_path.parent == gui_nav_dir
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name in canonical_classes:
                if not in_gui_nav:
                    violations.append((str(py_path.relative_to(APP_ROOT)), node.name))
    assert not violations, (
        f"Architekturdrift: Globale Navigation außerhalb gui/navigation definiert: {violations}. "
        "NavigationSidebar und CommandPalette gehören ausschließlich nach app/gui/navigation/."
    )


# --- Test 5: Feature-Packages importieren weder gui noch Root-Legacy ---


@pytest.mark.architecture
@pytest.mark.contract
def test_feature_packages_no_gui_imports():
    """
    Sentinel: Feature-Packages (core, agents, rag, prompts, providers, tools, metrics, debug)
    dürfen app.gui nicht importieren.
    Bekannte Ausnahmen: siehe arch_guard_config.KNOWN_IMPORT_EXCEPTIONS.
    """
    feature_packages = {"core", "agents", "rag", "prompts", "providers", "tools", "metrics", "debug"}
    violations = []
    for py_path, rel_str, source_top_override in _iter_topology_py_for_package_guards():
        top = (
            source_top_override
            if source_top_override is not None
            else _get_top_package(Path(rel_str))
        )
        if top not in feature_packages:
            continue
        for _src, _dst in _extract_app_imports(py_path, source_top=top):
            if _dst != "gui":
                continue
            if any(pat in rel_str for pat, dst in KNOWN_IMPORT_EXCEPTIONS if dst == "gui"):
                continue
            violations.append((rel_str, _src, _dst))
    assert not violations, (
        f"Architekturdrift: Feature-Packages dürfen app.gui nicht importieren. "
        f"Verletzungen: {violations}. "
        "Siehe docs/architecture/APP_TARGET_PACKAGE_ARCHITECTURE.md Abschnitt 3.2."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_feature_packages_no_root_legacy_imports():
    """
    Sentinel: Feature-Packages dürfen Root-Legacy-Module (chat_widget, sidebar_widget, ...)
    nicht importieren.
    """
    feature_packages = {"core", "agents", "rag", "prompts", "providers", "tools", "metrics", "debug"}
    violations = []
    for py_path, rel_str, source_top_override in _iter_topology_py_for_package_guards():
        top = (
            source_top_override
            if source_top_override is not None
            else _get_top_package(Path(rel_str))
        )
        if top not in feature_packages:
            continue
        imports = _extract_app_imports(py_path, source_top=top)
        for _src, _dst in imports:
            if _dst in ROOT_LEGACY_MODULES:
                violations.append((rel_str, f"app.{_dst}"))
    assert not violations, (
        f"Architekturdrift: Feature-Packages dürfen Root-Legacy-Module nicht importieren. "
        f"Verletzungen: {violations}. "
        f"Root-Legacy: {sorted(ROOT_LEGACY_MODULES)}."
    )


# --- Test 6: Core importiert keine GUI ---


@pytest.mark.architecture
@pytest.mark.contract
def test_core_no_gui_imports():
    """
    Sentinel: app.core darf keine Module aus app.gui importieren.

    Core ist testbar ohne Qt. Keine PySide6, keine GUI-Abhängigkeiten.
    Temporäre Ausnahme: siehe KNOWN_IMPORT_EXCEPTIONS und docs/architecture/FEATURE_SYSTEM.md.
    """
    violations = []
    for py_path in _iter_app_python_files():
        rel = py_path.relative_to(APP_ROOT)
        rel_str = str(rel).replace("\\", "/")
        if not rel_str.startswith("core/"):
            continue
        for _src, _dst in _extract_app_imports(py_path):
            if _dst != "gui":
                continue
            if any(pat in rel_str for pat, dst in KNOWN_IMPORT_EXCEPTIONS if dst == "gui"):
                continue
            violations.append((rel_str, "app.gui"))
    assert not violations, (
        f"Architekturdrift: app.core darf app.gui nicht importieren. "
        f"Verletzungen: {[v[0] for v in violations]}. "
        "Core muss ohne Qt/GUI testbar bleiben."
    )


# --- Test 7: Utils importiert keine Feature- oder UI-Module ---


@pytest.mark.architecture
@pytest.mark.contract
def test_utils_no_feature_or_ui_imports():
    """
    Sentinel: app.utils darf keine Feature-Packages (core, gui, agents, …) oder ui importieren.

    Utils ist reine Infrastruktur (Paths, Datetime, Env). Keine Fachlogik.
    Quelle: eingebettetes Paket linux-desktop-chat-utils (nicht mehr unter APP_ROOT/utils).
    """
    forbidden = _utils_forbidden_targets()
    violations = []
    root = app_utils_source_root()
    for py_path in root.rglob("*.py"):
        if "__pycache__" in py_path.parts:
            continue
        rel_str = str(py_path.relative_to(root)).replace("\\", "/")
        for _src, _dst in _extract_app_imports_with_source_top(py_path, "utils"):
            if _dst in forbidden:
                violations.append((rel_str, f"app.{_dst}"))
    assert not violations, (
        f"Architekturdrift: app.utils darf keine Feature- oder UI-Module importieren. "
        f"Verletzungen: {violations}. "
        f"Erlaubt: nur stdlib. Verboten: {sorted(forbidden)}."
    )


# --- Test 8: ui nur von erlaubten Übergangsmodulen importiert ---


@pytest.mark.architecture
@pytest.mark.contract
def test_ui_only_imported_by_allowed_transition_modules():
    """
    Sentinel: app.ui darf nur von explizit erlaubten Übergangsmodulen importiert werden.

    Erlaubt: gui/, main.py, chat_widget.py, core/project_context_manager (emit).
    Ziel: ui → gui Migration; keine neuen ui-Abhängigkeiten.
    """
    violations = []
    for py_path in _iter_app_python_files():
        rel = py_path.relative_to(APP_ROOT)
        rel_str = str(rel).replace("\\", "/")
        for _src, _dst in _extract_app_imports(py_path):
            if _dst != "ui":
                continue
            if _is_allowed_ui_importer(rel_str):
                continue
            violations.append((rel_str, "app.ui"))
    assert not violations, (
        f"Architekturdrift: app.ui darf nur von erlaubten Übergangsmodulen importiert werden. "
        f"Unerlaubte Importeure: {[v[0] for v in violations]}. "
        f"Erlaubt: {sorted(ALLOWED_UI_IMPORTER_PATTERNS)}. "
        "Siehe docs/architecture/APP_UI_TO_GUI_TRANSITION_PLAN.md."
    )


# --- Test 9: Navigation klar getrennt (global vs. domain) ---


@pytest.mark.architecture
@pytest.mark.contract
def test_global_navigation_only_in_gui_navigation():
    """
    Sentinel: Globale Navigation (NavigationSidebar, CommandPalette) nur in gui/navigation/.
    """
    gui_nav_dir = APP_ROOT / "gui" / "navigation"
    violations = []
    for py_path in _iter_app_python_files():
        try:
            tree = ast.parse(py_path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        in_gui_nav = gui_nav_dir in py_path.parents or py_path.parent == gui_nav_dir
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name in GLOBAL_NAVIGATION_CLASSES:
                if not in_gui_nav:
                    rel = py_path.relative_to(APP_ROOT)
                    violations.append((str(rel).replace("\\", "/"), node.name))
    assert not violations, (
        f"Architekturdrift: Globale Navigation außerhalb gui/navigation/: {violations}. "
        f"Erlaubt nur in: app/gui/navigation/. "
        "Domain-Nav-Panels gehören in gui/domains/*/."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_domain_nav_panels_not_in_global_navigation():
    """
    Sentinel: Domain-spezifische Nav-Panels (ChatNavigationPanel, SettingsNavigation, …)
    liegen in domains/ oder ui/, nicht in gui/navigation/.

    gui/navigation/ = nur globale Sidebar, Command Palette, Workspace Graph.
    """
    gui_nav_dir = APP_ROOT / "gui" / "navigation"
    violations = []
    for py_path in _iter_app_python_files():
        try:
            tree = ast.parse(py_path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        rel_str = str(py_path.relative_to(APP_ROOT)).replace("\\", "/")
        in_gui_nav = gui_nav_dir in py_path.parents or py_path.parent == gui_nav_dir
        if not in_gui_nav:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            if node.name in ALLOWED_IN_GUI_NAVIGATION:
                continue
            if "Navigation" in node.name or "Nav" in node.name:
                violations.append((rel_str, node.name))
    assert not violations, (
        f"Architekturdrift: Domain-Nav-Panels in gui/navigation/: {violations}. "
        "Domain-Nav gehört in gui/domains/*/ oder ui/ (Übergang). "
        "gui/navigation/ nur für: NavigationSidebar, CommandPalette, WorkspaceGraph, nav_areas, sidebar_config."
    )
