"""Tests: tools/icon_svg_guard.py gegen resources/icons/."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUARD_SCRIPT = ROOT / "tools" / "icon_svg_guard.py"


def _load_guard():
    spec = importlib.util.spec_from_file_location("icon_svg_guard", GUARD_SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_guard = _load_guard()


def test_cli_passes_on_resources_icons():
    r = subprocess.run(
        [sys.executable, str(GUARD_SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr + r.stdout


def test_resources_icons_passes_validate_tree():
    icons_root = ROOT / "resources" / "icons"
    err = _guard.validate_tree(icons_root)
    assert err == [], "\n".join(err)


def test_guard_detects_bad_viewbox(tmp_path):
    p = tmp_path / "bad.svg"
    p.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" '
        'fill="none" stroke="currentColor" stroke-width="1.5" '
        'stroke-linecap="round" stroke-linejoin="round">'
        "<path d=\"M4 4h16\"/></svg>",
        encoding="utf-8",
    )
    err = _guard.validate_svg_file(p)
    assert any("viewBox" in e for e in err)


def test_guard_detects_linear_gradient(tmp_path):
    p = tmp_path / "g.svg"
    p.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="1.5" '
        'stroke-linecap="round" stroke-linejoin="round">'
        "<linearGradient id=\"a\"><stop/></linearGradient>"
        "<path d=\"M4 4h16\"/></svg>",
        encoding="utf-8",
    )
    err = _guard.validate_svg_file(p)
    assert any("lineargradient" in e.lower() for e in err)


def test_guard_detects_hex_fill(tmp_path):
    p = tmp_path / "c.svg"
    p.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="1.5" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="4" fill="#f00"/></svg>',
        encoding="utf-8",
    )
    err = _guard.validate_svg_file(p)
    assert any("#f00" in e for e in err)
