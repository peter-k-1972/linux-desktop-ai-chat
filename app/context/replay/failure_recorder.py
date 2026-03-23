"""
Failure recorder – persist repro case as sorted JSON.

No DB access. No randomness. No datetime.
Deterministic: sort_keys=True, canonicalize before dump.
"""

import json
from pathlib import Path
from typing import Any, Dict, Union

from app.context.replay.canonicalize import canonicalize
from app.context.replay.repro_case_models import FailureMetadata, ReproCase


def load_repro_case(path: Union[str, Path]) -> ReproCase:
    """Load ReproCase from JSON file. Deterministic."""
    path = Path(path)
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    meta = data.get("metadata", {})
    metadata = FailureMetadata(
        failure_type=str(meta.get("failure_type", "")),
        drift_types=tuple(meta.get("drift_types", [])),
        expected_signature=str(meta.get("expected_signature", "")),
        actual_signature=str(meta.get("actual_signature", "")),
    )
    return ReproCase(
        replay_input=data["replay_input"],
        expected_result=data["expected_result"],
        metadata=metadata,
    )


def persist_repro_case(
    repro_case: ReproCase,
    path: Union[str, Path],
    *,
    registry_overlay: Dict[str, Any] | None = None,
) -> None:
    """
    Persist ReproCase as sorted JSON. Deterministic output.
    No DB access. No randomness.

    Optional registry_overlay is merged into top-level ``registry`` for tooling/index rebuilds.
    """
    path = Path(path)
    data = repro_case.to_dict()
    if registry_overlay:
        reg = data.get("registry")
        base: Dict[str, Any] = dict(reg) if isinstance(reg, dict) else {}
        merged = {**base, **registry_overlay}
        data["registry"] = merged
    data = canonicalize(data)
    json_str = json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2)
    path.write_text(json_str, encoding="utf-8")
