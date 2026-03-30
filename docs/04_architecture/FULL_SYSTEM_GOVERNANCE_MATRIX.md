# Full System Governance Matrix

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-17

---

## 1. Konsolidierte Governance-Blöcke

| Block | Policy | Test-Modul | Absichert | Überschneidungen | Lücken |
|-------|--------|------------|-----------|-----------------|--------|
| **GUI Governance** | GUI_GOVERNANCE_POLICY | test_gui_governance_guards | Screen/Workspace-Map, NavAreas, Commands | Mit GUI Domain | — |
| **GUI Domain Dependency** | GUI_DOMAIN_DEPENDENCY_POLICY | test_gui_domain_dependency_guards | Domain-zu-Domain-Imports | Mit GUI Governance | 2 dokumentierte Ausnahmen |
| **Service Governance** | SERVICE_GOVERNANCE_POLICY | test_service_governance_guards | services→gui, gui→providers | Mit Layer-Guards | — |
| **Startup Governance** | STARTUP_GOVERNANCE_POLICY | test_startup_governance_guards | Entrypoints, Bootstrap-Reihenfolge | Mit App Package | — |
| **Registry Governance** | REGISTRY_GOVERNANCE_POLICY | test_registry_governance_guards | Model, Nav, Screen, Command | — | Tools bewusst ohne Registry |
| **Provider Orchestrator** | PROVIDER_ORCHESTRATOR_GOVERNANCE | test_provider_orchestrator_guards | Provider-Strings, Hardcoding | Mit Registry | — |
| **EventBus Governance** | EVENTBUS_GOVERNANCE_POLICY | test_eventbus_governance_guards | emit_event, get_event_bus | — | Event-Schema nicht validiert |
| **Feature Governance** | FEATURE_GOVERNANCE_POLICY | test_feature_governance_guards | Feature-Registry-Konsistenz | — | Manuelle Pflege |
| **App Package** | APP_TARGET_PACKAGE_ARCHITECTURE | test_app_package_guards | Root-Dateien, Target-Packages, ui | Mit allen Layer-Guards | TEMPORARILY_ALLOWED |
| **Root Entrypoint** | ROOT_ENTRYPOINT_POLICY | test_root_entrypoint_guards | Root-Skripte, erlaubte Entrypoints | Mit Startup | — |
| **Runtime Lifecycle** | RUNTIME_LIFECYCLE_POLICY | test_lifecycle_guards | Single-Instance, Shutdown-Hooks | Mit Startup | — |
| **Architecture Drift Radar** | ARCHITECTURE_DRIFT_RADAR_POLICY | test_architecture_drift_radar | Konsolidierter Drift-Report | Aggregiert alle | — |
| **gui does not import ui** | ARCHITECTURE_GUARD_RULES | test_gui_does_not_import_ui | gui→ui Verbot | Mit App Package | Sentinel (ui entfernt) |
| **Pipeline Engine** | PIPELINE_ENGINE_POLICY | test_pipelines_* | Pipelines-Struktur | — | — |

---

## 2. Abdeckung nach Systemteil

| Systemteil | Governance | Ungesichert |
|------------|------------|-------------|
| **app/** Root | App Package | Rollenklassifizierte Restmenge unter `TEMPORARILY_ALLOWED_ROOT_FILES`: `application_release_info.py`, `gui_smoke_constants.py`, `gui_smoke_harness.py`, `qml_alternative_gui_validator.py`, `qml_theme_governance.py`, `critic.py` |
| **core/** | Layer, Registry, Provider | llm-Re-Export (dokumentiert); core→help nicht explizit geregelt |
| **gui/** | GUI, GUI Domain, App Package | — |
| **services/** | Service Governance | — |
| **providers/** | Provider Orchestrator, Layer | — |
| **agents/** | Layer, EventBus | Agent-Registry ohne formale Policy |
| **tools/** | TOOLS_GOVERNANCE_DECISION | Bewusst keine Registry |
| **rag/** | Layer, EventBus | — |
| **debug/** | EventBus | Event-Schema |
| **metrics/** | EventBus, Layer | — |
| **prompts/** | Layer | — |
| **pipelines/** | PIPELINE_ENGINE_POLICY | — |
| **qa/** | — | Keine explizite QA-Modul-Governance |
| **help/** | — | Keine explizite Governance |
| **commands/** | — | Re-Export von core/commands |
| **llm/** | LLM_MODULE_STRUCTURE | Re-Export dokumentiert |
| **runtime/** | RUNTIME_LIFECYCLE_POLICY | — |

---

## 3. Überschneidungen

| Überschneidung | Blöcke | Bewertung |
|----------------|--------|-----------|
| Layer-Import-Regeln | App Package, Service, GUI, Provider, EventBus | Bewusst – mehrfache Absicherung |
| GUI-Struktur | GUI Governance, GUI Domain | Komplementär (Struktur vs. Dependencies) |
| Entrypoints | Startup, App Package, Root Entrypoint | Startup detailliert, App Package strukturell |
| Provider-Strings | Registry, Provider Orchestrator | Registry: ModelEntry; Provider: Hardcoding |

---

## 4. Lücken (Restpunkte)

| Lücke | Schwere | Empfehlung |
|-------|---------|------------|
| docs_path | **behoben** | DOCS_ARCH = docs/04_architecture |
| Tools-Registry | — | Bewusst keine Registry (TOOLS_GOVERNANCE_DECISION) |
| Event-Payload-Schema | low | Optional: JSON-Schema für AgentEvent |
| app/llm vs core/llm | — | Dokumentiert (LLM_MODULE_STRUCTURE) |
| Agent-Registry Policy | low | Optional: REGISTRY_GOVERNANCE erweitern |
| QA-Modul (app/qa) | low | Keine spezifische Governance |
| core→help | low | Optional: Layer-Regel prüfen |
| TEMPORARILY_ALLOWED_ROOT_FILES | low | Kein pauschaler Shim-Block mehr; verbleibende Root-Dateien sind rollenklassifiziert, `critic.py` bleibt separater Legacy-Follow-up |

---

## 5. QA-Governance (separater Kontext)

| Bereich | Ort | Rolle |
|---------|-----|-------|
| Test Governance | docs/qa/governance/ | TEST_GOVERNANCE_RULES, CI_TEST_LEVELS |
| QA Coverage Map | scripts/qa/, tests/qa/coverage_map | Schema, Loader |
| Test Inventory | scripts/qa/build_test_inventory | Governance-Tests |
| Incidents | docs/qa/incidents/ | YAML-Schema |
| Architecture Drift Sentinels | docs/qa/governance/ARCHITECTURE_DRIFT_SENTINELS | Ergänzt Arch-Guards |

Diese sind **nicht** Teil der Architektur-Governance-Guards, aber Teil des Gesamtsystems.
