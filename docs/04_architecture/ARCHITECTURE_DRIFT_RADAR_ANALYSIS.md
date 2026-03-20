# Architecture Drift Radar – Analyse

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Kontext:** Übergeordnete Drift-Erkennungsschicht zur Konsolidierung aller Governance-Signale.

---

## 1. Vorhandene Governance-Quellen

| Quelle | Pfad | Inhalt |
|--------|------|--------|
| **arch_guard_config** | tests/architecture/arch_guard_config.py | Zentrale Konfiguration: FORBIDDEN_IMPORT_RULES, KNOWN_IMPORT_EXCEPTIONS, GUI_SCREEN_WORKSPACE_MAP, CANONICAL_SERVICE_MODULES, KNOWN_MODEL_PROVIDER_STRINGS, ALLOWED_EMIT_EVENT_IMPORTERS, etc. |
| **App Package Guards** | test_app_package_guards.py | Root-Dateien, TARGET_PACKAGES, FORBIDDEN_PARALLEL_PACKAGES, ui-Importeure |
| **Feature Governance** | test_feature_governance_guards.py | Feature-Registry, Domänen-Mapping |
| **GUI Governance** | test_gui_governance_guards.py | Screen-Registry, Navigation, Commands |
| **GUI Domain Dependency** | test_gui_domain_dependency_guards.py | FORBIDDEN_GUI_DOMAIN_PAIRS |
| **Service Governance** | test_service_governance_guards.py | services→gui, gui→providers, CANONICAL_SERVICE_MODULES |
| **Startup Governance** | test_startup_governance_guards.py | CANONICAL_GUI_ENTRY_POINTS, REQUIRED_BOOTSTRAP_PATTERNS |
| **Registry Governance** | test_registry_governance_guards.py | ModelRegistry, Provider-Strings, Nav/Screen/Command-Registries |
| **Provider Orchestrator** | test_provider_orchestrator_governance_guards.py | Provider-Konsistenz, Auflösungsorte |
| **EventBus Governance** | test_eventbus_governance_guards.py | emit_event, EventBus, EventType |

---

## 2. Vorhandene Signalquellen

| Signalquelle | Typ | Liefert |
|--------------|-----|---------|
| **pytest -m architecture** | Test-Lauf | Pass/Fail pro Guard; 70+ Tests |
| **arch_guard_config** | Statisch | Konfigurationswerte für Guards |
| **QA checks.py** | Script | Marker-Disziplin, Top-Risiken (QA_RISK_RADAR) |
| **generate_qa_dependency_graph** | Script | Subsystem-Abhängigkeiten, Kaskaden |

---

## 3. Welche Drift-Typen bereits indirekt erkannt werden

| Drift-Typ | Erkannt durch | Test-Datei |
|-----------|---------------|------------|
| **layer_drift** | FORBIDDEN_IMPORT_RULES, KNOWN_EXCEPTIONS | app_package_guards, service_guards |
| **startup_drift** | CANONICAL_GUI_ENTRY_POINTS, REQUIRED_BOOTSTRAP_PATTERNS | startup_governance_guards |
| **registry_drift** | ModelRegistry, Nav/Screen/Command-Registries | registry_governance_guards |
| **provider_drift** | KNOWN_MODEL_PROVIDER_STRINGS, ALLOWED_PROVIDER_STRING_FILES | provider_orchestrator_guards, registry_guards |
| **event_drift** | ALLOWED_EMIT_EVENT_IMPORTERS, EventType | eventbus_governance_guards |
| **entrypoint_drift** | CANONICAL_GUI_ENTRY_POINTS | startup_governance_guards |
| **hardcoding_drift** | ALLOWED_PROVIDER_STRING_FILES | provider_orchestrator_guards |
| **gui_domain_drift** | FORBIDDEN_GUI_DOMAIN_PAIRS | gui_domain_dependency_guards |
| **feature_drift** | Feature-Registry, Domänen | feature_governance_guards |

---

## 4. Welche Drift-Typen noch nicht konsolidiert sind

- **orphan_drift:** Keine explizite Prüfung auf verwaiste Module
- **Konsolidierte Ausgabe:** Kein zentraler Report, der alle Drift-Signale bündelt
- **Schweregrade:** Keine einheitliche Severity-Zuordnung
- **Maschinenlesbare Zusammenfassung:** pytest liefert nur Exit-Code; kein strukturiertes JSON

---

## 5. Vorhandene Reports

| Report | Pfad | Inhalt |
|--------|------|--------|
| GUI Governance | GUI_GOVERNANCE_GUARDS_REPORT.md | Screen, Navigation, Commands |
| Service Governance | SERVICE_GOVERNANCE_GUARDS_REPORT.md | Layer, Services |
| Feature Governance | FEATURE_GOVERNANCE_GUARDS_REPORT.md | Feature-Registry |
| Registry Governance | REGISTRY_GOVERNANCE_REPORT.md | Registries |
| Provider Orchestrator | PROVIDER_ORCHESTRATOR_GOVERNANCE_REPORT.md | Provider-Konsistenz |
| EventBus Governance | EVENTBUS_GOVERNANCE_REPORT.md | Event-System |
| Startup Governance | STARTUP_GOVERNANCE_REPORT.md | Bootstrap |

**Kein übergreifender Drift-Radar-Report.**

---

## 6. Wiederverwendungsoptionen

| Option | Beschreibung |
|--------|--------------|
| **pytest als Signalquelle** | `pytest tests/architecture -m architecture --tb=no -q` → Exit-Code, stdout mit Test-Namen |
| **pytest JSON-Report** | `pytest --json-report` (falls Plugin) oder `pytest -v --tb=no` + Parsing |
| **arch_guard_config importieren** | Direkt importieren für leichte Strukturprüfungen ohne pytest |
| **Governance-Domänen-Mapping** | Mapping Test-Datei → Drift-Kategorie aus Policy ableiten |
| **QA paths** | scripts/qa/qa_paths.py für Artefakt-Pfade |

---

## 7. Empfohlene Radar-Architektur

1. **Radar-Skript** ruft pytest auf (keine Logik-Duplikation)
2. **Parsing** der pytest-Ausgabe (oder pytest-Plugin falls vorhanden)
3. **Zuordnung** Test → Drift-Kategorie → Domäne
4. **Zusätzliche leichte Checks** ohne pytest: Config-Existenz, Governance-Dateien
5. **JSON-Ausgabe** für CI/automatisierte Auswertung
6. **Markdown-Report** für Menschen
