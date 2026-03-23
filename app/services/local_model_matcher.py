"""
Konservative Zuordnung von Dateipfaden zu Registry-Modell-IDs.

Nur eindeutige, nachvollziehbare Treffer – sonst None (unassigned).
"""

from __future__ import annotations

from pathlib import Path
from typing import FrozenSet, Optional, Set, Tuple


def load_registry_model_ids() -> FrozenSet[str]:
    from app.core.models.registry import get_registry

    return frozenset(e.id for e in get_registry().list_all() if (e.id or "").strip())


def suggest_model_id_with_confidence(
    path: Path, root: Path, registry_ids: Set[str]
) -> Tuple[Optional[str], str]:
    """
    Gibt (registry_model_id | None, confidence) zurück.

    confidence: ``high`` bei eindeutigem exaktem Treffer, sonst ``none``.
    """
    root_r = root.resolve()
    try:
        path_r = path.resolve()
        rel = path_r.relative_to(root_r)
    except (ValueError, OSError):
        rel = Path(path.name) if path.name else path

    parts = list(rel.parts)
    for seg in parts:
        if seg in registry_ids:
            return seg, "high"
        lower_hits = [r for r in registry_ids if r.lower() == seg.lower()]
        if len(lower_hits) == 1:
            return lower_hits[0], "high"

    stem = path.stem
    if stem in registry_ids:
        return stem, "high"
    lower_stem = [r for r in registry_ids if r.lower() == stem.lower()]
    if len(lower_stem) == 1:
        return lower_stem[0], "high"

    prefixed = [rid for rid in registry_ids if rid.startswith(stem + ":")]
    if len(prefixed) == 1:
        return prefixed[0], "high"

    return None, "none"
