# Architektur-Baseline 2026 – Erstellungsreport

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16

---

## 1. Erstellt

| Dokument | Pfad | Inhalt |
|----------|------|--------|
| **Architektur-Baseline** | docs/04_architecture/ARCHITECTURE_BASELINE_2026.md | Vollständige Referenz des gehärteten Systemzustands |

---

## 2. Konsolidierte Quellen

| Quelle | Verwendung |
|--------|------------|
| tests/architecture/arch_guard_config.py | FORBIDDEN_IMPORT_RULES, GUI_SCREEN_WORKSPACE_MAP, Registry/Provider/EventBus-Konfiguration |
| docs/04_architecture/FULL_SYSTEM_CHECKUP_REPORT.md | Gesamtstatus, Domänen, Stärken |
| docs/04_architecture/FULL_SYSTEM_RESTPOINT_REMEDIATION_REPORT.md | Behobene Restpunkte, verbleibende |
| docs/04_architecture/FULL_SYSTEM_GOVERNANCE_MATRIX.md | Governance-Blöcke, Abdeckung |
| docs/04_architecture/STARTUP_GOVERNANCE_POLICY.md | Bootstrap-Reihenfolge, Contract |
| docs/04_architecture/REGISTRY_GOVERNANCE_POLICY.md | Registry-Orte, Lifecycle |
| docs/04_architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md | Provider-Auflösung, Resolver |
| docs/04_architecture/EVENTBUS_GOVERNANCE_POLICY.md | Event-Publisher, -Consumer |
| docs/04_architecture/ARCHITECTURE_DRIFT_RADAR_POLICY.md | Drift-Kategorien |
| docs/04_architecture/LEGACY_MAIN_GOVERNANCE.md | app.main Status |
| docs/04_architecture/LLM_MODULE_STRUCTURE.md | app/llm vs core/llm |
| docs/04_architecture/TOOLS_GOVERNANCE_DECISION.md | Tools ohne Registry |
| docs/00_map_of_the_system.md | Systemübersicht |

---

## 3. Vollständigkeit

Die Baseline bildet den aktuellen gehärteten Zustand vollständig ab:

- **Systemstruktur:** Alle Hauptschichten und Domänen erfasst
- **Architekturregeln:** FORBIDDEN_IMPORT_RULES, Service/GUI-Regeln, Ausnahmen
- **Einstiegspunkte:** Kanonisch und Legacy
- **Startup:** Reihenfolge, Contract, Settings-Injektion
- **Registry:** Alle fünf Registries; Tools bewusst ohne
- **Provider:** ModelRegistry, Orchestrator, Resolver-Pfade
- **EventBus:** Publisher, Consumer, Verbote
- **Governance-Blöcke:** Alle 11 mit Policy- und Test-Referenz
- **Drift-Radar:** Kategorien, Skript
- **Restpunkte:** Dokumentiert
- **Änderungspflicht:** Kompakte Sektion ergänzt

---

## 4. Restunsicherheiten

| Punkt | Status |
|-------|--------|
| **KNOWN_IMPORT_EXCEPTIONS settings_dialog** | settings_dialog wurde von Provider-Imports entkoppelt (Remediation). Der Eintrag in KNOWN_IMPORT_EXCEPTIONS könnte obsolet sein – arch_guard_config wurde nicht angepasst. Kein funktionaler Einfluss. |
| **app/commands vs core/commands** | Re-Export-Pattern; nicht explizit in Baseline. Niedrige Priorität. |
| **app/qa, app/help** | Keine explizite Architektur-Governance; in Baseline als Domänen genannt, nicht vertieft. |

---

## 5. Empfehlung

Baseline als Referenz freigeben. Bei Architekturänderungen zuerst ARCHITECTURE_BASELINE_2026.md und arch_guard_config prüfen; bei Abweichung Policy und Guards anpassen.
