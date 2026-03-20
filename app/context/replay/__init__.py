# app.context.replay – Context Decision Replay System.
#
# Determinism guards: no dict iteration without sorted(), no sets, no random, no datetime.now().
# Snapshot integrity: ReplayInput contains everything; no external access in replay.
# QA: signature (sha256), assert_replay_qa_pass, classify_drift (CONTEXT_DRIFT, TRACE_DRIFT, EXPLAINABILITY_DRIFT).
# Failure pipeline: ReproCase, build_repro_case_from_failure, persist_repro_case, run_repro_case_from_file.

from app.context.replay.canonicalize import canonicalize
from app.context.replay.replay_diff import DriftType, assert_replay_qa_pass, classify_drift
from app.context.replay.replay_models import CURRENT_VERSION, ReplayInput, ReplayVersionMismatchError
from app.context.replay.replay_service import compute_replay_signature

__all__ = [
    "ReplayInput",
    "CURRENT_VERSION",
    "ReplayVersionMismatchError",
    "canonicalize",
    "compute_replay_signature",
    "DriftType",
    "assert_replay_qa_pass",
    "classify_drift",
]
