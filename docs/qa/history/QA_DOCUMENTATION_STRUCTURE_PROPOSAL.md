# QA Documentation Structure Proposal

**Project:** Linux Desktop Chat  
**Date:** 2026-03-16  
**Role:** Senior QA Documentation Architect / Repository Information Architect  
**Status:** Proposal – Do not implement yet

---

## Executive Summary

The `docs/qa/` area contains **121 files** across architecture docs, reports, generated artifacts, schemas, governance rules, incident data, feedback traces, and historical Phase 3 materials. These are currently mixed in a flat or loosely grouped layout, which reduces discoverability and blurs the line between active reference, generated output, and archival material.

This proposal defines a **target folder structure** that:

1. **Separates by purpose** – architecture, standards, reports, artifacts, incidents, feedback, governance, history
2. **Improves discoverability** – clear entry points and predictable locations
3. **Establishes source-of-truth rules** – where each document type belongs
4. **Enables stable migration** – rules for future additions and archival

---

## 1. Proposed docs/qa Hierarchy

```
docs/qa/
├── README.md                          # Root anchor – QA overview, navigation
├── MAP_OF_QA_DOCS.md                  # Optional: visual map of docs/qa
│
├── architecture/                      # QA system design, component architecture
│   ├── README.md
│   ├── autopilot/
│   │   ├── QA_AUTOPILOT_V2_ARCHITECTURE.md
│   │   ├── QA_AUTOPILOT_V3_ARCHITECTURE.md
│   │   └── QA_AUTOPILOT_V2_PILOT_CONSTELLATIONS.md
│   ├── coverage/
│   │   ├── QA_COVERAGE_MAP_ARCHITECTURE.md
│   │   └── QA_COVERAGE_MAP_GENERATOR.md
│   ├── inventory/
│   │   └── QA_TEST_INVENTORY_ARCHITECTURE.md
│   ├── incident_replay/
│   │   ├── QA_INCIDENT_REPLAY_ARCHITECTURE.md
│   │   ├── QA_INCIDENT_INTEGRATION.md
│   │   └── QA_INCIDENT_REPLAY_INTEGRATION.md
│   └── graphs/
│       ├── QA_ARCHITECTURE_GRAPH.md
│       ├── QA_ARCHITECTURE_GRAPH.svg
│       ├── QA_ARCHITECTURE_GRAPH.dot
│       ├── QA_ARCHITECTURE_GRAPH.mmd
│       ├── QA_DEPENDENCY_GRAPH.md
│       ├── QA_DEPENDENCY_GRAPH.svg
│       ├── QA_DEPENDENCY_GRAPH.dot
│       └── QA_DEPENDENCY_GRAPH.mmd
│
├── governance/                        # Standards, rules, schemas
│   ├── README.md
│   ├── TEST_GOVERNANCE_RULES.md
│   ├── CI_TEST_LEVELS.md
│   ├── ARCHITECTURE_DRIFT_SENTINELS.md
│   ├── REGRESSION_CATALOG.md
│   ├── schemas/
│   │   ├── qa_coverage_map.schema.json
│   │   ├── qa_test_inventory.schema.json
│   │   └── README.md
│   └── incident_schemas/
│       ├── QA_INCIDENT_SCHEMA.md
│       ├── QA_REPLAY_SCHEMA.md
│       ├── QA_INCIDENT_ARTIFACT_STANDARD.md
│       ├── QA_INCIDENT_LIFECYCLE.md
│       ├── incident.schema.yaml
│       ├── bindings.schema.json
│       ├── replay.schema.yaml
│       ├── INCIDENT_YAML_FIELD_STANDARD.md
│       ├── BINDINGS_JSON_FIELD_STANDARD.md
│       ├── REPLAY_YAML_FIELD_STANDARD.md
│       ├── QA_INCIDENT_REGISTRY.md
│       ├── QA_INCIDENT_ANALYTICS.md
│       ├── QA_VALIDATION_STANDARD.md
│       ├── QA_INCIDENT_REPLAY_LIFECYCLE.md
│       └── QA_INCIDENT_SCRIPTS_ARCHITECTURE.md
│
├── reports/                           # Human-authored reports, reviews, analyses
│   ├── README.md
│   ├── QA_RISK_RADAR_ITERATION1_REPORT.md
│   ├── QA_COCKPIT_ITERATION2_REPORT.md
│   ├── QA_LEVEL3_REPORT.md
│   ├── QA_TEST_INVENTORY_REVIEW.md
│   ├── QA_COVERAGE_MAP_REVIEW.md
│   ├── QA_AUTOPILOT_V3_ARCHITECTURE_REVIEW.md
│   ├── QA_AUTOPILOT_V3_GOVERNANCE_REVIEW.md
│   ├── QA_AUTOPILOT_V3_VERIFICATION_REPORT.md
│   ├── QA_AUTOPILOT_V3_FINAL_RELEASE_CHECK.md
│   ├── QA_COVERAGE_MAP_MAPPING_RULES.md
│   ├── QA_TEST_INVENTORY_MAPPING_RULES.md
│   ├── QA_COVERAGE_MAP_PHASE2_PROMPTS.md
│   ├── UX_DEFECTS_QA_GAP_ANALYSIS.md
│   └── QA_AUTOPILOT_V3_CHANGE_SUMMARY.md
│
├── artifacts/                         # Machine-generated JSON, CSV, SVG (current snapshots)
│   ├── README.md
│   ├── dashboards/                    # Human-readable MD dashboards (generated)
│   │   ├── QA_STATUS.md
│   │   ├── QA_CONTROL_CENTER.md
│   │   ├── QA_STABILITY_INDEX.md
│   │   ├── QA_RISK_RADAR.md
│   │   ├── QA_PRIORITY_SCORE.md
│   │   ├── QA_AUTOPILOT.md
│   │   ├── QA_HEATMAP.md
│   │   ├── QA_EVOLUTION_MAP.md
│   │   ├── QA_LEVEL3_COVERAGE_MAP.md
│   │   ├── QA_ANOMALY_DETECTION.md
│   │   └── QA_SELF_HEALING.md
│   ├── json/                          # Machine-readable JSON snapshots
│   │   ├── QA_STATUS.json
│   │   ├── QA_TEST_INVENTORY.json
│   │   ├── QA_COVERAGE_MAP.json
│   │   ├── QA_STABILITY_INDEX.json
│   │   ├── QA_HEATMAP.json
│   │   ├── QA_KNOWLEDGE_GRAPH.json
│   │   ├── QA_TEST_STRATEGY.json
│   │   ├── QA_AUTOPILOT.json
│   │   ├── QA_AUTOPILOT_V2.json
│   │   ├── QA_AUTOPILOT_V3.json
│   │   ├── QA_CONTROL_CENTER.json
│   │   ├── QA_PRIORITY_SCORE.json
│   │   ├── QA_RISK_RADAR.json
│   │   ├── QA_ANOMALY_DETECTION.json
│   │   ├── QA_SELF_HEALING.json
│   │   ├── FEEDBACK_LOOP_REPORT.json
│   │   ├── PHASE3_GAP_REPORT.json
│   │   └── QA_STABILITY_HISTORY.json
│   └── csv/
│       └── QA_HEATMAP.csv
│
├── incidents/                         # Incident registry, cases, templates (keep structure)
│   ├── INC-20260315-001/
│   │   ├── incident.yaml
│   │   └── bindings.json
│   ├── INC-20260315-002/
│   │   ├── incident.yaml
│   │   └── bindings.json
│   ├── templates/
│   │   ├── README.md
│   │   ├── incident.template.yaml
│   │   ├── replay.template.yaml
│   │   ├── bindings.template.json
│   │   └── notes.template.md
│   ├── index.json                     # Generated registry
│   ├── analytics.json                # Generated analytics
│   └── QA_INCIDENT_PILOT_ITERATION.md
│
├── feedback_loop/                     # Feedback loop traces (keep structure)
│   ├── README.md
│   ├── autopilot_v3_trace.json
│   ├── knowledge_graph_trace.json
│   ├── test_strategy_trace.json
│   ├── risk_radar_feedback_trace.json
│   ├── priority_score_feedback_trace.json
│   └── control_center_feedback_trace.json
│
├── config/                            # Active configuration (Phase 3 configs in use)
│   ├── README.md
│   ├── phase3_ci_config.json
│   ├── phase3_orphan_governance.json
│   ├── phase3_gap_prioritization.json
│   ├── phase3_failure_class_hints.json
│   ├── phase3_guard_type_overrides.json
│   └── phase3_ci_build_order.md
│
├── plans/                             # Active plans (not yet historical)
│   ├── CHAOS_QA_PLAN.md
│   └── QA_AUTOPILOT_V3_SANIERUNGSPLAN.md
│
└── history/                           # Archived phase documents, superseded material
    ├── README.md
    └── phase3/
        ├── PHASE3_SUMMARY.md
        ├── PHASE3_IMPLEMENTATION_REPORT.md
        ├── PHASE3_GAP_REPORT.md
        ├── PHASE3_GAP_PRIORITIZATION.md
        ├── PHASE3_ORPHAN_REVIEW_GOVERNANCE.md
        ├── PHASE3_SEMANTIC_ENRICHMENT_PLAN.md
        ├── PHASE3_CI_INTEGRATION_PLAN.md
        ├── PHASE3_REPLAY_BINDING_ARCHITECTURE.md
        ├── PHASE3_TECHNICAL_DOCS.md
        ├── PHASE3_VERIFICATION_REVIEW.md
        └── PHASE3_RESTRISIKEN_REPORT.md
```

---

## 2. Folder Purposes

| Folder | Purpose | Audience |
|--------|---------|----------|
| **architecture/** | QA system design, component architecture, how generators work | Architects, developers extending QA |
| **governance/** | Test rules, CI levels, drift sentinels, regression catalog, schemas, incident standards | Developers, QA, CI maintainers |
| **reports/** | Human-authored reports, reviews, iteration reports, gap analyses | QA leads, stakeholders |
| **artifacts/** | Machine-generated dashboards (MD), JSON snapshots, CSV, graphs | Scripts, dashboards, CI |
| **incidents/** | Incident registry, case data, templates | Incident workflow, replay system |
| **feedback_loop/** | Trace files from feedback loop runs | Debugging, audit |
| **config/** | Active configuration files (orphan governance, gap prioritization, CI) | Scripts, CI |
| **plans/** | Active QA plans (chaos, sanitization) | QA planning |
| **history/** | Archived phase documents, superseded designs | Reference, audit trail |

---

## 3. File Classification Strategy

### 3.1 Classification Matrix

| Category | Criteria | Target Location | Examples |
|----------|----------|-----------------|----------|
| **Active reference** | Architecture, design, how things work | `architecture/` | QA_AUTOPILOT_V3_ARCHITECTURE.md |
| **Governance / standards** | Rules, schemas, field standards | `governance/` | TEST_GOVERNANCE_RULES.md, incident.schema.yaml |
| **Reports** | Human-authored reviews, iteration reports | `reports/` | QA_RISK_RADAR_ITERATION1_REPORT.md |
| **Generated dashboards** | MD generated by scripts | `artifacts/dashboards/` | QA_STATUS.md, QA_HEATMAP.md |
| **Generated JSON/CSV** | Machine-readable snapshots | `artifacts/json/`, `artifacts/csv/` | QA_COVERAGE_MAP.json |
| **Generated graphs** | SVG, DOT, MMD | `architecture/graphs/` or `artifacts/graphs/` | QA_ARCHITECTURE_GRAPH.svg |
| **Incident data** | incident.yaml, bindings.json, index, analytics | `incidents/` | INC-20260315-001/incident.yaml |
| **Feedback traces** | Trace JSON from feedback loop | `feedback_loop/` | autopilot_v3_trace.json |
| **Config** | Active config (JSON, MD) for scripts | `config/` | phase3_ci_config.json |
| **Plans** | Active plans | `plans/` | CHAOS_QA_PLAN.md |
| **Historical** | Phase docs, superseded designs | `history/phase3/` | PHASE3_SUMMARY.md |

### 3.2 Special Cases

| File | Classification | Rationale |
|------|----------------|-----------|
| **QA_INCIDENT_REPLAY_SCHEMA.json** | governance/incident_schemas/ | Schema definition, not generated snapshot |
| **incidents/_schema/** | Merge into governance/incident_schemas/ | All incident-related schemas in one place |
| **schemas/** (qa_coverage_map, qa_test_inventory) | governance/schemas/ | JSON schemas for validation |
| **QA_EVOLUTION_MAP.md** | artifacts/dashboards/ | Generated by scripts (from Risk Radar, Regression Catalog) |
| **QA_DEPENDENCY_GRAPH.md** | architecture/graphs/ | Human-readable doc wrapping generated graph |

---

## 4. Source-of-Truth Rules

| Document Type | Location | Rule |
|---------------|----------|------|
| **Architecture docs** | `architecture/` | One subfolder per major component (autopilot, coverage, inventory, incident_replay, graphs) |
| **Generated JSON/CSV** | `artifacts/json/`, `artifacts/csv/` | Scripts must write here; no hand-editing |
| **Generated MD dashboards** | `artifacts/dashboards/` | Scripts generate; human edits discouraged |
| **Reports** | `reports/` | Human-authored; dated; iteration reports stay |
| **Schemas** | `governance/schemas/` (JSON), `governance/incident_schemas/` (YAML/JSON) | Single source of truth for validation |
| **Phase/history docs** | `history/phaseN/` | Archived when phase is complete; configs in use stay in `config/` |
| **Incident cases** | `incidents/INC-YYYYMMDD-NNN/` | Per-incident folder; index.json and analytics.json generated |
| **Config** | `config/` | Active config only; historical config → `history/` |

---

## 5. Root-Anchor Documents

### 5.1 docs/qa/README.md (Required)

**Purpose:** QA documentation landing page.

**Contents:**
- What is docs/qa? (QA documentation hub for Linux Desktop Chat)
- Quick links: QA Status, Control Center, Risk Radar, Autopilot
- Folder overview (table: folder → purpose → key files)
- How to run QA scripts (cockpit, feedback loop, inventory, coverage map)
- Where to find: architecture, governance, reports, artifacts, incidents, feedback, config, history

### 5.2 MAP_OF_QA_DOCS.md (Optional)

**Purpose:** Visual map of docs/qa structure.

**Contents:**
- Mermaid or ASCII diagram of folder hierarchy
- Flow: scripts → artifacts; incidents → analytics; feedback loop → traces
- Cross-references to main docs (00_map_of_the_system.md, docs/README.md)

---

## 6. Migration Rules

### 6.1 Script Path Updates

All scripts that read/write `docs/qa/` paths must be updated to the new structure. Key scripts:

| Script | Current Paths | New Paths |
|--------|---------------|-----------|
| `build_test_inventory.py` | docs/qa/QA_TEST_INVENTORY.json | docs/qa/artifacts/json/QA_TEST_INVENTORY.json |
| `build_coverage_map.py` | docs/qa/QA_COVERAGE_MAP.json | docs/qa/artifacts/json/QA_COVERAGE_MAP.json |
| `qa_cockpit.py` | docs/qa/QA_STATUS.md | docs/qa/artifacts/dashboards/QA_STATUS.md |
| `generate_qa_*.py` | docs/qa/*.md, docs/qa/*.json | docs/qa/artifacts/ |
| `update_control_center.py` | docs/qa/QA_CONTROL_CENTER.json | docs/qa/artifacts/json/ |
| `generate_gap_report.py` | docs/qa/PHASE3_GAP_REPORT.* | docs/qa/artifacts/json/ or docs/qa/reports/ |
| `feedback_loop/loader.py` | docs/qa/ | docs/qa/ (base unchanged; subpaths may change) |
| `incidents/build_registry.py` | docs/qa/incidents/index.json | docs/qa/incidents/index.json (unchanged) |
| `incidents/analyze_incidents.py` | docs/qa/incidents/analytics.json | docs/qa/incidents/analytics.json (unchanged) |

**Recommendation:** Introduce a `docs/qa/paths.py` or config file that defines all paths, so scripts import from a single source. This reduces migration risk and makes future moves easier.

### 6.2 Internal Links

Many documents reference each other (e.g. `[QA_RISK_RADAR.md](QA_RISK_RADAR.md)`). After migration:

- Relative links must be updated to new paths
- Consider: keep root-level symlinks for frequently used files (e.g. `QA_STATUS.md` → `artifacts/dashboards/QA_STATUS.md`) for backward compatibility during transition

### 6.3 Incident Schema Path

`incidents/_schema/` is referenced by incident templates and validators. Options:

- **A:** Move `_schema/` content to `governance/incident_schemas/` and update incident tooling to use that path
- **B:** Keep `incidents/_schema/` as-is (incident-specific schemas stay with incidents) and only move generic schemas to `governance/schemas/`

**Recommendation:** Option A for consistency; all schemas in governance. Update `incidents/templates/README.md` to point to `governance/incident_schemas/`.

### 6.4 Feedback Loop Traces

`feedback_loop/` already has a clear structure. Keep as-is. Ensure `run_feedback_loop.py` and other scripts write traces to `docs/qa/feedback_loop/`.

### 6.5 Phase 3 Config vs History

- **Config in use:** `phase3_ci_config.json`, `phase3_orphan_governance.json`, etc. → `config/`
- **Phase 3 design docs:** `PHASE3_*.md` (summary, implementation, gap prioritization, etc.) → `history/phase3/`

The config files are **actively referenced** by scripts; the design docs are **historical**.

---

## 7. What Should Remain at docs/qa Root

| File | Purpose |
|------|---------|
| **README.md** | Landing page, navigation |
| **MAP_OF_QA_DOCS.md** | Optional map |

**All other files** move into subfolders. No flat mix of architecture, reports, and artifacts at root.

---

## 8. What Should Move to history/archive

| Material | Target | Rationale |
|----------|--------|-----------|
| PHASE3_SUMMARY.md | history/phase3/ | Phase summary, superseded by current state |
| PHASE3_IMPLEMENTATION_REPORT.md | history/phase3/ | Implementation report for completed phase |
| PHASE3_GAP_REPORT.md | history/phase3/ or reports/ | If still generated → artifacts; if one-off → history |
| PHASE3_GAP_PRIORITIZATION.md | history/phase3/ | Design doc; logic lives in config |
| PHASE3_ORPHAN_REVIEW_GOVERNANCE.md | history/phase3/ | Design doc; config in config/ |
| PHASE3_SEMANTIC_ENRICHMENT_PLAN.md | history/phase3/ | Design doc |
| PHASE3_CI_INTEGRATION_PLAN.md | history/phase3/ | Design doc |
| PHASE3_REPLAY_BINDING_ARCHITECTURE.md | history/phase3/ | Design doc |
| PHASE3_TECHNICAL_DOCS.md | history/phase3/ | Technical reference for phase |
| PHASE3_VERIFICATION_REVIEW.md | history/phase3/ | Verification report |
| PHASE3_RESTRISIKEN_REPORT.md | history/phase3/ | Risk report |

**PHASE3_GAP_REPORT.md / .json:** These are **generated** by `generate_gap_report.py`. They should go to `artifacts/json/` (and optionally `artifacts/dashboards/` for MD). The **plan** (PHASE3_GAP_PRIORITIZATION.md) goes to history.

---

## 9. Future-Proofing

### 9.1 Naming Conventions

- **Architecture:** `QA_<COMPONENT>_ARCHITECTURE.md`
- **Reports:** `QA_<TOPIC>_<TYPE>_REPORT.md` or `QA_<TOPIC>_ITERATION<N>_REPORT.md`
- **Generated artifacts:** Same base name as today; location in `artifacts/`
- **Config:** `phase<N>_<name>.json` or `qa_<name>.json` for phase-agnostic config

### 9.2 New Document Placement

| New document type | Place in |
|-------------------|----------|
| New architecture doc | `architecture/<subfolder>/` |
| New governance rule | `governance/` |
| New report | `reports/` |
| New generated artifact | `artifacts/json/` or `artifacts/dashboards/` |
| New incident | `incidents/INC-YYYYMMDD-NNN/` |
| New phase design | `history/phaseN/` when phase completes |
| New config | `config/` |

### 9.3 Deprecation

When a document is superseded:
1. Move to `history/` with date or phase suffix if needed
2. Add a short `README.md` in the original location: "Moved to history/phaseN/..."
3. Update `docs/qa/README.md` and any index documents

---

## 10. Summary Checklist

- [ ] Create folder structure (architecture, governance, reports, artifacts, config, plans, history)
- [ ] Create README.md in each major folder
- [ ] Create docs/qa/README.md as root anchor
- [ ] Classify all 121 files per matrix
- [ ] Move files (do not execute yet – this proposal is design only)
- [ ] Update all script paths (paths config recommended)
- [ ] Update internal document links
- [ ] Decide: incidents/_schema merge into governance/incident_schemas (Option A)
- [ ] Add MAP_OF_QA_DOCS.md if useful
- [ ] Document migration in a MIGRATION.md for execution phase

---

*End of proposal. No files have been moved or modified.*
