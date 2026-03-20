"""
Phase 3 – Semantische Anreicherung.

Additive Konfigurationspfade für:
- failure_class hints (phase3_failure_class_hints.json)
- guard_type overrides (phase3_guard_type_overrides.json)
- Reduktion manual_review_required

Nur anwenden wenn Test noch kein catalog_bound hat.
inferred bleibt transparent; catalog_bound bleibt maßgeblich für Coverage.
"""

from __future__ import annotations

import fnmatch
import json
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_QA_DIR = _PROJECT_ROOT / "docs" / "qa"


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _get_file_stem(file_path: str) -> str:
    return Path(file_path).stem


def _apply_failure_class_hints(
    tests: list[dict[str, Any]],
    hints: dict[str, Any],
) -> int:
    """
    Wendet failure_class Hints an. Nur bei Tests ohne catalog_bound.
    confidence=high → inference_sources.failure_class = "catalog_bound" (nur wenn aus REGRESSION_CATALOG)
    confidence=medium → inference_sources.failure_class = "inferred"
    """
    enriched = 0
    file_patterns = hints.get("file_patterns") or []
    test_name_patterns = hints.get("test_name_patterns") or []

    for t in tests:
        fc_source = (t.get("inference_sources") or {}).get("failure_class", "")
        if fc_source == "catalog_bound":
            continue

        file_stem = _get_file_stem(t.get("file_path") or "")
        test_name = t.get("test_name") or ""

        matched_fc = None
        matched_confidence = "medium"

        for fp in file_patterns:
            pattern = fp.get("pattern", "")
            if not pattern:
                continue
            if fnmatch.fnmatch(file_stem, pattern) or fnmatch.fnmatch(file_stem + ".py", pattern):
                matched_fc = fp.get("failure_class")
                matched_confidence = fp.get("confidence", "medium")
                break

        if not matched_fc:
            for tp in test_name_patterns:
                pattern = tp.get("pattern", "")
                if pattern and fnmatch.fnmatch(test_name, pattern):
                    matched_fc = tp.get("failure_class")
                    matched_confidence = "medium"
                    break

        if matched_fc:
            existing = t.get("failure_classes") or []
            if matched_fc not in existing:
                t["failure_classes"] = list(existing) + [matched_fc]
            inference_sources = dict(t.get("inference_sources") or {})
            inference_sources["failure_class"] = "catalog_bound" if matched_confidence == "high" else "inferred"
            t["inference_sources"] = inference_sources
            enriched += 1

    return enriched


def _apply_guard_type_overrides(
    tests: list[dict[str, Any]],
    overrides: dict[str, Any],
) -> int:
    """Wendet guard_type Overrides an. Überschreibt inferierte guard_types."""
    enriched = 0
    override_list = overrides.get("overrides") or []

    for t in tests:
        test_id = t.get("test_id") or ""
        for ov in override_list:
            pattern = ov.get("test_id_pattern", "")
            if not pattern:
                continue
            if fnmatch.fnmatch(test_id, pattern):
                guard_types = ov.get("guard_types") or []
                if guard_types:
                    t["guard_types"] = list(guard_types)
                    enriched += 1
                break

    return enriched


def _recompute_manual_review(t: dict[str, Any]) -> bool:
    """
    Wenn alle inference_sources != "unknown", dann manual_review_required = false.
    Ausnahme: inference_confidence.* == "low" kann manual_review bleiben.
    """
    sources = t.get("inference_sources") or {}
    if any(v == "unknown" for v in sources.values()):
        return True
    confidence = t.get("inference_confidence") or {}
    if any(v == "low" for v in confidence.values()):
        return t.get("manual_review_required", True)
    return False


def apply_semantic_enrichment(
    inventory: dict[str, Any],
    qa_dir: Path | None = None,
) -> dict[str, int]:
    """
    Wendet failure_class Hints und guard_type Overrides an.
    Reduziert manual_review_required wo möglich.
    Returns: {"failure_class_hints": n, "guard_type_overrides": n, "manual_review_reduced": n}
    """
    qa_dir = qa_dir or DEFAULT_QA_DIR
    tests = inventory.get("tests") or []
    stats: dict[str, int] = {
        "failure_class_hints": 0,
        "guard_type_overrides": 0,
        "manual_review_reduced": 0,
    }

    hints = _load_json(qa_dir / "config" / "phase3_failure_class_hints.json")
    if hints:
        stats["failure_class_hints"] = _apply_failure_class_hints(tests, hints)

    overrides = _load_json(qa_dir / "config" / "phase3_guard_type_overrides.json")
    if overrides:
        stats["guard_type_overrides"] = _apply_guard_type_overrides(tests, overrides)

    for t in tests:
        prev = t.get("manual_review_required", True)
        new_val = _recompute_manual_review(t)
        t["manual_review_required"] = new_val
        if prev and not new_val:
            stats["manual_review_reduced"] += 1

    if inventory.get("summary"):
        summary = inventory["summary"]
        mrr_count = sum(1 for t in tests if t.get("manual_review_required"))
        summary["manual_review_required_count"] = mrr_count

    return stats
