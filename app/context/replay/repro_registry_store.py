"""
Repro registry persistence – single deterministic JSON failure index.

No DB. No randomness. No datetime.
"""

import json
from pathlib import Path
from typing import Dict, Mapping, Union

from app.context.replay.canonicalize import canonicalize
from app.context.replay.repro_registry_models import ReproRegistryEntry

_SCHEMA_VERSION = "3"
_ROOT_KEY = "entries"
_SCHEMA_KEY = "schema_version"


def load_repro_registry(path: Union[str, Path]) -> Dict[str, ReproRegistryEntry]:
    """
    Load registry from JSON. Missing or empty file yields {}.
    Entries are keyed by failure_id (must match entry.failure_id).
    """
    path = Path(path)
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("registry root must be a JSON object")
    entries_raw = data.get(_ROOT_KEY, {})
    if not isinstance(entries_raw, dict):
        raise ValueError(f"{_ROOT_KEY!r} must be a JSON object")
    out: Dict[str, ReproRegistryEntry] = {}
    for key in sorted(entries_raw.keys()):
        row = entries_raw[key]
        if not isinstance(row, dict):
            raise ValueError(f"entry {key!r} must be a JSON object")
        entry = ReproRegistryEntry.from_dict(row)
        if entry.failure_id != key:
            raise ValueError(
                f"entry key {key!r} must equal failure_id {entry.failure_id!r}"
            )
        out[key] = entry
    return out


def save_repro_registry(
    entries: Mapping[str, ReproRegistryEntry],
    path: Union[str, Path],
) -> None:
    """
    Persist registry as canonical sorted JSON (failure index ordered by failure_id).
    """
    path = Path(path)
    payload = {
        _SCHEMA_KEY: _SCHEMA_VERSION,
        _ROOT_KEY: {fid: ent.to_dict() for fid, ent in sorted(entries.items())},
    }
    payload = canonicalize(payload)
    json_str = json.dumps(payload, sort_keys=True, ensure_ascii=False, indent=2)
    path.write_text(json_str, encoding="utf-8")
