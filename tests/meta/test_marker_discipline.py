"""
Meta-Test: Marker-Disziplin.

Prüft, ob Testdateien in spezialisierten Domänen den erwarteten pytest-Marker verwenden.
"""

import pytest

from scripts.qa.checks import get_marker_violations


@pytest.mark.contract
def test_no_marker_violations_in_specialized_domains():
    """
    Sentinel: Jede Testdatei in contracts/, async_behavior/, failure_modes/,
    cross_layer/, startup/, meta/ muss den erwarteten Marker enthalten.

    Bei Verletzung: @pytest.mark.<erwartet> in der Datei ergänzen.
    Siehe docs/qa/TEST_GOVERNANCE_RULES.md.
    """
    violations = get_marker_violations()
    assert not violations, (
        f"Marker-Disziplin verletzt: {len(violations)} Datei(en) ohne erwarteten Marker. "
        f"Verletzungen: {violations}"
    )
