# QA Level 3 – Architecture Drift Sentinels

**Datum:** 15. März 2026  
**Zweck:** Früherkennung von Architektur-Drift. Keine großen Frameworks – minimale Hilfen.

---

## 1. Implementierte Sentinels

### 1.1 Marker-Disziplin

**Datei:** `tests/meta/test_marker_discipline.py`

| Test | Zweck |
|------|-------|
| `test_no_marker_violations_in_specialized_domains` | Dateien in contracts/, async_behavior/, etc. haben erwarteten Marker |

**Domänen:** contracts→contract, async_behavior→async_behavior, failure_modes→failure_mode, cross_layer→cross_layer, startup→startup, meta→contract

### 1.2 EventType-Contract-Drift

**Datei:** `tests/meta/test_event_type_drift.py`

| Test | Zweck |
|------|-------|
| `test_all_event_types_have_contract_coverage` | Neuer EventType ohne Registry-Eintrag → Fail |
| `test_event_type_registry_matches_enum` | Entfernter EventType noch in Registry → Fail |
| `test_all_event_types_have_timeline_display` | EventType liefert leeren Anzeigetext → Fail |

**Workflow bei neuem EventType:**
1. `app/debug/agent_event.py`: EventType ergänzen
2. `tests/contracts/event_type_registry.py`: EVENT_TYPE_CONTRACT ergänzen
3. `app/ui/debug/event_timeline_view.py`: type_map ergänzen (optional, Fallback auf .value)
4. Meta-Tests laufen → Drift erkannt falls Schritt 2 vergessen

---

## 2. Geplante / Erweiterbare Sentinels

| Sentinel | Beschreibung | Aufwand | Status |
|----------|--------------|---------|--------|
| Marker-Disziplin | tests/*/ ohne passenden Marker | Meta-Test + Cockpit | ✅ Implementiert |
| Neuer Service ohne Failure-Test | app/*/ mit Service, kein failure_mode in tests/ | Manuell / Audit | Offen |
| Neuer UI-Pfad ohne Behavior-Test | UI-Komponenten ohne UI-Test | Manuell | Offen |

---

## 3. Testkonventionen (für Drift-Vermeidung)

- **tests/contracts/**: Nur Contract-Tests, Marker `contract`
- **tests/failure_modes/**: Nur Failure-Tests, Marker `failure_mode`
- **tests/async_behavior/**: Nur Async-Tests, Marker `async_behavior`
- **tests/cross_layer/**: Nur Cross-Layer-Tests, Marker `cross_layer`
- **tests/startup/**: Nur Startup-Tests, Marker `startup`
- **tests/meta/**: Meta-Tests, Drift-Sentinels, Marker `contract`

---

## 4. QA-Cockpit

Das QA-Cockpit (`scripts/qa/qa_cockpit.py`) aggregiert alle Drift-Signale:

- Marker-Disziplin
- EventType-Coverage (Registry, Timeline)
- Regression-Coverage

```bash
python scripts/qa/qa_cockpit.py
```

Output: `docs/qa/artifacts/dashboards/QA_STATUS.md`

---

## 5. Prüfskript (optional)

```bash
# Alle Meta-Tests ausführen
pytest tests/meta/ -v

# QA-Cockpit (Status-Report)
python scripts/qa/qa_cockpit.py
```

---

*Architecture Drift Sentinels erstellt am 15. März 2026. QA Cockpit Iteration 2 ergänzt.*
