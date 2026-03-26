"""cl.file.patch — unified diff (git apply / patch) oder replace_block (ein eindeutiges Vorkommen)."""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from app.pipelines.executors.cursor_light.result import err, tool_result
from app.pipelines.executors.cursor_light.workspace import (
    PathOutsideWorkspaceError,
    normalize_relative_path,
    resolve_under_workspace,
)

logger = logging.getLogger(__name__)

TOOL_ID = "cl.file.patch"


def _git_dir(workspace: Path) -> bool:
    return (workspace / ".git").exists()


def _replace_block(workspace_root: str, inp: Dict[str, Any]) -> Dict[str, Any]:
    path = inp.get("path")
    old_text = inp.get("old_text")
    new_text = inp.get("new_text")
    cwd = str(Path(workspace_root).resolve())
    if not path or not isinstance(path, str):
        return tool_result(
            False,
            error=err("INVALID_INPUT", "replace_block requires path (string)"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )
    if not isinstance(old_text, str):
        return tool_result(
            False,
            error=err("INVALID_INPUT", "replace_block requires old_text (string)"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )
    if not isinstance(new_text, str):
        return tool_result(
            False,
            error=err("INVALID_INPUT", "replace_block requires new_text (string)"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )
    try:
        norm = normalize_relative_path(path)
        target = resolve_under_workspace(workspace_root, path)
    except PathOutsideWorkspaceError as e:
        return tool_result(
            False,
            error=err("PATH_OUTSIDE_WORKSPACE", str(e)),
            metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": path},
        )
    except FileNotFoundError as e:
        return tool_result(
            False,
            error=err("WORKSPACE_NOT_FOUND", str(e)),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )

    if not target.is_file():
        return tool_result(
            False,
            error=err("NOT_FOUND", f"not a file: {path}"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm},
        )

    encoding = str(inp.get("encoding") or "utf-8")
    try:
        content = target.read_text(encoding=encoding, errors="strict")
    except (OSError, UnicodeDecodeError) as e:
        return tool_result(
            False,
            error=err("READ_ERROR", str(e)),
            metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm},
        )

    count = content.count(old_text)
    if count == 0:
        return tool_result(
            False,
            error=err("NO_MATCH", "old_text not found in file"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm},
        )
    if count > 1:
        return tool_result(
            False,
            error=err(
                "AMBIGUOUS_MATCH",
                f"old_text occurs {count} times; must be unique for replace_block",
                occurrence_count=count,
            ),
            metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm},
        )

    new_content = content.replace(old_text, new_text, 1)
    try:
        target.write_text(new_content, encoding=encoding, newline="\n")
    except OSError as e:
        logger.exception("%s replace_block write failed", TOOL_ID)
        return tool_result(
            False,
            error=err("WRITE_ERROR", str(e)),
            metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm},
        )

    logger.info("%s: replace_block path=%s", TOOL_ID, norm)
    return tool_result(
        True,
        data={"files_changed": [norm], "applied": True, "method": "replace_block"},
        metadata={"tool_id": TOOL_ID, "cwd": cwd, "target_path": norm},
    )


def run(workspace_root: str, inp: Dict[str, Any]) -> Dict[str, Any]:
    mode = str(inp.get("mode") or "unified_diff").strip().lower()
    if mode in ("replace_block", "replace"):
        return _replace_block(workspace_root, inp)

    patch = inp.get("patch")
    try:
        cwd_early = str(Path(workspace_root).resolve())
    except Exception:
        cwd_early = workspace_root or ""
    if not patch or not isinstance(patch, str):
        return tool_result(
            False,
            error=err("INVALID_INPUT", "input.patch (non-empty string) required for unified_diff"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd_early},
        )
    strip = inp.get("strip", 1)
    try:
        strip_n = int(strip)
    except (TypeError, ValueError):
        return tool_result(
            False,
            error=err("INVALID_INPUT", "strip must be int"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd_early},
        )

    workspace = Path(workspace_root).resolve()
    cwd = str(workspace)
    if not workspace.is_dir():
        return tool_result(
            False,
            error=err("WORKSPACE_NOT_FOUND", f"not a directory: {workspace_root}"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )

    patch_bytes = patch.encode("utf-8")
    timeout = float(inp.get("timeout_sec") or 120)
    err_txt = ""

    if _git_dir(workspace):
        check = subprocess.run(
            ["git", "apply", f"-p{strip_n}", "--check", "--whitespace=nowarn", "-"],
            cwd=str(workspace),
            input=patch_bytes,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        if check.returncode != 0:
            err_txt = (check.stderr or check.stdout or b"").decode("utf-8", errors="replace")[:4000]
            logger.warning("%s: git apply --check failed: %s", TOOL_ID, err_txt[:200])
            return tool_result(
                False,
                error=err(
                    "PATCH_REJECTED",
                    "patch does not apply cleanly (git apply --check)",
                    stderr_preview=err_txt,
                ),
                metadata={"tool_id": TOOL_ID, "cwd": cwd},
            )

        proc = subprocess.run(
            ["git", "apply", f"-p{strip_n}", "--whitespace=nowarn", "-"],
            cwd=str(workspace),
            input=patch_bytes,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        if proc.returncode == 0:
            logger.info("%s: git apply ok strip=%s", TOOL_ID, strip_n)
            paths = _paths_from_patch(patch)
            return tool_result(
                True,
                data={"files_changed": paths, "applied": True, "method": "git_apply"},
                metadata={"tool_id": TOOL_ID, "cwd": cwd},
            )
        err_txt = (proc.stderr or proc.stdout or b"").decode("utf-8", errors="replace")[:4000]
        logger.warning("%s: git apply failed after check: %s", TOOL_ID, err_txt[:200])
        return tool_result(
            False,
            error=err(
                "PATCH_FAILED",
                "git apply failed unexpectedly after successful --check",
                stderr_preview=err_txt,
            ),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )

    patch_bin = shutil.which("patch")
    if not patch_bin:
        return tool_result(
            False,
            error=err(
                "PATCH_UNAVAILABLE",
                "no .git: need GNU patch for unified_diff, but 'patch' not found on PATH",
                stderr_preview=err_txt if err_txt else None,
            ),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )

    proc2 = subprocess.run(
        [patch_bin, f"-p{strip_n}", "--forward", "-i", "-"],
        cwd=str(workspace),
        input=patch_bytes,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    if proc2.returncode != 0:
        msg = (proc2.stderr or proc2.stdout or b"").decode("utf-8", errors="replace")[:4000]
        logger.warning("%s: patch failed: %s", TOOL_ID, msg[:200])
        return tool_result(
            False,
            error=err("PATCH_FAILED", msg or "patch returned non-zero"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )

    logger.info("%s: patch ok strip=%s", TOOL_ID, strip_n)
    return tool_result(
        True,
        data={"files_changed": _paths_from_patch(patch), "applied": True, "method": "patch"},
        metadata={"tool_id": TOOL_ID, "cwd": cwd},
    )


def _paths_from_patch(patch_text: str) -> List[str]:
    paths: List[str] = []
    for line in patch_text.splitlines():
        if line.startswith("+++ "):
            p = line[4:].strip()
            if p.startswith("b/"):
                p = p[2:]
            if p and p != "/dev/null" and p not in paths:
                paths.append(p)
    return paths
