"""
Repro failure indexer – rebuild registry entries from repro case JSON on disk.

Iterates repro JSON files in sorted path order. failure_id is the path relative to
the scan root with the ``.json`` suffix removed (POSIX, stable, no UUID).

Optional per-file JSON overrides (top-level)::

    "registry": {
        "status": "fixed",
        "classification": "regression_case",
        "test_name": "tests/context/test_x.py::test_y"
    }

``test_name`` may also come from ``metadata.test_name``, ``replay_input.test_name``,
or top-level ``test_name`` when not set in ``registry``.

No DB. Deterministic. Registry JSON can be regenerated from the repro directory.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Union

from app.context.replay.repro_registry_classification import (
    REPLAY_FAILURE,
    is_valid_classification,
)
from app.context.replay.repro_registry_models import ReproRegistryEntry
from app.context.replay.repro_registry_status import ACTIVE, is_valid_status
from app.context.replay.repro_registry_store import save_repro_registry


def iter_sorted_repro_json_paths(
    repro_root: Union[str, Path],
    *,
    exclude_resolved: frozenset[Path] | None = None,
) -> tuple[Path, ...]:
    """
    All ``*.json`` files under repro_root, sorted by POSIX path string.

    ``exclude_resolved`` removes paths by resolved location (e.g. derived registry
    JSON colocated under repro_root).
    """
    root = Path(repro_root).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"not a directory: {root}")
    skip = exclude_resolved or frozenset()
    paths: list[Path] = []
    for p in root.rglob("*.json"):
        if not p.is_file():
            continue
        if p.resolve() in skip:
            continue
        paths.append(p)
    return tuple(sorted(paths, key=lambda q: q.resolve().relative_to(root).as_posix()))


def failure_id_for_repro_path(repro_root: Union[str, Path], file_path: Union[str, Path]) -> str:
    """
    Stable failure_id: relative path from repro_root, ``.json`` stripped, forward slashes.
    """
    root = Path(repro_root).resolve()
    path = Path(file_path).resolve()
    rel = path.relative_to(root)
    return rel.with_suffix("").as_posix()


def _as_str(v: Any) -> str:
    if v is None:
        return ""
    return str(v)


def _registry_overlay(data: Dict[str, Any]) -> Dict[str, Any]:
    raw = data.get("registry")
    return raw if isinstance(raw, dict) else {}


def _resolve_test_name(data: Dict[str, Any], overlay: Dict[str, Any]) -> str:
    if "test_name" in overlay:
        return _as_str(overlay.get("test_name"))
    md = data.get("metadata")
    if isinstance(md, dict) and "test_name" in md:
        return _as_str(md.get("test_name"))
    ri = data.get("replay_input")
    if isinstance(ri, dict) and "test_name" in ri:
        return _as_str(ri.get("test_name"))
    return _as_str(data.get("test_name"))


def _parse_repro_case_dict(raw: str, *, source: Path) -> Dict[str, Any]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"invalid JSON: {source}: {e}") from e
    if not isinstance(data, dict):
        raise ValueError(f"repro case root must be object: {source}")
    return data


def registry_entry_from_repro_file(
    repro_root: Union[str, Path],
    file_path: Union[str, Path],
) -> ReproRegistryEntry:
    """
    Build one registry row from a repro case JSON file (must have replay_input + metadata).
    """
    path = Path(file_path).resolve()
    data = _parse_repro_case_dict(path.read_text(encoding="utf-8"), source=path)
    if not isinstance(data.get("replay_input"), dict):
        raise ValueError(f"missing replay_input object: {path}")
    if not isinstance(data.get("metadata"), dict):
        raise ValueError(f"missing metadata object: {path}")

    failure_id = failure_id_for_repro_path(repro_root, path)
    overlay = _registry_overlay(data)

    status = overlay.get("status", ACTIVE)
    status_s = _as_str(status)
    if not is_valid_status(status_s):
        raise ValueError(f"invalid registry.status for {path}: {status_s!r}")

    classification = overlay.get("classification", REPLAY_FAILURE)
    class_s = _as_str(classification)
    if not is_valid_classification(class_s):
        raise ValueError(f"invalid registry.classification for {path}: {class_s!r}")

    meta = data["metadata"]
    failure_type = _as_str(meta.get("failure_type", ""))

    replay_input = data["replay_input"]
    ver_raw = replay_input.get("system_version")
    version = _as_str(ver_raw) if ver_raw is not None else ""

    test_name = _resolve_test_name(data, overlay)

    file_path = _as_str(overlay.get("file_path", ""))
    if not file_path:
        file_path = f"{failure_id}.json"
    source = _as_str(overlay.get("source", ""))

    return ReproRegistryEntry(
        failure_id=failure_id,
        status=status_s,
        classification=class_s,
        failure_type=failure_type,
        test_name=test_name,
        version=version,
        file_path=file_path,
        source=source,
    )


def build_registry_from_repro_directory(
    repro_root: Union[str, Path],
    *,
    exclude_resolved: frozenset[Path] | None = None,
) -> Dict[str, ReproRegistryEntry]:
    """
    Scan repro_root and produce a full failure_id -> entry map (sorted scan order).
    """
    out: Dict[str, ReproRegistryEntry] = {}
    for path in iter_sorted_repro_json_paths(repro_root, exclude_resolved=exclude_resolved):
        entry = registry_entry_from_repro_file(repro_root, path)
        if entry.failure_id in out:
            raise ValueError(f"duplicate failure_id {entry.failure_id!r} from {path}")
        out[entry.failure_id] = entry
    return out


def rebuild_repro_registry(
    repro_root: Union[str, Path],
    registry_path: Union[str, Path],
) -> Dict[str, ReproRegistryEntry]:
    """
    Scan repro_root, write deterministic registry JSON to registry_path, return entries.
    """
    reg_resolved = Path(registry_path).resolve()
    entries = build_registry_from_repro_directory(
        repro_root,
        exclude_resolved=frozenset({reg_resolved}),
    )
    save_repro_registry(entries, registry_path)
    return entries
