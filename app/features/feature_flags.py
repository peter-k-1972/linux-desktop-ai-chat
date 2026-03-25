"""
Feature-Flags / Kill-Switches — Abfrage über FeatureDescriptor.

Später: Umgebungsvariablen, Edition-Manifest.
"""

from __future__ import annotations

from app.features.descriptors import FeatureDescriptor


def is_feature_experimental(descriptor: FeatureDescriptor) -> bool:
    """True, wenn das Feature als experimentell markiert ist."""
    return bool(descriptor.experimental)
