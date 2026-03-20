"""
Repro case runner – load replay input, run replay, compare, return structured result.

No DB access. No randomness. No datetime.
All inputs explicit; no hidden defaults.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

from app.context.replay.canonicalize import canonicalize
from app.context.replay.replay_diff import (
    DriftType,
    classify_drift,
    diff_replay_output,
)
from app.context.replay.replay_models import ReplayInput
from app.context.replay.replay_service import (
    compute_replay_signature,
    get_context_replay_service,
)


def dict_to_replay_input(data: Dict[str, Any]) -> ReplayInput:
    """Build ReplayInput from dict. Deterministic. No hidden defaults."""
    data = canonicalize(data)
    fields = data.get("fields")
    if isinstance(fields, list):
        fields = tuple(fields)
    elif fields is None:
        fields = ()
    return ReplayInput(
        chat_id=int(data["chat_id"]),
        project_id=data.get("project_id"),
        project_name=data.get("project_name"),
        chat_title=str(data.get("chat_title", "")),
        topic_id=data.get("topic_id"),
        topic_name=data.get("topic_name"),
        is_global_chat=bool(data.get("is_global_chat", False)),
        mode=str(data.get("mode", "semantic")),
        detail=str(data.get("detail", "standard")),
        include_project=bool(data.get("include_project", True)),
        include_chat=bool(data.get("include_chat", True)),
        include_topic=bool(data.get("include_topic", False)),
        max_project_chars=data.get("max_project_chars"),
        max_chat_chars=data.get("max_chat_chars"),
        max_topic_chars=data.get("max_topic_chars"),
        max_total_lines=data.get("max_total_lines"),
        limits_source=str(data.get("limits_source", "default")),
        source=str(data.get("source", "individual_settings")),
        profile=data.get("profile"),
        policy=data.get("policy"),
        hint=data.get("hint"),
        chat_policy=data.get("chat_policy"),
        project_policy=data.get("project_policy"),
        profile_enabled=bool(data.get("profile_enabled", False)),
        fields=fields,
        base_explanation=None,
        system_version=data.get("system_version"),
    )


@dataclass
class ReproRunResult:
    """Structured result of repro case run. No hidden defaults."""

    passed: bool
    actual_result: Dict[str, Any]
    expected_result: Dict[str, Any]
    content_diff: Any = None
    content_identical: bool = True
    signature_match: bool = True
    drift_types: tuple[str, ...] = ()
    expected_signature: str = ""
    actual_signature: str = ""


def load_repro_case_data(path: Union[str, Path]) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Load replay_input and expected_result from repro case JSON.
    No DB access. Deterministic.
    """
    path = Path(path)
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    return data["replay_input"], data["expected_result"]


def run_repro_case(
    replay_input: Dict[str, Any],
    expected_result: Dict[str, Any],
    *,
    allow_version_mismatch: bool = False,
) -> ReproRunResult:
    """
    Load replay input, run replay, compare expected vs actual.
    Returns structured result. No DB access. No randomness.
    """
    inp = dict_to_replay_input(replay_input)
    svc = get_context_replay_service()
    replay_result = svc.replay(
        inp,
        return_trace=True,
        return_fragment=True,
        allow_version_mismatch=allow_version_mismatch,
    )
    actual_result = replay_result.to_dict()

    expected_content = {k: v for k, v in expected_result.items() if k != "signature"}
    actual_content = {k: v for k, v in actual_result.items() if k != "signature"}
    content_diff = diff_replay_output(actual_content, expected_content)
    content_identical = not content_diff

    exp_sig = expected_result.get("signature", "") or compute_replay_signature(expected_result)
    act_sig = actual_result.get("signature", "") or compute_replay_signature(actual_result)
    signature_match = exp_sig == act_sig

    drift_types = tuple(
        sorted(d.name for d in classify_drift(content_diff))
    ) if content_diff else ()

    passed = content_identical and signature_match

    return ReproRunResult(
        passed=passed,
        actual_result=actual_result,
        expected_result=expected_result,
        content_diff=content_diff,
        content_identical=content_identical,
        signature_match=signature_match,
        drift_types=drift_types,
        expected_signature=exp_sig,
        actual_signature=act_sig,
    )


def run_repro_case_from_file(
    path: Union[str, Path],
    *,
    allow_version_mismatch: bool = False,
) -> ReproRunResult:
    """
    Load repro case from file, run, compare. Returns structured result.
    """
    replay_input, expected_result = load_repro_case_data(path)
    return run_repro_case(
        replay_input,
        expected_result,
        allow_version_mismatch=allow_version_mismatch,
    )
