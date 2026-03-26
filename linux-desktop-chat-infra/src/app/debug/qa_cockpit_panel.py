"""
QA Cockpit Panel – Visualisiert QA-Health-Metriken aus docs/qa/artifacts/json/.

Liest ausschließlich Artefakte, keine QA-Berechnung. Einfache Karten, lesbar, minimalistisch.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QFrame,
    QLabel,
    QGroupBox,
)
from PySide6.QtCore import QTimer, QFileSystemWatcher, Slot

from app.debug.qa_artifact_loader import (
    load_test_inventory,
    load_coverage,
    load_risk_radar,
    load_gap_status,
    load_incidents,
    load_stability,
)


class QACockpitPanel(QWidget):
    """
    QA Cockpit – 6 Sektionen: Test Inventory, Coverage, Risk Radar,
    Gap Status, Incidents, Stability.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("qaCockpitPanel")
        self._card_layouts: dict[str, QVBoxLayout] = {}
        self._setup_ui()
        self._watcher = QFileSystemWatcher(self)
        self._connect_watcher()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(4000)
        self._refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(0, 0, 0, 0)

        for title in ("Test Inventory", "Coverage", "Risk Radar", "Gap Status", "Incidents", "Stability"):
            card = self._make_card(title)
            content_layout.addWidget(card)
        content_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _make_card(self, title: str) -> QGroupBox:
        g = QGroupBox(title)
        g.setObjectName("qaCockpitCard")
        g.setMinimumHeight(60)
        gl = QVBoxLayout(g)
        self._card_layouts[title] = gl
        return g

    def _clear_card(self, title: str):
        gl = self._card_layouts.get(title)
        if not gl:
            return
        while gl.count():
            item = gl.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _add_row(self, title: str, key: str, value: str):
        gl = self._card_layouts.get(title)
        if not gl:
            return
        row = QLabel(f"{key}: {value}")
        row.setObjectName("qaCockpitRow")
        row.setWordWrap(True)
        gl.addWidget(row)

    def _connect_watcher(self):
        from pathlib import Path
        base = Path(__file__).resolve().parent.parent / "docs" / "qa" / "artifacts" / "json"
        inc = Path(__file__).resolve().parent.parent / "docs" / "qa" / "incidents" / "index.json"
        for name in ("QA_TEST_INVENTORY.json", "QA_COVERAGE_MAP.json", "QA_RISK_RADAR.json",
                     "QA_STABILITY_INDEX.json", "PHASE3_GAP_REPORT.json", "QA_ANOMALY_DETECTION.json"):
            p = base / name
            if p.exists():
                try:
                    self._watcher.addPath(str(p))
                except OSError:
                    pass
        if inc.exists():
            try:
                self._watcher.addPath(str(inc))
            except OSError:
                pass
        self._watcher.fileChanged.connect(self._on_file_changed)

    @Slot(str)
    def _on_file_changed(self, path: str):
        QTimer.singleShot(600, self._refresh)

    def _refresh(self):
        self._render_test_inventory()
        self._render_coverage()
        self._render_risk_radar()
        self._render_gap_status()
        self._render_incidents()
        self._render_stability()

    def _render_test_inventory(self):
        self._clear_card("Test Inventory")
        d = load_test_inventory()
        self._add_row("Test Inventory", "Total", str(d.total_count))
        if d.domains:
            top = sorted(d.domains.items(), key=lambda x: -x[1])[:6]
            for domain, cnt in top:
                self._add_row("Test Inventory", domain, str(cnt))
        if not d.total_count and not d.domains:
            self._add_row("Test Inventory", "Status", "No data")

    def _render_coverage(self):
        self._clear_card("Coverage")
        d = load_coverage()
        self._add_row("Coverage", "Failure classes covered", f"{d.failure_classes_covered}/{d.failure_classes_total}" if d.failure_classes_total else "—")
        if d.missing_coverage:
            self._add_row("Coverage", "Missing coverage", ", ".join(d.missing_coverage[:5]))
        if not d.failure_classes_covered and not d.failure_classes_total and not d.missing_coverage:
            self._add_row("Coverage", "Status", "No data")

    def _render_risk_radar(self):
        self._clear_card("Risk Radar")
        d = load_risk_radar()
        high = [(k, v) for k, v in d.subsystems.items() if v in ("high", "critical")]
        for sub, level in sorted(high, key=lambda x: (0 if x[1] == "critical" else 1, x[0]))[:8]:
            self._add_row("Risk Radar", sub, level)
        if not d.subsystems:
            self._add_row("Risk Radar", "Status", "No data")

    def _render_gap_status(self):
        self._clear_card("Gap Status")
        d = load_gap_status()
        self._add_row("Gap Status", "Replay unbound", str(d.replay_unbound_count))
        self._add_row("Gap Status", "Regression requirement unbound", str(d.regression_requirement_unbound_count))
        if d.uncovered_failure_classes:
            self._add_row("Gap Status", "Uncovered failure classes", ", ".join(d.uncovered_failure_classes[:5]))
        if d.gap_ids and len(d.gap_ids) <= 5:
            self._add_row("Gap Status", "Gap IDs", ", ".join(d.gap_ids[:5]))
        elif d.gap_ids:
            self._add_row("Gap Status", "Gap IDs", ", ".join(d.gap_ids[:3]) + f" (+{len(d.gap_ids)-3})")
        if not d.replay_unbound_count and not d.regression_requirement_unbound_count and not d.uncovered_failure_classes:
            self._add_row("Gap Status", "Status", "No gaps")

    def _render_incidents(self):
        self._clear_card("Incidents")
        d = load_incidents()
        self._add_row("Incidents", "Open", str(d.open_count))
        self._add_row("Incidents", "Replay defined", str(d.replay_defined))
        self._add_row("Incidents", "Replay verified", str(d.replay_verified))
        self._add_row("Incidents", "Bound to regression", str(d.bound_to_regression))
        if not d.open_count and not d.replay_defined:
            self._add_row("Incidents", "Status", "No incidents")

    def _render_stability(self):
        self._clear_card("Stability")
        d = load_stability()
        self._add_row("Stability", "Index", str(d.index))
        self._add_row("Stability", "Klasse", d.klasse or "—")
        for s in d.anomaly_summary[:4]:
            self._add_row("Stability", "Anomaly", (s[:70] + "…") if len(s) > 70 else s)
        if not d.index and not d.klasse and not d.anomaly_summary:
            self._add_row("Stability", "Status", "No data")
