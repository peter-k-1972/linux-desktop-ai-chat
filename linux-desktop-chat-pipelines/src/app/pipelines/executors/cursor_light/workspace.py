"""Workspace-Pfadregeln: nur innerhalb des konfigurierten Roots."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple


class PathOutsideWorkspaceError(ValueError):
    """Relativer Pfad würde außerhalb workspace_root landen."""


def normalize_relative_path(raw: str) -> str:
    """Liefert POSIX-artigen relativen Pfad ohne führende Slashes."""
    s = (raw or "").strip().replace("\\", "/").lstrip("/")
    if not s:
        raise PathOutsideWorkspaceError("empty path")
    parts = []
    for p in s.split("/"):
        if p in ("", "."):
            continue
        if p == "..":
            raise PathOutsideWorkspaceError("path traversal")
        parts.append(p)
    if not parts:
        raise PathOutsideWorkspaceError("empty path")
    return "/".join(parts)


def resolve_under_workspace(workspace_root: str, relative_path: str) -> Path:
    """
    Löst einen relativen Pfad strikt unter workspace_root auf.
    """
    root = Path(workspace_root).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"workspace_root is not a directory: {root}")
    rel = normalize_relative_path(relative_path)
    candidate = (root / rel).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as e:
        raise PathOutsideWorkspaceError("path escapes workspace") from e
    return candidate


def ensure_parent_under_workspace(workspace_root: str, relative_path: str) -> Tuple[Path, Path]:
    """Wie resolve_under_workspace, aber für Zieldateien die ggf. noch nicht existieren."""
    root = Path(workspace_root).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"workspace_root is not a directory: {root}")
    rel = normalize_relative_path(relative_path)
    candidate = (root / rel).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as e:
        raise PathOutsideWorkspaceError("path escapes workspace") from e
    return root, candidate


def is_probably_binary(sample: bytes) -> bool:
    if b"\x00" in sample[:8192]:
        return True
    return False
