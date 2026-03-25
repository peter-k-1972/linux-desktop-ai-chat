"""
Konsistenz Edition / Dependency-Manifest ↔ eingebaute FeatureRegistrare.

Siehe docs/architecture/EDITION_AND_DEPENDENCY_MANIFESTS.md
"""

import ast
import pytest
from pathlib import Path

from tests.architecture.app_features_source_root import app_features_source_root
from tests.architecture.arch_guard_config import APP_ROOT, PROJECT_ROOT

from app.features.feature_name_catalog import ALL_BUILTIN_FEATURE_NAMES
from app.features.registry import build_default_feature_registry


def _iter_py_under(app_sub: str):
    if app_sub.startswith("features/"):
        base = app_features_source_root()
        rest = app_sub.removeprefix("features/").strip("/")
        root = base.joinpath(*rest.split("/")) if rest else base
    else:
        root = APP_ROOT.joinpath(*app_sub.split("/"))
    if not root.is_dir():
        return
    for p in root.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        yield p


def _imports_app_gui(path: Path) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("app.gui"):
                    return True
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("app.gui"):
                return True
    return False


@pytest.mark.architecture
@pytest.mark.contract
def test_feature_name_catalog_matches_builtin_registrars():
    """Katalog = eingebaute Namen; Registry kann zusätzliche Discovery-Features enthalten."""
    reg = build_default_feature_registry()
    names = frozenset(reg.list_registrar_names())
    assert ALL_BUILTIN_FEATURE_NAMES <= names
    assert not (ALL_BUILTIN_FEATURE_NAMES - names)


@pytest.mark.architecture
@pytest.mark.contract
def test_editions_and_dependency_groups_packages_remain_gui_free():
    """Manifest-Unterpakete bleiben ohne statischen app.gui-Import."""
    violations = []
    fr = app_features_source_root()
    for sub in ("features/editions", "features/dependency_groups"):
        for p in _iter_py_under(sub):
            if _imports_app_gui(p):
                violations.append(str(Path("features") / p.relative_to(fr)))
    assert not violations, (
        "Edition/Dependency-Manifeste dürfen app.gui nicht importieren "
        f"(Integrationsgrenze bleibt bei Registraren). Verletzungen: {violations}"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_builtin_navigation_entry_ids_exist_in_central_registry():
    """FeatureDescriptor.navigation_entries → nur bekannte navigation_registry-IDs."""
    from app.core.navigation.navigation_registry import get_all_entries
    from app.features.registry import build_default_feature_registry

    nav_ids = set(get_all_entries().keys())
    reg = build_default_feature_registry()
    violations = []
    for r in reg.list_registrars():
        d = r.get_descriptor()
        for eid in d.navigation_entries:
            if eid not in nav_ids:
                violations.append((d.name, eid))
    assert not violations, (
        "navigation_entries verweisen auf unbekannte Registry-IDs: "
        f"{violations}. Siehe docs/architecture/NAVIGATION_FEATURE_BINDING.md"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_full_edition_collect_active_nav_matches_descriptor_union():
    from app.features.nav_binding import collect_active_navigation_entry_ids
    from app.features.edition_resolution import build_feature_registry_for_edition

    reg = build_feature_registry_for_edition("full")
    collected = collect_active_navigation_entry_ids(reg)
    union: set[str] = set()
    for r in reg.list_registrars():
        if not reg.is_registrar_enabled(r.get_descriptor().name):
            continue
        if not r.is_available():
            continue
        union.update(r.get_descriptor().navigation_entries)
    assert collected == frozenset(union)


@pytest.mark.architecture
@pytest.mark.contract
def test_run_gui_shell_bootstraps_edition_aware_feature_registry():
    """Widget-Pfad: Edition auflösen und Registry nach init_infrastructure."""
    path = PROJECT_ROOT / "run_gui_shell.py"
    source = path.read_text(encoding="utf-8")
    assert "init_infrastructure" in source
    assert "resolve_active_edition_name" in source
    assert "build_feature_registry_for_edition" in source
    pos_infra = source.find("init_infrastructure")
    pos_ed = source.find("resolve_active_edition_name")
    assert pos_infra != -1 and pos_ed != -1 and pos_infra < pos_ed, (
        "run_gui_shell: init_infrastructure muss vor resolve_active_edition_name stehen."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_breadcrumb_manager_uses_nav_context():
    text = (APP_ROOT / "gui" / "breadcrumbs" / "manager.py").read_text(encoding="utf-8")
    assert "nav_context" in text
    assert "is_nav_entry_allowed" in text


@pytest.mark.architecture
@pytest.mark.contract
def test_features_builtins_wires_discovery():
    text = (app_features_source_root() / "builtins.py").read_text(encoding="utf-8")
    assert "register_discovered_feature_registrars" in text
    assert "feature_discovery" in text


@pytest.mark.architecture
@pytest.mark.contract
def test_feature_discovery_wires_governance_validation():
    text = (app_features_source_root() / "feature_discovery.py").read_text(encoding="utf-8")
    assert "plan_registration_order" in text
    assert "DiscoveredFeatureRegistrar" in text


@pytest.mark.architecture
@pytest.mark.contract
def test_dependency_packaging_declares_canonical_policies_and_validation():
    text = (app_features_source_root() / "dependency_packaging.py").read_text(encoding="utf-8")
    assert "CANONICAL_GROUP_POLICIES" in text
    assert "validate_packaging_alignment" in text
    assert "validate_availability_probe_names_align" in text


@pytest.mark.architecture
@pytest.mark.contract
def test_release_matrix_wires_edition_and_packaging():
    text = (app_features_source_root() / "release_matrix.py").read_text(encoding="utf-8")
    assert "OFFICIAL_BUILD_RELEASE_EDITION_NAMES" in text
    assert "validate_release_matrix_consistency" in text
    assert "edition_declared_and_implied_dependency_groups" in text
    assert "packaging_target_for" in text


@pytest.mark.architecture
@pytest.mark.contract
def test_pyproject_toml_exists_for_pep621():
    assert (PROJECT_ROOT / "pyproject.toml").is_file()


@pytest.mark.architecture
@pytest.mark.contract
def test_edition_smoke_workflow_uses_release_matrix_ci_script():
    path = PROJECT_ROOT / ".github" / "workflows" / "edition-smoke-matrix.yml"
    assert path.is_file(), f"missing {path}"
    text = path.read_text(encoding="utf-8")
    assert "release_matrix_ci.py" in text
    assert "fromJson" in text
    assert "LDC_EDITION" in text
    assert "matrix.smoke_paths" in text
    assert "matrix.pip_extras" in text


@pytest.mark.architecture
@pytest.mark.contract
def test_nav_context_delegates_to_nav_binding():
    text = (APP_ROOT / "gui" / "navigation" / "nav_context.py").read_text(encoding="utf-8")
    assert "collect_active_navigation_entry_ids" in text
    assert (
        "from app.features.nav_binding import collect_active_navigation_entry_ids" in text
        or (
            "from app.features import" in text
            and "collect_active_navigation_entry_ids" in text
        )
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_dependency_availability_has_no_gui_import():
    path = app_features_source_root() / "dependency_availability.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("app.gui"):
            pytest.fail(f"dependency_availability.py darf app.gui nicht importieren: {node.module}")
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("app.gui"):
                    pytest.fail(f"dependency_availability.py darf app.gui nicht importieren: {alias.name}")


@pytest.mark.architecture
@pytest.mark.contract
def test_core_does_not_import_manifest_subpackages():
    violations = []
    for p in APP_ROOT.joinpath("core").rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module.startswith("app.features.editions"):
                    violations.append(str(p.relative_to(APP_ROOT)))
                if node.module.startswith("app.features.dependency_groups"):
                    violations.append(str(p.relative_to(APP_ROOT)))
                if node.module.startswith("app.features.edition_resolution"):
                    violations.append(str(p.relative_to(APP_ROOT)))
    assert not violations, (
        "core darf Edition-/Dependency-Manifeste nicht importieren. "
        f"Verletzungen: {violations}"
    )
