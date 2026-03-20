"""
Repro case builder – build ReproCase from replay input + expected result + metadata.

No DB access. No randomness. No datetime.
All inputs explicit; no hidden defaults.
"""

from typing import Any, Dict, FrozenSet

from app.context.replay.failure_types import (
    COMBINED_DRIFT,
    SIGNATURE_MISMATCH,
    VERSION_MISMATCH,
)
from app.context.replay.replay_diff import DriftType, classify_drift, diff_replay_output
from app.context.replay.replay_service import compute_replay_signature
from app.context.replay.repro_case_models import FailureMetadata, ReproCase


def _drift_type_to_failure_constant(d: DriftType) -> str:
    """Map DriftType to failure_types constant."""
    from app.context.replay.failure_types import (
        CONTEXT_DRIFT,
        EXPLAINABILITY_DRIFT,
        TRACE_DRIFT,
    )
    return {
        DriftType.CONTEXT_DRIFT: CONTEXT_DRIFT,
        DriftType.TRACE_DRIFT: TRACE_DRIFT,
        DriftType.EXPLAINABILITY_DRIFT: EXPLAINABILITY_DRIFT,
    }[d]


def build_repro_case(
    replay_input: Dict[str, Any],
    expected_result: Dict[str, Any],
    *,
    failure_type: str,
    drift_types: FrozenSet[DriftType] = frozenset(),
    expected_signature: str = "",
    actual_signature: str = "",
    version_mismatch: bool = False,
) -> ReproCase:
    """
    Build ReproCase from replay input, expected result, and failure metadata.

    All parameters explicit. No hidden defaults.
    """
    exp_sig = expected_signature or expected_result.get("signature", "")
    act_sig = actual_signature
    if not exp_sig:
        exp_sig = compute_replay_signature(expected_result)

    drift_constants = tuple(
        sorted(_drift_type_to_failure_constant(d) for d in drift_types)
    )
    if version_mismatch:
        ft = VERSION_MISMATCH
    elif len(drift_constants) > 1:
        ft = COMBINED_DRIFT
    elif len(drift_constants) == 1:
        ft = drift_constants[0]
    elif exp_sig != act_sig:
        ft = SIGNATURE_MISMATCH
    else:
        ft = failure_type

    metadata = FailureMetadata(
        failure_type=ft,
        drift_types=drift_constants,
        expected_signature=exp_sig,
        actual_signature=act_sig,
    )
    return ReproCase(
        replay_input=replay_input,
        expected_result=expected_result,
        metadata=metadata,
    )


def build_repro_case_from_failure(
    replay_input: Dict[str, Any],
    expected_result: Dict[str, Any],
    actual_result: Dict[str, Any],
    *,
    version_mismatch: bool = False,
) -> ReproCase:
    """
    Build ReproCase from actual vs expected. Computes diff and classifies drift.
    No hidden defaults.
    """
    expected_content = {k: v for k, v in expected_result.items() if k != "signature"}
    actual_content = {k: v for k, v in actual_result.items() if k != "signature"}
    content_diff = diff_replay_output(actual_content, expected_content)
    drift_types = classify_drift(content_diff)
    exp_sig = expected_result.get("signature", "") or compute_replay_signature(expected_result)
    act_sig = actual_result.get("signature", "") or compute_replay_signature(actual_result)

    return build_repro_case(
        replay_input=replay_input,
        expected_result=expected_result,
        failure_type=COMBINED_DRIFT if drift_types else SIGNATURE_MISMATCH,
        drift_types=drift_types,
        expected_signature=exp_sig,
        actual_signature=act_sig,
        version_mismatch=version_mismatch,
    )
