"""
Konsistenz: Paketlandkarte (Doku + Repo) und maschinenlesbare Landmarken.

Regeln: docs/architecture/PACKAGE_MAP.md, app/packaging/landmarks.py
"""

from __future__ import annotations

import importlib.util

import pytest

from app.features import ENTRY_POINT_GROUP
from app.packaging.landmarks import (
    BRIDGE_APP_ROOT_MODULES,
    EXTENDED_APP_TOP_PACKAGES,
    PLUGIN_ENTRY_POINT_GROUP,
    REPO_LANDMARK_FILES,
)
from tests.architecture.arch_guard_config import APP_ROOT, PROJECT_ROOT, TARGET_PACKAGES


def _app_toplevel_packages_with_init() -> frozenset[str]:
    names: set[str] = set()
    for p in APP_ROOT.iterdir():
        if not p.is_dir():
            continue
        if p.name.startswith("_") or p.name == "__pycache__":
            continue
        if (p / "__init__.py").is_file():
            names.add(p.name)
    return frozenset(names)


@pytest.mark.architecture
@pytest.mark.contract
def test_plugin_entry_point_group_matches_contract():
    assert PLUGIN_ENTRY_POINT_GROUP == ENTRY_POINT_GROUP


@pytest.mark.architecture
@pytest.mark.contract
def test_repo_landmark_files_exist():
    missing = [rel for rel in REPO_LANDMARK_FILES if not (PROJECT_ROOT / rel).exists()]
    assert not missing, (
        "Fehlende Repo-Landmarken (siehe app/packaging/landmarks.py): "
        + ", ".join(missing)
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_arch_guard_target_packages_exist_on_disk():
    missing: list[str] = []
    for name in TARGET_PACKAGES:
        if name == "features":
            if importlib.util.find_spec("app.features") is None:
                missing.append(name)
            continue
        if name == "ui_contracts":
            if importlib.util.find_spec("app.ui_contracts") is None:
                missing.append(name)
            continue
        if name == "pipelines":
            if importlib.util.find_spec("app.pipelines") is None:
                missing.append(name)
            continue
        if not (APP_ROOT / name).is_dir():
            missing.append(name)
    missing.sort()
    assert not missing, (
        "arch_guard_config.TARGET_PACKAGES verweist auf fehlende Verzeichnisse bzw. fehlendes app.features: "
        + ", ".join(f"app/{m}" for m in missing)
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_app_toplevel_packages_are_guarded_or_extended():
    """
    Jedes app/* mit __init__.py muss in TARGET_PACKAGES oder EXTENDED_APP_TOP_PACKAGES
    dokumentiert sein — keine stillen neuen Top-Level-Pakete.
    """
    on_disk = _app_toplevel_packages_with_init()
    allowed = TARGET_PACKAGES | EXTENDED_APP_TOP_PACKAGES
    undocumented = sorted(on_disk - allowed)
    assert not undocumented, (
        "Neue Top-Level-Pakete unter app/ mit __init__.py — bitte dokumentieren: "
        f"{undocumented}. Trage sie in app/packaging/landmarks.py (EXTENDED_APP_TOP_PACKAGES) "
        "und docs/architecture/PACKAGE_MAP.md ein, oder erweitere TARGET_PACKAGES nach Review."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_extended_packages_disjoint_from_target_packages():
    overlap = sorted(EXTENDED_APP_TOP_PACKAGES & TARGET_PACKAGES)
    assert not overlap, (
        "EXTENDED_APP_TOP_PACKAGES und TARGET_PACKAGES überschneiden sich: "
        f"{overlap}. Einträge nur auf einer Seite führen."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_bridge_app_root_modules_match_temporarily_allowed():
    """Brückenmodule: Doku in landmarks.py ↔ arch_guard TEMPORARILY_ALLOWED_ROOT_FILES."""
    from tests.architecture.arch_guard_config import TEMPORARILY_ALLOWED_ROOT_FILES

    expected_files = {f"{name}.py" for name in BRIDGE_APP_ROOT_MODULES}
    assert expected_files <= TEMPORARILY_ALLOWED_ROOT_FILES, (
        "BRIDGE_APP_ROOT_MODULES und TEMPORARILY_ALLOWED_ROOT_FILES weichen ab. "
        f"Erwartete .py-Dateien: {sorted(expected_files)}, "
        f"temporär erlaubt: {sorted(TEMPORARILY_ALLOWED_ROOT_FILES)}"
    )
