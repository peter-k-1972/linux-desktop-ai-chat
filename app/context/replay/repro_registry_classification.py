"""
Repro registry classification (stable string tokens).

No DB. No UUID. No timestamps.
"""

REPLAY_FAILURE = "replay_failure"
REGRESSION_CASE = "regression_case"
AUDIT_CASE = "audit_case"

CLASSIFICATIONS: tuple[str, ...] = (REPLAY_FAILURE, REGRESSION_CASE, AUDIT_CASE)


def is_valid_classification(value: str) -> bool:
    return value in CLASSIFICATIONS
