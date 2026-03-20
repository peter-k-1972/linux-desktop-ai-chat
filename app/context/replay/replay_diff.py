"""
Replay diff – DeepDiff comparison for replay output.

ignore_order=False to preserve list order (resolver order matters).
Diff classifier: CONTEXT_DRIFT, TRACE_DRIFT, EXPLAINABILITY_DRIFT.
FAIL: any diff != {}, signature mismatch.
"""

from enum import Enum
from typing import Any, Dict, FrozenSet, List, Set

from deepdiff import DeepDiff


class DriftType(str, Enum):
    """Classified drift types for replay QA."""

    CONTEXT_DRIFT = "context_drift"
    TRACE_DRIFT = "trace_drift"
    EXPLAINABILITY_DRIFT = "explainability_drift"


def _paths_from_diff(diff: DeepDiff) -> Set[str]:
    """Extract all paths from DeepDiff result."""
    paths: Set[str] = set()
    for key in (
        "values_changed",
        "dictionary_item_added",
        "dictionary_item_removed",
        "iterable_item_added",
        "iterable_item_removed",
        "type_changes",
    ):
        val = diff.get(key) if hasattr(diff, "get") else getattr(diff, key, None)
        if val is None:
            continue
        if isinstance(val, dict):
            paths.update(str(k) for k in val.keys())
        elif isinstance(val, (list, set)):
            for item in val:
                if isinstance(item, str):
                    paths.add(item)
                elif hasattr(item, "path"):
                    paths.add(str(item.path()))
                else:
                    paths.add(str(item))
    return paths


def classify_drift(diff: DeepDiff) -> FrozenSet[DriftType]:
    """
    Classify drift types from DeepDiff result.

    CONTEXT_DRIFT: fragment or context
    TRACE_DRIFT: trace
    EXPLAINABILITY_DRIFT: explanation
    """
    if not diff:
        return frozenset()
    paths = _paths_from_diff(diff)
    drifts: List[DriftType] = []
    for p in paths:
        path_str = str(p)
        if "['fragment']" in path_str or path_str.startswith("root['fragment']"):
            drifts.append(DriftType.CONTEXT_DRIFT)
        elif "['context']" in path_str or path_str.startswith("root['context']"):
            drifts.append(DriftType.CONTEXT_DRIFT)
        elif "['trace']" in path_str or path_str.startswith("root['trace']"):
            drifts.append(DriftType.TRACE_DRIFT)
        elif "['explanation']" in path_str or path_str.startswith("root['explanation']"):
            drifts.append(DriftType.EXPLAINABILITY_DRIFT)
    return frozenset(drifts)


def diff_replay_output(
    actual: Dict[str, Any],
    expected: Dict[str, Any],
    *,
    ignore_order: bool = False,
) -> DeepDiff:
    """ignore_order=True is not allowed. List order must be preserved."""
    if ignore_order:
        raise ValueError("ignore_order=True not allowed. List order must be preserved.")
    """
    Compare two replay outputs using DeepDiff.

    Args:
        actual: Dict from actual replay run
        expected: Dict from expected/baseline run
        ignore_order: If False (default), list order is significant (resolver order)

    Returns:
        DeepDiff result. Empty when identical.
    """
    return DeepDiff(expected, actual, ignore_order=ignore_order)


def are_identical(actual: Dict[str, Any], expected: Dict[str, Any]) -> bool:
    """
    Return True if actual and expected are identical (no diff).

    Uses ignore_order=False to enforce list order.
    """
    result = diff_replay_output(actual, expected, ignore_order=False)
    return not result


def assert_replay_qa_pass(
    actual: Dict[str, Any],
    expected: Dict[str, Any],
    *,
    msg: str = "",
) -> None:
    """
    FAIL if any diff != {} or signature mismatch.
    Content diff excludes signature key. Signature checked separately.
    Raises AssertionError with drift classification on failure.
    """
    actual_content = {k: v for k, v in actual.items() if k != "signature"}
    expected_content = {k: v for k, v in expected.items() if k != "signature"}
    diff = diff_replay_output(actual_content, expected_content, ignore_order=False)
    if diff:
        drifts = classify_drift(diff)
        raise AssertionError(
            f"{msg} FAIL: diff not empty. Drifts: {sorted(d.name for d in drifts)}. Diff: {diff}"
        )
    sig_a = actual.get("signature", "")
    sig_e = expected.get("signature", "")
    if sig_a != sig_e:
        raise AssertionError(
            f"{msg} FAIL: signature mismatch. actual={sig_a!r} expected={sig_e!r}"
        )
