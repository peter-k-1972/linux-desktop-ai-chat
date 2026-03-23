"""
Repro registry entry lifecycle status (stable string tokens).

No DB. No UUID. No timestamps.
"""

ACTIVE = "active"
FIXED = "fixed"
EXPECTED_DRIFT = "expected_drift"
INVALIDATED = "invalidated"

STATUSES: tuple[str, ...] = (ACTIVE, FIXED, EXPECTED_DRIFT, INVALIDATED)


def is_valid_status(value: str) -> bool:
    return value in STATUSES
