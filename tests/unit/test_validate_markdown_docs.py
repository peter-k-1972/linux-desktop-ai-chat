"""Smoke tests for tools/validate_markdown_docs.py (stdlib, no pytest plugins required)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _PROJECT_ROOT / "tools" / "validate_markdown_docs.py"


def _load_validator():
    name = "validate_markdown_docs"
    spec = importlib.util.spec_from_file_location(name, _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def vmd():
    return _load_validator()


def test_unclosed_fence_blocker(tmp_path: Path, vmd):
    f = tmp_path / "x.md"
    f.write_text("# T\n\n```python\nprint(1)\n", encoding="utf-8")
    r = vmd.analyze_file(f, tmp_path, {})
    assert any(i.severity == "blocker" and i.category == "codeblocks" for i in r.issues)


def test_tilde_fence_high(vmd, tmp_path: Path):
    f = tmp_path / "y.md"
    f.write_text("# T\n\n~~~\nfoo\n~~~\n", encoding="utf-8")
    r = vmd.analyze_file(f, tmp_path, {})
    assert any(i.category == "codeblocks" and "Tilden" in i.message for i in r.issues)


def test_table_column_mismatch(vmd, tmp_path: Path):
    f = tmp_path / "z.md"
    f.write_text(
        "| a | b |\n|---|---|\n| only |\n",
        encoding="utf-8",
    )
    r = vmd.analyze_file(f, tmp_path, {})
    assert any(i.category == "tables" and "Spalten" in i.message for i in r.issues)


def test_validator_script_runs_project_scan(vmd):
    files = vmd._collect_markdown_files(_PROJECT_ROOT)
    assert (_PROJECT_ROOT / "README.md") in files or any(
        p.name == "README.md" and p.parent == _PROJECT_ROOT for p in files
    )


def test_help_bare_topic_ids_resolve(vmd):
    root = _PROJECT_ROOT
    hi = vmd._build_help_topic_index(root)
    intro = root / "help" / "getting_started" / "introduction.md"
    if not intro.is_file():
        pytest.skip("help introduction missing")
    r = vmd.analyze_file(intro, root, hi)
    bad = [i for i in r.issues if i.category == "links" and "chat_overview" in i.message]
    assert not bad
