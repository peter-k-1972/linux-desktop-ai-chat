"""
QA Autopilot v3 – Lader für Input-Artefakte.

Reused FeedbackLoopInputs aus dem Feedback-Loop.
"""

from __future__ import annotations

from pathlib import Path

from scripts.qa.feedback_loop import FeedbackLoopInputs, load_feedback_inputs_from_paths


def load_autopilot_v3_inputs(
    incident_index_path: Path | None = None,
    analytics_path: Path | None = None,
    autopilot_path: Path | None = None,
    control_center_path: Path | None = None,
    priority_score_path: Path | None = None,
) -> FeedbackLoopInputs:
    """
    Lädt alle Inputs für Autopilot v3.
    Nutzt load_feedback_inputs_from_paths aus dem Feedback-Loop.
    """
    return load_feedback_inputs_from_paths(
        incident_index_path=incident_index_path,
        analytics_path=analytics_path,
        autopilot_path=autopilot_path,
        control_center_path=control_center_path,
        priority_score_path=priority_score_path,
    )
