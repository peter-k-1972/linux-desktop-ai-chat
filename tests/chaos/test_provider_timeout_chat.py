"""
Chaos: Provider Timeout / starke Verzögerung.

Szenario: Provider antwortet stark verzögert oder Timeout.
Erwartung: UI bleibt stabil, kein doppelter Send, Streaming-State sauber,
System danach benutzbar.
"""

import asyncio

import pytest

from tests.async_behavior.conftest import MinimalChatWidget, FakeDB, async_settings
from tests.helpers.chaos_fixtures import TimeoutProviderStub, DelayedProviderStub


@pytest.mark.chaos
@pytest.mark.asyncio
@pytest.mark.integration
async def test_provider_delay_then_cancel_cleans_up_streaming_state(qtbot, async_settings):
    """
    Provider verzögert stark → Task wird abgebrochen → _streaming wird zurückgesetzt.
    UI bleibt nicht in Busy-State hängen.
    """
    client = TimeoutProviderStub(wait_sec=5.0)
    db = FakeDB()
    widget = MinimalChatWidget(client, async_settings, db)
    widget.chat_id = db.create_chat()

    task = asyncio.create_task(widget.run_chat("Test"))
    for _ in range(50):
        if getattr(widget, "_streaming", False):
            break
        await asyncio.sleep(0.01)

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    assert getattr(widget, "_streaming", True) is False


@pytest.mark.chaos
@pytest.mark.asyncio
@pytest.mark.integration
async def test_provider_delay_completes_then_second_send_works(qtbot, async_settings):
    """
    Provider antwortet verzögert, aber vollständig.
    Nach Abschluss: zweiter Send funktioniert, kein doppelter Send.
    """
    client = DelayedProviderStub(delay_sec=0.1, response="Antwort")
    db = FakeDB()
    widget = MinimalChatWidget(client, async_settings, db)
    widget.chat_id = db.create_chat()

    await widget.run_chat("Erste Nachricht")
    assert getattr(widget, "_streaming", False) is False
    assert client.call_count == 1

    await widget.run_chat("Zweite Nachricht")
    assert client.call_count == 2
    assert getattr(widget, "_streaming", False) is False


@pytest.mark.chaos
@pytest.mark.asyncio
@pytest.mark.integration
async def test_no_double_send_while_streaming(qtbot, async_settings):
    """
    Während Streaming: zweiter run_chat wird ignoriert (_streaming-Guard).
    """
    client = DelayedProviderStub(delay_sec=0.2, response="Antwort")
    db = FakeDB()
    widget = MinimalChatWidget(client, async_settings, db)
    widget.chat_id = db.create_chat()

    task = asyncio.create_task(widget.run_chat("Erste"))
    await asyncio.sleep(0.05)
    await widget.run_chat("Zweite")  # Sollte sofort returnen (Guard)
    await task

    assert client.call_count == 1
