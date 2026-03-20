# QA Test Inventory – Phase 1 Review-Report

**Datum:** 15. März 2026  
**Status:** Phase 1 abgeschlossen  
**Reifegrad:** Release-fähig für Phase 1

---

## 1. Reifegrad Phase 1

| Kriterium | Status | Anmerkung |
|-----------|--------|-----------|
| **Discovery-Stabilität** | ✅ | pytest/fallback sammelt Tests, nodeids/file_paths erhalten |
| **Determinismus** | ✅ | Gleicher Input + --timestamp => identischer Output |
| **Feldvollständigkeit** | ✅ | Alle Pflichtfelder pro Test-Eintrag vorhanden |
| **Heuristik-Sicherheit** | ✅ | inference_sources dokumentiert, keine Überklassifikation |
| **Summary-Korrektheit** | ✅ | Counts konsistent mit Testmenge |
| **Governance** | ✅ | Keine Mutation von incidents/, replay, bindings, REGRESSION_CATALOG |

---

## 2. pytest-Suite

| Datei | Fokus |
|-------|-------|
| `tests/qa/test_inventory/test_inventory_happy_path.py` | Struktur, Pflichtfelder, nodeid-Erhalt, Summary-Counts |
| `tests/qa/test_inventory/test_inventory_determinism.py` | Determinismus, Sortierung |
| `tests/qa/test_inventory/test_inventory_rules.py` | Ableitungsregeln, Heuristik, Catalog-Parser |
| `tests/qa/test_inventory/test_inventory_governance.py` | Dry-Run, keine Seiteneffekte |

**Ausführung:**
```bash
pytest tests/qa/test_inventory/ -v
pytest tests/qa/test_inventory/ -v -m unit
```

**Stand:** 32 Tests, alle bestanden.  
*Hinweis:* Der Generator leitet während `pytest.main(--collect-only)` stdout um, damit `--dry-run --output -` sauberes JSON liefert (keine Vermischung mit pytest-Ausgabe).

---

## 3. Verbleibende Unsicherheiten

| Bereich | Unsicherheit | Mitigation |
|---------|--------------|------------|
| **subsystem** | Heuristik bei Mehrdeutigkeit (z.B. test_chat_rag_*) | manual_review_required für Konfliktfälle |
| **covers_replay** | Immer "unknown" ohne bindings | Phase 2: bindings.json auswerten |
| **failure_class** | Nur für Catalog-Einträge | Kein Raten – bewusst auf unknown |
| **Root-Tests** | test_type = unknown | manual_review_required gesetzt |
| **pytest vs. Fallback** | Ohne pytest: Marker fehlen | test_type aus test_domain |

---

## 4. Voraussetzungen für Phase 2 (Coverage Map)

1. **QA_TEST_INVENTORY.json** als Eingabe nutzen
2. **failure_class-Abdeckung** pro Subsystem berechnen (nur catalog_bound zählen)
3. **Gap Detection** gegen Inventar: Welche failure_classes haben keine Tests?
4. **covers_replay** aus bindings.json befüllen (wenn Incident-Replay flächendeckend)
5. **Keine Änderung** an Autopilot v3, Incidents, Replay, Regression Catalog

---

## 5. Freigabe

Phase 1 ist **freigegeben** für:
- Produktive Nutzung des Generators
- Grundlage für Phase 2 (Coverage Map)
- Integration in CI (z.B. `python scripts/qa/build_test_inventory.py` vor Autopilot-Runs)

---

*Review erstellt am 15. März 2026.*
