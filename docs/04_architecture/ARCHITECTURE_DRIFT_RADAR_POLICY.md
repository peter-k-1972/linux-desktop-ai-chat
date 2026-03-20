# Architecture Drift Radar – Policy

**Projekt:** Linux Desktop Chat  
**Referenz:** `docs/architecture/ARCHITECTURE_DRIFT_RADAR_ANALYSIS.md`  
**Skript:** `scripts/architecture/architecture_drift_radar.py`

---

## 1. Drift-Kategorien

| Kategorie | Beschreibung | Signalquelle |
|-----------|--------------|--------------|
| **layer_drift** | Verletzung von Import-Richtungen (FORBIDDEN_IMPORT_RULES) | app_package_guards, service_guards |
| **startup_drift** | Bootstrap/Entrypoint-Abweichungen | startup_governance_guards |
| **registry_drift** | Registry-Inkonsistenzen (Model, Nav, Screen, Command) | registry_governance_guards |
| **provider_drift** | Provider-String/Orchestrator-Drift | provider_orchestrator_guards |
| **event_drift** | EventBus/Event-Namensraum-Drift | eventbus_governance_guards |
| **entrypoint_drift** | Neue unerlaubte Einstiegspunkte | startup_governance_guards |
| **hardcoding_drift** | Unerlaubte Hardcodings (Provider-Strings etc.) | provider_orchestrator_guards |
| **orphan_drift** | Potenziell verwaiste oder ungebundene Teile | (noch nicht implementiert) |
| **gui_domain_drift** | GUI-Domain-Abhängigkeitsverletzungen | gui_domain_dependency_guards |
| **feature_drift** | Feature-Registry-Divergenzen | feature_governance_guards |

---

## 2. Schweregrade

| Schweregrad | Bedeutung | Beispiel |
|-------------|-----------|----------|
| **critical** | Architektur-Kern verletzt; sofortiger Handlungsbedarf | core → gui Import |
| **high** | Klare Regelverletzung; zeitnahe Behebung | services → gui |
| **medium** | Dokumentierte Ausnahme oder Abweichung | provider_drift |
| **low** | Hinweis; Follow-up | orphan_drift |

---

## 3. Signalquellen

| Quelle | Typ | Liefert |
|--------|-----|---------|
| **pytest -m architecture** | Test-Lauf | Pass/Fail pro Guard |
| **arch_guard_config** | Statisch | Konfigurationsvalidierung |
| **Governance-Dateien** | Existenz | Policy/Report-Vorhandensein |

---

## 4. Zuordnung zu Architekturdomänen

| Domäne | Drift-Kategorien | Test-Dateien |
|--------|------------------|---------------|
| **app_package** | layer_drift, entrypoint_drift | test_app_package_guards |
| **gui** | layer_drift, gui_domain_drift | test_gui_governance_guards, test_gui_domain_dependency_guards |
| **services** | layer_drift | test_service_governance_guards |
| **startup** | startup_drift, entrypoint_drift | test_startup_governance_guards |
| **registry** | registry_drift | test_registry_governance_guards |
| **provider** | provider_drift, hardcoding_drift | test_provider_orchestrator_guards |
| **eventbus** | event_drift | test_eventbus_governance_guards |
| **feature** | feature_drift | test_feature_governance_guards |

---

## 5. Ausgabestruktur für Reports/JSON

```json
{
  "version": "1.0",
  "timestamp": "2026-03-16T12:00:00Z",
  "summary": {
    "total_tests": 70,
    "passed": 70,
    "failed": 0,
    "status": "ok"
  },
  "drift_categories": {
    "layer_drift": {"status": "ok", "passed": 5, "failed": 0},
    "startup_drift": {"status": "ok", "passed": 7, "failed": 0},
    ...
  },
  "domains": {
    "app_package": {"status": "ok", "tests": [...]},
    ...
  },
  "failures": []
}
```

---

## 6. Regeln für neue Drift-Kategorien

1. Kategorie in Policy dokumentieren
2. Zuordnung zu Signalquelle (Test-Datei) definieren
3. Schweregrad festlegen
4. Radar-Skript-Mapping erweitern

---

## 7. Regeln für CI-/lokale Nutzung

- **Lokal:** `python scripts/architecture/architecture_drift_radar.py`
- **CI:** `python scripts/architecture/architecture_drift_radar.py --json`; Exit-Code 0 bei status=ok
- **Ausgabe:** docs/architecture/ARCHITECTURE_DRIFT_RADAR.json, ARCHITECTURE_DRIFT_RADAR_REPORT.md
