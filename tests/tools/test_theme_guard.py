"""Integrationstests für tools/theme_guard.py (Subprocess, temporäres Root)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
THEME_GUARD = ROOT / "tools" / "theme_guard.py"


def _run_guard(root: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(THEME_GUARD), "--root", str(root), *extra],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_theme_guard_clean_project_passes(tmp_path: Path):
    (tmp_path / "pkg").mkdir(parents=True)
    (tmp_path / "pkg" / "mod.py").write_text("def f():\n    return 42\n", encoding="utf-8")
    r = _run_guard(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


def test_theme_guard_detects_hex(tmp_path: Path):
    (tmp_path / "pkg").mkdir(parents=True)
    (tmp_path / "pkg" / "bad.py").write_text(
        'STYLE = "background: #1e1e1e"\n',
        encoding="utf-8",
    )
    r = _run_guard(tmp_path)
    assert r.returncode == 1
    assert "bad.py" in r.stdout
    assert "#1e1e1e" in r.stdout or "hex" in r.stdout


def test_theme_guard_detects_qcolor_string(tmp_path: Path):
    (tmp_path / "w").mkdir()
    (tmp_path / "w" / "x.py").write_text(
        'from PySide6.QtGui import QColor\n'
        'c = QColor("#ff0000")\n',
        encoding="utf-8",
    )
    r = _run_guard(tmp_path)
    assert r.returncode == 1
    assert "QColor(" in r.stdout


def test_theme_guard_detects_qt_red(tmp_path: Path):
    (tmp_path / "w").mkdir()
    (tmp_path / "w" / "x.py").write_text(
        "# Kein Laufzeit-Import nötig — nur statische Zeile\n"
        "pen.setColor(Qt.red)\n",
        encoding="utf-8",
    )
    r = _run_guard(tmp_path)
    assert r.returncode == 1
    assert "Qt.red" in r.stdout or "Qt." in r.stdout


def test_theme_guard_allows_app_gui_themes_prefix(tmp_path: Path):
    (tmp_path / "app" / "gui" / "themes").mkdir(parents=True)
    (tmp_path / "app" / "gui" / "themes" / "profile.py").write_text(
        'X = "#0f172a"\n',
        encoding="utf-8",
    )
    r = _run_guard(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


def test_theme_guard_qss_base_scanned(tmp_path: Path):
    (tmp_path / "assets" / "themes" / "base").mkdir(parents=True)
    (tmp_path / "assets" / "themes" / "base" / "bad.qss").write_text(
        "QFrame { background: #111111; }\n",
        encoding="utf-8",
    )
    r = _run_guard(tmp_path)
    assert r.returncode == 1
    assert "bad.qss" in r.stdout


def test_theme_guard_qss_legacy_allowed(tmp_path: Path):
    (tmp_path / "assets" / "themes" / "legacy").mkdir(parents=True)
    (tmp_path / "assets" / "themes" / "legacy" / "dark.qss").write_text(
        "QWidget { color: #ffffff; }\n",
        encoding="utf-8",
    )
    r = _run_guard(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


def test_theme_guard_suggest_flag(tmp_path: Path):
    (tmp_path / "p").mkdir()
    (tmp_path / "p" / "a.py").write_text('S = "background: #abc"\n', encoding="utf-8")
    r = _run_guard(tmp_path, "--suggest")
    assert r.returncode == 1
    assert "Suggestion:" in r.stdout
