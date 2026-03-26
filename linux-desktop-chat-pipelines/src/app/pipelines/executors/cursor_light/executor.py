"""cursor_light: Dispatcher für cl.* Tools (Workspace-sicher, strukturierte Fehler)."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict

from app.pipelines.executors.base import StepExecutor, StepResult
from app.pipelines.executors.cursor_light.result import err, tool_result
from app.pipelines.executors.cursor_light.tools import (
    file_patch,
    file_read,
    file_write,
    git_diff,
    git_status,
    repo_search,
    test_run,
)

logger = logging.getLogger(__name__)

_TOOL_HANDLERS: Dict[str, Callable[[str, Dict[str, Any]], Dict[str, Any]]] = {
    file_read.TOOL_ID: file_read.run,
    file_write.TOOL_ID: file_write.run,
    file_patch.TOOL_ID: file_patch.run,
    repo_search.TOOL_ID: repo_search.run,
    test_run.TOOL_ID: test_run.run,
    git_status.TOOL_ID: git_status.run,
    git_diff.TOOL_ID: git_diff.run,
}

KNOWN_TOOL_IDS = frozenset(_TOOL_HANDLERS.keys())


class CursorLightExecutor(StepExecutor):
    """
    config (executor_config):
      - workspace_root: Pfad zum erlaubten Arbeitsverzeichnis (Pflicht)
      - tool_id: z. B. cl.file.read (Pflicht)
      - input: dict mit tool-spezifischen Parametern (optional, default {})

    Optional: workspace_root auch im workflow context, falls nicht in config.
    """

    def execute(
        self,
        step_id: str,
        config: Dict[str, Any],
        context: Dict[str, Any],
    ) -> StepResult:
        t0 = time.perf_counter()
        root = str(config.get("workspace_root") or context.get("workspace_root") or "").strip()
        tool_id = str(config.get("tool_id") or "").strip()

        if not root:
            body = tool_result(
                False,
                error=err("INVALID_INPUT", "workspace_root required in executor_config or context"),
                metadata={
                    "tool_id": tool_id or None,
                    "duration_ms": (time.perf_counter() - t0) * 1000,
                },
            )
            return StepResult(success=True, logs=["cursor_light: missing workspace_root"], output=body)

        cwd_resolved_early = str(Path(root).resolve())
        if not tool_id:
            body = tool_result(
                False,
                error=err("INVALID_INPUT", "tool_id required in executor_config"),
                metadata={
                    "cwd": cwd_resolved_early,
                    "duration_ms": (time.perf_counter() - t0) * 1000,
                },
            )
            return StepResult(success=True, logs=["cursor_light: missing tool_id"], output=body)

        raw_in = config.get("input")
        if raw_in is None:
            raw_in = config.get("tool_input")
        if raw_in is None:
            inp: Dict[str, Any] = {}
        elif isinstance(raw_in, dict):
            inp = dict(raw_in)
        else:
            body = tool_result(
                False,
                error=err("INVALID_INPUT", "input / tool_input must be an object"),
                metadata={
                    "tool_id": tool_id,
                    "cwd": cwd_resolved_early,
                    "duration_ms": (time.perf_counter() - t0) * 1000,
                },
            )
            return StepResult(success=True, logs=["cursor_light: bad input type"], output=body)

        handler = _TOOL_HANDLERS.get(tool_id)
        if handler is None:
            body = tool_result(
                False,
                error=err(
                    "UNKNOWN_TOOL",
                    f"unknown tool_id: {tool_id!r}",
                    known=sorted(_TOOL_HANDLERS.keys()),
                ),
                metadata={
                    "tool_id": tool_id,
                    "cwd": cwd_resolved_early,
                    "duration_ms": (time.perf_counter() - t0) * 1000,
                },
            )
            return StepResult(success=True, logs=[f"cursor_light: unknown tool {tool_id}"], output=body)

        cwd_resolved = cwd_resolved_early
        logger.info("cursor_light step=%s tool_id=%s workspace=%s", step_id, tool_id, cwd_resolved)
        try:
            body = handler(root, inp)
        except Exception as e:
            logger.exception("cursor_light tool %s failed", tool_id)
            body = tool_result(
                False,
                error=err("INTERNAL_ERROR", str(e)),
                metadata={
                    "tool_id": tool_id,
                    "cwd": cwd_resolved,
                    "duration_ms": (time.perf_counter() - t0) * 1000,
                },
            )
        else:
            md = body.setdefault("metadata", {})
            if not isinstance(md, dict):
                md = {}
                body["metadata"] = md
            md["duration_ms"] = (time.perf_counter() - t0) * 1000
            md.setdefault("tool_id", tool_id)
            md["cwd"] = cwd_resolved

        logs = [f"cursor_light {tool_id} success={body.get('success')}"]
        # Immer success=True auf StepResult-Ebene, damit Workflows nicht crashen
        return StepResult(success=True, logs=logs, output=body)
