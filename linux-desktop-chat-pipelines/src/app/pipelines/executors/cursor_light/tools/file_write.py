"""cl.file.write"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

from app.pipelines.executors.cursor_light.result import err, tool_result
from app.pipelines.executors.cursor_light.workspace import (
    PathOutsideWorkspaceError,
    ensure_parent_under_workspace,
    normalize_relative_path,
)

logger = logging.getLogger(__name__)

TOOL_ID = "cl.file.write"


def run(workspace_root: str, inp: Dict[str, Any]) -> Dict[str, Any]:
    path = inp.get("path")
    content = inp.get("content")
    if not path or not isinstance(path, str):
        return tool_result(
            False,
            error=err("INVALID_INPUT", "input.path (string) required"),
            metadata={"tool_id": TOOL_ID},
        )
    if not isinstance(content, str):
        return tool_result(
            False,
            error=err("INVALID_INPUT", "input.content (string) required"),
            metadata={"tool_id": TOOL_ID},
        )
    create_dirs = bool(inp.get("create_dirs", False))
    cwd = str(Path(workspace_root).resolve())
    try:
        norm = normalize_relative_path(path)
    except PathOutsideWorkspaceError as e:
        return tool_result(
            False,
            error=err("PATH_OUTSIDE_WORKSPACE", str(e)),
            metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": path},
        )

    try:
        _root, target = ensure_parent_under_workspace(workspace_root, path)
    except PathOutsideWorkspaceError as e:
        logger.warning("%s: path denied: %s", TOOL_ID, e)
        return tool_result(
            False,
            error=err("PATH_OUTSIDE_WORKSPACE", str(e)),
            metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm},
        )
    except FileNotFoundError as e:
        return tool_result(
            False,
            error=err("WORKSPACE_NOT_FOUND", str(e)),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )

    parent = target.parent
    if not parent.exists():
        if create_dirs:
            try:
                parent.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                return tool_result(
                    False,
                    error=err("WRITE_ERROR", str(e)),
                    metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm},
                )
        else:
            return tool_result(
                False,
                error=err("PARENT_MISSING", "parent directory does not exist; set create_dirs true"),
                metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm},
            )

    try:
        target.write_text(content, encoding="utf-8", newline="\n")
    except OSError as e:
        logger.exception("%s: write failed", TOOL_ID)
        return tool_result(
            False,
            error=err("WRITE_ERROR", str(e)),
            metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm},
        )

    nbytes = len(content.encode("utf-8"))
    logger.info("%s: wrote path=%s bytes=%s", TOOL_ID, norm, nbytes)
    return tool_result(
        True,
        data={"path": path, "bytes_written": nbytes},
        metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm},
    )
