"""Hilfs-Callables für den Dev-Assist-Workflow (python_callable / tool_call)."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict

from app.pipelines.executors import StepResult

logger = logging.getLogger(__name__)

_JSON_FENCE = re.compile(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", re.IGNORECASE)


def dev_assist_normalize_inputs(context: Dict[str, Any]) -> StepResult:
    """Setzt abgeleitete Tool-Felder (path, pytest-Args, command_key)."""
    delta: Dict[str, Any] = {}
    tf = str(context.get("target_file") or "").strip()
    if tf:
        delta["path"] = tf
    if context.get("test_scope") is None:
        delta["test_scope"] = ""
    ta = context.get("test_args")
    scope = str(context.get("test_scope") or "").strip()
    if isinstance(ta, list):
        delta["test_args"] = ta
    elif scope:
        delta["test_args"] = ["-q", scope]
    else:
        delta["test_args"] = ["-q"]
    ck = str(context.get("command_key") or "pytest").strip() or "pytest"
    delta["command_key"] = ck
    wr = str(context.get("workspace_root") or "").strip()
    if not wr:
        logger.warning("dev_assist_normalize_inputs: workspace_root fehlt")
    return StepResult(success=True, output=delta)


def dev_assist_lift_file_read(context: Dict[str, Any]) -> StepResult:
    """Übernimmt Text aus dem letzten cl.file.read tool_result in Klartext-Felder."""
    tr = context.get("tool_result") or {}
    data = tr.get("data") if isinstance(tr, dict) else {}
    content = ""
    if isinstance(data, dict):
        content = str(data.get("content") or "")
    ok = bool(isinstance(tr, dict) and tr.get("success"))
    return StepResult(
        success=True,
        output={
            "source_file_content": content,
            "file_read_success": ok,
        },
    )


def _parse_json_object(text: str) -> Dict[str, Any] | None:
    t = str(text or "").strip()
    m = _JSON_FENCE.search(t)
    if m:
        try:
            obj = json.loads(m.group(1))
            return obj if isinstance(obj, dict) else None
        except json.JSONDecodeError:
            pass
    try:
        obj = json.loads(t)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None


def dev_assist_parse_developer_patch(context: Dict[str, Any]) -> StepResult:
    """
    Liest JSON aus der Developer-Antwort und legt Felder für cl.file.patch im Payload ab.
    """
    raw = str(context.get("response_text") or "")
    obj = _parse_json_object(raw)
    if not obj:
        logger.warning("dev_assist_parse_developer_patch: kein JSON gefunden")
        return StepResult(
            success=True,
            output={"patch_parse_error": "Kein gültiges JSON (erwartet ```json { ... } ```)."},
        )

    mode = str(obj.get("mode") or "replace_block").strip().lower()
    delta: Dict[str, Any] = {"mode": mode}

    if mode in ("replace_block", "replace"):
        delta["mode"] = "replace_block"
        for key in ("path", "old_text", "new_text"):
            if key not in obj:
                return StepResult(
                    success=True,
                    output={
                        "patch_parse_error": f"Pflichtfeld fehlt: {key}",
                    },
                )
            delta[key] = obj[key]
    elif mode in ("unified_diff", "patch"):
        patch = obj.get("patch")
        if not isinstance(patch, str) or not patch.strip():
            return StepResult(
                success=True,
                output={"patch_parse_error": "unified_diff erfordert nicht-leeres Feld patch (string)."},
            )
        delta["mode"] = "unified_diff"
        delta["patch"] = patch
        if "strip" in obj:
            delta["strip"] = obj["strip"]
    else:
        return StepResult(
            success=True,
            output={"patch_parse_error": f"Unbekannter mode: {mode!r}"},
        )

    return StepResult(success=True, output=delta)


def dev_assist_finalize_report(context: Dict[str, Any]) -> StepResult:
    """Baut die öffentliche Ergebnisstruktur für den End-Knoten."""
    report = {
        "analysis": context.get("analysis"),
        "plan": context.get("plan"),
        "patch_applied": bool(context.get("patch_applied")),
        "test_results": context.get("test_results"),
        "review": context.get("review"),
        "documentation": context.get("documentation"),
    }
    return StepResult(success=True, output=report)
