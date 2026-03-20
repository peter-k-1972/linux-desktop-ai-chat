"""
Async Test: Shutdown / Abbruch während Task.

Verhindert: Hang oder Crash wenn run_chat abgebrochen wird,
z.B. durch Fensterschließen oder Task-Cancellation.
"""

import asyncio

import pytest

from tests.async_behavior.conftest import (
    MinimalChatWidget,
    SlowStreamFakeClient,
    FakeDB,
    async_settings,
)


@pytest.mark.async_behavior
@pytest.mark.asyncio
@pytest.mark.integration
async def test_run_chat_cancellation_cleans_up(async_db, async_settings, qtbot):
    """
    Wenn run_chat-Task abgebrochen wird, wird _streaming zurückgesetzt.
    Verhindert: UI bleibt in "Streaming"-State hängen.
    """
    client = SlowStreamFakeClient()
    settings = async_settings
    widget = MinimalChatWidget(client, settings, async_db)
    widget.chat_id = async_db.create_chat()

    task = asyncio.create_task(widget.run_chat("Test"))
    # Warten bis Streaming gestartet
    for _ in range(50):
        if getattr(widget, "_streaming", False):
            break
        await asyncio.sleep(0.01)

    # Task abbrechen (simuliert Fenster schließen / Abbruch)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    # _streaming muss zurückgesetzt sein – run_chat hat finally-Block der _streaming = False setzt.
    # Verhindert: UI bleibt in "Streaming"-State hängen, zweiter Send blockiert.
    from tests.helpers.diagnostics import dump_streaming_state

    assert getattr(widget, "_streaming", True) is False, (
        f"_streaming muss nach Task-Cancellation False sein. {dump_streaming_state(widget)}"
    )


@pytest.mark.async_behavior
@pytest.mark.asyncio
@pytest.mark.integration
async def test_second_send_after_first_completes(async_db, async_settings, qtbot):
    """
    Nach Abschluss des ersten Sends kann ein zweiter Send erfolgen.
    Verhindert: _streaming bleibt dauerhaft True.
    """
    client = SlowStreamFakeClient()
    settings = async_settings
    widget = MinimalChatWidget(client, settings, async_db)
    widget.chat_id = async_db.create_chat()

    await widget.run_chat("Erste Nachricht")
    assert getattr(widget, "_streaming", False) is False

    await widget.run_chat("Zweite Nachricht")
    assert client.call_count == 2
