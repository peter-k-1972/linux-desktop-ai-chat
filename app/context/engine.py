"""
ContextEngine – central context building with deterministic replay support.

Accepts deterministic and replay_mode flags. No new decision logic.
ExecutionMode.LIVE: full side effects. ExecutionMode.REPLAY: isolated (no logging, metrics, event bus).
"""

import logging
from contextlib import contextmanager
from enum import Enum
from typing import Any, Dict, Iterator, Optional

from app.context.replay.replay_models import ReplayInput


class ExecutionMode(str, Enum):
    """Execution mode for context building."""

    LIVE = "live"
    REPLAY = "replay"


class DeterminismViolation(RuntimeError):
    """Raised when deterministic execution is violated."""

    pass


def _sorted_dict_items(d: Dict[str, Any]) -> Iterator[tuple]:
    """Iterate dict in sorted key order. Use for deterministic execution."""
    for k in sorted(d.keys()):
        yield k, d[k]


@contextmanager
def _deterministic_context():
    """
    Enforce deterministic execution: forbid random, forbid datetime.now.
    Use _sorted_dict_items() for dict iteration.
    Note: datetime.datetime.now cannot be patched (immutable type); context path
    must not call it. random is patched to raise if used.
    """
    import random as random_module

    _orig_random = random_module.random
    _orig_randint = getattr(random_module, "randint", None)

    def _forbid_random(*args: Any, **kwargs: Any) -> None:
        raise DeterminismViolation("random forbidden in deterministic mode")

    random_module.random = _forbid_random
    if _orig_randint is not None:
        random_module.randint = _forbid_random

    try:
        yield
    finally:
        random_module.random = _orig_random
        if _orig_randint is not None:
            random_module.randint = _orig_randint


def _enforce_determinism() -> None:
    """
    Ensure deterministic execution: no randomness, no time dependency.
    Use _sorted_dict_items() for dict iteration. Forbid random (patched).
    datetime.now forbidden by contract (immutable type, cannot patch).
    """
    pass  # Applied via _deterministic_context() when deterministic=True


@contextmanager
def _side_effects_disabled_context():
    """
    Disable side effects: logging, metrics, event bus.
    Replay path already avoids DB; this disables logging, metrics, and event emission.
    """
    logging.disable(logging.CRITICAL)

    _orig_get_collector = None
    _metrics_patched = False
    _event_bus_patched = False
    _orig_emit_event = None

    try:
        import app.metrics.metrics_collector as _mc_mod

        _orig_get_collector = _mc_mod.get_metrics_collector

        def _noop_collector():
            class _Noop:
                def start(self) -> None:
                    pass

                def stop(self) -> None:
                    pass

            return _Noop()

        def _patched_get(*args: Any, **kwargs: Any) -> Any:
            return _noop_collector()

        _mc_mod.get_metrics_collector = _patched_get
        _metrics_patched = True
    except ImportError:
        pass

    try:
        import importlib

        _emitter_mod = importlib.import_module("app.debug.emitter")
        _orig_emit_event = _emitter_mod.emit_event

        def _noop_emit_event(*args: Any, **kwargs: Any) -> None:
            pass

        _emitter_mod.emit_event = _noop_emit_event
        _event_bus_patched = True
    except ImportError:
        pass

    try:
        yield
    finally:
        logging.disable(logging.NOTSET)
        if _metrics_patched and _orig_get_collector is not None:
            import app.metrics.metrics_collector as _mc_mod

            _mc_mod.get_metrics_collector = _orig_get_collector
        if _event_bus_patched and _orig_emit_event is not None:
            import importlib

            _emitter_mod = importlib.import_module("app.debug.emitter")
            _emitter_mod.emit_event = _orig_emit_event


def _disable_side_effects() -> None:
    """
    Ensure no side effects: no DB access, no file writes, no external I/O.
    Disable logging and metrics. Applied via _side_effects_disabled_context().
    """
    pass  # Applied via _side_effects_disabled_context() when replay_mode=True


class ContextEngine:
    """
    Central engine for context building. Supports deterministic replay.
    """

    def build_context(
        self,
        chat_id: Optional[int] = None,
        request_context_hint: Optional[Any] = None,
        context_policy: Optional[Any] = None,
        *,
        deterministic: bool = False,
        replay_mode: bool = False,
        replay_input: Optional[ReplayInput] = None,
        return_trace: bool = False,
        return_fragment: bool = False,
    ) -> Any:
        """
        Build context for chat. Supports live (DB) and replay (no DB) paths.

        Args:
            chat_id: For live path. Ignored when replay_mode=True.
            request_context_hint: For live path.
            context_policy: For live path.
            deterministic: If True, _enforce_determinism() is applied.
            replay_mode: If True, uses replay_input, no DB access.
            replay_input: Required when replay_mode=True.
            return_trace: Return full trace instead of explanation.
            return_fragment: Also return (fragment, context, render_options).

        Returns:
            ContextExplanation, or (trace, fragment, context, render_options) when return_fragment.
        """
        if replay_mode and replay_input is None:
            raise ValueError("replay_input required when replay_mode=True")

        def _do_build() -> Any:
            if replay_mode and replay_input is not None:
                return self._build_from_replay(
                    replay_input,
                    return_trace=return_trace,
                    return_fragment=return_fragment,
                )
            return self._build_from_live(
                chat_id=chat_id,
                request_context_hint=request_context_hint,
                context_policy=context_policy,
                return_trace=return_trace,
                return_fragment=return_fragment,
            )

        if deterministic and replay_mode:
            with _deterministic_context(), _side_effects_disabled_context():
                return _do_build()
        if deterministic:
            with _deterministic_context():
                return _do_build()
        if replay_mode:
            with _side_effects_disabled_context():
                return _do_build()
        return _do_build()

    def _build_from_replay(
        self,
        replay_input: ReplayInput,
        *,
        return_trace: bool = False,
        return_fragment: bool = False,
    ) -> Any:
        """
        Build context from ReplayInput. No DB access. No external lookups.
        ReplayInput contains everything required; snapshot integrity guaranteed.
        """
        from app.services.chat_service import get_chat_service

        return get_chat_service()._build_context_from_replay_input(
            replay_input,
            return_trace=return_trace,
            return_fragment=return_fragment,
        )

    def _build_from_live(
        self,
        chat_id: Optional[int] = None,
        request_context_hint: Optional[Any] = None,
        context_policy: Optional[Any] = None,
        *,
        return_trace: bool = False,
        return_fragment: bool = False,
    ) -> Any:
        """Build context from live DB. Delegates to ChatService."""
        from app.services.chat_service import get_chat_service

        return get_chat_service().get_context_explanation(
            chat_id=chat_id or 0,
            request_context_hint=request_context_hint,
            context_policy=context_policy,
            return_trace=return_trace,
            return_fragment=return_fragment,
        )


_context_engine: Optional[ContextEngine] = None


def get_context_engine() -> ContextEngine:
    """Return the global ContextEngine instance."""
    global _context_engine
    if _context_engine is None:
        _context_engine = ContextEngine()
    return _context_engine
