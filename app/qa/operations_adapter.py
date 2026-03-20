"""
Operations Adapter – Read-only Service für das Operations Center (Phase C).

Liest docs/qa/incidents/, PHASE3_*, AUDIT_REPORT.md.
Keine Änderung an scripts/qa oder docs/qa.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.qa.operations_models import (
    AuditItem,
    AuditOperationsData,
    IncidentItem,
    IncidentOperationsData,
    QAOperationsData,
    ReviewBatchItem,
    ReviewOperationsData,
    VerificationStatus,
    WorkflowEntry,
    GuidedWorkflowData,
)


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _default_qa_dir() -> Path:
    return _project_root() / "docs" / "qa"


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _load_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


class OperationsAdapter:
    """
    Read-only Adapter für Operations-Daten.
    Liefert strukturierte DTOs für QA, Incident, Review, Audit.
    """

    def __init__(self, qa_dir: Path | None = None, project_root: Path | None = None):
        self.qa_dir = qa_dir or _default_qa_dir()
        self.project_root = project_root or _project_root()

    def load_incident_operations(self) -> IncidentOperationsData:
        """Lädt Incident-Übersicht aus incidents/index.json."""
        data = IncidentOperationsData()
        index = _load_json(self.qa_dir / "incidents" / "index.json")
        if not index:
            return data

        data.has_data = True
        data.incident_count = index.get("incident_count", 0)
        metrics = index.get("metrics") or {}
        data.open_count = metrics.get("open_incidents", 0)
        data.bound_count = metrics.get("bound_to_regression", 0)
        data.replay_ready_count = metrics.get("replay_defined", 0) + metrics.get("replay_verified", 0)

        for inc in index.get("incidents") or []:
            data.incidents.append(IncidentItem(
                incident_id=str(inc.get("incident_id", "")),
                title=str(inc.get("title", "")),
                status=str(inc.get("status", "")),
                severity=str(inc.get("severity", "")),
                subsystem=str(inc.get("subsystem", "")),
                failure_class=str(inc.get("failure_class", "")),
                regression_required=bool(inc.get("regression_required", False)),
                binding_status=inc.get("binding_status"),
                replay_status=inc.get("replay_status"),
            ))

        for w in index.get("warnings") or []:
            msg = w.get("message", "") if isinstance(w, dict) else str(w)
            if msg:
                data.warnings.append(msg)

        return data

    def load_qa_operations(self) -> QAOperationsData:
        """Lädt QA-Operations-Daten (Verifikation, Artefakte)."""
        data = QAOperationsData()
        gap_report = _load_json(self.qa_dir / "PHASE3_GAP_REPORT.json")
        coverage_map = _load_json(self.qa_dir / "QA_COVERAGE_MAP.json")

        if gap_report or coverage_map:
            data.has_data = True

        # Verification Status
        data.verification = VerificationStatus()
        if gap_report:
            data.verification.last_run = gap_report.get("generated_at", "")
            data.verification.orphan_count = gap_report.get("orphan_count", 0)
            data.verification.gaps_closed = len(gap_report.get("prioritized_gaps") or []) == 0
            data.verification.has_data = True
        if coverage_map:
            data.verification.verification_steps = [
                "Coverage Map",
                "Gap Report",
                "Test Inventory",
            ]

        # Artefakt-Links
        data.artifact_links = [
            ("Gap Report", "PHASE3_GAP_REPORT.md"),
            ("Coverage Map", "QA_COVERAGE_MAP.json"),
            ("Test Inventory", "QA_TEST_INVENTORY.json"),
            ("Verifikations-Review", "PHASE3_VERIFICATION_REVIEW.md"),
        ]
        return data

    def load_review_operations(self) -> ReviewOperationsData:
        """Lädt Review-Operations (Orphan Backlog, Batches)."""
        data = ReviewOperationsData()
        gap_report = _load_json(self.qa_dir / "PHASE3_GAP_REPORT.json")
        coverage_map = _load_json(self.qa_dir / "QA_COVERAGE_MAP.json")

        if gap_report or coverage_map:
            data.has_data = True

        ob = (gap_report or {}).get("orphan_breakdown") or (coverage_map or {}).get("governance", {}).get("orphan_breakdown") or {}
        data.orphan_count = ob.get("review_candidates", (gap_report or {}).get("orphan_count", 0))
        data.treat_as = ob.get("treat_as", "review_candidate")

        data.batches = [
            ReviewBatchItem(
                id="orphan_review",
                label="Orphan Review Backlog",
                count=data.orphan_count,
                treat_as=data.treat_as,
                description="Tests zur manuellen Prüfung (catalog_bound fehlt).",
            ),
        ]
        return data

    def load_audit_operations(self) -> AuditOperationsData:
        """Lädt Audit-Follow-ups aus AUDIT_REPORT.md."""
        data = AuditOperationsData()
        path = self.project_root / "AUDIT_REPORT.md"
        text = _load_text(path)
        if not text:
            return data

        data.has_data = True
        current_category = ""

        for line in text.splitlines():
            if "### 4.1 Kritisch" in line:
                current_category = "kritisch"
            elif "### 4.2 Mittel" in line:
                current_category = "mittel"
            elif "### 4.3 Niedrig" in line:
                current_category = "niedrig"
            elif current_category and line.strip().startswith("|") and "---" not in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 5 and parts[1].startswith("`") and parts[1].endswith("`"):
                    source = parts[1].strip("`")
                    loc = parts[2]
                    desc = parts[3]
                    if source != "-" and "Keine" not in desc:
                        data.items.append(AuditItem(
                            category=current_category,
                            source=source,
                            description=desc,
                            location=loc,
                        ))

        for item in data.items:
            data.by_category[item.category] = data.by_category.get(item.category, 0) + 1
        return data

    def load_guided_workflows(self) -> GuidedWorkflowData:
        """Liefert die verfügbaren Guided-Workflow-Einstiege."""
        return GuidedWorkflowData(entries=[
            WorkflowEntry(
                id="orphan_review",
                label="Orphan Review öffnen",
                description="Review-Backlog mit Tests zur Prüfung.",
                target="review_ops",
            ),
            WorkflowEntry(
                id="qa_verification",
                label="QA Verification prüfen",
                description="Verifikationsstatus und Artefakte.",
                target="qa_ops",
            ),
            WorkflowEntry(
                id="incident_status",
                label="Incident-Status prüfen",
                description="Incidents, Bindings, Replay-Readiness.",
                target="incident_ops",
            ),
            WorkflowEntry(
                id="audit_followup",
                label="Audit Follow-up öffnen",
                description="Technische Schulden und Empfehlungen.",
                target="audit_ops",
            ),
        ])
