"""cl.test.run — Allowlist-basierte Testkommandos im Workspace."""

from __future__ import annotations

import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Sequence

from app.pipelines.executors.cursor_light.result import err, tool_result

logger = logging.getLogger(__name__)

TOOL_ID = "cl.test.run"

# command_key -> argv prefix (cwd = workspace); Interpreter = aktuelles Python (kein PATH-"python")
def _pytest_argv() -> list[str]:
    return [sys.executable, "-m", "pytest"]


_ALLOWLIST: Dict[str, Any] = {
    "pytest": _pytest_argv,
    "python_pytest": _pytest_argv,
}

_ARG_SAFE = re.compile(r"^[a-zA-Z0-9_./@=-]+$")


def _validate_args(args: Sequence[Any]) -> bool:
    for a in args:
        if not isinstance(a, str):
            return False
        if ".." in a or a.startswith("/"):
            return False
        if not _ARG_SAFE.match(a):
            return False
    return True


def run(workspace_root: str, inp: Dict[str, Any]) -> Dict[str, Any]:
    workspace = Path(workspace_root).resolve()
    cwd = str(workspace)

    key = inp.get("command_key")
    if not key or not isinstance(key, str):
        return tool_result(
            False,
            error=err("INVALID_INPUT", "input.command_key (string) required"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )
    key = key.strip()
    if key not in _ALLOWLIST:
        return tool_result(
            False,
            error=err(
                "POLICY_DENIED",
                f"command_key not allowlisted: {key!r}",
                allowed=list(_ALLOWLIST.keys()),
            ),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )

    raw_args = inp.get("args") or []
    if not isinstance(raw_args, list):
        return tool_result(
            False,
            error=err("INVALID_INPUT", "args must be a list of strings"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )
    if not _validate_args(raw_args):
        return tool_result(
            False,
            error=err("INVALID_INPUT", "args contain forbidden characters or absolute paths"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )

    if not workspace.is_dir():
        return tool_result(
            False,
            error=err("WORKSPACE_NOT_FOUND", f"not a directory: {workspace_root}"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )

    timeout = float(inp.get("timeout_sec") or 300)
    prefix = _ALLOWLIST[key]
    cmd = list(prefix() if callable(prefix) else prefix) + list(raw_args)
    logger.info("%s: running %s in %s", TOOL_ID, cmd, workspace)

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(workspace),
            capture_output=True,
            timeout=timeout,
            check=False,
            text=True,
            errors="replace",
        )
    except subprocess.TimeoutExpired:
        return tool_result(
            False,
            error=err("TIMEOUT", f"command exceeded {timeout}s"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )
    except OSError as e:
        logger.exception("%s: spawn failed", TOOL_ID)
        return tool_result(
            False,
            error=err("EXEC_ERROR", str(e)),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )

    cap = 200_000
    stdout = (proc.stdout or "")[:cap]
    stderr = (proc.stderr or "")[:cap]
    ok = proc.returncode == 0
    logger.info("%s: exit_code=%s", TOOL_ID, proc.returncode)
    return tool_result(
        ok,
        data={"exit_code": proc.returncode, "stdout": stdout, "stderr": stderr},
        error=None if ok else err("TEST_FAILED", f"exit code {proc.returncode}", stderr_preview=stderr[:2000]),
        metadata={
            "tool_id": TOOL_ID,
            "cwd": cwd,
            "command": cmd,
            "exit_code": proc.returncode,
        },
    )
