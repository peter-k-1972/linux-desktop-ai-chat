"""
Repro registry status – update lifecycle status on the authoritative repro artifact.

The on-disk repro case JSON is the source of truth (``registry.status``). The
aggregated registry file is a derived index; pass ``registry_path`` to refresh
it after a status change.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from app.context.replay.canonicalize import canonicalize
from app.context.replay.repro_failure_indexer import (
    rebuild_repro_registry,
    registry_entry_from_repro_file,
)
from app.context.replay.repro_registry_models import ReproRegistryEntry
from app.context.replay.repro_registry_status import is_valid_status


def repro_case_path_for_failure_id(
    repro_root: Union[str, Path],
    failure_id: str,
) -> Path:
    """
    Resolve repro_root + failure_id to the repro case ``.json`` path.

    failure_id uses POSIX segments (as produced by the indexer), no ``.json`` suffix.
    """
    root = Path(repro_root).resolve()
    fid = str(failure_id).strip()
    if not fid:
        raise ValueError("failure_id must be non-empty")
    if "\\" in fid or fid.startswith("/"):
        raise ValueError("failure_id must be a relative POSIX path")
    parts = fid.split("/")
    if any(p == ".." or p == "" for p in parts):
        raise ValueError("failure_id segments must be non-empty and not '..'")
    candidate = (root / Path(*parts)).with_suffix(".json").resolve()
    try:
        candidate.relative_to(root)
    except ValueError as e:
        raise ValueError("failure_id resolves outside repro_root") from e
    return candidate


def update_status_by_failure_id(
    repro_root: Union[str, Path],
    failure_id: str,
    status: str,
    *,
    registry_path: Union[str, Path] | None = None,
) -> ReproRegistryEntry:
    """
    Set ``registry.status`` on the repro case JSON for failure_id.

    Writes canonical JSON (sorted keys, recursive). Optionally rebuilds the
    derived registry file at registry_path.
    """
    if not is_valid_status(status):
        raise ValueError(f"invalid status: {status!r}")

    path = repro_case_path_for_failure_id(repro_root, failure_id)
    if not path.is_file():
        raise FileNotFoundError(f"repro case not found: {path}")

    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"repro case root must be object: {path}")

    reg = data.get("registry")
    if reg is None:
        reg = {}
    elif not isinstance(reg, dict):
        raise ValueError(f"registry must be object if present: {path}")
    else:
        reg = dict(reg)
    reg["status"] = status
    data["registry"] = reg

    data = canonicalize(data)
    out = json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2)
    path.write_text(out, encoding="utf-8")

    if registry_path is not None:
        rebuild_repro_registry(repro_root, registry_path)

    return registry_entry_from_repro_file(repro_root, path)
