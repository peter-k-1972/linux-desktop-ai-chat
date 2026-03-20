"""
QA Observability Panel – Visualisiert QA-Health-Metriken aus docs/qa/artifacts/json/.

Liest bestehende Artefakte (QA_STATUS, QA_COVERAGE_MAP, QA_RISK_RADAR, etc.).
Keine Duplikation von QA-Logik. Aktualisiert automatisch bei Artefakt-Änderung.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QFrame,
    QLabel,
    QGroupBox,
)
from PySide6.QtCore import QTimer, QFileSystemWatcher, Slot


def _project_root() -> Path:
    p = Path(__file__).resolve().parent
    for _ in range(5):
        p = p.parent
    return p


def _artifacts_dir() -> Path:
    return _project_root() / "docs" / "qa" / "artifacts" / "json"


def _incidents_index_path() -> Path:
    return _project_root() / "docs" / "qa" / "incidents" / "index.json"


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


class QAObservabilityPanel(QWidget):
    """
    QA Observability – gruppierte Karten für Coverage, Risk Radar, Incidents,
    Test System, Stability. Liest docs/qa/artifacts/json/*.json.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("qaObservabilityPanel")
        self._cards: dict[str, QGroupBox] = {}
        self._card_layouts: dict[str, QVBoxLayout] = {}
        self._setup_ui()
        self._watcher = QFileSystemWatcher(self)
        self._connect_watcher()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(3000)
        self._refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self._cards["coverage"] = self._make_card("Coverage")
        self._cards["risk"] = self._make_card("Risk Radar")
        self._cards["incidents"] = self._make_card("Incidents")
        self._cards["tests"] = self._make_card("Test System")
        self._cards["stability"] = self._make_card("Stability")

        for card in self._cards.values():
            content_layout.addWidget(card)
        content_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _make_card(self, title: str) -> QGroupBox:
        g = QGroupBox(title)
        g.setObjectName("qaObservabilityCard")
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

    def _add_card_row(self, title: str, key: str, value: str):
        gl = self._card_layouts.get(title)
        if not gl:
            return
        row = QLabel(f"{key}: {value}")
        row.setObjectName("qaObservabilityRow")
        row.setWordWrap(True)
        gl.addWidget(row)

    def _connect_watcher(self):
        artifacts = _artifacts_dir()
        if not artifacts.exists():
            return
        files = [
            str(artifacts / "QA_STATUS.json"),
            str(artifacts / "QA_COVERAGE_MAP.json"),
            str(artifacts / "QA_RISK_RADAR.json"),
            str(artifacts / "QA_STABILITY_INDEX.json"),
            str(artifacts / "QA_TEST_INVENTORY.json"),
            str(artifacts / "QA_ANOMALY_DETECTION.json"),
        ]
        inc = _incidents_index_path()
        if inc.exists():
            files.append(str(inc))
        for f in files:
            if Path(f).exists():
                try:
                    self._watcher.addPath(f)
                except OSError:
                    pass
        self._watcher.fileChanged.connect(self._on_file_changed)

    @Slot(str)
    def _on_file_changed(self, path: str):
        """Artefakt geändert – Refresh nach kurzer Verzögerung (Datei kann noch geschrieben werden)."""
        QTimer.singleShot(500, self._refresh)

    def _refresh(self):
        self._render_coverage()
        self._render_risk_radar()
        self._render_incidents()
        self._render_test_system()
        self._render_stability()

    def _render_coverage(self):
        self._clear_card("Coverage")
        gl = self._card_layouts.get("Coverage")
        if not gl:
            return

        cov = _load_json(_artifacts_dir() / "QA_COVERAGE_MAP.json")
        status = _load_json(_artifacts_dir() / "QA_STATUS.json")
        gap = _load_json(_artifacts_dir() / "PHASE3_GAP_REPORT.json")

        if status:
            reg = status.get("regression", {})
            self._add_card_row("Coverage", "Failure classes covered", str(reg.get("covered_count", "—")))
            self._add_card_row("Coverage", "Regression open", str(reg.get("open_count", "—")))
            if reg.get("covered"):
                covered = ", ".join(reg["covered"][:5])
                if len(reg.get("covered", [])) > 5:
                    covered += f" (+{len(reg['covered'])-5})"
                self._add_card_row("Coverage", "Covered classes", covered)

        if cov:
            by_axis = cov.get("coverage_by_axis", {})
            fc = by_axis.get("failure_class", {})
            if isinstance(fc, dict):
                covered_fc = sum(1 for v in fc.values() if isinstance(v, dict) and v.get("coverage_strength") == "covered")
                total_fc = len([k for k, v in fc.items() if isinstance(v, dict) and "coverage_strength" in (v or {})])
                if total_fc > 0:
                    self._add_card_row("Coverage", "Failure class coverage", f"{covered_fc}/{total_fc}")

            rr = by_axis.get("regression_requirement", {})
            if isinstance(rr, dict):
                bound = rr.get("covered_count", 0)
                total = rr.get("total_recommendations", 0)
                if total > 0 or bound > 0:
                    self._add_card_row("Coverage", "Regression requirements bound", f"{bound}/{total}")

        if gap:
            gaps = gap.get("prioritized_gaps", [])
            uncovered = [g.get("gap_id", g.get("value", "?")) for g in gaps[:5]]
            if uncovered:
                self._add_card_row("Coverage", "Uncovered risk areas", ", ".join(uncovered[:5]))

        if not cov and not status and not gap:
            self._add_card_row("Coverage", "Status", "Keine Daten (Artefakte prüfen)")

    def _render_risk_radar(self):
        self._clear_card("Risk Radar")
        gl = self._card_layouts.get("Risk Radar")
        if not gl:
            return

        radar = _load_json(_artifacts_dir() / "QA_RISK_RADAR.json")
        if not radar:
            self._add_card_row("Risk Radar", "Status", "Keine Daten")
            return

        subs = radar.get("subsystems", {})
        high_critical = [(k, v.get("new_risk_level", "?")) for k, v in subs.items() if v.get("new_risk_level") in ("high", "critical")]
        for sub, level in sorted(high_critical, key=lambda x: (0 if x[1] == "critical" else 1, x[0]))[:6]:
            self._add_card_row("Risk Radar", sub, level)

        escalations = radar.get("escalations", [])[:3]
        for e in escalations:
            text = e if isinstance(e, str) else e.get("message", str(e))
            self._add_card_row("Risk Radar", "Escalation", text[:80] + ("…" if len(text) > 80 else ""))

    def _render_incidents(self):
        self._clear_card("Incidents")
        gl = self._card_layouts.get("Incidents")
        if not gl:
            return

        idx = _load_json(_incidents_index_path())
        if not idx:
            self._add_card_row("Incidents", "Status", "Keine Incident-Daten")
            return

        metrics = idx.get("metrics", {})
        self._add_card_row("Incidents", "Open", str(metrics.get("open_incidents", 0)))
        self._add_card_row("Incidents", "Replay defined", str(metrics.get("replay_defined", 0)))
        self._add_card_row("Incidents", "Replay verified", str(metrics.get("replay_verified", 0)))
        self._add_card_row("Incidents", "Bound to regression", str(metrics.get("bound_to_regression", 0)))

        incidents = idx.get("incidents", [])[:5]
        for inc in incidents:
            iid = inc.get("incident_id", "?")
            status = inc.get("status", "?")
            replay = inc.get("replay_status") or "—"
            binding = inc.get("binding_status") or "—"
            self._add_card_row("Incidents", iid, f"status={status} replay={replay} binding={binding}")

    def _render_test_system(self):
        self._clear_card("Test System")
        gl = self._card_layouts.get("Test System")
        if not gl:
            return

        inv = _load_json(_artifacts_dir() / "QA_TEST_INVENTORY.json")
        if not inv:
            self._add_card_row("Test System", "Status", "Keine Daten")
            return

        summary = inv.get("summary", {})
        count = inv.get("test_count", summary.get("test_count", 0))
        self._add_card_row("Test System", "Test count", str(count))

        by_domain = summary.get("by_test_domain", {})
        top_domains = sorted(by_domain.items(), key=lambda x: -x[1])[:8]
        for domain, cnt in top_domains:
            self._add_card_row("Test System", domain, str(cnt))

        self._add_card_row("Test System", "Catalog-bound failure classes", str(summary.get("catalog_bound_failure_class_count", "—")))
        self._add_card_row("Test System", "Covers regression", str(summary.get("covers_regression_count", "—")))

    def _render_stability(self):
        self._clear_card("Stability")
        gl = self._card_layouts.get("Stability")
        if not gl:
            return

        stab = _load_json(_artifacts_dir() / "QA_STABILITY_INDEX.json")
        anom = _load_json(_artifacts_dir() / "QA_ANOMALY_DETECTION.json")

        if stab:
            self._add_card_row("Stability", "Index", str(stab.get("index", "—")))
            self._add_card_row("Stability", "Klasse", stab.get("stabilitaetsklasse", "—"))
            factors = stab.get("belastungsfaktoren", [])[:3]
            for f in factors:
                self._add_card_row("Stability", "Belastung", (f[:70] + "…") if len(f) > 70 else f)

        if anom:
            snapshot = anom.get("aktueller_snapshot", {})
            self._add_card_row("Stability", "Anomalie-Snapshot", f"Index={snapshot.get('stability_index', '—')}")
            warn = anom.get("warnsignale", [])[:3]
            for w in warn:
                text = w.get("text", str(w)) if isinstance(w, dict) else str(w)
                self._add_card_row("Stability", "Warnung", text[:60] + ("…" if len(text) > 60 else ""))

        if not stab and not anom:
            self._add_card_row("Stability", "Status", "Keine Daten")
