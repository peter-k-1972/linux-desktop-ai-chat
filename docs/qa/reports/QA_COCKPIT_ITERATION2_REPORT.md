# QA Cockpit – Iteration 2 Report

**Datum:** 15. März 2026  
**Status:** Abgeschlossen

---

## 1. Neu angelegte / geänderte Dateien

| Datei | Aktion |
|-------|--------|
| scripts/qa/__init__.py | Neu |
| scripts/qa/checks.py | Neu – Marker-, EventType-, Regression-Checks |
| scripts/qa/qa_cockpit.py | Neu – Hauptscript, generiert QA_STATUS.md |
| docs/qa/QA_STATUS.md | Neu – generiert vom Cockpit |
| docs/qa/QA_COCKPIT_ITERATION2_REPORT.md | Neu |
| tests/meta/test_marker_discipline.py | Neu – Meta-Test für Marker-Disziplin |
| docs/qa/CI_TEST_LEVELS.md | Geändert – Abschnitt 7 QA-Cockpit |
| docs/qa/ARCHITECTURE_DRIFT_SENTINELS.md | Geändert – Marker-Disziplin, QA-Cockpit |

---

## 2. Umgesetzte Cockpit-Fähigkeiten

| Fähigkeit | Status | Beschreibung |
|-----------|--------|--------------|
| Marker-Disziplin-Check | ✅ | Prüft contracts/, async_behavior/, failure_modes/, cross_layer/, startup/, meta/ |
| EventType-Coverage-Check | ✅ | Registry + Timeline-Abdeckung |
| Regression-Coverage-Check | ✅ | Parst REGRESSION_CATALOG.md, zeigt abgedeckte/offene Fehlerklassen |
| CI-Integration vorbereitet | ✅ | Dokumentation in CI_TEST_LEVELS.md, Kommandos definiert |
| QA_STATUS.md generieren | ✅ | Vollständiger Report mit allen Signalen |
| QA_STATUS.json (optional) | ✅ | `--json` Flag |

---

## 3. Automatisch sichtbare Governance-Lücken

| Lücke | Sichtbar durch |
|-------|----------------|
| Testdatei ohne erwarteten Marker | Marker-Disziplin-Check + Meta-Test |
| Neuer EventType ohne Registry | EventType-Check (Registry) |
| EventType ohne Timeline-Anzeige | EventType-Check (Timeline) |
| Fehlerklasse ohne Test im Catalog | Regression-Coverage (offene Klassen) |
| Testanzahl | pytest --collect-only |

---

## 4. Kommandos / Nutzung

```bash
# QA-Cockpit ausführen (generiert docs/qa/QA_STATUS.md)
python scripts/qa/qa_cockpit.py

# Mit JSON-Output
python scripts/qa/qa_cockpit.py --json

# Meta-Tests (inkl. Marker-Disziplin)
pytest tests/meta/ -v

# Empfohlene CI-Reihenfolge
pytest -m "not live and not slow"
pytest tests/meta/ -v
python scripts/qa/qa_cockpit.py
```

---

## 5. Verbleibende Lücken

| Lücke | Priorität | Empfehlung |
|-------|-----------|------------|
| Test-Count ohne venv ungenau | Niedrig | Cockpit mit venv ausführen |
| Regression-Catalog-Parser bei Formatänderung | Mittel | Konvention dokumentieren |
| Keine Warnung bei neuem Ordner in tests/ | Niedrig | DOMAIN_MARKER_MAP erweitern |

---

## 6. Empfehlung für QA Cockpit Iteration 3

| Priorität | Schritt | Nutzen |
|-----------|---------|--------|
| 1 | Cockpit in CI-Pipeline integrieren | QA_STATUS.md bei jedem PR |
| 2 | Testdomänen-Größen im Cockpit | Welche Domäne wie viele Tests |
| 3 | Risk-based Coverage Verweis | Link zu Lücken aus QA_LEVEL3_COVERAGE_MAP |
| 4 | Exit-Code bei kritischen Lücken | Cockpit failt bei Marker-Violations |

---

*QA Cockpit Iteration 2 Report erstellt am 15. März 2026.*
