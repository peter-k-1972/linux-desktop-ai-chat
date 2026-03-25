"""Minimaler Smoke-Test ohne Host-`app.gui`."""

from __future__ import annotations

import app.features as feat


def test_root_exports_feature_descriptor_and_entry_point_group():
    assert feat.FeatureDescriptor is not None
    assert feat.ENTRY_POINT_GROUP == "linux_desktop_chat.features"
