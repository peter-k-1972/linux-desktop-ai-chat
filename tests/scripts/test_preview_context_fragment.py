"""
Minimaltests für scripts/dev/preview_context_fragment.py.

- Script läuft
- off erzeugt keinen Fragmentblock
- Feldprofile werden korrekt gemappt
"""

import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = PROJECT_ROOT / "scripts" / "dev" / "preview_context_fragment.py"


def test_script_runs():
    """Script läuft ohne Fehler."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--mode", "semantic", "--detail", "standard", "--fields", "all"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_off_produces_no_fragment_block():
    """off erzeugt keinen Fragmentblock."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--mode", "off"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "no fragment" in result.stdout
    assert "[[CTX]]" not in result.stdout
    assert "Arbeitskontext" not in result.stdout
    assert "Kontext:" not in result.stdout


def test_field_profiles_mapped_correctly():
    """Feldprofile werden korrekt gemappt."""
    # project_only: nur Projekt
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--mode", "semantic", "--detail", "minimal", "--fields", "project_only"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Projekt: Obsidian Core" in result.stdout
    assert "Chat:" not in result.stdout or "Fields: project" in result.stdout
    assert "Topic:" not in result.stdout

    # chat_only: nur Chat
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--mode", "neutral", "--detail", "minimal", "--fields", "chat_only"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Chat: Architekturprüfung" in result.stdout
    assert "Fields: chat" in result.stdout

    # topic_only: nur Topic (semantic standard/full zeigt Topic)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--mode", "semantic", "--detail", "standard", "--fields", "topic_only"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Topic:" in result.stdout
    assert "Fields: topic" in result.stdout


def test_policy_budget_preview():
    """Policy-Budgets werden korrekt angezeigt."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--policy", "architecture", "--mode", "semantic", "--detail", "standard"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Limits:" in result.stdout
    assert "max_project_chars: 100" in result.stdout
    assert "max_chat_chars: 100" in result.stdout
    assert "max_topic_chars: 80" in result.stdout
    assert "max_total_lines: 8" in result.stdout
    assert "Policy: architecture" in result.stdout


def test_long_names_are_truncated_in_preview():
    """Lange Namen werden bei kleinem Budget gekürzt."""
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--policy",
            "debug",
            "--project-name",
            "A" * 100,
            "--chat-title",
            "B" * 100,
            "--topic-name",
            "C" * 50,
        ],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "max_project_chars: 60" in result.stdout
    assert "max_chat_chars: 60" in result.stdout
    assert "max_topic_chars: 40" in result.stdout
    assert "A" * 100 not in result.stdout
    assert "B" * 100 not in result.stdout
    assert "..." in result.stdout


def test_preview_shows_limits_source():
    """Preview zeigt limits_source in der Ausgabe."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--policy", "exploration"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "source: exploration" in result.stdout
    assert "Limits:" in result.stdout
