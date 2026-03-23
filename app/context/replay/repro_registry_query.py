"""
Repro registry queries – deterministic filters over loaded registry entries.

All query functions return a tuple sorted by failure_id. Pass a mapping from
``load_repro_registry`` or ``build_registry_from_repro_directory``.
"""

from typing import Mapping

from app.context.replay.repro_registry_models import ReproRegistryEntry


def _by_failure_id(entries: tuple[ReproRegistryEntry, ...]) -> tuple[ReproRegistryEntry, ...]:
    return tuple(sorted(entries, key=lambda e: e.failure_id))


def query_all(entries: Mapping[str, ReproRegistryEntry]) -> tuple[ReproRegistryEntry, ...]:
    """Every entry, ordered by failure_id."""
    return _by_failure_id(tuple(entries.values()))


def query_by_failure_type(
    entries: Mapping[str, ReproRegistryEntry],
    failure_type: str,
) -> tuple[ReproRegistryEntry, ...]:
    """Entries whose failure_type equals the given string (including empty string)."""
    return _by_failure_id(tuple(e for e in entries.values() if e.failure_type == failure_type))


def query_by_status(
    entries: Mapping[str, ReproRegistryEntry],
    status: str,
) -> tuple[ReproRegistryEntry, ...]:
    """Entries with the given lifecycle status."""
    return _by_failure_id(tuple(e for e in entries.values() if e.status == status))


def query_by_test_name(
    entries: Mapping[str, ReproRegistryEntry],
    test_name: str,
) -> tuple[ReproRegistryEntry, ...]:
    """Entries with the given test_name (exact match)."""
    return _by_failure_id(tuple(e for e in entries.values() if e.test_name == test_name))


def query_by_version(
    entries: Mapping[str, ReproRegistryEntry],
    version: str,
) -> tuple[ReproRegistryEntry, ...]:
    """Entries whose indexed replay system_version string equals the given value."""
    return _by_failure_id(tuple(e for e in entries.values() if e.version == version))
