"""
QA Test Strategy Engine – Lader für Input-Artefakte.

Lädt QA_AUTOPILOT_V3.json und optional QA_CONTROL_CENTER.json für Pilot-Tracking.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .utils import load_json


@dataclass(frozen=False)
class TestStrategyInputs:
    """Input-Daten für die Test Strategy Engine."""
    autopilot_v3: dict[str, Any] | None
    control_center: dict[str, Any] | None
    loaded_sources: list[str]


def _to_relative_source(path: Path, project_root: Path) -> str:
    """Konvertiert Pfad zu relativem Source-String (deterministisch)."""
    try:
        rel = path.resolve().relative_to(project_root.resolve())
        return str(rel).replace("\\", "/")
    except ValueError:
        return str(path)


def load_test_strategy_inputs(
    autopilot_v3_path: Path | None = None,
    control_center_path: Path | None = None,
) -> TestStrategyInputs:
    """
    Lädt alle Inputs für die Test Strategy Engine.
    Primär: QA_AUTOPILOT_V3.json (Pflicht).
    Optional: QA_CONTROL_CENTER.json für Pilot-Tracking.
    """
    from .utils import get_project_root

    project_root = get_project_root()
    sources: list[str] = []
    autopilot_v3: dict[str, Any] | None = None
    control_center: dict[str, Any] | None = None

    if autopilot_v3_path:
        autopilot_v3 = load_json(autopilot_v3_path)
        if autopilot_v3:
            sources.append(_to_relative_source(autopilot_v3_path, project_root))

    if control_center_path:
        control_center = load_json(control_center_path)
        if control_center:
            sources.append(_to_relative_source(control_center_path, project_root))

    return TestStrategyInputs(
        autopilot_v3=autopilot_v3,
        control_center=control_center,
        loaded_sources=sources,
    )
