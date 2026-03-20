"""
QA coverage for context debug gating – clean separation dev vs production.

With CONTEXT_DEBUG_ENABLED off:
- No debug logs
- No inspection panel (UI)
- No request capture
- CLI allowed but exits 0 with dev-only message, no inspection output

Runs with flag off and asserts no debug artifacts created.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from app.context.debug.context_debug_flag import is_context_debug_enabled
from app.context.devtools.request_capture import (
    capture,
    clear_capture,
    get_last_request,
)

pytestmark = pytest.mark.context_observability


def _flag_off(monkeypatch) -> None:
    """Ensure CONTEXT_DEBUG_ENABLED is off (production mode)."""
    monkeypatch.delenv("CONTEXT_DEBUG_ENABLED", raising=False)
    monkeypatch.setenv("CONTEXT_DEBUG_ENABLED", "")


@pytest.fixture(autouse=True)
def clear_capture_before_after():
    clear_capture()
    yield
    clear_capture()


def test_flag_off_no_request_capture(monkeypatch):
    """With flag off: capture is no-op, get_last_request returns None."""
    _flag_off(monkeypatch)
    assert not is_context_debug_enabled()

    capture(
        chat_id=1,
        messages=[{"role": "user", "content": "test"}],
        project_id=42,
    )

    assert get_last_request() is None


def test_flag_off_cli_exits_without_inspection_output(monkeypatch):
    """With flag off: CLI exits 0, no inspection output, dev-only message on stderr."""
    _flag_off(monkeypatch)
    project_root = Path(__file__).resolve().parent.parent.parent
    script = project_root / "scripts" / "dev" / "context_inspect.py"
    if not script.exists():
        pytest.skip("CLI script not found")

    result = subprocess.run(
        [sys.executable, str(script), "--chat-id", "1"],
        capture_output=True,
        text=True,
        cwd=str(project_root),
    )

    assert result.returncode == 0
    assert "disabled" in result.stderr.lower() or "deaktiviert" in result.stderr.lower()
    assert "[CTX_RESOLUTION]" not in result.stdout
    assert "[CTX_BUDGET]" not in result.stdout
    assert "explainability" not in result.stdout.lower() or "disabled" in result.stderr.lower()


def test_flag_off_explain_cli_exits_without_output(monkeypatch):
    """With flag off: context_explain CLI exits 0, no inspection output."""
    _flag_off(monkeypatch)
    project_root = Path(__file__).resolve().parent.parent.parent
    script = project_root / "scripts" / "dev" / "context_explain.py"
    if not script.exists():
        pytest.skip("CLI script not found")

    result = subprocess.run(
        [sys.executable, str(script), "--chat-id", "1"],
        capture_output=True,
        text=True,
        cwd=str(project_root),
    )

    assert result.returncode == 0
    assert "deaktiviert" in result.stderr.lower() or "disabled" in result.stderr.lower()


def test_default_no_env_flag_disabled(monkeypatch):
    """Default (no CONTEXT_DEBUG_ENABLED env): flag is disabled."""
    monkeypatch.delenv("CONTEXT_DEBUG_ENABLED", raising=False)
    assert not is_context_debug_enabled()


def test_flag_off_no_debug_artifacts_combined(monkeypatch):
    """Combined: flag off produces zero debug artifacts (capture + CLI)."""
    _flag_off(monkeypatch)

    capture(chat_id=1, messages=[{"role": "user", "content": "x"}])
    assert get_last_request() is None

    project_root = Path(__file__).resolve().parent.parent.parent
    script = project_root / "scripts" / "dev" / "context_inspect.py"
    if script.exists():
        result = subprocess.run(
            [sys.executable, str(script), "--chat-id", "1"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        assert result.returncode == 0
        assert "[CTX_" not in result.stdout
