"""
Chaos: Persistenz-Fehler nach erfolgreicher Provider-Antwort.

Szenario: Provider-Antwort erfolgreich, DB-Schreiben schlägt danach fehl.
Erwartung: UI bleibt konsistent, _streaming zurückgesetzt, Folgeaktionen möglich.
"""

from typing import Dict, List

import pytest

from tests.failure_modes.conftest import MinimalChatWidget, failure_settings
from tests.helpers.chaos_fixtures import FailingRepositoryStub, DelayedProviderStub


class FastFakeClient:
    """Schneller Client für Persistenz-Tests."""

    def __init__(self):
        self.call_count = 0

    async def get_models(self):
        return []

    async def chat(self, model: str, messages: List[Dict[str, str]], **kwargs):
        self.call_count += 1
        async def _gen():
            yield {"message": {"content": "Antwort", "thinking": ""}, "done": True}
        return _gen()


@pytest.mark.chaos
@pytest.mark.asyncio
@pytest.mark.integration
async def test_persistence_failure_resets_streaming_state(qtbot, failure_settings):
    """
    DB schlägt beim Speichern der Assistant-Antwort fehl.
    Erwartung: _streaming wird im finally zurückgesetzt, Widget bleibt benutzbar.
    """
    client = FastFakeClient()
    db = FailingRepositoryStub(fail_on_role="assistant")
    widget = MinimalChatWidget(client, failure_settings, db)
    widget.chat_id = db.create_chat()

    with pytest.raises(OSError):
        await widget.run_chat("Test")

    assert getattr(widget, "_streaming", True) is False


@pytest.mark.chaos
@pytest.mark.asyncio
@pytest.mark.integration
async def test_after_persistence_failure_second_chat_with_working_db_works(qtbot, failure_settings):
    """
    Nach Persistenz-Fehler: Wechsel zu funktionierender DB, zweiter Chat funktioniert.
    System bleibt benutzbar.
    """
    from tests.async_behavior.conftest import FakeDB

    client = FastFakeClient()
    failing_db = FailingRepositoryStub(fail_on_role="assistant")
    widget = MinimalChatWidget(client, failure_settings, failing_db)
    widget.chat_id = failing_db.create_chat()

    with pytest.raises(OSError):
        await widget.run_chat("Erste")

    working_db = FakeDB()
    working_db._messages = dict(failing_db._messages)
    working_db._next_id = failing_db._next_id
    widget.db = working_db

    await widget.run_chat("Zweite Nachricht")

    assert client.call_count == 2
    assert getattr(widget, "_streaming", False) is False
