"""
Sentinel: Entry-Point-Gruppe für externe Feature-Pakete bleibt stabil.

Siehe docs/architecture/PLUGIN_PACKAGES_ENTRY_POINTS.md
"""

import pytest

from app.features import (
    ENTRY_POINT_GROUP,
    ENTRY_POINT_LEGACY_REGISTRARS_ATTR,
    ENTRY_POINT_PRIMARY_CALLABLE,
    feature_discovery as fd,
)


@pytest.mark.architecture
@pytest.mark.contract
def test_entry_point_group_matches_discovery():
    assert fd.ENTRY_POINT_GROUP == ENTRY_POINT_GROUP
    assert ENTRY_POINT_GROUP == "linux_desktop_chat.features"


@pytest.mark.architecture
@pytest.mark.contract
def test_entry_point_contract_documents_primary_and_legacy_names():
    assert ENTRY_POINT_PRIMARY_CALLABLE == "get_feature_registrars"
    assert ENTRY_POINT_LEGACY_REGISTRARS_ATTR == "FEATURE_REGISTRARS"
