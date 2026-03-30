"""
Architektur-Guard: Feature Governance.

Prüft Konsistenz zwischen Feature Registry, Navigation, Commands und GUI.
Regeln: docs/architecture/FEATURE_GOVERNANCE_POLICY.md

Scope: generator-definierte Workspace-Features aus FEATURES.
Bewusst nicht Teil dieses Guards: zusätzliche Navigationseinträge/Area-only-Ziele,
die außerhalb der kanonischen Generator-Liste liegen.
"""

import importlib.util
import re
import pytest
from pathlib import Path

from tests.architecture.arch_guard_config import (
    APP_ROOT,
    GUI_SCREEN_WORKSPACE_MAP,
    PROJECT_ROOT,
)


def _get_generator_features():
    """Lädt FEATURES aus tools/generate_feature_registry.py."""
    path = PROJECT_ROOT / "tools" / "generate_feature_registry.py"
    if not path.exists():
        return []
    spec = importlib.util.spec_from_file_location("generate_feature_registry", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, "FEATURES", [])


def _extract_workspace_ids_from_features() -> list[tuple[str, str]]:
    """(workspace_id, display_name) aus FEATURES."""
    result = []
    for _area_title, features in _get_generator_features():
        for display_name, workspace_id in features:
            result.append((workspace_id, display_name))
    return result


def _parse_feature_registry_md() -> list[tuple[str, str]]:
    """Parst docs/FEATURE_REGISTRY.md. Returns [(display_name, workspace_id), ...]."""
    path = PROJECT_ROOT / "docs" / "FEATURE_REGISTRY.md"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    result = []
    current_feature = ""
    current_workspace = ""
    for line in text.splitlines():
        m = re.match(r"^### (.+)$", line)
        if m:
            if current_feature and current_workspace:
                result.append((current_feature.strip(), current_workspace.strip()))
            current_feature = m.group(1)
            current_workspace = ""
            continue
        m = re.match(r"^\|\s*Workspace\s*\|\s*`([^`]+)`\s*\|", line)
        if m:
            current_workspace = m.group(1)
            continue
    if current_feature and current_workspace:
        result.append((current_feature.strip(), current_workspace.strip()))
    return result


# --- Feature Identity Guards ---


@pytest.mark.architecture
@pytest.mark.contract
def test_feature_workspace_ids_unique():
    """
    Sentinel: Keine doppelten workspace_ids in FEATURES.
    """
    items = _extract_workspace_ids_from_features()
    ids = [ws for ws, _ in items]
    seen = set()
    duplicates = []
    for ws in ids:
        if ws in seen:
            duplicates.append(ws)
        seen.add(ws)
    assert not duplicates, (
        f"Architekturdrift: Doppelte workspace_ids in FEATURES: {duplicates}. "
        "Siehe docs/architecture/FEATURE_GOVERNANCE_POLICY.md Abschnitt 2."
    )


# --- Feature Reachability Guards ---


@pytest.mark.architecture
@pytest.mark.contract
def test_feature_workspace_ids_in_navigation_registry():
    """
    Sentinel: Jeder workspace_id aus FEATURES existiert in der Navigation Registry.
    """
    from app.core.navigation.navigation_registry import get_all_entries

    items = _extract_workspace_ids_from_features()
    entries = get_all_entries()
    nav_ids = set(entries.keys())
    violations = []
    for workspace_id, display_name in items:
        if workspace_id not in nav_ids:
            violations.append((workspace_id, display_name))
    assert not violations, (
        f"Architekturdrift: workspace_ids ohne Nav-Eintrag: {violations}. "
        "Siehe docs/architecture/FEATURE_GOVERNANCE_POLICY.md Abschnitt 3."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_feature_workspace_ids_in_screen_map():
    """
    Sentinel: Jeder workspace_id aus FEATURES ist in GUI_SCREEN_WORKSPACE_MAP.
    """
    items = _extract_workspace_ids_from_features()
    all_valid = set()
    for ws_set in GUI_SCREEN_WORKSPACE_MAP.values():
        all_valid.update(ws_set)
    violations = []
    for workspace_id, display_name in items:
        if workspace_id not in all_valid:
            violations.append((workspace_id, display_name))
    assert not violations, (
        f"Architekturdrift: workspace_ids nicht in GUI_SCREEN_WORKSPACE_MAP: {violations}. "
        "Siehe docs/architecture/FEATURE_GOVERNANCE_POLICY.md Abschnitt 3."
    )


# --- Feature Registry Integrity Guards ---


@pytest.mark.architecture
@pytest.mark.contract
def test_feature_registry_md_parseable():
    """
    Sentinel: FEATURE_REGISTRY.md ist parsebar und enthält Workspace-Einträge.
    """
    parsed = _parse_feature_registry_md()
    assert len(parsed) > 0, (
        "Architekturdrift: FEATURE_REGISTRY.md leer oder nicht parsebar. "
        "Run: python3 tools/generate_feature_registry.py"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_feature_registry_md_contains_all_features():
    """
    Sentinel: FEATURE_REGISTRY.md enthält alle generator-definierten workspace_ids aus FEATURES.
    """
    from_features = {ws for ws, _ in _extract_workspace_ids_from_features()}
    parsed = _parse_feature_registry_md()
    from_md = {ws for _, ws in parsed}
    missing = from_features - from_md
    assert not missing, (
        f"Architekturdrift: FEATURE_REGISTRY.md fehlt workspace_ids: {missing}. "
        "Run: python3 tools/generate_feature_registry.py"
    )


# --- Generator Consistency Guards ---


@pytest.mark.architecture
@pytest.mark.contract
def test_generator_runs_successfully():
    """
    Sentinel: tools/generate_feature_registry.py läuft ohne Fehler.
    """
    path = PROJECT_ROOT / "tools" / "generate_feature_registry.py"
    assert path.exists(), "tools/generate_feature_registry.py nicht gefunden"
    spec = importlib.util.spec_from_file_location("generate_feature_registry", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    content = mod.generate()
    assert isinstance(content, str)
    assert "Feature Registry" in content
    assert "Workspace" in content
