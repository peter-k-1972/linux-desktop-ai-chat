# QA Gap Report (Phase 3)

*Generiert aus 2026-03-16T14:22:19Z*

## Blockierende Gaps

- Keine (Phase 3: Gaps sind nicht blockierend)

## Warnungen (nicht blockierend)

| Gap-Typ | Anzahl | Schwere |
|---------|--------|---------|
| failure_class_uncovered | 2 | medium |
| regression_requirement_unbound | 2 | medium |
| replay_unbound | 2 | low |
| autopilot_recommendation_uncovered | 1 | low |
| orphan_review_backlog | 104 | low |

## Priorisierte Gaps (Top 20)

| # | Gap | Severity | Score | Faktoren |
|---|-----|----------|-------|----------|
| 1 | GAP-RR-002 (INC-20260315-002) | critical | 75 | incident, incident_severity_high, critical_subsystem |
| 2 | GAP-RB-001 (INC-20260315-002) | critical | 75 | incident, incident_severity_high, critical_subsystem |
| 3 | GAP-RR-001 (INC-20260315-001) | high | 65 | incident, critical_subsystem |
| 4 | GAP-RB-002 (INC-20260315-001) | high | 65 | incident, critical_subsystem |
| 5 | RTB-001 | high | 50 | autopilot, critical_subsystem |
| 6 | GAP-SB-ui_state_drift (ui_state_drift) | high | 45 | strategy |
| 7 | GAP-FC-008 (rag_silent_failure) | medium | 20 | - |
| 8 | GAP-FC-009 (request_context_loss) | medium | 20 | - |
| 9 | GAP-SB-debug_false_truth (debug_false_truth) | medium | 20 | - |
| 10 | GAP-SB-degraded_mode_failure (degraded_mode_failure) | medium | 20 | - |
| 11 | GAP-SB-rag_silent_failure (rag_silent_failure) | medium | 20 | - |
| 12 | GAP-SB-request_context_loss (request_context_loss) | medium | 20 | - |

## Details

- **GAP-RR-002:** Add regression_test to bindings.json; create test if missing
- **GAP-RB-001:** Set regression_catalog.regression_test in bindings.json
- **GAP-RR-001:** Add regression_test to bindings.json; create test if missing
- **GAP-RB-002:** Set regression_catalog.regression_test in bindings.json
- **GAP-FC-008:** Add test to failure_modes/ or appropriate domain; register in REGRESSION_CATALOG
- **GAP-FC-009:** Add test to failure_modes/ or appropriate domain; register in REGRESSION_CATALOG
