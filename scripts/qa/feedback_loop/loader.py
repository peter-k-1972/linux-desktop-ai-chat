"""
QA Feedback Loop – Lader für Input-Artefakte.

Lädt incidents/index.json, incidents/analytics.json, QA_AUTOPILOT_V2.json
und optionale Governance-Artefakte (QA_CONTROL_CENTER, QA_PRIORITY_SCORE, QA_RISK_RADAR).
Robust gegen fehlende Dateien.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .utils import get_docs_qa_dir, get_incidents_dir, load_json


@dataclass
class FeedbackLoopInputs:
    """Geladene Input-Daten für den Feedback Loop."""
    incident_index: dict[str, Any] | None = None
    analytics: dict[str, Any] | None = None
    autopilot_v2: dict[str, Any] | None = None
    control_center: dict[str, Any] | None = None
    priority_score: dict[str, Any] | None = None
    risk_radar_raw: str | None = None  # Markdown
    base_path: Path = field(default_factory=Path)
    loaded_sources: list[str] = field(default_factory=list)
    missing_sources: list[str] = field(default_factory=list)


def load_feedback_inputs(
    base_path: Path | None = None,
    incidents_dir: Path | None = None,
) -> FeedbackLoopInputs:
    """
    Lädt alle Feedback-Loop-Inputs.
    base_path: Projekt-Root (dann docs/qa) oder direkt docs/qa.
    incidents_dir: Falls abweichend, z.B. docs/qa/incidents.
    """
    if base_path and (base_path / "artifacts" / "json" / "QA_AUTOPILOT_V2.json").exists():
        docs_qa = base_path
    elif base_path and (base_path / "QA_AUTOPILOT_V2.json").exists():
        docs_qa = base_path  # Legacy flat layout
    else:
        docs_qa = get_docs_qa_dir(base_path)
    inc_dir = incidents_dir or (docs_qa / "incidents")
    artifacts_json = docs_qa / "artifacts" / "json"
    artifacts_dashboards = docs_qa / "artifacts" / "dashboards"

    result = FeedbackLoopInputs(base_path=docs_qa)
    sources: list[str] = []
    missing: list[str] = []

    # Pflicht-Inputs
    idx_path = inc_dir / "index.json"
    idx = load_json(idx_path)
    if idx:
        result.incident_index = idx
        sources.append("incidents/index.json")
    else:
        missing.append("incidents/index.json")

    analytics_path = inc_dir / "analytics.json"
    analytics_data = load_json(analytics_path)
    if analytics_data:
        result.analytics = analytics_data
        sources.append("incidents/analytics.json")
    else:
        missing.append("incidents/analytics.json")

    autopilot_path = artifacts_json / "QA_AUTOPILOT_V2.json"
    if not autopilot_path.exists():
        autopilot_path = docs_qa / "QA_AUTOPILOT_V2.json"  # Legacy
    ap = load_json(autopilot_path)
    if ap:
        result.autopilot_v2 = ap
        sources.append("QA_AUTOPILOT_V2.json")
    else:
        missing.append("QA_AUTOPILOT_V2.json")

    # Optionale Governance-Artefakte
    cc_path = artifacts_json / "QA_CONTROL_CENTER.json"
    if not cc_path.exists():
        cc_path = docs_qa / "QA_CONTROL_CENTER.json"  # Legacy
    cc = load_json(cc_path)
    if cc:
        result.control_center = cc
        sources.append("QA_CONTROL_CENTER.json")
    else:
        missing.append("QA_CONTROL_CENTER.json (optional)")

    ps_path = artifacts_json / "QA_PRIORITY_SCORE.json"
    if not ps_path.exists():
        ps_path = docs_qa / "QA_PRIORITY_SCORE.json"  # Legacy
    ps = load_json(ps_path)
    if ps:
        result.priority_score = ps
        sources.append("QA_PRIORITY_SCORE.json")
    else:
        missing.append("QA_PRIORITY_SCORE.json (optional)")

    rr_path = artifacts_dashboards / "QA_RISK_RADAR.md"
    if not rr_path.exists():
        rr_path = docs_qa / "QA_RISK_RADAR.md"  # Legacy
    if rr_path.exists():
        try:
            result.risk_radar_raw = rr_path.read_text(encoding="utf-8")
            sources.append("QA_RISK_RADAR.md")
        except OSError:
            missing.append("QA_RISK_RADAR.md (optional)")
    else:
        missing.append("QA_RISK_RADAR.md (optional)")

    result.loaded_sources = sources
    result.missing_sources = missing
    return result


def load_feedback_inputs_from_paths(
    incident_index_path: Path | None = None,
    analytics_path: Path | None = None,
    autopilot_path: Path | None = None,
    control_center_path: Path | None = None,
    priority_score_path: Path | None = None,
) -> FeedbackLoopInputs:
    """
    Lädt Feedback-Loop-Inputs aus expliziten Pfaden.
    Für update_control_center und andere Generatoren mit CLI-Pfaden.
    """
    result = FeedbackLoopInputs()
    sources: list[str] = []
    missing: list[str] = []

    def _load(p: Path | None, name: str) -> dict[str, Any] | None:
        if not p:
            return None
        data = load_json(p)
        if data:
            sources.append(name)
            return data
        missing.append(name)
        return None

    result.incident_index = _load(incident_index_path, "incidents/index.json")
    result.analytics = _load(analytics_path, "incidents/analytics.json")
    result.autopilot_v2 = _load(autopilot_path, "QA_AUTOPILOT_V2.json")
    result.control_center = _load(control_center_path, "QA_CONTROL_CENTER.json")
    result.priority_score = _load(priority_score_path, "QA_PRIORITY_SCORE.json")

    result.loaded_sources = sources
    result.missing_sources = missing
    return result
