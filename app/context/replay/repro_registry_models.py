"""
Repro registry models – indexed failure/repro metadata for context replay.

Deterministic serialization only. No DB. No UUID. No timestamps.
"""

from dataclasses import dataclass
from typing import Any, Dict

from app.context.replay.repro_registry_classification import is_valid_classification
from app.context.replay.repro_registry_status import is_valid_status


@dataclass(frozen=True)
class ReproRegistryEntry:
    """
    One row in the failure/repro index, keyed by failure_id.

    failure_type / test_name / version are filled by the repro indexer from case JSON;
    they may be empty when entries are hand-authored or legacy.
    """

    failure_id: str
    status: str
    classification: str
    failure_type: str = ""
    test_name: str = ""
    version: str = ""
    file_path: str = ""
    source: str = ""

    def __post_init__(self) -> None:
        if not str(self.failure_id).strip():
            raise ValueError("failure_id must be non-empty")
        if not is_valid_status(self.status):
            raise ValueError(f"invalid status: {self.status!r}")
        if not is_valid_classification(self.classification):
            raise ValueError(f"invalid classification: {self.classification!r}")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for JSON; keys sorted at document level via canonicalize + sort_keys."""
        return {
            "classification": self.classification,
            "failure_id": self.failure_id,
            "failure_type": self.failure_type,
            "file_path": self.file_path,
            "source": self.source,
            "status": self.status,
            "test_name": self.test_name,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReproRegistryEntry":
        return cls(
            failure_id=str(data["failure_id"]),
            status=str(data["status"]),
            classification=str(data["classification"]),
            failure_type=str(data.get("failure_type", "")),
            test_name=str(data.get("test_name", "")),
            version=str(data.get("version", "")),
            file_path=str(data.get("file_path", "")),
            source=str(data.get("source", "")),
        )
