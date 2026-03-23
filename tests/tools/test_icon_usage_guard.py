"""Tests für tools/icon_usage_guard.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GUARD = ROOT / "tools" / "icon_usage_guard.py"


def test_icon_usage_guard_clean_tree():
    r = subprocess.run(
        [sys.executable, str(GUARD), "--root", str(ROOT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr + r.stdout


def test_icon_usage_guard_detects_qrc(tmp_path: Path):
    bad = tmp_path / "app" / "gui"
    bad.mkdir(parents=True)
    (bad / "x.py").write_text('QIcon(":/icons/x.svg")\n', encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(GUARD), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 1
    assert "QRC" in r.stderr or ":/" in r.stderr


def test_icon_usage_guard_detects_assets_string(tmp_path: Path):
    bad = tmp_path / "app" / "gui"
    bad.mkdir(parents=True)
    (bad / "y.py").write_text('x = "assets/icons/foo.svg"\n', encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(GUARD), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 1
    assert "assets/icons" in r.stderr


def test_icon_usage_guard_detects_qpixmap_literal(tmp_path: Path):
    bad = tmp_path / "app" / "gui"
    bad.mkdir(parents=True)
    (bad / "z.py").write_text('QPixmap("x.png")\n', encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(GUARD), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 1
    assert "QPixmap" in r.stderr
