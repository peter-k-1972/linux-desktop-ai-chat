"""
QA-/Release-Provenance aus :class:`GitContext`.

Klein, ohne Persistenz — für Reports, CLI und spätere CI-Anreicherung.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.qa.git_context import GitContext


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True, slots=True)
class QaRunProvenance:
    """Provenance eines QA-/Governance-Laufs (an Git gekoppelt, sofern verfügbar)."""

    captured_at_utc_iso: str
    repository_present: bool
    branch_name: str | None
    head_commit_sha: str | None
    short_commit_sha: str | None
    is_dirty: bool
    detached_head: bool
    staged_paths: tuple[str, ...]
    unstaged_paths: tuple[str, ...]
    untracked_paths: tuple[str, ...]
    changed_files_summary: str
    git_error_reason: str | None


def build_qa_run_provenance(
    ctx: GitContext,
    *,
    captured_at_utc_iso: str | None = None,
) -> QaRunProvenance:
    ts = captured_at_utc_iso or _utc_now_iso()
    parts = [
        f"{len(ctx.staged_files)} staged",
        f"{len(ctx.unstaged_files)} unstaged",
        f"{len(ctx.untracked_files)} untracked",
    ]
    summary = ", ".join(parts)
    return QaRunProvenance(
        captured_at_utc_iso=ts,
        repository_present=ctx.repository_present,
        branch_name=ctx.branch_name,
        head_commit_sha=ctx.head_commit,
        short_commit_sha=ctx.short_commit,
        is_dirty=ctx.is_dirty,
        detached_head=ctx.detached_head,
        staged_paths=ctx.staged_files,
        unstaged_paths=ctx.unstaged_files,
        untracked_paths=ctx.untracked_files,
        changed_files_summary=summary,
        git_error_reason=ctx.error_reason,
    )


def provenance_to_report_lines(prov: QaRunProvenance) -> list[str]:
    """Markdown-taugliche Zeilen für QA-/Release-Berichte (Soft-Gate: immer sichtbar)."""
    lines = [
        "| Feld | Wert |",
        "|------|------|",
        f"| **Erfasst (UTC)** | `{prov.captured_at_utc_iso}` |",
        f"| **Git-Repository** | {'ja' if prov.repository_present else 'nein'} |",
    ]
    if prov.git_error_reason:
        lines.append(f"| **Git-Hinweis** | `{prov.git_error_reason}` |")
    lines.extend(
        [
            f"| **Branch** | `{prov.branch_name or '—'}` |",
            f"| **HEAD (kurz)** | `{prov.short_commit_sha or '—'}` |",
            f"| **HEAD (voll)** | `{prov.head_commit_sha or '—'}` |",
            f"| **Detached HEAD** | {'ja' if prov.detached_head else 'nein'} |",
            f"| **Dirty Working Tree** | {'ja' if prov.is_dirty else 'nein'} |",
            f"| **Änderungen (Übersicht)** | {prov.changed_files_summary} |",
        ]
    )
    return lines
