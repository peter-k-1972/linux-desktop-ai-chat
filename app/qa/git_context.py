"""
Zentraler Git-Kontext für QA- und Release-Governance (fail-soft).

Alle Git-Aufrufe laufen hier; keine verstreuten subprocess-Aufrufe für denselben Zweck.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

_DEFAULT_TIMEOUT_S: Final[float] = 8.0


@dataclass(frozen=True, slots=True)
class GitContext:
    """Momentaufnahme des Git-Zustands am erfassten Arbeitsverzeichnis."""

    repository_present: bool
    branch_name: str | None
    head_commit: str | None
    short_commit: str | None
    is_dirty: bool
    detached_head: bool
    staged_files: tuple[str, ...] = ()
    unstaged_files: tuple[str, ...] = ()
    untracked_files: tuple[str, ...] = ()
    error_reason: str | None = None

    @property
    def has_resolved_commit(self) -> bool:
        return bool(self.head_commit)


GitRunner = Callable[[Sequence[str], Path], tuple[int, str, str]]


def _default_git_runner(argv: Sequence[str], cwd: Path) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            ["git", *argv],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=_DEFAULT_TIMEOUT_S,
            check=False,
        )
    except FileNotFoundError:
        return 127, "", "git executable not found"
    except subprocess.TimeoutExpired:
        return 124, "", "git command timed out"
    except OSError as exc:
        return 1, "", f"os error: {exc}"
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    return proc.returncode, out, err


def _parse_porcelain(porcelain: str) -> tuple[set[str], set[str], list[str]]:
    staged: set[str] = set()
    unstaged: set[str] = set()
    untracked: list[str] = []
    for raw in porcelain.splitlines():
        line = raw.rstrip("\n")
        if len(line) < 3:
            continue
        status = line[:2]
        rest = line[3:].strip()
        if status == "??":
            untracked.append(rest)
            continue
        path = rest
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        ix, wt = status[0], status[1]
        if ix not in (" ", "?", "."):
            staged.add(path)
        if wt not in (" ", "?", "."):
            unstaged.add(path)
    return staged, unstaged, untracked


def capture_git_context(
    cwd: Path | None = None,
    *,
    runner: GitRunner | None = None,
) -> GitContext:
    """
    Ermittelt GitContext für ``cwd`` (Standard: aktuelles Arbeitsverzeichnis).

    Bei fehlendem Git, Nicht-Repo oder Fehlern: fail-soft mit ``repository_present=False``
    bzw. gesetztem ``error_reason`` — keine Exceptions für normale Governance-Pfade.
    """
    base = cwd.resolve() if cwd is not None else Path.cwd().resolve()
    run = runner or _default_git_runner

    rc, out, err = run(["rev-parse", "--is-inside-work-tree"], base)
    if rc != 0 or out.strip().lower() != "true":
        reason = err or out or "not a git repository"
        return GitContext(
            repository_present=False,
            branch_name=None,
            head_commit=None,
            short_commit=None,
            is_dirty=False,
            detached_head=False,
            error_reason=reason.strip() or "not a git repository",
        )

    rc_head, head_out, head_err = run(["rev-parse", "HEAD"], base)
    head_commit = head_out.strip() if rc_head == 0 and head_out.strip() else None

    rc_ref, ref_out, _ = run(["symbolic-ref", "-q", "HEAD"], base)
    detached_head = rc_ref != 0

    rc_br, br_out, _ = run(["rev-parse", "--abbrev-ref", "HEAD"], base)
    branch_name = br_out.strip() if rc_br == 0 and br_out.strip() else None
    if branch_name == "HEAD":
        branch_name = None

    rc_por, por_out, por_err = run(["status", "--porcelain=v1"], base)
    error_reason: str | None = None
    if rc_por != 0:
        error_reason = (por_err or "git status failed").strip()
        staged_s, unstaged_s, untracked_l = set(), set(), []
        is_dirty = True
    else:
        staged_s, unstaged_s, untracked_l = _parse_porcelain(por_out)
        is_dirty = bool(staged_s or unstaged_s or untracked_l)

    short_commit = head_commit[:12] if head_commit else None

    return GitContext(
        repository_present=True,
        branch_name=branch_name,
        head_commit=head_commit,
        short_commit=short_commit,
        is_dirty=is_dirty,
        detached_head=detached_head,
        staged_files=tuple(sorted(staged_s)),
        unstaged_files=tuple(sorted(unstaged_s)),
        untracked_files=tuple(untracked_l),
        error_reason=error_reason,
    )
