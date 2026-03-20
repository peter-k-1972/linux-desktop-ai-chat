# Map of QA Documentation System

**Purpose:** Visual orientation for the docs/qa structure.  
**Audience:** New team members, anyone navigating QA documentation.

---

## 1. Folder Hierarchy

```
docs/qa/
├── README.md                    ← Start here
├── 00_map_of_qa_system.md       ← This file
│
├── architecture/                 QA system design
│   ├── autopilot/               Autopilot v2/v3 architecture
│   ├── coverage/                Coverage Map architecture
│   ├── inventory/               Test Inventory architecture
│   ├── incident_replay/         Incident Replay architecture
│   └── graphs/                  Architecture & Dependency graphs (MD, SVG, DOT)
│
├── governance/                   Standards, rules, schemas
│   ├── schemas/                 JSON schemas (coverage_map, test_inventory)
│   └── incident_schemas/         Incident YAML/JSON schemas, field standards
│
├── reports/                     Human-authored reports
│
├── artifacts/                   Machine-generated (do not hand-edit)
│   ├── dashboards/              MD dashboards (QA_STATUS, QA_RISK_RADAR, …)
│   ├── json/                    JSON snapshots
│   └── csv/                     CSV exports
│
├── incidents/                   Incident registry
│   ├── INC-YYYYMMDD-NNN/        Per-incident folders
│   ├── templates/               incident.template.yaml, bindings.template.json
│   ├── index.json               Generated registry
│   └── analytics.json           Generated analytics
│
├── feedback_loop/               Trace files from feedback loop
│
├── config/                      Active configuration
│
├── plans/                       Active QA plans
│
└── history/                     Archived phase documents
    └── phase3/
```

---

## 2. Data Flow

```
Scripts (scripts/qa/)
    │
    ├── build_test_inventory.py  ──► artifacts/json/QA_TEST_INVENTORY.json
    ├── build_coverage_map.py   ──► artifacts/json/QA_COVERAGE_MAP.json
    ├── qa_cockpit.py           ──► artifacts/dashboards/QA_STATUS.md
    ├── update_control_center.py ──► artifacts/json/QA_CONTROL_CENTER.json
    ├── run_feedback_loop.py    ──► artifacts/json/FEEDBACK_LOOP_REPORT.json
    │                             feedback_loop/*_trace.json
    └── incidents/build_registry.py ──► incidents/index.json
    └── incidents/analyze_incidents.py ──► incidents/analytics.json
```

---

## 3. Cross-References

| From | To |
|------|-----|
| [docs/00_map_of_the_system.md](../00_map_of_the_system.md) | System-wide map |
| [docs/06_operations_and_qa/](../06_operations_and_qa/) | Operations & QA consolidation |
| [docs/README.md](../README.md) | Documentation landing |
