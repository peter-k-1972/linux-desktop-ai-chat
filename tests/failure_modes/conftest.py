"""
Fixtures für Failure Injection Tests.
"""

from typing import Dict, List
from unittest.mock import MagicMock

import pytest

from app.gui.legacy import ChatWidget
from app.core.config.settings import AppSettings


class FakeDB:
    """Minimale DB für Failure-Tests."""

    def __init__(self):
        self._messages = {}
        self._next_id = 1

    def create_chat(self, title=""):
        cid = self._next_id
        self._next_id += 1
        self._messages[cid] = []
        return cid

    def save_message(self, cid, role, content):
        self._messages.setdefault(cid, []).append((role, content, "ts"))

    def load_chat(self, cid):
        return list(self._messages.get(cid, []))

    def list_workspace_roots_for_chat(self, cid):
        return []


class MinimalChatWidget(ChatWidget):
    def load_models(self):
        pass

    def on_update_chat(self, text, is_final):
        pass


@pytest.fixture
def failure_settings():
    s = AppSettings()
    s.model = "test:latest"
    return s
