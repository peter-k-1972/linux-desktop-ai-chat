"""
Smoke Tests: Runtime Lifecycle (Single-Instance, Shutdown).

Testet Lifecycle-Modul und Lock-Verhalten.
"""

import os
import pytest

# Single-Instance deaktivieren für Tests (conftest setzt das, aber sicher ist sicher)
os.environ["LINUX_DESKTOP_CHAT_SINGLE_INSTANCE"] = "0"


def test_lifecycle_module_importable():
    """app.runtime.lifecycle ist importierbar."""
    from app.runtime.lifecycle import (
        try_acquire_single_instance_lock,
        release_single_instance_lock,
        run_shutdown_cleanup,
        register_shutdown_hooks,
    )
    assert callable(try_acquire_single_instance_lock)
    assert callable(release_single_instance_lock)
    assert callable(run_shutdown_cleanup)
    assert callable(register_shutdown_hooks)


@pytest.mark.smoke
def test_single_instance_lock_acquired_when_disabled():
    """Bei LINUX_DESKTOP_CHAT_SINGLE_INSTANCE=0 wird Lock immer erworben (True)."""
    os.environ["LINUX_DESKTOP_CHAT_SINGLE_INSTANCE"] = "0"
    from app.runtime.lifecycle import try_acquire_single_instance_lock, release_single_instance_lock

    ok = try_acquire_single_instance_lock()
    assert ok is True
    release_single_instance_lock()


@pytest.mark.smoke
def test_run_shutdown_cleanup_no_exception():
    """run_shutdown_cleanup wirft keine Exception (auch ohne laufende App)."""
    from app.runtime.lifecycle import run_shutdown_cleanup

    # Ohne vorherige Infra-Init: sollte trotzdem durchlaufen
    run_shutdown_cleanup()


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_run_shutdown_cleanup_async_no_exception():
    """run_shutdown_cleanup_async wirft keine Exception (auch ohne ChatService)."""
    from app.runtime.lifecycle import run_shutdown_cleanup_async

    await run_shutdown_cleanup_async()
