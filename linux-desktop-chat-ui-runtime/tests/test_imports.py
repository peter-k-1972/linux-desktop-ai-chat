"""Smoke: distribution exposes app.ui_runtime."""

from __future__ import annotations

from app.ui_runtime import ThemeManifest
from app.ui_runtime.manifest_models import SUPPORTED_MANIFEST_SCHEMA_MAJOR


def test_package_importable() -> None:
    assert SUPPORTED_MANIFEST_SCHEMA_MAJOR >= 1
    assert ThemeManifest.__name__ == "ThemeManifest"
