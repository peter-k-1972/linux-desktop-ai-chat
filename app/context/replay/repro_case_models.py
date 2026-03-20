"""
Repro case models – deterministic failure capture for replay.

No DB access. No randomness. No datetime in equality-relevant metadata.
"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class FailureMetadata:
    """
    Metadata for a QA failure. No datetime. No randomness.
    All fields explicit; no hidden defaults.
    """

    failure_type: str
    drift_types: tuple[str, ...] = ()
    expected_signature: str = ""
    actual_signature: str = ""


@dataclass
class ReproCase:
    """
    Deterministic repro case: replay_input + expected_result + metadata.
    Persisted as sorted JSON for reproducibility.
    """

    replay_input: Dict[str, Any]
    expected_result: Dict[str, Any]
    metadata: FailureMetadata

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for JSON persistence. Deterministic key order."""
        return {
            "replay_input": self.replay_input,
            "expected_result": self.expected_result,
            "metadata": {
                "failure_type": self.metadata.failure_type,
                "drift_types": list(self.metadata.drift_types),
                "expected_signature": self.metadata.expected_signature,
                "actual_signature": self.metadata.actual_signature,
            },
        }
