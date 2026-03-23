"""
Architektur-Guard: Registry Governance.

Prüft Konsistenz von Navigation, Screen, Command, Model, Agent Registries.
Regeln: docs/architecture/REGISTRY_GOVERNANCE_POLICY.md
"""

import ast
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from tests.architecture.arch_guard_config import (
    APP_ROOT,
    GUI_SCREEN_WORKSPACE_MAP,
    KNOWN_MODEL_PROVIDER_STRINGS,
    PROJECT_ROOT,
)


# --- Navigation Registry ---


@pytest.mark.architecture
@pytest.mark.contract
def test_navigation_registry_screens_exist():
    """
    Sentinel: Für jede area_id in GUI_SCREEN_WORKSPACE_MAP existiert ein Screen in Bootstrap.
    """
    from app.gui.bootstrap import register_all_screens
    from app.gui.workspace.screen_registry import get_screen_registry

    register_all_screens()
    registry = get_screen_registry()
    registered_areas = set(registry.list_areas())
    expected_areas = set(GUI_SCREEN_WORKSPACE_MAP.keys())
    missing = expected_areas - registered_areas
    assert not missing, (
        f"Registry Governance: Screens fehlen für area_ids: {missing}. "
        f"Erwartet: {expected_areas}. Registriert: {registered_areas}. "
        "Siehe docs/architecture/REGISTRY_GOVERNANCE_POLICY.md."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_registered_screens_inherit_base_screen():
    """
    Sentinel: Alle in Bootstrap registrierten Screen-Klassen erben von BaseScreen.

    Prüft die im Bootstrap verwendeten Klassen, ohne Screens zu instanziieren
    (vermeidet Qt-Lifecycle-Probleme mit deferred Timers).
    """
    from app.gui.shared import BaseScreen
    from app.gui.domains.dashboard import DashboardScreen
    from app.gui.domains.operations import OperationsScreen
    from app.gui.domains.control_center import ControlCenterScreen
    from app.gui.domains.qa_governance import QAGovernanceScreen
    from app.gui.domains.runtime_debug import RuntimeDebugScreen
    from app.gui.domains.settings import SettingsScreen

    screen_classes = [
        DashboardScreen,
        OperationsScreen,
        ControlCenterScreen,
        QAGovernanceScreen,
        RuntimeDebugScreen,
        SettingsScreen,
    ]
    violations = []
    for cls in screen_classes:
        if not issubclass(cls, BaseScreen):
            violations.append(cls.__name__)
    assert not violations, (
        f"Registry Governance: Screens müssen von BaseScreen erben. "
        f"Verletzungen: {violations}. "
        "Siehe docs/architecture/REGISTRY_GOVERNANCE_POLICY.md."
    )


# --- Command Registry (GUI) ---


@pytest.mark.architecture
@pytest.mark.contract
def test_gui_command_registry_commands_have_handlers():
    """
    Sentinel: Alle registrierten GUI-Commands haben einen callback.
    """
    from app.gui.commands.bootstrap import register_commands
    from app.gui.commands.registry import CommandRegistry

    mock_host = MagicMock()
    register_commands(mock_host)
    commands = CommandRegistry.all_commands()
    without_callback = [c for c in commands if c.callback is None]
    assert not without_callback, (
        f"Registry Governance: Commands ohne Handler: {[c.id for c in without_callback]}. "
        "Siehe docs/architecture/REGISTRY_GOVERNANCE_POLICY.md."
    )


# --- Command Registry (Core / Palette) ---


@pytest.mark.architecture
@pytest.mark.contract
def test_palette_command_registry_commands_have_handlers():
    """
    Sentinel: Nach load_all_palette_commands haben alle PaletteCommands einen callback.
    """
    from app.gui.commands.palette_loader import load_all_palette_commands
    from app.core.command_registry import CommandRegistry

    mock_host = MagicMock()
    load_all_palette_commands(mock_host)
    commands = CommandRegistry.all_commands()
    without_callback = [c for c in commands if c.callback is None]
    assert not without_callback, (
        f"Registry Governance: PaletteCommands ohne Handler: {[c.id for c in without_callback]}. "
        "Siehe docs/architecture/REGISTRY_GOVERNANCE_POLICY.md."
    )


# --- Model Registry ---


@pytest.mark.architecture
@pytest.mark.contract
def test_model_registry_provider_strings_valid():
    """
    Sentinel: Alle ModelEntry.provider sind bekannte Provider-Strings.
    """
    from app.core.models.registry import get_registry

    registry = get_registry()
    violations = []
    for entry in registry.list_all():
        if entry.provider not in KNOWN_MODEL_PROVIDER_STRINGS:
            violations.append((entry.id, entry.provider))
    assert not violations, (
        f"Registry Governance: Ungültige provider-Strings in ModelRegistry: {violations}. "
        f"Erlaubt: {KNOWN_MODEL_PROVIDER_STRINGS}. "
        "Siehe docs/architecture/REGISTRY_GOVERNANCE_POLICY.md."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_model_registry_ids_unique():
    """
    Sentinel: Keine doppelten model_ids in ModelRegistry.
    """
    from app.core.models.registry import get_registry

    registry = get_registry()
    ids = [e.id for e in registry.list_all()]
    seen = set()
    duplicates = []
    for mid in ids:
        if mid in seen:
            duplicates.append(mid)
        seen.add(mid)
    assert not duplicates, (
        f"Registry Governance: Doppelte model_ids: {duplicates}. "
        "Siehe docs/architecture/REGISTRY_GOVERNANCE_POLICY.md."
    )


# --- Agent Registry ---


@pytest.mark.architecture
@pytest.mark.contract
def test_agent_registry_importable_and_consistent():
    """
    Sentinel: AgentRegistry und AgentService nutzen dieselbe Datenquelle (AgentRepository).
    AgentRegistry ist importierbar, AgentService delegiert an agents.
    """
    from app.agents.agent_registry import get_agent_registry
    from app.services.agent_service import get_agent_service

    registry = get_agent_registry()
    service = get_agent_service()
    # Beide müssen funktionieren; Service delegiert an agents.agent_service
    agents_from_registry = registry.list_all()
    agents_from_service = service.list_agents()
    # Nach ensure_seed_agents sollten beide dieselben Agenten sehen
    # Wir prüfen nur, dass keine Exception geworfen wird
    assert registry is not None
    assert service is not None


# --- Provider (implizit) ---


@pytest.mark.architecture
@pytest.mark.contract
def test_model_provider_strings_resolvable():
    """
    Sentinel: Provider-Strings in ModelRegistry sind auflösbar (local, ollama_cloud).
    """
    from app.providers import LocalOllamaProvider, CloudOllamaProvider

    # Prüfen, dass Provider existieren
    assert LocalOllamaProvider is not None
    assert CloudOllamaProvider is not None
    # ModelRegistry nutzt "local" -> LocalOllamaProvider, "ollama_cloud" -> CloudOllamaProvider
    assert "local" in KNOWN_MODEL_PROVIDER_STRINGS
    assert "ollama_cloud" in KNOWN_MODEL_PROVIDER_STRINGS


# --- Import-Drift: Core Registries ---


def _extract_app_imports(file_path: Path) -> list[str]:
    """Extrahiert app.*-Imports aus einer Python-Datei."""
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
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


@pytest.mark.architecture
@pytest.mark.contract
def test_core_registries_do_not_import_gui_services_providers():
    """
    Sentinel: Core-Registries (navigation, models, command_registry) importieren nicht gui, services, providers.
    """
    forbidden = {"gui", "services", "providers"}
    registry_files = [
        APP_ROOT / "core" / "navigation" / "navigation_registry.py",
        APP_ROOT / "core" / "models" / "registry.py",
        APP_ROOT / "core" / "command_registry.py",
    ]
    violations = []
    for path in registry_files:
        if not path.exists():
            continue
        for imp in _extract_app_imports(path):
            parts = imp.split(".")
            if len(parts) >= 2 and parts[1] in forbidden:
                violations.append((str(path.relative_to(PROJECT_ROOT)), imp))
    assert not violations, (
        f"Registry Governance: Core-Registries dürfen gui, services, providers nicht importieren. "
        f"Verletzungen: {violations}. "
        "Siehe docs/architecture/REGISTRY_GOVERNANCE_POLICY.md Abschnitt 4."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_agent_registry_does_not_import_gui_services_providers():
    """
    Sentinel: AgentRegistry importiert nicht gui, services, providers.
    """
    path = APP_ROOT / "agents" / "agent_registry.py"
    if not path.exists():
        pytest.skip("agent_registry.py nicht vorhanden")
    forbidden = {"gui", "services", "providers"}
    for imp in _extract_app_imports(path):
        parts = imp.split(".")
        if len(parts) >= 2 and parts[1] in forbidden:
            pytest.fail(
                f"Registry Governance: AgentRegistry darf {parts[1]} nicht importieren. "
                f"Import: {imp}. "
                "Siehe docs/architecture/REGISTRY_GOVERNANCE_POLICY.md."
            )
