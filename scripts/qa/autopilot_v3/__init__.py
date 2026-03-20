"""
QA Autopilot v3 – Systematische Erkennung fehlender Testabsicherung.

Erkennt Testlücken, Guard-Lücken und Translation-Gaps.
Empfiehlt priorisierte Test-Backlog-Einträge.
Schreibt NICHT: Tests, Incidents, Replay-Daten, Regression Catalog, Produktcode.
"""

from __future__ import annotations

from .loader import load_autopilot_v3_inputs
from .models import (
    AutopilotV3Output,
    GuardGapFinding,
    RecommendedTestBacklogItem,
    TestGapFinding,
    TranslationGapFinding,
)
from .projections import run_autopilot_v3_projections
from .traces import build_autopilot_v3_trace

__all__ = [
    "load_autopilot_v3_inputs",
    "run_autopilot_v3_projections",
    "build_autopilot_v3_trace",
    "AutopilotV3Output",
    "TestGapFinding",
    "GuardGapFinding",
    "TranslationGapFinding",
    "RecommendedTestBacklogItem",
]
