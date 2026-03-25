"""
Build-/Release-Matrix aus Editionen — ableitbar, testbar, exportierbar.

Offizielle Ziele: ``OFFICIAL_BUILD_RELEASE_EDITION_NAMES`` + ``EDITION_SMOKE_PROFILES``.
Interne Plugin-Validierung: ``INTERNAL_PLUGIN_VALIDATION_EDITION_NAMES`` +
``PLUGIN_VALIDATION_SMOKE_PROFILES`` (kein Eintrag in der öffentlichen CI-Matrix).

Dependency-Gruppen und pip-Extras: Manifeste + ``dependency_packaging``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

from app.features.dependency_groups.registry import DependencyGroupRegistry, build_default_dependency_group_registry
from app.features.dependency_packaging import packaging_target_for
from app.features.edition_resolution import DEFAULT_DESKTOP_EDITION
from app.features.editions.models import EditionDescriptor
from app.features.editions.registry import EditionRegistry, build_default_edition_registry
from app.features.manifest_resolution import edition_declared_and_implied_dependency_groups


class ReleaseChannel(str, Enum):
    """Ableitung aus ``EditionDescriptor.visibility_profile`` (kein zweites Kanal-Manifest)."""

    STABLE = "stable"
    INTERNAL = "internal"
    EXPERIMENTAL = "experimental"


# Offizielle Build-/Release-Ziele (kleine, realistische Menge). Nicht jede künftige Edition muss hier stehen.
OFFICIAL_BUILD_RELEASE_EDITION_NAMES: Tuple[str, ...] = ("minimal", "standard", "automation", "full")

# Interne Plugin-Validierungs-Editionen: **kein** öffentliches Release-/CI-Matrix-Ziel — nur Test-/Doku-Vertrag.
INTERNAL_PLUGIN_VALIDATION_EDITION_NAMES: Tuple[str, ...] = ("plugin_example",)

# Produkt-Referenz für Default-Bootstrap und Release-Vergleich — muss mit ``DEFAULT_DESKTOP_EDITION`` übereinstimmen.
REFERENCE_BUILD_EDITION_NAME: str = "full"

# CI: pip-Extras für Testjobs (offizielle Build-Targets + Profil-Hinweise).
DEFAULT_PIP_CI_EXTRAS: Tuple[str, ...] = ("dev",)

_ARTIFACT_PREFIX = "linux-desktop-chat"

_VISIBILITY_TO_CHANNEL: dict[str, ReleaseChannel] = {
    "public": ReleaseChannel.STABLE,
    "internal": ReleaseChannel.INTERNAL,
    "partner": ReleaseChannel.EXPERIMENTAL,
}


def _release_channel_for_edition(ed: EditionDescriptor) -> ReleaseChannel:
    return _VISIBILITY_TO_CHANNEL.get(ed.visibility_profile, ReleaseChannel.EXPERIMENTAL)


def artifact_name_for_edition(edition_name: str) -> str:
    """Konvention: ``linux-desktop-chat-<edition>`` (PEP-503-freundlich, Edition ohne Unterstriche)."""
    safe = edition_name.strip().lower().replace("_", "-")
    return f"{_ARTIFACT_PREFIX}-{safe}"


@dataclass(frozen=True, slots=True)
class EditionSmokeProfile:
    """Test-/Smoke-Vertrag pro Edition (Marker + Vorschläge, kein Pytest-Ersatz)."""

    scope_id: str
    pytest_markers: Tuple[str, ...]
    suggested_smoke_paths: Tuple[str, ...]


# Pytest-Marker sind Konvention (`pytest -m "smoke and edition_full"`); Pfade relativ zum Repo-Root.
EDITION_SMOKE_PROFILES: dict[str, EditionSmokeProfile] = {
    "minimal": EditionSmokeProfile(
        scope_id="minimal_core",
        pytest_markers=("smoke", "edition_minimal"),
        suggested_smoke_paths=(
            "tests/smoke/test_app_startup.py",
            "tests/smoke/test_basic_chat.py",
            "tests/smoke/test_shell_gui.py",
        ),
    ),
    "standard": EditionSmokeProfile(
        scope_id="standard_desktop",
        pytest_markers=("smoke", "edition_standard"),
        suggested_smoke_paths=(
            "tests/smoke/test_app_startup.py",
            "tests/smoke/test_basic_chat.py",
            "tests/smoke/test_prompt_studio_slice1_import.py",
            "tests/smoke/test_doc_search_service_smoke.py",
        ),
    ),
    "automation": EditionSmokeProfile(
        scope_id="automation_extended",
        pytest_markers=("smoke", "edition_automation"),
        suggested_smoke_paths=(
            "tests/smoke/test_app_startup.py",
            "tests/smoke/test_full_workflow.py",
            "tests/smoke/test_navigation_consistency.py",
        ),
    ),
    "full": EditionSmokeProfile(
        scope_id="full_product",
        pytest_markers=("smoke", "edition_full"),
        suggested_smoke_paths=(
            "tests/smoke/test_app_startup.py",
            "tests/smoke/test_navigation_consistency.py",
            "tests/architecture/test_edition_manifest_guards.py",
        ),
    ),
}


@dataclass(frozen=True, slots=True)
class PluginValidationSmokeProfile:
    """
    Maschinenlesbarer Vertrag für **interne** Plugin-/Edition-Tests — nicht Teil der öffentlichen Matrix.

    Ergänzt ``EDITION_SMOKE_PROFILES`` (nur offizielle Editionen); kein zweites Build-Target-Modell.
    """

    edition_name: str
    scope_id: str
    pytest_markers: Tuple[str, ...]
    suggested_test_paths: Tuple[str, ...]
    """Relativ zum Repo-Root; typ. Unit-/Arch-Tests statt vollständiger GUI-Smokes."""
    pip_ci_extras_hint: Tuple[str, ...]
    """Empfohlene pip-Extras für lokale/optionale Jobs (z. B. ``dev``)."""
    optional_plugin_install_hint: str
    """Kurztext für Operatoren (kein automatischer pip-Aufruf aus der Matrix)."""
    required_env_hints: Tuple[str, ...]
    """z. B. ``LDC_EDITION=…`` — Dokumentations-/Runner-Hinweis."""
    optional_config_hint: str
    """YAML/Env-Hinweis zur Produktfreigabe; leer wenn entbehrlich."""
    notes: str
    matrix_pip_extras: Tuple[str, ...] = ()
    """PEP-621-Extras für ``pip install -e ".[…]"`` im internen Plugin-CI-Job; leer → ``pip_ci_extras_hint``."""
    ci_install_demo_plugin: bool = False
    """True: Workflow installiert ``examples/plugins/ldc_plugin_example`` (Entry-Point sichtbar)."""


PLUGIN_VALIDATION_SMOKE_PROFILES: dict[str, PluginValidationSmokeProfile] = {
    "plugin_example": PluginValidationSmokeProfile(
        edition_name="plugin_example",
        scope_id="internal_plugin_example_demo",
        pytest_markers=("internal_plugin", "edition_plugin_example"),
        suggested_test_paths=(
            "tests/unit/features/test_plugin_product_activation.py",
            "tests/unit/features/test_plugin_release_configuration.py",
            "tests/unit/features/test_entry_point_plugin_integration.py",
        ),
        pip_ci_extras_hint=DEFAULT_PIP_CI_EXTRAS,
        matrix_pip_extras=("rag", "dev"),
        ci_install_demo_plugin=True,
        optional_plugin_install_hint=(
            "pip install -e examples/plugins/ldc_plugin_example  # Demo-Registrar ldc.plugin.example"
        ),
        required_env_hints=("LDC_EDITION=plugin_example",),
        optional_config_hint=(
            "Optional: config/plugin_feature_release.example.yaml — siehe PLUGIN_FEATURE_RELEASE_CONFIGURATION.md"
        ),
        notes=(
            "Interne Validierung Entry-Point + Produktfreigabe + YAML; kein Artefakt, kein öffentlicher Release-Kanal."
        ),
    ),
}


def is_official_release_edition(edition_name: str) -> bool:
    return edition_name.strip().lower() in {n.lower() for n in OFFICIAL_BUILD_RELEASE_EDITION_NAMES}


def is_internal_plugin_validation_edition(edition_name: str) -> bool:
    return edition_name.strip().lower() in {n.lower() for n in INTERNAL_PLUGIN_VALIDATION_EDITION_NAMES}


def get_plugin_validation_smoke_profile(edition_name: str) -> Optional[PluginValidationSmokeProfile]:
    key = edition_name.strip().lower()
    for canonical in INTERNAL_PLUGIN_VALIDATION_EDITION_NAMES:
        if canonical.lower() == key:
            return PLUGIN_VALIDATION_SMOKE_PROFILES.get(canonical)
    return None


def iter_internal_plugin_validation_editions(
    edition_registry: EditionRegistry,
) -> Iterator[EditionDescriptor]:
    for name in INTERNAL_PLUGIN_VALIDATION_EDITION_NAMES:
        ed = edition_registry.get_edition(name)
        if ed is not None:
            yield ed


def _repo_root_for_matrix_checks() -> Path:
    # app/features/release_matrix.py -> parents[2] = Repo-Root
    return Path(__file__).resolve().parents[2]


def validate_internal_plugin_smoke_consistency(
    *,
    edition_registry: Optional[EditionRegistry] = None,
) -> List[str]:
    """
    Konsistenz interner Plugin-Profile vs. Registry — für validate / leichte Governance.

    Leere Liste = ok.
    """
    errors: list[str] = []
    er = edition_registry or build_default_edition_registry()
    root = _repo_root_for_matrix_checks()

    overlap = frozenset(OFFICIAL_BUILD_RELEASE_EDITION_NAMES) & frozenset(
        INTERNAL_PLUGIN_VALIDATION_EDITION_NAMES
    )
    if overlap:
        errors.append(
            f"INTERNAL_PLUGIN_VALIDATION_EDITION_NAMES darf OFFICIAL_BUILD_RELEASE_EDITION_NAMES nicht schneiden: {sorted(overlap)}"
        )

    for name in INTERNAL_PLUGIN_VALIDATION_EDITION_NAMES:
        if name not in PLUGIN_VALIDATION_SMOKE_PROFILES:
            errors.append(f"Interne Plugin-Edition {name!r} ohne PLUGIN_VALIDATION_SMOKE_PROFILES-Eintrag.")
            continue
        prof = PLUGIN_VALIDATION_SMOKE_PROFILES[name]
        if prof.edition_name != name:
            errors.append(
                f"Plugin-Smoke-Profil: edition_name {prof.edition_name!r} weicht von Schlüssel {name!r} ab."
            )
        ed = er.get_edition(name)
        if ed is None:
            errors.append(f"Interne Plugin-Edition {name!r} fehlt im EditionRegistry.")
            continue
        if ed.visibility_profile != "internal":
            errors.append(
                f"Interne Plugin-Edition {name!r}: visibility_profile {ed.visibility_profile!r} — erwartet 'internal'."
            )
        for rel in prof.suggested_test_paths:
            p = root / rel
            if not p.is_file():
                errors.append(f"Plugin-Smoke {name!r}: suggested_test_paths-Eintrag fehlt: {rel!r}")

    for key in PLUGIN_VALIDATION_SMOKE_PROFILES:
        if key not in INTERNAL_PLUGIN_VALIDATION_EDITION_NAMES:
            errors.append(
                f"PLUGIN_VALIDATION_SMOKE_PROFILES enthält {key!r}, aber nicht in INTERNAL_PLUGIN_VALIDATION_EDITION_NAMES."
            )

    return errors


def plugin_validation_profiles_to_json_dict() -> Dict[str, Any]:
    """Export für Skripte/Doku — nicht Teil der öffentlichen Release-Matrix-JSON."""
    out: dict[str, Any] = {
        "internal_plugin_validation_edition_names": list(INTERNAL_PLUGIN_VALIDATION_EDITION_NAMES),
        "profiles": {},
    }
    for name, prof in PLUGIN_VALIDATION_SMOKE_PROFILES.items():
        out["profiles"][name] = {
            "edition_name": prof.edition_name,
            "scope_id": prof.scope_id,
            "pytest_markers": list(prof.pytest_markers),
            "suggested_test_paths": list(prof.suggested_test_paths),
            "pip_ci_extras_hint": list(prof.pip_ci_extras_hint),
            "matrix_pip_extras": list(prof.matrix_pip_extras),
            "ci_install_demo_plugin": prof.ci_install_demo_plugin,
            "optional_plugin_install_hint": prof.optional_plugin_install_hint,
            "required_env_hints": list(prof.required_env_hints),
            "optional_config_hint": prof.optional_config_hint,
            "notes": prof.notes,
        }
    return out


def build_internal_plugin_github_actions_matrix_payload() -> Dict[str, List[Dict[str, str]]]:
    """
    GitHub Actions ``strategy.matrix`` als ``{"include": [{"edition", "smoke_paths", "pip_extras", "install_demo_plugin"}, ...]}``.

    Alle Zeilen ausschließlich aus ``PLUGIN_VALIDATION_SMOKE_PROFILES`` — keine offiziellen Editionen.
    """
    rows: list[dict[str, str]] = []
    for _key, prof in PLUGIN_VALIDATION_SMOKE_PROFILES.items():
        extras_src = prof.matrix_pip_extras if prof.matrix_pip_extras else prof.pip_ci_extras_hint
        rows.append(
            {
                "edition": prof.edition_name,
                "smoke_paths": " ".join(prof.suggested_test_paths),
                "pip_extras": ",".join(sorted(extras_src)),
                "install_demo_plugin": "true" if prof.ci_install_demo_plugin else "false",
            }
        )
    return {"include": rows}


def pip_overlay_distribution_names_for_target(
    target: EditionBuildTarget,
    dep_registry: DependencyGroupRegistry,
) -> Tuple[str, ...]:
    """
    PyPI-Distributionsnamen aus den der Edition zugeordneten Runtime-/CI-Extras (ohne ``core``-Basisliste).

    Für CI: idempotenter ``pip install <names>`` neben ``requirements.txt`` — dokumentiert die Matrix,
    bis optional-dependencies produktiv sind.
    """
    names: set[str] = set()
    for ex in (*target.pip_runtime_extras, *target.pip_ci_extras):
        t = packaging_target_for(dep_registry, ex)
        if t is not None:
            names.update(t.pip_distribution_names)
    return tuple(sorted(names))


def _pip_runtime_extras_for_groups(
    dep_registry: DependencyGroupRegistry,
    groups: frozenset[str],
) -> Tuple[str, ...]:
    """pip-Extras (Gruppennamen = Extra-Keys), die zur Laufzeit für diese Gruppenmenge sinnvoll sind — ohne ``dev``."""
    names: list[str] = []
    for g in sorted(groups):
        t = packaging_target_for(dep_registry, g)
        if t is None or t.extra_name is None:
            continue
        if t.policy.dev_only:
            continue
        names.append(t.extra_name)
    return tuple(names)


@dataclass(frozen=True, slots=True)
class EditionBuildTarget:
    edition_name: str
    artifact_name: str
    release_channel: str
    dependency_groups: Tuple[str, ...]
    """Vereinigung deklarierter und feature-implizierter Gruppen (wie ``manifest_resolution``)."""
    pip_runtime_extras: Tuple[str, ...]
    """Subset der Gruppen mit publiziertem pip-Extra, ohne ``dev``."""
    pip_ci_extras: Tuple[str, ...]
    """Empfohlen für Testjobs (typisch ``dev``-Extra)."""
    smoke_test_scope: str
    pytest_markers: Tuple[str, ...]
    suggested_smoke_paths: Tuple[str, ...]
    default_shell: str
    platform_notes: str
    is_reference_edition: bool
    experimental_allowed: bool
    visibility_profile: str
    enabled_features: Tuple[str, ...]


def _smoke_profile_for(edition_name: str) -> EditionSmokeProfile:
    p = EDITION_SMOKE_PROFILES.get(edition_name)
    if p is None:
        return EditionSmokeProfile(
            scope_id="generic",
            pytest_markers=("smoke",),
            suggested_smoke_paths=("tests/smoke/test_app_startup.py",),
        )
    return p


def build_edition_build_target(
    edition: EditionDescriptor,
    *,
    dep_registry: DependencyGroupRegistry,
    pip_ci_extras: Tuple[str, ...] = DEFAULT_PIP_CI_EXTRAS,
) -> EditionBuildTarget:
    groups = edition_declared_and_implied_dependency_groups(edition, dep_registry)
    eff = tuple(sorted(edition.enabled_features - edition.disabled_features))
    sp = _smoke_profile_for(edition.name)
    ch = _release_channel_for_edition(edition)
    return EditionBuildTarget(
        edition_name=edition.name,
        artifact_name=artifact_name_for_edition(edition.name),
        release_channel=ch.value,
        dependency_groups=tuple(sorted(groups)),
        pip_runtime_extras=_pip_runtime_extras_for_groups(dep_registry, groups),
        pip_ci_extras=pip_ci_extras,
        smoke_test_scope=sp.scope_id,
        pytest_markers=sp.pytest_markers,
        suggested_smoke_paths=sp.suggested_smoke_paths,
        default_shell=edition.default_shell,
        platform_notes=edition.notes,
        is_reference_edition=(edition.name == REFERENCE_BUILD_EDITION_NAME),
        experimental_allowed=edition.experimental_allowed,
        visibility_profile=edition.visibility_profile,
        enabled_features=tuple(sorted(eff)),
    )


@dataclass(frozen=True, slots=True)
class ReleaseMatrix:
    """Eingebaute offizielle Ziele; erweiterbar, sobald neue Editionen in ``OFFICIAL_*`` aufgenommen werden."""

    targets: Tuple[EditionBuildTarget, ...]
    official_edition_names: Tuple[str, ...]
    reference_edition_name: str


def iter_official_edition_descriptors(edition_registry: EditionRegistry) -> Iterator[EditionDescriptor]:
    for name in OFFICIAL_BUILD_RELEASE_EDITION_NAMES:
        ed = edition_registry.get_edition(name)
        if ed is not None:
            yield ed


def build_release_matrix(
    *,
    edition_registry: Optional[EditionRegistry] = None,
    dep_registry: Optional[DependencyGroupRegistry] = None,
    pip_ci_extras: Tuple[str, ...] = DEFAULT_PIP_CI_EXTRAS,
) -> ReleaseMatrix:
    er = edition_registry or build_default_edition_registry()
    dr = dep_registry or build_default_dependency_group_registry()
    targets = tuple(
        build_edition_build_target(ed, dep_registry=dr, pip_ci_extras=pip_ci_extras)
        for ed in iter_official_edition_descriptors(er)
    )
    return ReleaseMatrix(
        targets=targets,
        official_edition_names=OFFICIAL_BUILD_RELEASE_EDITION_NAMES,
        reference_edition_name=REFERENCE_BUILD_EDITION_NAME,
    )


def resolve_build_target(
    edition_name: str,
    *,
    edition_registry: Optional[EditionRegistry] = None,
    dep_registry: Optional[DependencyGroupRegistry] = None,
) -> Optional[EditionBuildTarget]:
    if edition_name not in OFFICIAL_BUILD_RELEASE_EDITION_NAMES:
        return None
    er = edition_registry or build_default_edition_registry()
    ed = er.get_edition(edition_name)
    if ed is None:
        return None
    dr = dep_registry or build_default_dependency_group_registry()
    return build_edition_build_target(ed, dep_registry=dr)


def validate_release_matrix_consistency(
    matrix: Optional[ReleaseMatrix] = None,
    *,
    edition_registry: Optional[EditionRegistry] = None,
    dep_registry: Optional[DependencyGroupRegistry] = None,
) -> List[str]:
    """
    Governance: offizielle Editionen, Artefakte, Gruppen, Referenzedition.

    Leere Liste = konsistent.
    """
    errors: list[str] = []
    er = edition_registry or build_default_edition_registry()
    dr = dep_registry or build_default_dependency_group_registry()
    m = matrix or build_release_matrix(edition_registry=er, dep_registry=dr)
    known_editions = frozenset(er.list_editions())
    known_groups = frozenset(dr.list_groups())

    if REFERENCE_BUILD_EDITION_NAME != DEFAULT_DESKTOP_EDITION:
        errors.append(
            f"REFERENCE_BUILD_EDITION_NAME {REFERENCE_BUILD_EDITION_NAME!r} weicht von "
            f"DEFAULT_DESKTOP_EDITION {DEFAULT_DESKTOP_EDITION!r} ab."
        )

    for name in OFFICIAL_BUILD_RELEASE_EDITION_NAMES:
        if name not in known_editions:
            errors.append(f"Offizielle Build-Edition {name!r} fehlt im EditionRegistry.")

    seen_artifacts: set[str] = set()
    for t in m.targets:
        if t.artifact_name in seen_artifacts:
            errors.append(f"Doppelter artifact_name: {t.artifact_name!r}")
        seen_artifacts.add(t.artifact_name)
        for g in t.dependency_groups:
            if g not in known_groups:
                errors.append(
                    f"Edition {t.edition_name!r}: unbekannte Dependency-Gruppe {g!r} im Build-Target."
                )
        for ex in t.pip_runtime_extras:
            if ex not in known_groups:
                errors.append(f"Edition {t.edition_name!r}: pip_runtime_extra {ex!r} unbekannt.")
        if t.edition_name not in OFFICIAL_BUILD_RELEASE_EDITION_NAMES:
            errors.append(f"Target enthält nicht-offizielle Edition {t.edition_name!r}.")
        if t.is_reference_edition and t.edition_name != REFERENCE_BUILD_EDITION_NAME:
            errors.append(f"Mehrdeutige Referenzedition bei {t.edition_name!r}.")
        # Abgleich abgeleiteter Gruppen mit Manifest-Hilfsfunktion (keine Doppelwahrheit)
        ed = er.get_edition(t.edition_name)
        if ed is not None:
            expected = edition_declared_and_implied_dependency_groups(ed, dr)
            if frozenset(t.dependency_groups) != expected:
                errors.append(
                    f"Edition {t.edition_name!r}: dependency_groups im Target weichen von "
                    f"edition_declared_and_implied_dependency_groups ab: "
                    f"{t.dependency_groups!r} vs {tuple(sorted(expected))!r}."
                )

    ref_count = sum(1 for t in m.targets if t.is_reference_edition)
    if ref_count != 1:
        errors.append(f"Erwartet genau eine Referenzedition im Matrix, gefunden: {ref_count}.")

    for name in OFFICIAL_BUILD_RELEASE_EDITION_NAMES:
        if name not in EDITION_SMOKE_PROFILES:
            errors.append(
                f"Offizielle Edition {name!r} ohne Eintrag in EDITION_SMOKE_PROFILES (Smoke-Vertrag)."
            )

    errors.extend(validate_internal_plugin_smoke_consistency(edition_registry=er))

    return errors


def edition_build_target_to_json_dict(target: EditionBuildTarget) -> Dict[str, Any]:
    """JSON-serialisierbar (nur Standard-Typen)."""
    d = asdict(target)
    return d


def release_matrix_to_json_dict(matrix: ReleaseMatrix) -> Dict[str, Any]:
    return {
        "official_edition_names": list(matrix.official_edition_names),
        "reference_edition_name": matrix.reference_edition_name,
        "targets": [edition_build_target_to_json_dict(t) for t in matrix.targets],
    }
