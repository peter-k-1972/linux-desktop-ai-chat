"""
Determinism guards for replay path.

Contract – replay path must NOT use:
- dict iteration without sorted()
- sets (use sorted list instead)
- random
- datetime.now()

Use _sorted_dict_items() for dict iteration.
"""

from typing import Any, Dict, Iterator, List


def _sorted_dict_items(d: Dict[str, Any]) -> Iterator[tuple]:
    """Iterate dict in sorted key order. Use for deterministic execution."""
    for k in sorted(d.keys()):
        yield k, d[k]


def sorted_dict_keys(d: Dict[str, Any]) -> List[str]:
    """Return sorted keys. Use for deterministic iteration."""
    return sorted(d.keys())
