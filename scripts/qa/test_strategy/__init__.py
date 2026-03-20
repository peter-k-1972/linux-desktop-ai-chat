"""
QA Test Strategy Engine – Governance-Komponente.

Übersetzt Autopilot-v3-Erkenntnisse in eine strukturierte QA-Teststrategie.
Definiert, priorisiert und empfiehlt – schreibt NICHT: Tests, Incidents, Regression Catalog, Replay.
"""

from __future__ import annotations

from .loader import load_test_strategy_inputs
from .models import TestStrategyOutput
from .projections import run_test_strategy_projections
from .traces import build_test_strategy_trace

__all__ = [
    "load_test_strategy_inputs",
    "run_test_strategy_projections",
    "build_test_strategy_trace",
    "TestStrategyOutput",
]
