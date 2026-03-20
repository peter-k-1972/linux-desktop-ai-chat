# Linux Desktop Chat – Documentation

**Landing page** for all project documentation.

---

## Quick Start

- **[Map of the System](00_map_of_the_system.md)** — Start here. Human-readable overview of workspaces, navigation, and architecture.
- **[System Map](SYSTEM_MAP.md)** — Generated structural map (app, workspaces, services).
- **[Trace Map](TRACE_MAP.md)** — Code ↔ Help ↔ Tests traceability.
- **[Feature Registry](FEATURE_REGISTRY.md)** — System-wide index of features and their implementation.

---

## Documentation Structure

| Section | Purpose | Audience |
|---------|---------|----------|
| [01_product_overview](01_product_overview/) | Product vision, introduction, UX concept | All |
| [02_user_manual](02_user_manual/) | Feature reference (agents, models, RAG, prompts, settings) | End users |
| [03_feature_reference](03_feature_reference/) | Workspace details, project hub | End users, support |
| [04_architecture](04_architecture/) | System design, module structure | Architects, developers |
| [05_developer_guide](05_developer_guide/) | Implementation, setup, contribution | Developers |
| [06_operations_and_qa](06_operations_and_qa/) | QA, UX audits, consolidation | QA, operations |
| [qa](qa/) | QA documentation hub (architecture, governance, artifacts, incidents) | QA, developers |
| [07_troubleshooting](07_troubleshooting/) | Common issues, diagnostics | Support, users |
| [08_glossary](08_glossary/) | Terms, abbreviations | All |

---

## Root Anchors (Do Not Move)

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | This landing page |
| [00_map_of_the_system.md](00_map_of_the_system.md) | Human-readable orientation |
| [SYSTEM_MAP.md](SYSTEM_MAP.md) | Generated structural map |
| [TRACE_MAP.md](TRACE_MAP.md) | Code/help/test traceability |
| [FEATURE_REGISTRY.md](FEATURE_REGISTRY.md) | Feature → implementation index |

---

## Help Content

User-facing help articles live in **`help/`** (single source of truth).  
See [06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md](06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md) for the full documentation and help architecture.

---

## Consolidation & Implementation

- [06_operations_and_qa/CONSOLIDATION_REPORT.md](06_operations_and_qa/CONSOLIDATION_REPORT.md) — Audit, source-of-truth decisions
- [06_operations_and_qa/CONSOLIDATION_RULES.md](06_operations_and_qa/CONSOLIDATION_RULES.md) — Rules to prevent regression
- [06_operations_and_qa/DOCS_HELP_IMPLEMENTATION_REPORT.md](06_operations_and_qa/DOCS_HELP_IMPLEMENTATION_REPORT.md) — Docs/help implementation (Phases 1–8)
