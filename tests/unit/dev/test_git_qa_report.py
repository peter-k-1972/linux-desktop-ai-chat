"""Tests für QA-Report-Helfer (ohne echte Git-Aufrufe)."""

from __future__ import annotations

from app.qa.git_context import GitContext
from app.qa.git_provenance import QaRunProvenance
from app.qa.git_qa_report import (
    build_qa_report_json_dict,
    build_qa_report_text,
    iter_changed_paths_unique,
    segments_from_changed_files,
)


def test_iter_changed_paths_unique_dedupes_and_sorts():
    ctx = GitContext(
        repository_present=True,
        branch_name="main",
        head_commit="a" * 40,
        short_commit="a" * 12,
        is_dirty=True,
        detached_head=False,
        staged_files=("app/gui/a.py",),
        unstaged_files=("app/services/b.py", "app/gui/a.py"),
        untracked_files=("docs/x.md",),
    )
    assert iter_changed_paths_unique(ctx) == [
        "app/gui/a.py",
        "app/services/b.py",
        "docs/x.md",
    ]


def test_segments_from_changed_files_app_only():
    assert segments_from_changed_files(
        [
            "app/gui/x.py",
            "app/services/y.py",
            "README.md",
            "linux-desktop-chat-features/src/app/features/release_matrix.py",
        ]
    ) == ["features", "gui", "services"]


def test_segments_from_changed_files_maps_embedded_features_tree():
    assert segments_from_changed_files(
        ["linux-desktop-chat-features/src/app/features/builtins.py"]
    ) == ["features"]


def test_segments_from_changed_files_maps_embedded_ui_contracts_tree():
    assert segments_from_changed_files(
        ["linux-desktop-chat-ui-contracts/src/app/ui_contracts/common/errors.py"]
    ) == ["ui_contracts"]


def test_segments_from_changed_files_maps_embedded_pipelines_tree():
    assert segments_from_changed_files(
        ["linux-desktop-chat-pipelines/src/app/pipelines/engine/engine.py"]
    ) == ["pipelines"]


def test_segments_from_changed_files_maps_embedded_providers_tree():
    assert segments_from_changed_files(
        ["linux-desktop-chat-providers/src/app/providers/local_ollama_provider.py"]
    ) == ["providers"]


def test_segments_from_changed_files_maps_embedded_providers_utils_as_utils_segment():
    assert segments_from_changed_files(
        ["linux-desktop-chat-providers/src/app/utils/env_loader.py"]
    ) == ["utils"]


def test_segments_from_changed_files_maps_embedded_cli_tree():
    assert segments_from_changed_files(
        ["linux-desktop-chat-cli/src/app/cli/context_replay.py"]
    ) == ["cli"]


def test_segments_from_changed_files_both_embedded_distributions():
    assert segments_from_changed_files(
        [
            "linux-desktop-chat-features/src/app/features/release_matrix.py",
            "linux-desktop-chat-ui-contracts/src/app/ui_contracts/workspaces/chat.py",
        ]
    ) == ["features", "ui_contracts"]


def test_build_qa_report_text_shape():
    ctx = GitContext(
        repository_present=True,
        branch_name="topic/x",
        head_commit="b" * 40,
        short_commit="bbbbbbbbbbbb",
        is_dirty=True,
        detached_head=False,
        staged_files=("app/gui/chat_window.py",),
        unstaged_files=("app/services/chat_service.py",),
        untracked_files=("linux-desktop-chat-features/src/app/features/release_matrix.py",),
    )
    prov = QaRunProvenance(
        captured_at_utc_iso="2026-03-25T12:00:00Z",
        repository_present=True,
        branch_name="topic/x",
        head_commit_sha="b" * 40,
        short_commit_sha="bbbbbbbbbbbb",
        is_dirty=True,
        detached_head=False,
        staged_paths=ctx.staged_files,
        unstaged_paths=ctx.unstaged_files,
        untracked_paths=ctx.untracked_files,
        changed_files_summary="1, 1, 1",
        git_error_reason=None,
    )
    text = build_qa_report_text(ctx, prov=prov)
    assert "Linux Desktop Chat QA Report" in text
    assert "Branch: topic/x" in text
    assert "Commit: bbbbbbbbbbbb" in text
    assert "Dirty: true" in text
    assert "- features" in text
    assert "- gui" in text
    assert "- services" in text
    assert "app/gui/chat_window.py" in text


def test_build_qa_report_json_dict_matches_spec_keys():
    ctx = GitContext(
        repository_present=True,
        branch_name="main",
        head_commit="c" * 40,
        short_commit="cccccccccccc",
        is_dirty=False,
        detached_head=False,
        staged_files=(),
        unstaged_files=(),
        untracked_files=(),
    )
    prov = QaRunProvenance(
        captured_at_utc_iso="2026-03-25T12:00:00Z",
        repository_present=True,
        branch_name="main",
        head_commit_sha="c" * 40,
        short_commit_sha="cccccccccccc",
        is_dirty=False,
        detached_head=False,
        staged_paths=(),
        unstaged_paths=(),
        untracked_paths=(),
        changed_files_summary="0 staged, 0 unstaged, 0 untracked",
        git_error_reason=None,
    )
    d = build_qa_report_json_dict(ctx, prov=prov)
    assert d["branch"] == "main"
    assert d["commit"] == "c" * 40
    assert d["dirty"] is False
    assert d["changed_segments"] == []
    assert d["changed_files"] == []
