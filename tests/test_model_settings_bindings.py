"""Tests für ModelSettings-Bindings (Settings-Sync)."""

import unittest

from app.core.config.settings import AppSettings
from app.core.config.settings_backend import InMemoryBackend


class TestModelSettingsBindings(unittest.TestCase):
    def test_settings_web_search(self):
        """Web-Search wird in Settings persistiert."""
        backend = InMemoryBackend()
        s = AppSettings(backend=backend)
        s.web_search = True
        s.save()
        s2 = AppSettings(backend=backend)
        s2.load()
        self.assertTrue(s2.web_search)

    def test_settings_default_role(self):
        """Default-Rolle wird in Settings persistiert."""
        backend = InMemoryBackend()
        s = AppSettings(backend=backend)
        s.default_role = "THINK"
        s.save()
        s2 = AppSettings(backend=backend)
        s2.load()
        self.assertEqual(s2.default_role, "THINK")
