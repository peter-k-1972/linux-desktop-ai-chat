"""Tests für tools/normalize_markdown_docs.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "normalize_markdown_docs.py"


def _load():
    name = "normalize_markdown_docs"
    spec = importlib.util.spec_from_file_location(name, _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def nmd():
    return _load()


def test_idempotent_trailing_and_blank_collapse(nmd):
    raw = "Zeile a  \n\n\n\nZeile b\n"
    once, _ = nmd.normalize_markdown_content(raw)
    twice, _ = nmd.normalize_markdown_content(once)
    assert once == twice


def test_crlf_normalized(nmd):
    raw = "x\r\ny\r"
    out, stats = nmd.normalize_markdown_content(raw)
    assert "\r" not in out
    assert stats.line_endings >= 1


def test_fence_tick_shorten(nmd):
    raw = "````\ncode\n````\n"
    out, stats = nmd.normalize_markdown_content(raw)
    assert "`````" not in out
    assert "```" in out
    assert stats.fence_ticks_normalized >= 1


def test_code_body_tabs_preserved(nmd):
    raw = "```\n\ta = 1\n```\n"
    out, _ = nmd.normalize_markdown_content(raw)
    assert "\ta = 1" in out.split("\n")


def test_second_pass_no_stats(nmd):
    raw = "- item  \n\n\n- two\n"
    once, s1 = nmd.normalize_markdown_content(raw)
    _, s2 = nmd.normalize_markdown_content(once)
    assert s2.tabs_to_spaces == 0
    assert s2.trailing_removed == 0
    assert s2.blank_lines_collapsed == 0


def test_list_tab_expanded(nmd):
    raw = "-\tone\n"
    out, stats = nmd.normalize_markdown_content(raw)
    assert "\t" not in out
    assert stats.tabs_to_spaces >= 1
