"""
QA-Berichtsdaten aus Git-Kontext und geänderten Pfaden (Segment-Analyse).

Genutzt von ``scripts/dev/print_git_qa_report.py`` und Tests.
"""

from __future__ import annotations

from collections.abc import Sequence

from app.qa.git_context import GitContext
from app.qa.git_provenance import QaRunProvenance, build_qa_run_provenance


def normalize_repo_path(path: str) -> str:
    """Git-Pfade als repo-relative POSIX-Pfade."""
    return path.replace("\\", "/").strip()


def iter_changed_paths_unique(ctx: GitContext) -> list[str]:
    """Alle geänderten/neuen Pfade (staged, unstaged, untracked), sortiert, ohne Duplikate."""
    seen: set[str] = set()
    ordered: list[str] = []
    for p in (*ctx.staged_files, *ctx.unstaged_files, *ctx.untracked_files):
        n = normalize_repo_path(p)
        if not n or n in seen:
            continue
        seen.add(n)
        ordered.append(n)
    return sorted(ordered)


def segments_from_changed_files(paths: Sequence[str]) -> list[str]:
    """
    Top-Segmente unter ``app/<segment>/`` für geänderte Dateien.

    Monorepo: Änderungen unter ``linux-desktop-chat-features/src/app/features/`` werden wie
    Segment **features** gewertet (gleiches Label wie früher ``app/features/``). Änderungen unter
    ``linux-desktop-chat-ui-contracts/src/app/ui_contracts/`` → Segment **ui_contracts** (wie früher
    ``app/ui_contracts/``). Änderungen unter
    ``linux-desktop-chat-pipelines/src/app/pipelines/`` → Segment **pipelines** (wie früher
    ``app/pipelines/``). Änderungen unter
    ``linux-desktop-chat-providers/src/app/providers/`` → Segment **providers** (wie früher
    ``app/providers/``). Änderungen unter
    ``linux-desktop-chat-providers/src/app/utils/`` → Segment **utils** (mitgezogene Utility
    für ``cloud_ollama_provider``; Host behält kanonischen ``app/utils/``-Baum). Änderungen unter
    ``linux-desktop-chat-cli/src/app/cli/`` → Segment **cli** (wie früher ``app/cli/``).

    Pfade außerhalb dieser Muster liefern keinen Segment-Eintrag (außer den obigen Heuristiken).
    """
    found: set[str] = set()
    for raw in paths:
        parts = normalize_repo_path(raw).split("/")
        if len(parts) >= 2 and parts[0] == "app" and parts[1]:
            found.add(parts[1])
            continue
        if (
            len(parts) >= 5
            and parts[0] == "linux-desktop-chat-features"
            and parts[1] == "src"
            and parts[2] == "app"
            and parts[3] == "features"
        ):
            found.add("features")
            continue
        if (
            len(parts) >= 5
            and parts[0] == "linux-desktop-chat-ui-contracts"
            and parts[1] == "src"
            and parts[2] == "app"
            and parts[3] == "ui_contracts"
        ):
            found.add("ui_contracts")
            continue
        if (
            len(parts) >= 5
            and parts[0] == "linux-desktop-chat-pipelines"
            and parts[1] == "src"
            and parts[2] == "app"
            and parts[3] == "pipelines"
        ):
            found.add("pipelines")
            continue
        if (
            len(parts) >= 5
            and parts[0] == "linux-desktop-chat-providers"
            and parts[1] == "src"
            and parts[2] == "app"
            and parts[3] == "providers"
        ):
            found.add("providers")
            continue
        if (
            len(parts) >= 5
            and parts[0] == "linux-desktop-chat-providers"
            and parts[1] == "src"
            and parts[2] == "app"
            and parts[3] == "utils"
        ):
            found.add("utils")
            continue
        if (
            len(parts) >= 5
            and parts[0] == "linux-desktop-chat-cli"
            and parts[1] == "src"
            and parts[2] == "app"
            and parts[3] == "cli"
        ):
            found.add("cli")
    return sorted(found)


def build_qa_report_text(
    ctx: GitContext,
    *,
    prov: QaRunProvenance | None = None,
    changed_files: Sequence[str] | None = None,
    changed_segments: Sequence[str] | None = None,
) -> str:
    """Strukturierter Textbericht (stdout-freundlich)."""
    prov = prov or build_qa_run_provenance(ctx)
    files = list(changed_files) if changed_files is not None else iter_changed_paths_unique(ctx)
    segs = list(changed_segments) if changed_segments is not None else segments_from_changed_files(files)

    branch = prov.branch_name or "—"
    commit = prov.short_commit_sha or prov.head_commit_sha or "—"
    dirty = "true" if prov.is_dirty else "false"

    lines = [
        "Linux Desktop Chat QA Report",
        "--------------------------------",
        "",
        f"Branch: {branch}",
        f"Commit: {commit}",
        f"Dirty: {dirty}",
        "",
        "Changed segments:",
        "",
    ]
    if segs:
        for s in segs:
            lines.append(f"- {s}")
    else:
        lines.append("- (none under app/<segment>/)")
    lines.extend(["", "Changed files:", ""])
    if files:
        lines.extend(files)
    else:
        lines.append("(none)")
    lines.append("")
    return "\n".join(lines)


def build_qa_report_json_dict(
    ctx: GitContext,
    *,
    prov: QaRunProvenance | None = None,
    changed_files: Sequence[str] | None = None,
    changed_segments: Sequence[str] | None = None,
) -> dict:
    """Payload für ``--json`` (flach + Provenance-Kernfelder)."""
    prov = prov or build_qa_run_provenance(ctx)
    files = list(changed_files) if changed_files is not None else iter_changed_paths_unique(ctx)
    segs = list(changed_segments) if changed_segments is not None else segments_from_changed_files(files)

    return {
        "branch": prov.branch_name,
        "commit": prov.head_commit_sha,
        "short_commit": prov.short_commit_sha,
        "dirty": prov.is_dirty,
        "repository_present": prov.repository_present,
        "detached_head": prov.detached_head,
        "captured_at_utc_iso": prov.captured_at_utc_iso,
        "changed_segments": segs,
        "changed_files": files,
    }
