"""
Architektur-Guard: Runtime Lifecycle Governance.

Prüft, dass Single-Instance und Shutdown-Hooks im Startpfad verdrahtet sind.
Regeln: docs/04_architecture/RUNTIME_LIFECYCLE_POLICY.md
"""

import pytest
from pathlib import Path

from tests.architecture.arch_guard_config import PROJECT_ROOT


@pytest.mark.architecture
@pytest.mark.contract
def test_run_gui_shell_uses_single_instance_check():
    """
    Sentinel: run_gui_shell ruft try_acquire_single_instance_lock auf.
    """
    path = PROJECT_ROOT / "run_gui_shell.py"
    assert path.exists(), "run_gui_shell.py fehlt"
    source = path.read_text(encoding="utf-8")
    assert "try_acquire_single_instance_lock" in source, (
        "Startup Governance: run_gui_shell muss try_acquire_single_instance_lock aufrufen. "
        "Siehe RUNTIME_LIFECYCLE_POLICY.md."
    )
    assert "register_shutdown_hooks" in source, (
        "Startup Governance: run_gui_shell muss register_shutdown_hooks aufrufen. "
        "Siehe RUNTIME_LIFECYCLE_POLICY.md."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_lifecycle_module_exists():
    """Sentinel: app.runtime.lifecycle existiert mit erforderlichen Funktionen."""
    from app.runtime import lifecycle

    assert hasattr(lifecycle, "try_acquire_single_instance_lock")
    assert hasattr(lifecycle, "release_single_instance_lock")
    assert hasattr(lifecycle, "run_shutdown_cleanup")
    assert hasattr(lifecycle, "register_shutdown_hooks")


@pytest.mark.architecture
@pytest.mark.contract
def test_run_gui_shell_exits_on_second_instance():
    """
    Sentinel: run_gui_shell beendet sich bei zweitem Start (sys.exit(1)).
    """
    path = PROJECT_ROOT / "run_gui_shell.py"
    source = path.read_text(encoding="utf-8")
    assert "sys.exit(1)" in source, (
        "run_gui_shell muss bei bestehendem Lock mit sys.exit(1) beenden."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_shell_main_window_has_close_event():
    """Sentinel: ShellMainWindow hat closeEvent für Shutdown-Cleanup."""
    from app.gui.shell import ShellMainWindow
    assert hasattr(ShellMainWindow, "closeEvent")
    # closeEvent muss überschrieben sein (nicht nur von QWidget geerbt)
    assert "closeEvent" in ShellMainWindow.__dict__


@pytest.mark.architecture
@pytest.mark.contract
def test_lifecycle_has_async_cleanup():
    """Sentinel: Lifecycle-Modul bietet run_shutdown_cleanup_async."""
    from app.runtime import lifecycle
    assert hasattr(lifecycle, "run_shutdown_cleanup_async")
