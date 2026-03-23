# Linux Desktop Chat – Documentation

**Landing page** for all project documentation.

Diese Seite verlinkt die wichtigsten Einstiege und beschreibt, welche Themen in welchem Unterordner liegen. Nutzen Sie die **Quick Start**-Liste für die erste Orientierung; die tabellarische Übersicht danach ordnet die Bereiche nach Zielgruppe.

## Inhalt

- [Quick Start](#quick-start) (inkl. [Release Acceptance](RELEASE_ACCEPTANCE_REPORT.md))
- [Kategorien (Navigation)](#kategorien-navigation)
- [Documentation Structure](#documentation-structure)
- [Root Anchors (Do Not Move)](#root-anchors-do-not-move)
- [Help Content](#help-content)
- [Consolidation & Implementation](#consolidation--implementation)

**Siehe auch**

- [Repository-README](../README.md)  
- [Benutzerhandbuch](USER_GUIDE.md) · [Entwicklerhandbuch](DEVELOPER_GUIDE.md) · [Architektur](ARCHITECTURE.md)  
- [In-App-Hilfe](../help/README.md) · [Strukturiertes Handbuch (`docs_manual/`)](../docs_manual/README.md)

---

## Quick Start

- **[Release Acceptance Report](RELEASE_ACCEPTANCE_REPORT.md)** — Release Freeze **v0.9.0**, Testgate, Tag-Hinweis (*Operations Platform Foundation*).  
- **[Release-Architekturkarte](introduction/architecture.md)** — Ist-Stand: Operations, Services, DB, Datenflüsse (Mermaid).  
- **[Map of the System](00_map_of_the_system.md)** — Start here. Human-readable overview of workspaces, navigation, and architecture.
- **[Architecture (canonical summary)](ARCHITECTURE.md)** — Layers, data flow, Context / Settings / Provider.
- **[User Guide](USER_GUIDE.md)** — End-user manual (Context Mode, Detail Level, Profile, Override).
- **[Developer Guide](DEVELOPER_GUIDE.md)** — Setup, structure, CLI, pitfalls.
- **[Feature deep dives](FEATURES/)** — Per-feature reference (`chat`, `context`, `settings`, …).
- **[System Map](SYSTEM_MAP.md)** — Generated structural map (app, workspaces, services).
- **[Trace Map](TRACE_MAP.md)** — Code ↔ Help ↔ Tests traceability.
- **[Feature Registry](FEATURE_REGISTRY.md)** — System-wide index of features and their implementation.
- **[Documentation normalization changelog](CHANGELOG_NORMALIZATION.md)** — What changed in the 2026-03-20 doc pass.

Die folgende Tabelle ordnet die Verzeichnisse unter `docs/` nach Zweck und Leserschaft.

---

## Kategorien (Navigation)

### Architektur

- [ARCHITECTURE.md](ARCHITECTURE.md) — kanonische Schichten- und Datenflussbeschreibung  
- [introduction/architecture.md](introduction/architecture.md) — **Release-Systemkarte** (GUI-Operations-Workspaces, O1–O4 / R1–R4, Services, SQLite-Tabellen, Mermaid/PlantUML)  
- [04_architecture/](04_architecture/) — Policies, Governance, Tiefenanalysen  
- [architecture/README.md](architecture/README.md) — Wegweiser inkl. Markdown-Rendering  

### Systemkarten und Orientierung

- [00_map_of_the_system.md](00_map_of_the_system.md) — Lesbare Gesamtübersicht  
- [SYSTEM_MAP.md](SYSTEM_MAP.md) · [TRACE_MAP.md](TRACE_MAP.md) · [FEATURE_REGISTRY.md](FEATURE_REGISTRY.md)  

### QA und Betrieb

- [RELEASE_ACCEPTANCE_REPORT.md](RELEASE_ACCEPTANCE_REPORT.md) — Abnahme Release Freeze **v0.9.0**, pytest-Referenz, Governance-/Help-/Qt-Gates  
- [MODEL_USAGE_PHASE_E_QA_REPORT.md](MODEL_USAGE_PHASE_E_QA_REPORT.md) — Phase E: QA-Abnahme Modell-Verbrauch, Quotas, lokale Assets (`~/ai`), E2E-Matrix vs. Unit-Tests, Risiken  
- [06_operations_and_qa/](06_operations_and_qa/) — Audits, Konsolidierung, UX-/QA-Reports  
- [qa/](qa/) — QA-Hub (Governance, Artefakte, Incidents)  
- [operations/](operations/) — Operator-Doku: Audit/Incidents, Plattform-Gesundheit, Workflows/Runs (App-Datenbank & Services)  
- [user/](user/) — Fachtexte **Deployment** (`deployment.md`), **Scheduling** (`scheduling.md`); ergänzen das Benutzerhandbuch  
- [glossary/terminology.md](glossary/terminology.md) — kanonische Produktbegriffe  

**In-App-Hilfe (Workflows, Geplant, Deployment, Betrieb):** Artikelindex [`help/README.md`](../help/README.md) → Abschnitt *Operations* (`workflows_workspace`, `scheduling_workflows`, `deployment_workspace`, `operations_betrieb`).

### Entwicklerleitfäden

- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) — Setup, Struktur, CLI  
- [05_developer_guide/](05_developer_guide/) — vertiefende Developer-Dokumente  

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
| [operations](operations/) | App-Betrieb (Audit, Incidents, Plattform, Workflow-Runs) | Operators, developers |
| [user](user/) | Deployment- und Scheduling-Fachmodell (kurz) | Users, admins |
| [glossary](glossary/terminology.md) | Canonical terminology (Workflow, Run, Incident, …) | All |

Diese Dateien sind feste Anker im Repository; Verweise in CI und Skripten setzen auf genau diese Pfade.

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
Article index (paths for editors): [`help/README.md`](../help/README.md).  
See [06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md](06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md) for the full documentation and help architecture.

---

## Consolidation & Implementation

- [DOC_NAVIGATION_REPORT.md](DOC_NAVIGATION_REPORT.md) — Navigationsausbau (TOC, Crosslinks, Link-Check-Hinweise)
- [06_operations_and_qa/CONSOLIDATION_REPORT.md](06_operations_and_qa/CONSOLIDATION_REPORT.md) — Audit, source-of-truth decisions
- [06_operations_and_qa/CONSOLIDATION_RULES.md](06_operations_and_qa/CONSOLIDATION_RULES.md) — Rules to prevent regression
- [06_operations_and_qa/DOCS_HELP_IMPLEMENTATION_REPORT.md](06_operations_and_qa/DOCS_HELP_IMPLEMENTATION_REPORT.md) — Docs/help implementation (Phases 1–8)
