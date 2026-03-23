"""
Repro failure helper – record repro case when replay/live comparison fails.

Deterministic failure_id. No random. No live timestamps in equality-relevant metadata.
Output reproducible.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Union

from app.context.replay.canonicalize import canonicalize
from app.context.replay.failure_recorder import persist_repro_case
from app.context.replay.replay_diff import assert_replay_qa_pass
from app.context.replay.replay_models import ReplayInput
from app.context.replay.replay_service import compute_replay_signature
from app.context.replay.repro_case_builder import build_repro_case_from_failure
from app.context.replay.repro_failure_indexer import registry_entry_from_repro_file
from app.context.replay.repro_registry_classification import REPLAY_FAILURE
from app.context.replay.repro_registry_registrar import register_entry
from app.context.replay.repro_registry_source import QA_AUTO
from app.context.replay.repro_registry_status import ACTIVE


def _replay_input_to_dict(replay_input: Union[Dict[str, Any], ReplayInput]) -> Dict[str, Any]:
    """Convert ReplayInput or dict to canonical dict."""
    if hasattr(replay_input, "to_dict"):
        return replay_input.to_dict()
    return canonicalize(replay_input)


def compute_failure_id(
    replay_input: Dict[str, Any],
    expected_result: Dict[str, Any],
    actual_result: Dict[str, Any],
) -> str:
    """
    Deterministic failure_id from content. No random. Reproducible.
    Same failure => same id.
    """
    exp_sig = expected_result.get("signature", "") or compute_replay_signature(expected_result)
    act_sig = actual_result.get("signature", "") or compute_replay_signature(actual_result)
    payload = {
        "replay_input": canonicalize(replay_input),
        "expected_signature": exp_sig,
        "actual_signature": act_sig,
    }
    canonical = json.dumps(canonicalize(payload), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def record_repro_case_on_failure(
    replay_input: Union[Dict[str, Any], ReplayInput],
    expected_result: Dict[str, Any],
    actual_result: Dict[str, Any],
    output_dir: Path,
    *,
    msg: str = "",
) -> None:
    """
    Assert expected_result == actual_result. On failure:
    - compute signature
    - create deterministic failure_id
    - build repro case
    - persist repro case to output_dir/{failure_id}.json
    - re-raise AssertionError

    No random. No live timestamps in metadata. Output reproducible.
    """
    try:
        assert_replay_qa_pass(actual_result, expected_result, msg=msg)
    except AssertionError:
        replay_input_dict = _replay_input_to_dict(replay_input)
        repro_case = build_repro_case_from_failure(
            replay_input=replay_input_dict,
            expected_result=expected_result,
            actual_result=actual_result,
        )
        failure_id = compute_failure_id(
            replay_input_dict,
            expected_result,
            actual_result,
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        repro_path = output_dir / f"{failure_id}.json"
        rel_file = f"{failure_id}.json"
        persist_repro_case(
            repro_case,
            repro_path,
            registry_overlay={
                "classification": REPLAY_FAILURE,
                "file_path": rel_file,
                "source": QA_AUTO,
                "status": ACTIVE,
            },
        )
        entry = registry_entry_from_repro_file(output_dir.resolve(), repro_path.resolve())
        register_entry(output_dir / "registry.json", entry)
        raise
