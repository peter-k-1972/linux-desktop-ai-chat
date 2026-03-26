"""cl.git.diff — nur lesend (working / staged), optional Pfadfilter."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict

from app.pipelines.executors.cursor_light.result import err, tool_result
from app.pipelines.executors.cursor_light.workspace import (
    PathOutsideWorkspaceError,
    normalize_relative_path,
)

logger = logging.getLogger(__name__)

TOOL_ID = "cl.git.diff"


def run(workspace_root: str, inp: Dict[str, Any]) -> Dict[str, Any]:
    workspace = Path(workspace_root).resolve()
    cwd = str(workspace)
    if not workspace.is_dir():
        return tool_result(
            False,
            error=err("WORKSPACE_NOT_FOUND", f"not a directory: {workspace_root}"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )
    if not (workspace / ".git").exists():
        return tool_result(
            False,
            error=err("NOT_A_GIT_REPO", "no .git directory in workspace"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )

    scope = str(inp.get("scope") or "working").strip().lower()
    if scope not in ("working", "staged"):
        return tool_result(
            False,
            error=err("INVALID_INPUT", "scope must be 'working' or 'staged'"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )

    path_filter = inp.get("path")
    max_chars = int(inp.get("max_chars") or 500_000)

    cmd = ["git", "-C", str(workspace), "diff"]
    if scope == "staged":
        cmd.append("--cached")
    cmd.append("--no-color")

    if path_filter is not None and path_filter != "":
        if not isinstance(path_filter, str):
            return tool_result(
                False,
                error=err("INVALID_INPUT", "path must be string"),
                metadata={"tool_id": TOOL_ID, "cwd": cwd},
            )
        try:
            normalize_relative_path(path_filter)
        except PathOutsideWorkspaceError as e:
            return tool_result(
                False,
                error=err("PATH_OUTSIDE_WORKSPACE", str(e)),
                metadata={"tool_id": TOOL_ID, "cwd": cwd},
            )
        cmd.append("--")
        cmd.append(path_filter)

    logger.info("%s: scope=%s", TOOL_ID, scope)
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
            errors="replace",
        )
    except OSError as e:
        return tool_result(
            False,
            error=err("GIT_ERROR", str(e)),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )

    if proc.returncode != 0:
        return tool_result(
            False,
            error=err("GIT_ERROR", (proc.stderr or "")[:2000]),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )

    diff = proc.stdout or ""
    truncated = len(diff) > max_chars
    if truncated:
        diff = diff[:max_chars]

    return tool_result(
        True,
        data={"diff": diff, "truncated": truncated},
        metadata={"tool_id": TOOL_ID, "cwd": cwd, "truncated": truncated},
    )
