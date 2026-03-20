"""
UI Tests: Kommandozentrale / QA Dashboard.

- Adapter: Laden der wichtigsten Statuswerte, robust bei fehlenden Dateien
- View: sinnvolle Darstellung leerer Zustände
"""

import json
import tempfile
from pathlib import Path

import pytest

from app.qa.dashboard_adapter import QADashboardAdapter, DashboardData
from app.qa.operations_adapter import OperationsAdapter


# --- Adapter Tests (kein Qt) ---


def test_adapter_empty_qa_dir_returns_safe_defaults():
    """Bei leerem/fehlendem QA-Verzeichnis: keine Exception, sinnvolle Defaults."""
    with tempfile.TemporaryDirectory() as tmp:
        qa_dir = Path(tmp) / "nonexistent"
        adapter = QADashboardAdapter(qa_dir=qa_dir)
        data = adapter.load()

    assert isinstance(data, DashboardData)
    assert data.executive.test_count == 0
    assert data.executive.prioritized_gaps == 0
    assert data.executive.orphan_backlog == 0
    assert data.executive.qa_health == "unknown"
    assert data.has_data is False
    assert len(data.coverage_axes) == 4
    assert len(data.subsystems) >= 1
    assert len(data.next_actions) >= 1


def test_adapter_partial_inventory_loads():
    """Nur Inventory vorhanden: test_count und Subsysteme werden geladen."""
    with tempfile.TemporaryDirectory() as tmp:
        inv_path = Path(tmp) / "QA_TEST_INVENTORY.json"
        inv_path.write_text(
            json.dumps({
                "test_count": 42,
                "summary": {
                    "test_count": 42,
                    "by_subsystem": {"Chat": 10, "RAG": 15},
                },
            }),
            encoding="utf-8",
        )
        adapter = QADashboardAdapter(qa_dir=Path(tmp))
        data = adapter.load()

    assert data.has_data is True
    assert data.executive.test_count == 42
    assert data.executive.qa_health == "ok"
    assert any(s.name == "Chat" and s.test_count == 10 for s in data.subsystems)
    assert any(s.name == "RAG" and s.test_count == 15 for s in data.subsystems)


def test_adapter_gap_report_loads_orphan_count():
    """Gap-Report: orphan_count und prioritized_gaps werden gelesen."""
    with tempfile.TemporaryDirectory() as tmp:
        gap_path = Path(tmp) / "PHASE3_GAP_REPORT.json"
        gap_path.write_text(
            json.dumps({
                "prioritized_gaps": [{"id": "G1"}],
                "orphan_count": 50,
                "generated_at": "2026-03-15T12:00:00Z",
            }),
            encoding="utf-8",
        )
        adapter = QADashboardAdapter(qa_dir=Path(tmp))
        data = adapter.load()

    assert data.has_data is True
    assert data.executive.prioritized_gaps == 1
    assert data.executive.orphan_backlog == 50
    assert data.executive.last_verification == "2026-03-15T12:00:00Z"
    assert data.executive.qa_health == "warning"
    assert "Orphan Review" in data.next_actions[0] or "Gap-Follow-up" in str(data.next_actions)


def test_adapter_invalid_json_does_not_crash():
    """Ungültiges JSON: Adapter wirft nicht, liefert Defaults."""
    with tempfile.TemporaryDirectory() as tmp:
        inv_path = Path(tmp) / "QA_TEST_INVENTORY.json"
        inv_path.write_text("not valid json {{{", encoding="utf-8")
        adapter = QADashboardAdapter(qa_dir=Path(tmp))
        data = adapter.load()

    assert data.executive.test_count == 0
    assert data.has_data is False


def test_adapter_coverage_map_axes():
    """Coverage Map: Achsen failure_class, guard, regression_requirement, replay_binding."""
    with tempfile.TemporaryDirectory() as tmp:
        cov_path = Path(tmp) / "QA_COVERAGE_MAP.json"
        cov_path.write_text(
            json.dumps({
                "summary": {
                    "coverage_strength": {
                        "failure_class": "covered",
                        "guard": "covered",
                        "regression_requirement": "partial",
                        "replay_binding": "covered",
                    },
                    "gap_types": {
                        "failure_class_uncovered": 0,
                        "guard_missing": 1,
                        "regression_requirement_unbound": 2,
                        "replay_unbound": 0,
                    },
                },
            }),
            encoding="utf-8",
        )
        adapter = QADashboardAdapter(qa_dir=Path(tmp))
        data = adapter.load()

    axes = {a.axis: a for a in data.coverage_axes}
    assert "failure_class" in axes
    assert "guard" in axes
    assert "regression_requirement" in axes
    assert "replay_binding" in axes
    assert axes["failure_class"].strength == "covered"
    assert axes["guard"].gap_count == 1
    assert axes["regression_requirement"].gap_count == 2


# --- Phase B: Drilldown Adapter Tests ---


def test_adapter_load_qa_drilldown_empty():
    """QA-Drilldown bei fehlenden Dateien: sichere Defaults."""
    with tempfile.TemporaryDirectory() as tmp:
        adapter = QADashboardAdapter(qa_dir=Path(tmp))
        data = adapter.load_qa_drilldown()

    assert data.has_data is False
    assert len(data.gap_items) == 0
    assert len(data.coverage_axes) == 4
    assert data.orphan_breakdown is not None


def test_adapter_load_qa_drilldown_with_gap_report():
    """QA-Drilldown mit Gap-Report: orphan_breakdown und Gaps."""
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "PHASE3_GAP_REPORT.json").write_text(
            json.dumps({
                "prioritized_gaps": [{"id": "G1", "title": "Test Gap", "severity": "high"}],
                "orphan_count": 20,
                "orphan_breakdown": {"review_candidates": 20, "whitelisted": 5, "treat_as": "review_candidate"},
            }),
            encoding="utf-8",
        )
        adapter = QADashboardAdapter(qa_dir=Path(tmp))
        data = adapter.load_qa_drilldown()

    assert data.has_data is True
    assert len(data.gap_items) == 1
    assert data.gap_items[0].id == "G1"
    assert data.orphan_breakdown.review_candidates == 20


def test_adapter_load_subsystem_detail():
    """Subsystem-Detail: Name, Testanzahl, Domains."""
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "QA_TEST_INVENTORY.json").write_text(
            json.dumps({
                "summary": {"by_subsystem": {"Chat": 10}},
                "tests": [
                    {"subsystem": "Chat", "test_domain": "ui", "failure_classes": []},
                    {"subsystem": "Chat", "test_domain": "ui", "failure_classes": ["ui_state_drift"]},
                ],
            }),
            encoding="utf-8",
        )
        adapter = QADashboardAdapter(qa_dir=Path(tmp))
        data = adapter.load_subsystem_detail("Chat")

    assert data.has_data is True
    assert data.name == "Chat"
    assert data.test_count == 10
    assert data.status == "ok"
    assert any(d[0] == "ui" for d in data.test_domains)


def test_adapter_load_subsystem_detail_missing():
    """Subsystem-Detail bei fehlendem Inventar: leere Daten."""
    with tempfile.TemporaryDirectory() as tmp:
        adapter = QADashboardAdapter(qa_dir=Path(tmp))
        data = adapter.load_subsystem_detail("Chat")

    assert data.name == "Chat"
    assert data.test_count == 0
    assert data.status == "unknown"


def test_adapter_load_governance():
    """Governance: Zonen werden geladen."""
    with tempfile.TemporaryDirectory() as tmp:
        adapter = QADashboardAdapter(qa_dir=Path(tmp))
        data = adapter.load_governance()

    assert data.has_data is True
    assert len(data.zones) >= 2
    zone_ids = [z.id for z in data.zones]
    assert "qa_core" in zone_ids
    assert "product" in zone_ids


# --- View Tests (Qt) ---


def test_command_center_view_opens(qtbot):
    """CommandCenterView öffnet ohne Fehler."""
    from app.gui.domains.command_center import CommandCenterView

    view = CommandCenterView(theme="dark")
    qtbot.addWidget(view)
    view.show()
    assert view.isVisible()
    assert view.back_btn is not None


def test_command_center_view_empty_state_display(qtbot):
    """Bei fehlenden QA-Daten: Anzeige zeigt Platzhalter, kein Crash."""
    from PySide6.QtCore import Qt
    from app.gui.domains.command_center import CommandCenterView

    view = CommandCenterView(theme="dark")
    qtbot.addWidget(view)
    view.refresh()
    assert view.data is not None
    assert view.card_tests.value_label.text() != ""


def test_command_center_back_signal(qtbot):
    """Zurück-Button emittiert back_to_chat_requested."""
    from PySide6.QtCore import Qt
    from app.gui.domains.command_center import CommandCenterView

    view = CommandCenterView(theme="dark")
    qtbot.addWidget(view)
    emitted = []

    def on_back():
        emitted.append(True)

    view.back_to_chat_requested.connect(on_back)
    qtbot.mouseClick(view.back_btn, Qt.MouseButton.LeftButton)
    assert len(emitted) == 1


# --- Phase B: Drilldown Navigation ---


def test_qa_drilldown_navigation(qtbot):
    """QA Drilldown-Button wechselt zur QA-Detailansicht."""
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QPushButton
    from app.gui.domains.command_center import CommandCenterView

    view = CommandCenterView(theme="dark")
    qtbot.addWidget(view)
    view.refresh()
    assert view.stack.currentIndex() == CommandCenterView.IDX_OVERVIEW

    qa_btn = next((b for b in view.findChildren(QPushButton) if "Drilldown" in b.text()), None)
    assert qa_btn is not None, "QA Drilldown-Button nicht gefunden"
    qtbot.mouseClick(qa_btn, Qt.MouseButton.LeftButton)
    assert view.stack.currentIndex() == CommandCenterView.IDX_QA_DRILLDOWN


def test_qa_drilldown_view_opens(qtbot):
    """QADrilldownView öffnet und zeigt Daten."""
    from app.gui.domains.command_center import QADrilldownView

    view = QADrilldownView(theme="dark")
    qtbot.addWidget(view)
    view.show()
    assert view.isVisible()
    view.refresh()
    assert view.data is not None


def test_subsystem_detail_view_opens(qtbot):
    """SubsystemDetailView öffnet für Subsystem."""
    from app.gui.domains.command_center import SubsystemDetailView

    view = SubsystemDetailView("Chat", theme="dark")
    qtbot.addWidget(view)
    view.show()
    assert view.isVisible()
    assert view.subsystem_name == "Chat"


def test_governance_view_opens(qtbot):
    """GovernanceView öffnet und zeigt Zonen."""
    from app.gui.domains.command_center import GovernanceView

    view = GovernanceView(theme="dark")
    qtbot.addWidget(view)
    view.refresh()
    view.show()
    assert view.isVisible()
    assert view.data is not None
    assert len(view.data.zones) >= 2


def test_runtime_debug_view_opens(qtbot):
    """RuntimeDebugView öffnet."""
    from app.gui.domains.command_center import RuntimeDebugView

    view = RuntimeDebugView(theme="dark")
    qtbot.addWidget(view)
    view.show()
    assert view.isVisible()


# --- Phase C: Operations Tests ---


def test_operations_adapter_incident_empty():
    """Incident Operations bei fehlendem Index: sichere Defaults."""
    with tempfile.TemporaryDirectory() as tmp:
        adapter = OperationsAdapter(qa_dir=Path(tmp))
        data = adapter.load_incident_operations()

    assert data.has_data is False
    assert data.incident_count == 0
    assert len(data.incidents) == 0


def test_operations_adapter_incident_with_data():
    """Incident Operations mit index.json."""
    with tempfile.TemporaryDirectory() as tmp:
        inc_dir = Path(tmp) / "incidents"
        inc_dir.mkdir()
        (inc_dir / "index.json").write_text(
            json.dumps({
                "incident_count": 1,
                "incidents": [
                    {"incident_id": "INC-001", "title": "Test", "status": "new", "severity": "high",
                     "subsystem": "Chat", "failure_class": "ui_drift", "regression_required": True,
                     "binding_status": None, "replay_status": None},
                ],
                "metrics": {"open_incidents": 1, "bound_to_regression": 0, "replay_defined": 0},
            }),
            encoding="utf-8",
        )
        adapter = OperationsAdapter(qa_dir=Path(tmp))
        data = adapter.load_incident_operations()

    assert data.has_data is True
    assert data.incident_count == 1
    assert len(data.incidents) == 1
    assert data.incidents[0].incident_id == "INC-001"


def test_operations_adapter_review_loads():
    """Review Operations lädt Orphan-Backlog."""
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "PHASE3_GAP_REPORT.json").write_text(
            json.dumps({"orphan_count": 50, "orphan_breakdown": {"review_candidates": 50, "treat_as": "review_candidate"}}),
            encoding="utf-8",
        )
        adapter = OperationsAdapter(qa_dir=Path(tmp))
        data = adapter.load_review_operations()

    assert data.has_data is True
    assert data.orphan_count == 50
    assert data.treat_as == "review_candidate"
    assert len(data.batches) >= 1


def test_operations_adapter_guided_workflows():
    """Guided Workflows liefert Einstiege."""
    adapter = OperationsAdapter()
    data = adapter.load_guided_workflows()

    assert data.has_data is True
    assert len(data.entries) >= 4
    ids = [e.id for e in data.entries]
    assert "orphan_review" in ids
    assert "qa_verification" in ids
    assert "incident_status" in ids
    assert "audit_followup" in ids


def test_operations_navigation(qtbot):
    """Operations-Button wechselt zur richtigen View."""
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QPushButton
    from app.gui.domains.command_center import CommandCenterView

    view = CommandCenterView(theme="dark")
    qtbot.addWidget(view)
    view.refresh()

    qa_ops_btn = next((b for b in view.findChildren(QPushButton) if "QA Operations" in b.text()), None)
    assert qa_ops_btn is not None
    qtbot.mouseClick(qa_ops_btn, Qt.MouseButton.LeftButton)
    assert view.stack.currentIndex() == CommandCenterView.IDX_QA_OPS


def test_qa_operations_view_opens(qtbot):
    """QAOperationsView öffnet."""
    from app.gui.domains.command_center import QAOperationsView

    view = QAOperationsView(theme="dark")
    qtbot.addWidget(view)
    view.refresh()
    view.show()
    assert view.isVisible()
    assert view.data is not None


def test_audit_operations_empty_without_report():
    """Audit Operations ohne AUDIT_REPORT: leerer Zustand."""
    with tempfile.TemporaryDirectory() as tmp:
        adapter = OperationsAdapter(project_root=Path(tmp))
        data = adapter.load_audit_operations()

    assert len(data.items) == 0
