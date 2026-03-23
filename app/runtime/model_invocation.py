"""
Fachliche Metadaten für Modellaufrufe (transportierbar in Stream-Chunks, ohne GUI).

Erweiterung bestehender Chunk-Dicts um Schlüssel ``model_invocation`` (MILESTONE_KEY).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


MODEL_INVOCATION_CHUNK_KEY = "model_invocation"


class ModelInvocationOutcome(str, Enum):
    """Endzustand eines Aufrufs (fachlich, nicht nur Textfehler)."""

    SUCCESS = "success"
    POLICY_BLOCK = "policy_block"
    PROVIDER_ERROR = "provider_error"
    CONFIG_ERROR = "config_error"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class ModelInvocationChunkPayload:
    """Teilmenge der Felder, die an Aufrufer durchgereicht werden können."""

    outcome: Optional[str] = None
    preflight_decision: Optional[str] = None
    preflight_message: Optional[str] = None
    warning_active: bool = False
    block_reason: Optional[str] = None
    usage_record_id: Optional[int] = None
    latency_ms: Optional[int] = None
    token_counts_exact: Optional[bool] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None

    def as_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.outcome is not None:
            d["outcome"] = self.outcome
        if self.preflight_decision is not None:
            d["preflight_decision"] = self.preflight_decision
        if self.preflight_message:
            d["preflight_message"] = self.preflight_message
        if self.warning_active:
            d["warning_active"] = True
        if self.block_reason:
            d["block_reason"] = self.block_reason
        if self.usage_record_id is not None:
            d["usage_record_id"] = self.usage_record_id
        if self.latency_ms is not None:
            d["latency_ms"] = self.latency_ms
        if self.token_counts_exact is not None:
            d["token_counts_exact"] = self.token_counts_exact
        if self.prompt_tokens is not None:
            d["prompt_tokens"] = self.prompt_tokens
        if self.completion_tokens is not None:
            d["completion_tokens"] = self.completion_tokens
        if self.total_tokens is not None:
            d["total_tokens"] = self.total_tokens
        return d


def attach_model_invocation(chunk: Dict[str, Any], payload: ModelInvocationChunkPayload) -> Dict[str, Any]:
    """Mutiert den Chunk und hängt ``model_invocation`` an (flache Kopie)."""
    out = dict(chunk)
    existing = out.get(MODEL_INVOCATION_CHUNK_KEY)
    merged = dict(existing) if isinstance(existing, dict) else {}
    merged.update(payload.as_dict())
    out[MODEL_INVOCATION_CHUNK_KEY] = merged
    return out
