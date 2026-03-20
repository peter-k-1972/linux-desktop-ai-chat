"""
Meta-Tests: Architecture Drift Sentinels.

Erkennt Drift, wenn neue EventTypes ohne Contract/Governance hinzugefügt werden.
"""

import pytest

from app.debug.agent_event import EventType

from tests.contracts.event_type_registry import EVENT_TYPE_CONTRACT


@pytest.mark.contract
def test_all_event_types_have_contract_coverage():
    """
    Sentinel: Jeder EventType muss im Contract-Registry sein.

    Bei neuem EventType:
    1. tests/contracts/event_type_registry.py: EVENT_TYPE_CONTRACT ergänzen
    2. tests/contracts/test_debug_event_contract.py: Stabilitätstest erweitern
    3. app/ui/debug/event_timeline_view.py: type_map ergänzen (falls Anzeige)
    4. docs/qa/REGRESSION_CATALOG.md: ggf. eintragen
    """
    for et in EventType:
        assert et in EVENT_TYPE_CONTRACT, (
            f"EventType {et} fehlt im Contract-Registry. "
            "Siehe docs/qa/TEST_GOVERNANCE_RULES.md Abschnitt 'Neuer EventType'."
        )


@pytest.mark.contract
def test_event_type_registry_matches_enum():
    """
    Sentinel: Registry enthält keine veralteten Einträge.
    """
    registry_types = set(EVENT_TYPE_CONTRACT.keys())
    enum_types = set(EventType)
    extra = registry_types - enum_types
    assert not extra, f"Registry enthält entfernte EventTypes: {extra}"


@pytest.mark.contract
def test_all_event_types_have_timeline_display():
    """
    Sentinel: Jeder EventType liefert einen Anzeigetext in der Timeline.

    Nutzt die interne _event_display_text-Funktion.
    Bei neuem EventType: event_timeline_view type_map ergänzen für bessere UX.
    """
    from datetime import datetime, timezone

    from app.debug.agent_event import AgentEvent
    from app.gui.domains.runtime_debug.panels.event_timeline_view import _event_display_text

    for et in EventType:
        event = AgentEvent(
            timestamp=datetime.now(timezone.utc),
            agent_name="Test",
            event_type=et,
            message="",
        )
        text = _event_display_text(event)
        assert text, f"EventType {et} liefert leeren Anzeigetext"
        assert isinstance(text, str), f"EventType {et}: Anzeigetext muss str sein, got {type(text)}"
