"""
Zielmodell: Dependency-Gruppen → pip-Extras / Basisinstallation (PEP 621–fähig).

- Eine Namenswelt: ``DependencyGroupDescriptor.name`` == Extra-Key, sofern publiziert.
- Kein zweites Manifest für Gruppennamen; Validierung gegen :func:`build_default_dependency_group_registry`.
- Version-Pins: ``pyproject.toml`` (Quelle); ``requirements.txt`` verweist auf editierbare Installation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterator, List, Optional

from app.features.dependency_groups.models import DependencyGroupDescriptor
from app.features.dependency_groups.registry import (
    DependencyGroupRegistry,
    build_default_dependency_group_registry,
)


class PackagingExtraKind(str, Enum):
    """Rolle der Gruppe in einer späteren PEP-621-Abgrenzung."""

    # In project.dependencies (Basis), kein pip-Extra für Endnutzer.
    BASE_INSTALL = "base_install"
    # Sichtbares optional-dependencies[gruppe] mit ggf. leerer oder gefüllter Liste.
    RUNTIME_EXTRA = "runtime_extra"
    # Fachliche Gruppe ohne zusätzliche PyPI-Zeilen (Monolith); kein Extra.
    LOGICAL_MARKER = "logical_marker"
    # Nur CI/Entwicklung; optional-dependencies.dev oder dependency-groups — nicht Runtime-Feature.
    DEV_EXTRA = "dev_extra"


@dataclass(frozen=True, slots=True)
class PackagingGroupPolicy:
    """
    Architektur-Entscheidung pro registrierter Gruppe (unabhängig vom Descriptor-Inhalt).

    Bei Publikation als Extra ist der Key identisch zum Gruppennamen (keine zweite Namenswelt).
    """

    extra_kind: PackagingExtraKind
    include_in_default_install: bool
    """True: ``python_packages`` dieser Gruppe fließen in die Basisinstallation (project.dependencies)."""
    publish_as_pip_extra: bool
    """True: später ``[project.optional-dependencies.<name>]`` vorgesehen."""
    dev_only: bool
    runtime_only: bool
    """False für dev; True für alles, was nicht dev_only ist."""
    publish_for_end_users: bool
    """False: nur Tooling/Metapaket-Doku, nicht als Produkt-„Feature-Extra“ kommuniziert."""


@dataclass(frozen=True, slots=True)
class PackagingGroupTarget:
    """Gemergter Zielzustand: Descriptor + Policy (für Doku, Export, Validierung)."""

    descriptor: DependencyGroupDescriptor
    policy: PackagingGroupPolicy
    extra_name: Optional[str]
    """``None`` wenn ``publish_as_pip_extra`` False; sonst Gruppenname."""

    @property
    def pip_distribution_names(self) -> tuple[str, ...]:
        return self.descriptor.python_packages

    @property
    def implied_by_features(self) -> frozenset[str]:
        return self.descriptor.required_for_features


# Klare Produktentscheidungen — erweitern nur gemeinsam mit neuem Builtin-Descriptor + Tests.
CANONICAL_GROUP_POLICIES: dict[str, PackagingGroupPolicy] = {
    "core": PackagingGroupPolicy(
        extra_kind=PackagingExtraKind.BASE_INSTALL,
        include_in_default_install=True,
        publish_as_pip_extra=False,
        dev_only=False,
        runtime_only=True,
        publish_for_end_users=False,
    ),
    "workflows": PackagingGroupPolicy(
        extra_kind=PackagingExtraKind.LOGICAL_MARKER,
        include_in_default_install=False,
        publish_as_pip_extra=False,
        dev_only=False,
        runtime_only=True,
        publish_for_end_users=False,
    ),
    "rag": PackagingGroupPolicy(
        extra_kind=PackagingExtraKind.RUNTIME_EXTRA,
        include_in_default_install=False,
        publish_as_pip_extra=True,
        dev_only=False,
        runtime_only=True,
        publish_for_end_users=True,
    ),
    "agents": PackagingGroupPolicy(
        extra_kind=PackagingExtraKind.RUNTIME_EXTRA,
        include_in_default_install=False,
        publish_as_pip_extra=True,
        dev_only=False,
        runtime_only=True,
        publish_for_end_users=True,
    ),
    "ops": PackagingGroupPolicy(
        extra_kind=PackagingExtraKind.RUNTIME_EXTRA,
        include_in_default_install=False,
        publish_as_pip_extra=True,
        dev_only=False,
        runtime_only=True,
        publish_for_end_users=False,
    ),
    "qml": PackagingGroupPolicy(
        extra_kind=PackagingExtraKind.RUNTIME_EXTRA,
        include_in_default_install=False,
        publish_as_pip_extra=True,
        dev_only=False,
        runtime_only=True,
        publish_for_end_users=True,
    ),
    "governance": PackagingGroupPolicy(
        extra_kind=PackagingExtraKind.RUNTIME_EXTRA,
        include_in_default_install=False,
        publish_as_pip_extra=True,
        dev_only=False,
        runtime_only=True,
        publish_for_end_users=True,
    ),
    "dev": PackagingGroupPolicy(
        extra_kind=PackagingExtraKind.DEV_EXTRA,
        include_in_default_install=False,
        publish_as_pip_extra=True,
        dev_only=True,
        runtime_only=False,
        publish_for_end_users=False,
    ),
}


def _extra_name_for(policy: PackagingGroupPolicy, group_name: str) -> Optional[str]:
    if not policy.publish_as_pip_extra:
        return None
    return group_name


def iter_packaging_targets(registry: DependencyGroupRegistry) -> Iterator[PackagingGroupTarget]:
    for desc in registry.iter_groups():
        pol = CANONICAL_GROUP_POLICIES.get(desc.name)
        if pol is None:
            continue
        yield PackagingGroupTarget(
            descriptor=desc,
            policy=pol,
            extra_name=_extra_name_for(pol, desc.name),
        )


def packaging_target_for(registry: DependencyGroupRegistry, group_name: str) -> Optional[PackagingGroupTarget]:
    desc = registry.get_group(group_name)
    if desc is None:
        return None
    pol = CANONICAL_GROUP_POLICIES.get(group_name)
    if pol is None:
        return None
    return PackagingGroupTarget(
        descriptor=desc,
        policy=pol,
        extra_name=_extra_name_for(pol, group_name),
    )


def default_install_distribution_names(registry: DependencyGroupRegistry) -> tuple[str, ...]:
    """Alle PyPI-Namen für die Basisinstallation (derzeit nur ``core``)."""
    names: list[str] = []
    for t in iter_packaging_targets(registry):
        if t.policy.include_in_default_install:
            names.extend(t.pip_distribution_names)
    return tuple(names)


def optional_dependencies_target_dict(registry: DependencyGroupRegistry) -> dict[str, list[str]]:
    """
    Zielstruktur für ``[project.optional-dependencies]`` (Namen ohne Pins).

    Reihenfolge der Keys: Registry-Reihenfolge, gefiltert nach Publikation als Extra.
    """
    out: dict[str, list[str]] = {}
    for name in registry.list_groups():
        t = packaging_target_for(registry, name)
        if t is None or t.extra_name is None:
            continue
        out[t.extra_name] = list(t.pip_distribution_names)
    return out


def pyproject_optional_dependencies_snippet(registry: DependencyGroupRegistry) -> str:
    """Lesbarer TOML-Block als Vorlage — Abgleich mit ``pyproject.toml`` über :func:`validate_pep621_pyproject_alignment`."""
    lines = ["[project.optional-dependencies]"]
    for key, pkgs in optional_dependencies_target_dict(registry).items():
        if pkgs:
            lines.append(f"{key} = [")
            for p in pkgs:
                lines.append(f'  "{p}",')
            lines.append("]")
        else:
            lines.append(f"{key} = []")
    return "\n".join(lines) + "\n"


def validate_packaging_alignment(registry: DependencyGroupRegistry) -> List[str]:
    """
    Drift-Kontrolle: jede Registry-Gruppe hat Policy; jede Policy-Gruppe existiert in der Registry;
    Policy-Felder sind konsistent; Descriptor-Felder passen zur Rolle.
    """
    errors: list[str] = []
    reg_names = frozenset(registry.list_groups())
    pol_names = frozenset(CANONICAL_GROUP_POLICIES.keys())

    for n in reg_names - pol_names:
        errors.append(f"Dependency-Gruppe {n!r} hat keine Packaging-Policy in CANONICAL_GROUP_POLICIES.")
    for n in pol_names - reg_names:
        errors.append(f"Packaging-Policy {n!r} ohne Eintrag im DependencyGroupRegistry.")

    for name in reg_names & pol_names:
        desc = registry.get_group(name)
        pol = CANONICAL_GROUP_POLICIES[name]
        assert desc is not None

        if pol.dev_only and pol.runtime_only:
            errors.append(f"{name!r}: Policy widerspricht sich (dev_only und runtime_only).")
        if pol.extra_kind is PackagingExtraKind.BASE_INSTALL:
            if not pol.include_in_default_install:
                errors.append(f"{name!r}: BASE_INSTALL erwartet include_in_default_install.")
            if pol.publish_as_pip_extra:
                errors.append(f"{name!r}: BASE_INSTALL darf kein pip-Extra sein.")
        if pol.extra_kind is PackagingExtraKind.LOGICAL_MARKER:
            if pol.publish_as_pip_extra:
                errors.append(f"{name!r}: LOGICAL_MARKER darf nicht als pip-Extra publiziert werden.")
            if desc.python_packages:
                errors.append(
                    f"{name!r}: LOGICAL_MARKER sollte keine python_packages im Descriptor haben "
                    f"(Drift zur Paketierungsrolle)."
                )
        if pol.extra_kind is PackagingExtraKind.DEV_EXTRA:
            if not pol.dev_only:
                errors.append(f"{name!r}: DEV_EXTRA erwartet dev_only=True.")
            if pol.include_in_default_install:
                errors.append(f"{name!r}: dev-Gruppe nicht in die Basisinstallation einplanen.")

        if pol.publish_for_end_users and pol.dev_only:
            errors.append(f"{name!r}: dev_only-Gruppe nicht als Endnutzer-Extra kennzeichnen.")
        if pol.extra_kind is PackagingExtraKind.RUNTIME_EXTRA and pol.dev_only:
            errors.append(f"{name!r}: RUNTIME_EXTRA widerspricht dev_only.")

        if name == "core" and desc.optional:
            errors.append("core muss im Descriptor optional=False bleiben.")
        if pol.include_in_default_install and name != "core":
            errors.append(
                f"{name!r}: nur ``core`` ist als Basisinstallations-Träger vorgesehen — "
                f"weitere Gruppen nicht nach default mergen ohne Architekturreview."
            )

    return errors


def _requirement_line_to_distribution_name(line: str) -> str:
    s = line.strip()
    if not s:
        return ""
    base = s.split(";", 1)[0].strip()
    name = base.split("[", 1)[0].strip()
    for sep in (">=", "<=", "==", "!=", "~=", ">", "<"):
        idx = name.find(sep)
        if idx != -1:
            name = name[:idx].strip()
            break
    return name


def _canonical_package_name(name: str) -> str:
    try:
        from packaging.utils import canonicalize_name

        return canonicalize_name(name)
    except ImportError:
        return name.strip().lower().replace("_", "-")


def validate_pep621_pyproject_alignment(
    pyproject_path: Path,
    *,
    registry: Optional[DependencyGroupRegistry] = None,
) -> List[str]:
    """
    Drift-Check: ``[project.dependencies]`` = core-Gruppe, ``[project.optional-dependencies]`` = Packaging-Mapping.

    Vergleicht normalisierte Distributionsnamen (Versionsspezifikationen können in pyproject detaillierter sein).
    """
    import tomllib

    errors: list[str] = []
    if not pyproject_path.is_file():
        return [f"pyproject.toml nicht gefunden: {pyproject_path}"]

    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    proj = data.get("project") or {}
    opt = proj.get("optional-dependencies") or {}
    dr = registry or build_default_dependency_group_registry()

    expected_opt = optional_dependencies_target_dict(dr)
    exp_keys = frozenset(expected_opt.keys())
    act_keys = frozenset(opt.keys())
    if exp_keys != act_keys:
        errors.append(
            "[project.optional-dependencies]: Keys weichen von optional_dependencies_target_dict() ab — "
            f"erwartet {sorted(exp_keys)}, ist {sorted(act_keys)}."
        )

    for key in exp_keys & act_keys:
        exp_names = frozenset(_canonical_package_name(x) for x in expected_opt[key])
        raw_list = opt[key]
        if not isinstance(raw_list, list):
            errors.append(f"optional-dependencies.{key!r}: erwartet Liste, ist {type(raw_list).__name__}.")
            continue
        act_names = frozenset(
            _canonical_package_name(_requirement_line_to_distribution_name(str(x)))
            for x in raw_list
            if str(x).strip()
        )
        if exp_names != act_names:
            errors.append(
                f"optional-dependencies.{key!r}: Paketnamen weichen von DependencyGroupDescriptor.python_packages ab — "
                f"erwartet {sorted(exp_names)}, ist {sorted(act_names)}."
            )

    deps = proj.get("dependencies") or []
    if not isinstance(deps, list):
        errors.append("project.dependencies ist keine Liste.")
    else:
        core_expect = frozenset(_canonical_package_name(n) for n in default_install_distribution_names(dr))
        core_act = frozenset(
            _canonical_package_name(_requirement_line_to_distribution_name(str(x)))
            for x in deps
            if str(x).strip()
        )
        if core_expect != core_act:
            errors.append(
                "project.dependencies (core) weicht von default_install_distribution_names() ab — "
                f"erwartet {sorted(core_expect)}, ist {sorted(core_act)}."
            )

    return errors


def validate_availability_probe_names_align(registry: DependencyGroupRegistry) -> List[str]:
    """
    Gleiche Namensmenge wie :data:`app.features.dependency_availability._GROUP_PROBES`
    (keine zweite konkurrierende Wahrheit).
    """
    from app.features.dependency_availability import _GROUP_PROBES

    reg = frozenset(registry.list_groups())
    probes = frozenset(_GROUP_PROBES.keys())
    errors: list[str] = []
    for n in reg - probes:
        errors.append(
            f"Dependency-Gruppe {n!r} ohne Modulprobe in dependency_availability._GROUP_PROBES."
        )
    for n in probes - reg:
        errors.append(f"availability-Probe {n!r} ohne DependencyGroupDescriptor im Registry.")
    return errors
