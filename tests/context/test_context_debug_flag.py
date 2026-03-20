"""
QA coverage for context debug flag gating.

Verifies disabled mode produces no inspection data, enabled mode works fully.
No UI integration. No persistence.
"""

import os

import pytest

from app.context.debug.context_debug_flag import is_context_debug_enabled
from app.context.devtools.request_capture import (
    capture,
    clear_capture,
    get_last_request,
)

pytestmark = pytest.mark.context_observability


@pytest.fixture(autouse=True)
def clear_capture_before_after():
    clear_capture()
    yield
    clear_capture()


def test_disabled_mode_produces_no_inspection_data(monkeypatch):
    """When CONTEXT_DEBUG_ENABLED is not set, capture no-ops and get_last_request returns None."""
    monkeypatch.delenv("CONTEXT_DEBUG_ENABLED", raising=False)
    # Ensure config path also returns disabled (no infra in test)
    # is_context_debug_enabled checks env first, then config
    assert not is_context_debug_enabled()

    capture(
        chat_id=1,
        messages=[{"role": "user", "content": "test"}],
        project_id=42,
    )

    assert get_last_request() is None


def test_enabled_mode_via_env_works_fully(monkeypatch):
    """When CONTEXT_DEBUG_ENABLED=1, capture stores and get_last_request returns data."""
    monkeypatch.setenv("CONTEXT_DEBUG_ENABLED", "1")

    assert is_context_debug_enabled()

    capture(
        chat_id=1,
        messages=[{"role": "user", "content": "hello"}],
        project_id=42,
    )

    last = get_last_request()
    assert last is not None
    assert last["chat_id"] == 1
    assert last["project_id"] == 42
    assert last["message"] == "hello"


def test_enabled_mode_via_env_true(monkeypatch):
    """CONTEXT_DEBUG_ENABLED=true is enabled."""
    monkeypatch.setenv("CONTEXT_DEBUG_ENABLED", "true")
    assert is_context_debug_enabled()


def test_disabled_mode_env_empty(monkeypatch):
    """CONTEXT_DEBUG_ENABLED= or unset is disabled."""
    monkeypatch.setenv("CONTEXT_DEBUG_ENABLED", "")
    assert not is_context_debug_enabled()

    monkeypatch.delenv("CONTEXT_DEBUG_ENABLED", raising=False)
    assert not is_context_debug_enabled()


def test_cli_exits_gracefully_when_disabled(monkeypatch):
    """CLI exits 0 with message when disabled. No crash."""
    monkeypatch.delenv("CONTEXT_DEBUG_ENABLED", raising=False)

    import subprocess
    import sys
    from pathlib import Path

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


def test_cli_runs_when_enabled(monkeypatch):
    """CLI runs inspection when CONTEXT_DEBUG_ENABLED=1."""
    monkeypatch.setenv("CONTEXT_DEBUG_ENABLED", "1")

    import subprocess
    import sys
    import tempfile
    from pathlib import Path

    project_root = Path(__file__).resolve().parent.parent.parent
    script = project_root / "scripts" / "dev" / "context_inspect.py"
    if not script.exists():
        pytest.skip("CLI script not found")

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--db", db_path, "--chat-id", "1"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        assert result.returncode == 0
        assert "[CTX_RESOLUTION]" in result.stdout or "explainability" in result.stdout.lower()
    finally:
        try:
            os.unlink(db_path)
        except OSError:
            pass
