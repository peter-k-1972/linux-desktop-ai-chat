"""cl.file.read"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

from app.pipelines.executors.cursor_light.result import err, tool_result
from app.pipelines.executors.cursor_light.workspace import (
    PathOutsideWorkspaceError,
    is_probably_binary,
    normalize_relative_path,
    resolve_under_workspace,
)

logger = logging.getLogger(__name__)

TOOL_ID = "cl.file.read"


def _truncate_utf8_bytes(text: str, max_bytes: int) -> tuple[str, bool]:
    if max_bytes <= 0:
        return "", True
    raw = text.encode("utf-8")
    if len(raw) <= max_bytes:
        return text, False
    cut = raw[:max_bytes]
    while cut:
        try:
            return cut.decode("utf-8"), True
        except UnicodeDecodeError:
            cut = cut[:-1]
    return "", True


def run(workspace_root: str, inp: Dict[str, Any]) -> Dict[str, Any]:
    path = inp.get("path")
    if not path or not isinstance(path, str):
        return tool_result(
            False,
            error=err("INVALID_INPUT", "input.path (non-empty string) required"),
            metadata={"tool_id": TOOL_ID},
        )
    encoding = str(inp.get("encoding") or "utf-8")
    line_start = inp.get("line_start")
    line_end = inp.get("line_end")
    cwd = str(Path(workspace_root).resolve())
    try:
        norm_path = normalize_relative_path(path)
    except PathOutsideWorkspaceError as e:
        return tool_result(
            False,
            error=err("PATH_OUTSIDE_WORKSPACE", str(e)),
            metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": path},
        )

    try:
        target = resolve_under_workspace(workspace_root, path)
    except PathOutsideWorkspaceError as e:
        logger.warning("%s: path denied: %s", TOOL_ID, e)
        return tool_result(
            False,
            error=err("PATH_OUTSIDE_WORKSPACE", str(e)),
            metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm_path},
        )
    except FileNotFoundError as e:
        return tool_result(
            False,
            error=err("WORKSPACE_NOT_FOUND", str(e)),
            metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm_path},
        )

    if not target.is_file():
        return tool_result(
            False,
            error=err("NOT_FOUND", f"not a file: {path}"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm_path},
        )

    try:
        raw_head = target.read_bytes()[:8192]
    except OSError as e:
        logger.exception("%s: read failed", TOOL_ID)
        return tool_result(
            False,
            error=err("READ_ERROR", str(e)),
            metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm_path},
        )

    if is_probably_binary(raw_head):
        return tool_result(
            False,
            error=err("BINARY_FILE", "refusing to decode binary file"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm_path},
        )

    try:
        full = target.read_text(encoding=encoding, errors="strict")
    except UnicodeDecodeError:
        return tool_result(
            False,
            error=err("BINARY_FILE", "file is not valid text for encoding"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm_path},
        )
    except OSError as e:
        logger.exception("%s: read_text failed", TOOL_ID)
        return tool_result(
            False,
            error=err("READ_ERROR", str(e)),
            metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm_path},
        )

    lines = full.splitlines(keepends=True)
    total_lines = len(lines)
    truncated = False
    if line_start is not None or line_end is not None:
        try:
            lo = int(line_start) if line_start is not None else 1
            hi = int(line_end) if line_end is not None else total_lines
        except (TypeError, ValueError):
            return tool_result(
                False,
                error=err("INVALID_INPUT", "line_start/line_end must be integers"),
                metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm_path},
            )
        if lo < 1:
            lo = 1
        if hi < lo:
            hi = lo
        slice_lines = lines[lo - 1 : hi]
        content = "".join(slice_lines)
        if hi < total_lines or lo > 1:
            truncated = True
    else:
        content = full
        max_lines = inp.get("max_lines")
        if max_lines is not None:
            try:
                ml = int(max_lines)
            except (TypeError, ValueError):
                return tool_result(
                    False,
                    error=err("INVALID_INPUT", "max_lines must be int"),
                    metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm_path},
                )
            if ml < 1:
                ml = 1
            slice_lines = lines[:ml]
            content = "".join(slice_lines)
            if total_lines > ml:
                truncated = True

    max_bytes = inp.get("max_bytes")
    if max_bytes is not None:
        try:
            mb = int(max_bytes)
        except (TypeError, ValueError):
            return tool_result(
                False,
                error=err("INVALID_INPUT", "max_bytes must be int"),
                metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm_path},
            )
        content, t2 = _truncate_utf8_bytes(content, mb)
        truncated = truncated or t2
    else:
        max_chars = inp.get("max_chars")
        if max_chars is not None:
            try:
                mc = int(max_chars)
            except (TypeError, ValueError):
                return tool_result(
                    False,
                    error=err("INVALID_INPUT", "max_chars must be int"),
                    metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm_path},
                )
            if len(content) > mc:
                content = content[:mc]
                truncated = True
        elif line_start is None and line_end is None and inp.get("max_lines") is None:
            default_mc = 500_000
            if len(content) > default_mc:
                content = content[:default_mc]
                truncated = True

    logger.info("%s: read path=%s lines=%s truncated=%s", TOOL_ID, norm_path, total_lines, truncated)
    return tool_result(
        True,
        data={
            "content": content,
            "total_lines": total_lines,
            "truncated": truncated,
        },
        metadata={
            "tool_id": TOOL_ID,
            "cwd": cwd,
            "target_path": norm_path,
            "truncated": truncated,
        },
    )
