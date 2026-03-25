"""Tests für Git-Kontext, Provenance und Soft-Gates (gemockte Git-Läufe)."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.qa.git_context import GitContext, capture_git_context
from app.qa.git_governance import (
    STRONG_GOVERNANCE_CLAIMS,
    evaluate_soft_gates,
    strong_governance_claim_allowed,
)
from app.qa.git_provenance import build_qa_run_provenance, provenance_to_report_lines


def _runner_from_map(mapping: dict[tuple[str, ...], tuple[int, str, str]]):
    def runner(argv, cwd: Path) -> tuple[int, str, str]:
        key = tuple(argv)
        if key not in mapping:
            return 1, "", f"unexpected argv: {key}"
        return mapping[key]

    return runner


def test_capture_git_context_fail_soft_not_a_repo():
    mapping = {
        ("rev-parse", "--is-inside-work-tree"): (1, "", "fatal: not a git repository"),
    }
    ctx = capture_git_context(Path("/tmp"), runner=_runner_from_map(mapping))
    assert ctx.repository_present is False
    assert ctx.head_commit is None
    assert ctx.is_dirty is False


def test_capture_git_context_clean_repo_strong_gate_eligible():
    mapping = {
        ("rev-parse", "--is-inside-work-tree"): (0, "true", ""),
        ("rev-parse", "HEAD"): (0, "deadbeefcafebabe", ""),
        ("symbolic-ref", "-q", "HEAD"): (0, "refs/heads/main", ""),
        ("rev-parse", "--abbrev-ref", "HEAD"): (0, "main", ""),
        ("status", "--porcelain=v1"): (0, "", ""),
    }
    ctx = capture_git_context(Path("/repo"), runner=_runner_from_map(mapping))
    assert ctx.repository_present is True
    assert ctx.is_dirty is False
    assert ctx.head_commit == "deadbeefcafebabe"
    assert ctx.short_commit == "deadbeefcafe"
    assert ctx.branch_name == "main"
    assert ctx.detached_head is False
    gate = evaluate_soft_gates(ctx)
    assert gate.strong_claims_allowed is True
    assert gate.max_formal_tier.value == "sign_off_eligible"


def test_capture_git_context_dirty_blocks_strong_claims():
    mapping = {
        ("rev-parse", "--is-inside-work-tree"): (0, "true", ""),
        ("rev-parse", "HEAD"): (0, "abc123", ""),
        ("symbolic-ref", "-q", "HEAD"): (0, "refs/heads/dev", ""),
        ("rev-parse", "--abbrev-ref", "HEAD"): (0, "dev", ""),
        ("status", "--porcelain=v1"): (0, " M README.md\n?? x.txt", ""),
    }
    ctx = capture_git_context(Path("/repo"), runner=_runner_from_map(mapping))
    assert ctx.is_dirty is True
    assert "README.md" in ctx.unstaged_files
    assert "x.txt" in ctx.untracked_files
    gate = evaluate_soft_gates(ctx)
    assert gate.strong_claims_allowed is False
    assert gate.max_formal_tier.value == "informative"
    assert any("Dirty" in w for w in gate.warnings)


def test_detached_head_warns_but_allows_strong_when_clean():
    mapping = {
        ("rev-parse", "--is-inside-work-tree"): (0, "true", ""),
        ("rev-parse", "HEAD"): (0, "feedface", ""),
        ("symbolic-ref", "-q", "HEAD"): (1, "", ""),
        ("rev-parse", "--abbrev-ref", "HEAD"): (0, "HEAD", ""),
        ("status", "--porcelain=v1"): (0, "", ""),
    }
    ctx = capture_git_context(Path("/repo"), runner=_runner_from_map(mapping))
    assert ctx.detached_head is True
    assert ctx.branch_name is None
    gate = evaluate_soft_gates(ctx)
    assert gate.strong_claims_allowed is True
    assert any("Detached" in w for w in gate.warnings)


def test_no_commit_disallows_strong_claims():
    mapping = {
        ("rev-parse", "--is-inside-work-tree"): (0, "true", ""),
        ("rev-parse", "HEAD"): (1, "", "fatal: bad ref"),
        ("symbolic-ref", "-q", "HEAD"): (1, "", ""),
        ("rev-parse", "--abbrev-ref", "HEAD"): (0, "main", ""),
        ("status", "--porcelain=v1"): (0, "", ""),
    }
    ctx = capture_git_context(Path("/repo"), runner=_runner_from_map(mapping))
    assert ctx.head_commit is None
    gate = evaluate_soft_gates(ctx)
    assert gate.strong_claims_allowed is False


def test_provenance_contains_commit_and_branch():
    ctx = GitContext(
        repository_present=True,
        branch_name="topic/x",
        head_commit="a" * 40,
        short_commit="a" * 12,
        is_dirty=False,
        detached_head=False,
    )
    prov = build_qa_run_provenance(ctx, captured_at_utc_iso="2026-01-01T00:00:00Z")
    assert prov.head_commit_sha == "a" * 40
    assert prov.branch_name == "topic/x"
    lines = provenance_to_report_lines(prov)
    text = "\n".join(lines)
    assert "topic/x" in text
    assert ("a" * 12) in text


def test_strong_governance_claim_allowed_matrix():
    clean = GitContext(
        repository_present=True,
        branch_name="main",
        head_commit="b" * 40,
        short_commit="b" * 12,
        is_dirty=False,
        detached_head=False,
    )
    dirty = GitContext(
        repository_present=True,
        branch_name="main",
        head_commit="b" * 40,
        short_commit="b" * 12,
        is_dirty=True,
        detached_head=False,
        unstaged_files=("f.py",),
    )
    for claim in STRONG_GOVERNANCE_CLAIMS:
        assert strong_governance_claim_allowed(claim, clean) is True
        assert strong_governance_claim_allowed(claim, dirty) is False
    assert strong_governance_claim_allowed("smoke_ok_informal", dirty) is True


def test_porcelain_staged_file_detected():
    mapping = {
        ("rev-parse", "--is-inside-work-tree"): (0, "true", ""),
        ("rev-parse", "HEAD"): (0, "c0ffee", ""),
        ("symbolic-ref", "-q", "HEAD"): (0, "refs/heads/main", ""),
        ("rev-parse", "--abbrev-ref", "HEAD"): (0, "main", ""),
        ("status", "--porcelain=v1"): (0, "M  staged.txt\n", ""),
    }
    ctx = capture_git_context(Path("/repo"), runner=_runner_from_map(mapping))
    assert "staged.txt" in ctx.staged_files
    assert ctx.is_dirty is True


def test_status_failure_marks_dirty_and_blocks_strong_claims():
    mapping = {
        ("rev-parse", "--is-inside-work-tree"): (0, "true", ""),
        ("rev-parse", "HEAD"): (0, "abc", ""),
        ("symbolic-ref", "-q", "HEAD"): (0, "refs/heads/main", ""),
        ("rev-parse", "--abbrev-ref", "HEAD"): (0, "main", ""),
        ("status", "--porcelain=v1"): (1, "", "status exploded"),
    }
    ctx = capture_git_context(Path("/repo"), runner=_runner_from_map(mapping))
    assert ctx.is_dirty is True
    assert ctx.error_reason
    gate = evaluate_soft_gates(ctx)
    assert gate.strong_claims_allowed is False
