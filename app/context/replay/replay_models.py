"""
Replay models – frozen input for deterministic context replay.

No DB access. No randomness. No time dependency.
Version safety: system_version must match CURRENT_VERSION unless allow_version_mismatch.
"""

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

from app.context.replay.canonicalize import canonicalize

CURRENT_VERSION = "1.0"


class ReplayVersionMismatchError(ValueError):
    """Raised when replay_input.system_version does not match CURRENT_VERSION."""

    pass


@dataclass(frozen=True)
class ReplayInput:
    """
    Frozen input for context replay. All data required to reproduce output without DB.

    Contains resolved context data and configuration. No external lookups.
    """

    chat_id: int
    project_id: Optional[int]
    project_name: Optional[str]
    chat_title: str
    topic_id: Optional[int]
    topic_name: Optional[str]
    is_global_chat: bool
    mode: str
    detail: str
    include_project: bool
    include_chat: bool
    include_topic: bool
    max_project_chars: Optional[int]
    max_chat_chars: Optional[int]
    max_topic_chars: Optional[int]
    max_total_lines: Optional[int]
    limits_source: str
    source: str
    profile: Optional[str]
    policy: Optional[str]
    hint: Optional[str]
    chat_policy: Optional[str]
    project_policy: Optional[str]
    profile_enabled: bool
    fields: tuple[str, ...] = ()
    base_explanation: Optional[Any] = None  # From live trace; used for full explanation parity
    system_version: Optional[str] = None  # Must match CURRENT_VERSION for replay

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict with canonicalized keys. Deterministic."""
        d = asdict(self)
        d.pop("base_explanation", None)  # Not JSON-serializable
        return canonicalize(d)
