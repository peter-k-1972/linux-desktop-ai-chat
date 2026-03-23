"""run_gui_shell: Fallback ohne qasync darf kein „with asyncio_loop:“ nutzen (kein Context Manager)."""

from __future__ import annotations

import asyncio


def test_std_asyncio_loop_is_not_async_context_manager():
    """Invariante: asyncio.new_event_loop() unterstützt kein ``with loop`` (Py3.12)."""
    loop = asyncio.new_event_loop()
    assert getattr(loop, "__enter__", None) is None
