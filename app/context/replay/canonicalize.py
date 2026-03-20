"""
Canonicalization for deterministic replay output.

Enforces sorted keys on all dicts. Converts sets to sorted lists.
Ensures identical serialization regardless of insertion order.
"""

from typing import Any, Dict, List


def canonicalize(obj: Any) -> Any:
    """
    Recursively canonicalize a value for deterministic serialization.

    - dict: sorted keys, values canonicalized
    - list/tuple: order preserved, items canonicalized
    - set/frozenset: converted to sorted list (determinism guard)
    - other: returned as-is
    """
    if obj is None:
        return None
    if isinstance(obj, dict):
        return {k: canonicalize(obj[k]) for k in sorted(obj.keys())}
    if isinstance(obj, (list, tuple)):
        return [canonicalize(item) for item in obj]
    if isinstance(obj, (set, frozenset)):
        return [canonicalize(item) for item in sorted(obj, key=_sort_key)]
    return obj


def _sort_key(x: Any) -> tuple:
    """Sort key for non-ordered types. Handles None, bool, int, float, str."""
    if x is None:
        return (0, "")
    if isinstance(x, bool):
        return (1, str(x))
    if isinstance(x, (int, float)):
        return (2, str(x))
    if isinstance(x, str):
        return (3, x)
    return (4, repr(x))
