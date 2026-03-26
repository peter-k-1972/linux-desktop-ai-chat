"""cl.git.status — nur lesend, fester argv."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from app.pipelines.executors.cursor_light.result import err, tool_result
from app.pipelines.executors.cursor_light.workspace import (
    PathOutsideWorkspaceError,
    normalize_relative_path,
)

logger = logging.getLogger(__name__)

TOOL_ID = "cl.git.status"


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

    porcelain = bool(inp.get("porcelain", True))
    path_filter = inp.get("path")
    cmd = ["git", "-C", str(workspace), "status"]
    if porcelain:
        cmd.append("--porcelain=v1")
        cmd.append("-b")
    if path_filter:
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

    logger.info("%s: %s", TOOL_ID, " ".join(cmd[:6]))
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
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
            error=err("GIT_ERROR", (proc.stderr or proc.stdout or "")[:2000]),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )

    out = proc.stdout or ""
    branch: str | None = None
    staged: List[Dict[str, str]] = []
    unstaged: List[Dict[str, str]] = []
    untracked: List[str] = []

    if porcelain:
        lines = out.splitlines()
        if lines and lines[0].startswith("## "):
            branch = lines[0][3:].split("...", 1)[0].strip()
        for line in lines[1:]:
            if len(line) < 4:
                continue
            code = line[:2]
            path = line[3:].strip()
            if code == "??":
                untracked.append(path)
            else:
                entry = {"path": path, "index": code[0], "worktree": code[1]}
                if code[0] != " ":
                    staged.append(entry)
                if code[1] != " ":
                    unstaged.append(entry)
    else:
        branch = None

    logger.info("%s: ok branch=%s", TOOL_ID, branch)
    return tool_result(
        True,
        data={
            "branch": branch,
            "raw": out[:100_000],
            "staged": staged,
            "unstaged": unstaged,
            "untracked": untracked,
            "clean": not staged and not unstaged and not untracked and porcelain,
        },
        metadata={"tool_id": TOOL_ID, "cwd": cwd},
    )
