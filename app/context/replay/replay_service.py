"""
ContextReplayService – deterministic replay of context decisions.

Calls ContextEngine with deterministic=True and replay_mode=True.
No DB access. No randomness. No time dependency.
"""

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

from app.context.engine import get_context_engine
from app.context.replay.canonicalize import canonicalize
from app.context.replay.replay_models import CURRENT_VERSION, ReplayInput, ReplayVersionMismatchError


def compute_replay_signature(data: Dict[str, Any]) -> str:
    """Compute sha256 of canonical JSON. Excludes 'signature' key for reproducibility."""
    d = {k: v for k, v in data.items() if k != "signature"}
    canonical = json.dumps(canonicalize(d), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass
class ReplayResult:
    """Result of a replay run."""

    fragment: Optional[str]
    trace: Any
    explanation: Any
    context: Optional[Any] = None

    @property
    def signature(self) -> str:
        """Sha256 of serialized result. Attached to output."""
        d = self.to_dict()
        return d.get("signature", "")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for diff comparison."""
        from app.context.explainability.context_explanation import ContextExplanation
        from app.context.explainability.context_explanation_serializer import (
            explanation_to_dict,
            trace_to_dict,
        )

        expl = self.explanation or ContextExplanation()
        context_dict: Dict[str, Any] = {}
        if self.context is not None:
            context_dict = {
                "project_id": getattr(self.context, "project_id", None),
                "project_name": getattr(self.context, "project_name", None),
                "chat_id": getattr(self.context, "chat_id", None),
                "chat_title": getattr(self.context, "chat_title", None),
                "topic_id": getattr(self.context, "topic_id", None),
                "topic_name": getattr(self.context, "topic_name", None),
                "is_global_chat": getattr(self.context, "is_global_chat", False),
            }
        out: Dict[str, Any] = {
            "fragment": self.fragment,
            "context": context_dict,
            "trace": trace_to_dict(
                self.trace,
                include_explanation=False,
                include_budget=True,
                include_dropped=True,
            ) if self.trace else {},
            "explanation": explanation_to_dict(
                expl,
                include_budget=True,
                include_dropped=True,
            ),
        }
        out = canonicalize(out)
        out["signature"] = compute_replay_signature(out)
        return out


class ContextReplayService:
    """
    Service for deterministic context replay.

    Must call ContextEngine with deterministic=True and replay_mode=True.
    """

    def replay(
        self,
        replay_input: ReplayInput,
        *,
        return_trace: bool = True,
        return_fragment: bool = True,
        allow_version_mismatch: bool = False,
    ) -> ReplayResult:
        """
        Replay context building from ReplayInput.

        No DB access. Deterministic. Identical input produces identical output.
        Version safety: replay_input.system_version must match CURRENT_VERSION unless allow_version_mismatch.
        """
        if not allow_version_mismatch:
            if replay_input.system_version != CURRENT_VERSION:
                raise ReplayVersionMismatchError(
                    f"Replay version mismatch: input has {replay_input.system_version!r}, "
                    f"current is {CURRENT_VERSION!r}. Use allow_version_mismatch=True to bypass."
                )
        engine = get_context_engine()
        result = engine.build_context(
            deterministic=True,
            replay_mode=True,
            replay_input=replay_input,
            return_trace=return_trace,
            return_fragment=return_fragment,
        )
        if return_fragment and isinstance(result, tuple):
            trace_or_expl, fragment, context, _ = result
            explanation = getattr(trace_or_expl, "explanation", None) or trace_or_expl
            trace = trace_or_expl if hasattr(trace_or_expl, "explanation") else None
            return ReplayResult(
                fragment=fragment,
                trace=trace,
                explanation=explanation,
                context=context,
            )
        trace = result if hasattr(result, "explanation") else None
        explanation = getattr(result, "explanation", None) or result
        return ReplayResult(
            fragment=None,
            trace=trace,
            explanation=explanation,
            context=None,
        )


_context_replay_service: Optional[ContextReplayService] = None


def get_context_replay_service() -> ContextReplayService:
    """Return the global ContextReplayService instance."""
    global _context_replay_service
    if _context_replay_service is None:
        _context_replay_service = ContextReplayService()
    return _context_replay_service
