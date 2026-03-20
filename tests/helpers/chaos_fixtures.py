"""
Chaos-Test-Helfer: Stubs für kontrollierte Fault-Injection.

Leichtgewichtig – keine große Infrastruktur.
"""

import asyncio
from typing import Any, AsyncGenerator, Dict, List


class DelayedProviderStub:
    """Provider-Stub mit konfigurierbarer Verzögerung (Timeout-Simulation)."""

    def __init__(self, delay_sec: float = 2.0, response: str = "Antwort"):
        self.delay_sec = delay_sec
        self.response = response
        self.call_count = 0

    async def get_models(self):
        return []

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        self.call_count += 1
        await asyncio.sleep(self.delay_sec)
        yield {"message": {"content": self.response, "thinking": ""}, "done": True}


class TimeoutProviderStub:
    """Provider-Stub der sehr lange wartet (simuliert Timeout/Hang)."""

    def __init__(self, wait_sec: float = 10.0):
        self.wait_sec = wait_sec
        self.call_count = 0

    async def get_models(self):
        return []

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        self.call_count += 1
        await asyncio.sleep(self.wait_sec)
        yield {"message": {"content": "spät", "thinking": ""}, "done": True}


class FailingRepositoryStub:
    """DB-Repository das bei assistant-Save fehlschlägt (nach erfolgreichem user-Save)."""

    def __init__(self, fail_on_role: str = "assistant"):
        self._messages = {}
        self._next_id = 1
        self.fail_on_role = fail_on_role

    def create_chat(self, title: str = ""):
        cid = self._next_id
        self._next_id += 1
        self._messages[cid] = []
        return cid

    def save_message(self, cid: int, role: str, content: str):
        if role == self.fail_on_role:
            raise OSError("Simulierter DB-Fehler: Persistenz nach Erfolg")
        self._messages.setdefault(cid, []).append((role, content, "ts"))

    def load_chat(self, cid: int):
        return list(self._messages.get(cid, []))

    def list_workspace_roots_for_chat(self, cid: int):
        return []
