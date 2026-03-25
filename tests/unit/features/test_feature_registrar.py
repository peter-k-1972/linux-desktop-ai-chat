"""FeatureRegistrar-Vertrag und eingebaute Registrare."""

import pytest

from app.features.descriptors import FeatureDescriptor
from app.features.registrar import FeatureRegistrar
from app.gui.registration.feature_builtins import (
    KnowledgeRAGCapabilityRegistrar,
    OperationsHubFeatureRegistrar,
    QAGovernanceFeatureRegistrar,
)
from app.gui.workspace.screen_registry import ScreenRegistry


def test_operations_hub_descriptor_fields():
    r = OperationsHubFeatureRegistrar()
    d = r.get_descriptor()
    assert d.name == "operations_hub"
    assert "operations_chat" in d.navigation_entries
    assert "operations_knowledge" not in d.navigation_entries
    assert d.enabled_by_default is True


def test_qa_governance_is_protocol_compatible():
    r = QAGovernanceFeatureRegistrar()
    assert isinstance(r, FeatureRegistrar)


def test_knowledge_capability_no_screen_side_effects():
    r = KnowledgeRAGCapabilityRegistrar()
    assert r.get_descriptor().screens == ()
    sr = ScreenRegistry()
    before = len(sr.list_areas())
    r.register_screens(sr)
    assert len(sr.list_areas()) == before


def test_feature_descriptor_is_frozen():
    d = FeatureDescriptor(name="a", description="b")
    with pytest.raises(Exception):
        d.name = "c"  # type: ignore[misc]
