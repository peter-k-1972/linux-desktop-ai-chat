# QA Level 3 – Implementierungsbericht

**Datum:** 15. März 2026  
**Status:** Phase 1 abgeschlossen  
**Basis:** QA Level 2 (425 Tests ohne live/slow)

---

## 1. Umgesetzte Artefakte

| Artefakt | Pfad | Zweck |
|----------|------|-------|
| Risk-based Coverage Map | docs/qa/QA_LEVEL3_COVERAGE_MAP.md | Sichtbarkeit: Welche Risikoarten abgedeckt, welche nicht |
| Regression Catalog | docs/qa/REGRESSION_CATALOG.md | Fehlerklassen, Zuordnung Tests → Klassen |
| Test Governance Rules | docs/qa/TEST_GOVERNANCE_RULES.md | Konkrete Testpflichten für neue Codepfade |
| CI/Test-Gating | docs/qa/CI_TEST_LEVELS.md | Stufung fast/full/live, pytest-Kommandos |
| Architecture Drift Sentinels | docs/qa/ARCHITECTURE_DRIFT_SENTINELS.md | Dokumentation der Sentinels |
| EventType Registry | tests/contracts/event_type_registry.py | Single Source of Truth für EventType-Contract |
| Meta-Tests | tests/meta/test_event_type_drift.py | Drift-Erkennung bei neuen EventTypes |

---

## 2. Geschlossene Governance-Lücken

| Lücke | Lösung |
|-------|--------|
| Risiken nicht sichtbar | Coverage Map zeigt 8 Risikoarten mit Status |
| Regressionen unstrukturiert | Regression Catalog mit 12 Fehlerklassen |
| Unklare Testpflichten | Governance Rules für Workflow, EventType, Service, UI, etc. |
| CI-Stufung unklar | CI_TEST_LEVELS mit konkreten Kommandos |
| Neuer EventType ohne Contract | Meta-Test + Registry → Fail bei Drift |
| RAG_RETRIEVAL_FAILED ohne Timeline-Label | event_timeline_view type_map ergänzt |

---

## 3. Risiken jetzt sichtbar/kontrollierbar

- **Contract Drift:** Meta-Test erkennt neuen EventType ohne Registry-Eintrag
- **Timeline Drift:** Meta-Test prüft Anzeigetext für alle EventTypes
- **Coverage-Lücken:** Map dokumentiert bekannte Lücken (ChromaDB Netzwerk, Ollama degraded)
- **Regressions-Klassifikation:** Jeder Bug kann Fehlerklasse zugeordnet werden

---

## 4. Geänderte/Neue Dateien

| Datei | Aktion |
|-------|--------|
| docs/qa/QA_LEVEL3_COVERAGE_MAP.md | Neu |
| docs/qa/REGRESSION_CATALOG.md | Neu |
| docs/qa/TEST_GOVERNANCE_RULES.md | Neu |
| docs/qa/CI_TEST_LEVELS.md | Neu |
| docs/qa/ARCHITECTURE_DRIFT_SENTINELS.md | Neu |
| docs/qa/QA_LEVEL3_REPORT.md | Neu |
| tests/contracts/event_type_registry.py | Neu |
| tests/contracts/test_debug_event_contract.py | Geändert (nutzt Registry) |
| tests/meta/__init__.py | Neu |
| tests/meta/test_event_type_drift.py | Neu |
| app/ui/debug/event_timeline_view.py | Geändert (RAG_RETRIEVAL_FAILED in type_map) |

---

## 5. Nächste Level-3-Schritte (höchster Nutzen)

| Priorität | Schritt | Nutzen |
|-----------|---------|--------|
| 1 | Meta-Tests in CI ausführen | Drift bei jedem PR erkannt |
| 2 | Prüfskript für Testdomänen ohne Marker | tests/*/ Konsistenz |
| 3 | ChromaDB Netzwerk-Failure-Test (optional) | Lücke in Coverage Map schließen |
| 4 | Governance-Checkliste in PR-Template | Entwickler erinnert an Testpflichten |

---

## 6. Verwendung

```bash
# Standard-CI (ohne live/slow)
pytest -m "not live and not slow"

# Meta-Tests (Drift-Check)
pytest tests/meta/ -v

# Nur Contract + Meta
pytest tests/contracts/ tests/meta/ -m "not live and not slow"
```

---

*QA Level 3 Report erstellt am 15. März 2026.*
