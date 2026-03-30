"""
Architektur-Guard: GUI Governance (Screen, Navigation, Commands, Bootstrap).

Prüft strukturelle Konsistenz: Screen Registry, Navigation Targets, Command IDs.
Regeln: docs/architecture/GUI_GOVERNANCE_POLICY.md
"""

import pytest
from pathlib import Path

from tests.architecture.arch_guard_config import (
    APP_ROOT,
    GUI_SCREEN_WORKSPACE_MAP,
    PROJECT_ROOT,
)


# --- Screen / Bootstrap Guards ---


@pytest.mark.architecture
@pytest.mark.contract
def test_screen_registry_no_duplicate_area_ids():
    """
    Sentinel: Keine doppelten area_ids in der ScreenRegistry.
    """
    from app.gui.bootstrap import register_all_screens
    from app.gui.workspace.screen_registry import get_screen_registry

    register_all_screens()
    registry = get_screen_registry()
    areas = registry.list_areas()
    unique = set(areas)
    assert len(areas) == len(unique), (
        f"Architekturdrift: Doppelte area_ids in ScreenRegistry. "
        f"Bereiche: {sorted(areas)}. "
        "Siehe docs/architecture/GUI_GOVERNANCE_POLICY.md Abschnitt 2."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_bootstrap_area_ids_in_nav_area():
    """
    Sentinel: Alle Bootstrap area_ids sind gültige NavArea-Konstanten.
    """
    from app.gui.bootstrap import register_all_screens
    from app.gui.navigation.nav_areas import NavArea

    register_all_screens()
    registry = __import__("app.gui.workspace.screen_registry", fromlist=["get_screen_registry"])
    reg = registry.get_screen_registry()
    areas = reg.list_areas()
    valid = {
        NavArea.COMMAND_CENTER,
        NavArea.OPERATIONS,
        NavArea.CONTROL_CENTER,
        NavArea.QA_GOVERNANCE,
        NavArea.RUNTIME_DEBUG,
        NavArea.SETTINGS,
    }
    invalid = [a for a in areas if a not in valid]
    assert not invalid, (
        f"Architekturdrift: Bootstrap registriert ungültige area_ids: {invalid}. "
        f"Gültig: {sorted(valid)}. "
        "Siehe docs/architecture/GUI_GOVERNANCE_POLICY.md Abschnitt 2."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_registered_screens_are_importable():
    """
    Sentinel: Alle in Bootstrap registrierten Screen-Klassen sind importierbar.
    """
    from app.gui.domains.dashboard import DashboardScreen
    from app.gui.domains.operations import OperationsScreen
    from app.gui.domains.control_center import ControlCenterScreen
    from app.gui.domains.qa_governance import QAGovernanceScreen
    from app.gui.domains.runtime_debug import RuntimeDebugScreen
    from app.gui.domains.settings import SettingsScreen

    screens = [
        DashboardScreen,
        OperationsScreen,
        ControlCenterScreen,
        QAGovernanceScreen,
        RuntimeDebugScreen,
        SettingsScreen,
    ]
    for cls in screens:
        assert cls is not None, f"Screen-Klasse {cls} nicht importierbar"


# --- Navigation Guards ---


@pytest.mark.architecture
@pytest.mark.contract
def test_nav_entries_area_in_nav_area():
    """
    Sentinel: Jeder NavEntry.area ist eine gültige NavArea-Konstante.
    """
    from app.core.navigation.navigation_registry import get_all_entries
    from app.core.navigation.nav_areas import NavArea

    valid_areas = {
        NavArea.COMMAND_CENTER,
        NavArea.OPERATIONS,
        NavArea.CONTROL_CENTER,
        NavArea.QA_GOVERNANCE,
        NavArea.RUNTIME_DEBUG,
        NavArea.SETTINGS,
    }
    entries = get_all_entries()
    violations = []
    for eid, entry in entries.items():
        if entry.area not in valid_areas:
            violations.append((eid, entry.area))
    assert not violations, (
        f"Architekturdrift: NavEntry mit ungültigem area: {violations}. "
        "Siehe docs/architecture/GUI_GOVERNANCE_POLICY.md Abschnitt 3."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_nav_entries_workspace_resolvable():
    """
    Sentinel: workspace_id eines NavEntry wird vom zugehörigen Screen unterstützt.
    """
    from app.core.navigation.navigation_registry import get_all_entries

    entries = get_all_entries()
    violations = []
    for eid, entry in entries.items():
        area = entry.area
        workspace = entry.workspace
        if workspace is None:
            continue
        allowed = GUI_SCREEN_WORKSPACE_MAP.get(area)
        if allowed is None:
            violations.append((eid, area, workspace, "area nicht in GUI_SCREEN_WORKSPACE_MAP"))
        elif workspace not in allowed:
            violations.append((eid, area, workspace, f"workspace nicht in {allowed}"))
    assert not violations, (
        f"Architekturdrift: NavEntry mit nicht auflösbarem workspace: "
        f"{violations}. "
        "Siehe docs/architecture/GUI_GOVERNANCE_POLICY.md Abschnitt 3."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_nav_entries_help_topic_ids_exist_in_help_index():
    """
    Sentinel: Ist help_topic_id gesetzt, muss HelpIndex ein passendes Thema liefern
    (Kontexthilfe / Discoverability).
    """
    from app.core.navigation.navigation_registry import get_all_entries
    from app.help.help_index import HelpIndex

    idx = HelpIndex()
    missing: list[tuple[str, str]] = []
    for eid, entry in get_all_entries().items():
        hid = entry.help_topic_id
        if not hid:
            continue
        if idx.get_topic(hid) is None:
            missing.append((eid, hid))
    assert not missing, (
        "NavEntry mit help_topic_id ohne Eintrag im HelpIndex: "
        f"{missing}. Hilfe-Datei anlegen oder ID korrigieren."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_help_index_resolves_operations_workflows_workspace():
    """Kontexthilfe für Workflow-Workspace (Phase Integrationsabgleich)."""
    from app.help.help_index import HelpIndex

    t = HelpIndex().get_topic_by_workspace("operations_workflows")
    assert t is not None
    assert t.id == "workflows_workspace"


@pytest.mark.architecture
@pytest.mark.contract
def test_nav_sections_reference_existing_entries():
    """
    Sentinel: Alle entry_ids in NavSectionDef existieren in _ENTRIES.
    """
    from app.core.navigation.navigation_registry import get_all_entries, get_sidebar_sections

    entries = get_all_entries()
    sections = get_sidebar_sections()
    violations = []
    for sec in sections:
        for eid in sec.entry_ids:
            if eid not in entries:
                violations.append((sec.id, eid))
    assert not violations, (
        f"Architekturdrift: NavSection referenziert nicht existierende entry_id: "
        f"{violations}. "
        "Siehe docs/architecture/GUI_GOVERNANCE_POLICY.md Abschnitt 3."
    )


# --- Command Guards (gui CommandRegistry) ---


@pytest.mark.architecture
@pytest.mark.contract
def test_gui_command_ids_unique():
    """
    Sentinel: Keine doppelten Command-IDs in gui CommandRegistry nach register_commands.

    Scope dieses Guards: Standard-Navigation in app.gui.commands.registry.
    Die Core-/Palette-Registry wird in anderen Governance-Tests abgedeckt.
    """
    from app.gui.commands.registry import CommandRegistry

    class MockWorkspaceHost:
        def show_area(self, area_id, workspace_id=None):
            pass

    from app.gui.commands.bootstrap import register_commands

    register_commands(MockWorkspaceHost())
    commands = CommandRegistry.all_commands()
    ids = [c.id for c in commands]
    seen = set()
    duplicates = []
    for i in ids:
        if i in seen:
            duplicates.append(i)
        seen.add(i)
    assert not duplicates, (
        f"Architekturdrift: Doppelte Command-IDs in gui CommandRegistry: "
        f"{duplicates}. "
        "Siehe docs/architecture/GUI_GOVERNANCE_POLICY.md Abschnitt 4."
    )


# --- Bootstrap Guards ---


@pytest.mark.architecture
@pytest.mark.contract
def test_bootstrap_screen_registry_creates_screens():
    """
    Sentinel: ScreenRegistry liefert für jede area_id eine Factory.
    Kein voller QWidget-Instanziierungstest; geprüft wird der Bootstrap-/Registry-Vertrag.
    """
    from app.gui.bootstrap import register_all_screens
    from app.gui.workspace.screen_registry import get_screen_registry

    register_all_screens()
    registry = get_screen_registry()
    areas = registry.list_areas()
    for area_id in areas:
        factory = registry.get_factory(area_id)
        assert factory is not None, (
            f"Architekturdrift: Keine Factory für area_id {area_id}. "
            "Siehe docs/architecture/GUI_GOVERNANCE_POLICY.md Abschnitt 5."
        )
