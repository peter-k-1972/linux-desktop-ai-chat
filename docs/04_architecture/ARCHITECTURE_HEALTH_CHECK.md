# Architecture Health Check

**Projekt:** Linux Desktop Chat  
**Skript:** `scripts/architecture/architecture_health_check.py`

---

## 1. Zweck

Schnelle Prüfung des Architekturzustands ohne Volltestlauf. Bündelt vorhandene Governance-Signale und liefert einen eindeutigen Gesamtstatus für Release-Readiness und Refactor-Vorchecks.

---

## 2. Was wird geprüft

| Check | Beschreibung |
|-------|--------------|
| **baseline** | ARCHITECTURE_BASELINE_2026.md vorhanden |
| **governance_policies** | 8 zentrale Policy-Dateien in docs/04_architecture |
| **arch_guard_config** | arch_guard_config.py importierbar, DOCS_ARCH = docs/04_architecture |
| **entrypoints** | run_gui_shell.py, app/__main__.py, main.py vorhanden |
| **architecture_tests** | Mindestens 8 Architektur-Testdateien in tests/architecture/ |
| **docs_path** | docs/04_architecture existiert, enthält Policies |
| **drift_radar** | ARCHITECTURE_DRIFT_RADAR.json vorhanden und status=ok (falls ausgeführt) |

---

## 3. Was wird nicht geprüft

- **Kein pytest-Lauf:** Der Health-Check führt keine Architektur-Tests aus. Dafür: `pytest tests/architecture/ -m architecture` oder `architecture_drift_radar.py`
- **Kein Netzwerk**
- **Keine Laufzeit-Integration:** Kein App-Start, keine Services
- **Keine semantische Code-Analyse:** Keine AST-Prüfung, keine Import-Zyklen
- **Keine funktionalen Tests**

---

## 4. Ausführung

```bash
# Standard (Terminal-Ausgabe)
python scripts/architecture/architecture_health_check.py

# JSON-Ausgabe
python scripts/architecture/architecture_health_check.py --json
```

---

## 5. Status-Interpretation

| Status | Bedeutung | Exit-Code |
|--------|-----------|-----------|
| **OK** | Alle Checks bestanden, Drift-Radar (falls vorhanden) ok | 0 |
| **WARNING** | Keine kritischen Fehler, aber Warnungen (z.B. Drift-Radar nicht ausgeführt oder drift) | 1 |
| **FAIL** | Mindestens ein kritischer Check fehlgeschlagen (Baseline, Policies, Entrypoints, Config, Tests, docs-Pfad) | 2 |

### Kritische Checks (→ FAIL)

- Baseline fehlt
- Governance-Policies fehlen
- arch_guard_config nicht ladbar oder DOCS_ARCH inkonsistent
- Entrypoints fehlen
- Architektur-Tests fehlen oder zu wenige
- docs/04_architecture fehlt oder leer

### Nicht-kritische Checks (→ WARNING)

- Drift-Radar-JSON fehlt (Hinweis: `architecture_drift_radar.py` ausführen)
- Drift-Radar status=drift (Tests fehlgeschlagen)

---

## 6. Abhängigkeiten

- Python 3.x
- Keine externen Pakete (nur stdlib)
- Vorhandene Projektstruktur (docs/, tests/, scripts/)

---

## 7. Referenzen

- [ARCHITECTURE_BASELINE_2026.md](./ARCHITECTURE_BASELINE_2026.md)
- [ARCHITECTURE_DRIFT_RADAR_POLICY.md](./ARCHITECTURE_DRIFT_RADAR_POLICY.md)
- [ARCHITECTURE_HEALTH_CHECK_REPORT.md](./ARCHITECTURE_HEALTH_CHECK_REPORT.md)
