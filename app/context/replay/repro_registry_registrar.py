"""
Repro registry registrar – register and update entries by failure_id.

File-backed only; uses repro_registry_store load/save.
"""

from pathlib import Path
from typing import Mapping, Union

from app.context.replay.repro_registry_models import ReproRegistryEntry
from app.context.replay.repro_registry_store import load_repro_registry, save_repro_registry


def register_entry(
    path: Union[str, Path],
    entry: ReproRegistryEntry,
) -> ReproRegistryEntry:
    """
    Insert or replace the entry for entry.failure_id and persist.
    Returns the stored entry.
    """
    path = Path(path)
    reg = load_repro_registry(path)
    reg[entry.failure_id] = entry
    save_repro_registry(reg, path)
    return entry


def update_entry(
    path: Union[str, Path],
    failure_id: str,
    *,
    status: str | None = None,
    classification: str | None = None,
) -> ReproRegistryEntry:
    """
    Patch status and/or classification for failure_id. Other fields unchanged.
    Raises KeyError if failure_id is not present.
    """
    path = Path(path)
    reg = load_repro_registry(path)
    if failure_id not in reg:
        raise KeyError(failure_id)
    cur = reg[failure_id]
    reg[failure_id] = ReproRegistryEntry(
        failure_id=cur.failure_id,
        status=status if status is not None else cur.status,
        classification=classification if classification is not None else cur.classification,
        failure_type=cur.failure_type,
        test_name=cur.test_name,
        version=cur.version,
        file_path=cur.file_path,
        source=cur.source,
    )
    save_repro_registry(reg, path)
    return reg[failure_id]


def upsert_entry(
    path: Union[str, Path],
    failure_id: str,
    *,
    status: str,
    classification: str,
) -> ReproRegistryEntry:
    """
    Register a full entry or replace if failure_id exists.
    """
    return register_entry(
        path,
        ReproRegistryEntry(
            failure_id=failure_id,
            status=status,
            classification=classification,
        ),
    )


def get_entry(path: Union[str, Path], failure_id: str) -> ReproRegistryEntry | None:
    return load_repro_registry(path).get(failure_id)


def list_entries(path: Union[str, Path]) -> Mapping[str, ReproRegistryEntry]:
    """Snapshot of the registry (sorted keys in JSON on save; dict order is insertion)."""
    return dict(sorted(load_repro_registry(path).items()))
