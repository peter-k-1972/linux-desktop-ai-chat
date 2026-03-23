"""Smoke: icon_guard_report / run_icon_guards."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_icon_guard_report_exits_zero():
    r = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "icon_guard_report.py"), "--root", str(ROOT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert (ROOT / "ICON_GUARD_REPORT.md").is_file()


def test_run_icon_guards_exits_zero():
    r = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "run_icon_guards.py"), "--root", str(ROOT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr + r.stdout
