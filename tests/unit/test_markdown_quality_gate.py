"""Unit tests: Markdown Quality Gate (Klassifikation, ohne vollständigen Repo-Scan)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GATE_SCRIPT = ROOT / "tools" / "run_markdown_quality_gate.py"


def _load_gate_module():
    spec = importlib.util.spec_from_file_location("_markdown_qg", GATE_SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_markdown_qg"] = mod
    spec.loader.exec_module(mod)
    return mod


_g = _load_gate_module()


@pytest.mark.parametrize(
    "rel,severity,auto_fixable,category,fail",
    [
        ("docs/x.md", "blocker", False, "codeblocks", True),
        ("docs/x.md", "high", False, "links", True),
        ("docs/x.md", "high", True, "codeblocks", False),
        ("docs/x.md", "medium", False, "headings", False),
        ("README.md", "medium", False, "links", True),
        ("docs/other.md", "medium", False, "links", False),
    ],
)
def test_issue_fail_classification(rel, severity, auto_fixable, category, fail):
    assert _g._issue_is_fail(rel, severity, auto_fixable, category) is fail


def test_high_auto_is_warn_not_fail():
    rel = "docs/x.md"
    assert not _g._issue_is_fail(rel, "high", True, "codeblocks")
    assert _g._issue_is_warn(rel, "high", True, "codeblocks")


def test_fail_excludes_warn():
    rel = "docs/x.md"
    assert _g._issue_is_fail(rel, "blocker", False, "x")
    assert not _g._issue_is_warn(rel, "blocker", False, "x")


def test_effective_fail_ci_downgrades_non_product_high():
    rel = "docs/qa/x.md"
    assert _g._effective_validator_fail(rel, "high", False, "links", "strict")
    assert not _g._effective_validator_fail(rel, "high", False, "links", "ci")


def test_effective_fail_ci_keeps_help_high():
    rel = "help/topics/foo.md"
    assert _g._effective_validator_fail(rel, "high", False, "links", "ci")


def test_broken_markdown_demo_has_malformed_or_code_segment():
    from app.gui.shared.markdown.markdown_api import render_segments

    text = (ROOT / "app/resources/demo_markdown/broken_markdown.md").read_text(encoding="utf-8")
    kinds = {s.kind for s in render_segments(text, promote_ascii=True)}
    assert kinds & {"malformed_block", "code_block"}


def test_code_blocks_demo_has_code_block_segment():
    from app.gui.shared.markdown.markdown_api import render_segments

    text = (ROOT / "app/resources/demo_markdown/code_blocks.md").read_text(encoding="utf-8")
    kinds = {s.kind for s in render_segments(text, promote_ascii=True)}
    assert "code_block" in kinds
