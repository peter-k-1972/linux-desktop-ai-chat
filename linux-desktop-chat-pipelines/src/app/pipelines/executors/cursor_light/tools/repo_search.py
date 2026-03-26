"""cl.repo.search — Text-/Regex-Suche nur unter workspace_root."""

from __future__ import annotations

import logging
import os
import re
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Dict, List

from app.pipelines.executors.cursor_light.result import err, tool_result
from app.pipelines.executors.cursor_light.workspace import is_probably_binary

logger = logging.getLogger(__name__)

TOOL_ID = "cl.repo.search"

_SKIP_DIR_NAMES = frozenset(
    {
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "node_modules",
        ".venv",
        "venv",
        "dist",
        "build",
        ".idea",
        ".cursor",
    }
)


def _glob_match(rel_posix: str, patterns: List[str]) -> bool:
    if not patterns:
        return True
    base = Path(rel_posix).name
    for g in patterns:
        if fnmatch(rel_posix, g) or fnmatch(base, g):
            return True
    return False


def _glob_excluded(rel_posix: str, patterns: List[str]) -> bool:
    if not patterns:
        return False
    base = Path(rel_posix).name
    for g in patterns:
        if fnmatch(rel_posix, g) or fnmatch(base, g):
            return True
    return False


def run(workspace_root: str, inp: Dict[str, Any]) -> Dict[str, Any]:
    try:
        cwd_meta = str(Path(workspace_root).resolve())
    except Exception:
        cwd_meta = workspace_root or ""

    pattern = inp.get("pattern")
    if not pattern or not isinstance(pattern, str):
        return tool_result(
            False,
            error=err("INVALID_INPUT", "input.pattern (non-empty string) required"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd_meta},
        )
    literal = bool(inp.get("literal", False))
    try:
        rx = re.compile(re.escape(pattern) if literal else pattern, re.MULTILINE)
    except re.error as e:
        return tool_result(
            False,
            error=err("INVALID_PATTERN", str(e)),
            metadata={"tool_id": TOOL_ID, "cwd": cwd_meta},
        )

    include = [str(x) for x in (inp.get("include_glob") or []) if x]
    exclude = [str(x) for x in (inp.get("exclude_glob") or []) if x]
    max_matches = int(inp.get("max_matches") or 200)

    root = Path(workspace_root).resolve()
    cwd = str(root)
    if not root.is_dir():
        return tool_result(
            False,
            error=err("WORKSPACE_NOT_FOUND", f"not a directory: {workspace_root}"),
            metadata={"tool_id": TOOL_ID, "cwd": cwd},
        )

    matches: List[Dict[str, Any]] = []
    truncated = False

    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIR_NAMES]
        for name in filenames:
            full = Path(dirpath) / name
            try:
                rel_file = full.relative_to(root).as_posix()
            except ValueError:
                continue
            if include and not _glob_match(rel_file, include):
                continue
            if _glob_excluded(rel_file, exclude):
                continue
            try:
                sample = full.read_bytes()[:4096]
            except OSError:
                continue
            if is_probably_binary(sample):
                continue
            try:
                text = full.read_text(encoding="utf-8", errors="strict")
            except (OSError, UnicodeDecodeError):
                continue
            for i, line in enumerate(text.splitlines(), start=1):
                if rx.search(line):
                    matches.append(
                        {
                            "path": rel_file,
                            "line": i,
                            "column": None,
                            "snippet": line[:500],
                        }
                    )
                    if len(matches) >= max_matches:
                        truncated = True
                        break
            if truncated:
                break
        if truncated:
            break

    logger.info("%s: matches=%s truncated=%s", TOOL_ID, len(matches), truncated)
    return tool_result(
        True,
        data={"matches": matches, "truncated": truncated},
        metadata={"tool_id": TOOL_ID, "cwd": cwd, "truncated": truncated},
    )
