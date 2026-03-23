"""
Unit Tests: Settings Theme Persistence.

Prüft theme_id in AppSettings, Normalisierung und Persistenz.
"""

import pytest

from app.core.config.settings import AppSettings
from app.core.config.settings_backend import InMemoryBackend
from app.gui.themes.theme_id_utils import is_registered_theme_id, registered_theme_ids


def test_settings_theme_id_default():
    """AppSettings hat theme_id nach load."""
    backend = InMemoryBackend()
    settings = AppSettings(backend=backend)
    assert hasattr(settings, "theme_id")
    assert is_registered_theme_id(settings.theme_id)


def test_settings_theme_id_normalized_from_legacy_light():
    """Legacy theme='light' wird zu theme_id='light_default' normalisiert."""
    backend = InMemoryBackend()
    backend.setValue("theme", "light")
    backend.setValue("theme_id", "")
    settings = AppSettings(backend=backend)
    assert settings.theme_id == "light_default"


def test_settings_theme_id_normalized_from_legacy_dark():
    """Legacy theme='dark' wird zu theme_id='dark_default' normalisiert."""
    backend = InMemoryBackend()
    backend.setValue("theme", "dark")
    backend.setValue("theme_id", "")
    settings = AppSettings(backend=backend)
    assert settings.theme_id == "dark_default"


def test_settings_theme_id_persisted():
    """theme_id wird beim save persistiert."""
    backend = InMemoryBackend()
    settings = AppSettings(backend=backend)
    settings.theme_id = "dark_default"
    settings.theme = "dark"
    settings.save()
    assert backend.value("theme_id", "") == "dark_default"


def test_settings_theme_id_roundtrip():
    """theme_id überlebt load/save roundtrip."""
    backend = InMemoryBackend()
    s1 = AppSettings(backend=backend)
    s1.theme_id = "dark_default"
    s1.theme = "dark"
    s1.save()
    s2 = AppSettings(backend=backend)
    assert s2.theme_id == "dark_default"


def test_settings_workbench_theme_id_roundtrip():
    """workbench theme_id wird persistiert und wieder erkannt."""
    backend = InMemoryBackend()
    s1 = AppSettings(backend=backend)
    s1.theme_id = "workbench"
    s1.theme = "dark"
    s1.save()
    s2 = AppSettings(backend=backend)
    assert s2.theme_id == "workbench"
    assert s2.theme == "dark"
    assert "workbench" in registered_theme_ids()
