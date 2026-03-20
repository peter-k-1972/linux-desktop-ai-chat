# QA Documentation Restructuring – Implementation Report

**Date:** 2026-03-16  
**Status:** Completed

---

## 1. Summary

The docs/qa folder has been restructured from a flat mixed layout into a structured QA documentation system.

---

## 2. Folders Created

| Folder | Purpose |
|--------|---------|
| `architecture/` | QA system design (autopilot, coverage, inventory, incident_replay, graphs) |
| `architecture/autopilot/` | Autopilot v2/v3 architecture |
| `architecture/coverage/` | Coverage Map architecture |
| `architecture/inventory/` | Test Inventory architecture |
| `architecture/incident_replay/` | Incident Replay architecture |
| `architecture/graphs/` | QA Architecture Graph, Dependency Graph |
| `governance/` | Standards, rules, schemas |
| `governance/schemas/` | JSON schemas (coverage_map, test_inventory) |
| `governance/incident_schemas/` | Incident YAML/JSON schemas, field standards |
| `reports/` | Human-authored reports, reviews |
| `artifacts/` | Machine-generated output |
| `artifacts/dashboards/` | MD dashboards |
| `artifacts/json/` | JSON snapshots |
| `artifacts/csv/` | CSV exports |
| `config/` | Active configuration (Phase 3 configs) |
| `plans/` | Active QA plans |
| `history/` | Archived phase documents |
| `history/phase3/` | Phase 3 design docs |

---

## 3. Files Moved

### Architecture
- QA_AUTOPILOT_V2_ARCHITECTURE.md, QA_AUTOPILOT_V3_ARCHITECTURE.md, QA_AUTOPILOT_V2_PILOT_CONSTELLATIONS.md → `architecture/autopilot/`
- QA_COVERAGE_MAP_ARCHITECTURE.md, QA_COVERAGE_MAP_GENERATOR.md → `architecture/coverage/`
- QA_TEST_INVENTORY_ARCHITECTURE.md, QA_TEST_INVENTORY_README.md → `architecture/inventory/`
- QA_INCIDENT_REPLAY_ARCHITECTURE.md, QA_INCIDENT_INTEGRATION.md, QA_INCIDENT_REPLAY_INTEGRATION.md → `architecture/incident_replay/`
- QA_ARCHITECTURE_GRAPH.*, QA_DEPENDENCY_GRAPH.* → `architecture/graphs/`

### Governance
- TEST_GOVERNANCE_RULES.md, CI_TEST_LEVELS.md, ARCHITECTURE_DRIFT_SENTINELS.md, REGRESSION_CATALOG.md → `governance/`
- schemas/*.json → `governance/schemas/`
- incidents/_schema/* → `governance/incident_schemas/`
- QA_INCIDENT_SCHEMA.md, QA_REPLAY_SCHEMA.md, QA_INCIDENT_ARTIFACT_STANDARD.md, QA_INCIDENT_LIFECYCLE.md, QA_INCIDENT_REPLAY_SCHEMA.json → `governance/incident_schemas/`

### Reports
- QA_RISK_RADAR_ITERATION1_REPORT.md, QA_COCKPIT_ITERATION2_REPORT.md, QA_LEVEL3_REPORT.md, QA_TEST_INVENTORY_REVIEW.md, QA_COVERAGE_MAP_REVIEW.md, QA_AUTOPILOT_V3_ARCHITECTURE_REVIEW.md, QA_AUTOPILOT_V3_GOVERNANCE_REVIEW.md, QA_AUTOPILOT_V3_VERIFICATION_REPORT.md, QA_AUTOPILOT_V3_FINAL_RELEASE_CHECK.md, QA_COVERAGE_MAP_MAPPING_RULES.md, QA_TEST_INVENTORY_MAPPING_RULES.md, QA_COVERAGE_MAP_PHASE2_PROMPTS.md, UX_DEFECTS_QA_GAP_ANALYSIS.md, QA_AUTOPILOT_V3_CHANGE_SUMMARY.md → `reports/`

### Artifacts
- QA_STATUS.md, QA_CONTROL_CENTER.md, QA_STABILITY_INDEX.md, QA_RISK_RADAR.md, QA_PRIORITY_SCORE.md, QA_AUTOPILOT.md, QA_HEATMAP.md, QA_EVOLUTION_MAP.md, QA_LEVEL3_COVERAGE_MAP.md, QA_ANOMALY_DETECTION.md, QA_SELF_HEALING.md, PHASE3_GAP_REPORT.md → `artifacts/dashboards/`
- All *.json → `artifacts/json/`
- QA_HEATMAP.csv → `artifacts/csv/`

### Config
- phase3_ci_config.json, phase3_orphan_governance.json, phase3_gap_prioritization.json, phase3_failure_class_hints.json, phase3_guard_type_overrides.json, phase3_ci_build_order.md → `config/`

### Plans
- CHAOS_QA_PLAN.md, QA_AUTOPILOT_V3_SANIERUNGSPLAN.md → `plans/`

### History
- PHASE3_*.md (design docs) → `history/phase3/`
- QA_DOCUMENTATION_STRUCTURE_PROPOSAL.md → `history/`

---

## 4. Files Kept at Root

| File | Purpose |
|------|---------|
| README.md | QA documentation landing page |
| 00_map_of_qa_system.md | Visual map of docs/qa structure |
| RESTRUCTURING_IMPLEMENTATION_REPORT.md | This report |

---

## 5. Scripts Updated

- `scripts/qa/qa_paths.py` – New central path definitions
- `scripts/qa/qa_cockpit.py` – Uses ARTIFACTS_DASHBOARDS, ARTIFACTS_JSON
- `scripts/qa/checks.py` – Uses ARTIFACTS_DASHBOARDS, GOVERNANCE
- `scripts/qa/build_test_inventory.py` – Uses ARTIFACTS_JSON, GOVERNANCE
- `scripts/qa/build_coverage_map.py` – Uses ARTIFACTS_JSON
- `scripts/qa/coverage_map_loader.py` – Loads from artifacts/json/
- `scripts/qa/generate_gap_report.py` – Writes to artifacts/
- `scripts/qa/generate_qa_graph.py` – Reads from artifacts/dashboards, governance; writes to architecture/graphs
- `scripts/qa/update_control_center.py` – Uses ARTIFACTS_JSON, INCIDENTS, FEEDBACK_LOOP
- `scripts/qa/update_risk_radar.py` – Uses ARTIFACTS_JSON, ARTIFACTS_DASHBOARDS, INCIDENTS, FEEDBACK_LOOP
- `scripts/qa/update_priority_scores.py` – Uses ARTIFACTS_JSON, INCIDENTS, FEEDBACK_LOOP
- `scripts/qa/feedback_loop/loader.py` – Loads from artifacts/json, artifacts/dashboards
- `scripts/qa/semantic_enrichment.py` – Config from config/
- `scripts/qa/gap_prioritization.py` – Config from config/
- `scripts/qa/coverage_map_rules.py` – Config from config/

---

## 6. Config Updated

- `docs/qa/config/phase3_ci_config.json` – output_paths updated

---

## 7. Validation Results

| Check | Status |
|-------|--------|
| docs/qa navigable | ✅ README.md, 00_map_of_qa_system.md at root |
| Root no longer overloaded | ✅ Only 3 files at root |
| QA cockpit runs | ✅ Generates QA_STATUS.md |
| build_test_inventory runs | ✅ Generates QA_TEST_INVENTORY.json |
| build_coverage_map runs | ✅ Generates QA_COVERAGE_MAP.json |
| generate_gap_report runs | ✅ Generates PHASE3_GAP_REPORT.md/.json |
| No QA artifacts lost | ✅ All 121 files accounted for |
| Incident materials intact | ✅ incidents/ structure preserved |
| Schemas/templates discoverable | ✅ governance/incident_schemas/, incidents/templates/ |

---

## 8. Unresolved Issues

1. **Remaining scripts** – Some generate scripts (generate_qa_autopilot, generate_qa_heatmap, generate_qa_stability_index, generate_qa_priority_score, generate_qa_self_healing, generate_qa_anomaly_detection, generate_qa_control_center, generate_autopilot_v3, generate_autopilot_v2, generate_knowledge_graph, update_test_strategy, enrich_replay_binding, generate_qa_dependency_graph) may still use old paths. They have fallback logic in the feedback_loop loader. Update these when run.

2. **Cross-document links** – Some docs in docs/ (e.g. docs/05_developer_guide/QA_GOVERNANCE_IMPLEMENTATION.md, docs/TRACE_MAP.md, docs/FEATURE_REGISTRY.md) reference old docs/qa paths. Update as needed.

3. **App/QA adapters** – If app/qa reads from docs/qa paths, those may need updating (see docs/04_architecture/COMMAND_CENTER_ARCHITECTURE.md).
