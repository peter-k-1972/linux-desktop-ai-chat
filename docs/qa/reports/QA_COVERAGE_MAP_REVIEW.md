# QA Coverage Map – Phase 2 Review-Report

**Datum:** 15. März 2026  
**Status:** Phase 2 abgeschlossen  
**Reifegrad:** Release-fähig für Phase 2

---

## 1. Reifegrad der Coverage-Map

| Kriterium | Status | Anmerkung |
|-----------|--------|-----------|
| **Input-Verarbeitung** | ✅ | Inventory, Strategy, Graph, Autopilot werden korrekt geladen |
| **Aggregationslogik** | ✅ | failure_class, guard, test_domain, regression_requirement, replay_binding, autopilot_recommendation |
| **Coverage Strength** | ✅ | covered, partial, gap, n/a nachvollziehbar |
| **Coverage Quality** | ✅ | high, medium, low mit manual_review-Einfluss |
| **Gap Detection** | ✅ | failure_class_uncovered, guard_missing, regression_requirement_unbound, replay_unbound, semantic_binding_gap, orphan_test |
| **Governance** | ✅ | Keine Mutation von Input-Artefakten; deterministisch |

---

## 2. pytest-Suite

| Datei | Fokus |
|-------|-------|
| `tests/qa/coverage_map/test_coverage_map_loader.py` | Input-Verarbeitung, load_json, load_inventory, load_all_inputs |
| `tests/qa/coverage_map/test_coverage_map_aggregation.py` | failure_class, guard, test_domain, regression_requirement, replay_binding, autopilot_recommendation |
| `tests/qa/coverage_map/test_coverage_map_strength.py` | coverage_strength (covered/partial/gap/n/a), coverage_quality |
| `tests/qa/coverage_map/test_coverage_map_gaps.py` | Gap Detection, orphan_tests, semantic_binding_gaps, build_gap_types |
| `tests/qa/coverage_map/test_coverage_map_governance.py` | Keine Mutation, Determinismus, dry-run |

**Ausführung:**
```bash
pytest tests/qa/coverage_map/ -v
```

**Stand:** 46 Tests, alle bestanden.

---

## 3. Bekannte Unsicherheiten

| Bereich | Unsicherheit | Mitigation |
|---------|--------------|------------|
| **failure_class** | Nur catalog_bound zählt; 26/550 Tests im aktuellen Inventar | Keine Halluzination; Gaps nur für definierte failure_classes |
| **guard_types** | Inferiert aus test_type; kein Marker-basiertes Discovery | coverage_quality = medium für guard-Axis |
| **regression_requirement** | Abhängig von Strategy/Bindings; ohne Bindings keine Abdeckung | Optional; Fallback leer |
| **autopilot_recommendation** | Heuristischer Abgleich subsystem + failure_class + guard | Kann falsch-negativ sein |
| **orphan_tests** | Definition (root/helpers/qa) kann zu vielen False Positives führen | Dokumentiert; nicht zwangsläufig schlecht |
| **covers_replay** | Immer unknown im Inventar | Phase 3: Bindings-Integration vertiefen |

---

## 4. Terminologie-Mapping

Die Architektur verwendet folgende Werte (nicht die in der Aufgabenstellung genannten):

| Aufgabenstellung | Implementierung |
|------------------|-----------------|
| none / weak / medium / strong / robust | covered / partial / gap / n/a |
| high_confidence / mixed / inference_only / manual_review_required | high / medium / low |
| uncovered | gap, failure_class_uncovered, guard_missing, etc. |
| undercovered | partial |
| semantic_binding_gap | semantic_binding_gaps (governance) |
| orphan_test | orphan_tests (governance) |

---

## 5. Empfehlungen für Phase 3

1. **covers_replay befüllen:** Aus bindings.json regression_test → Inventar-Test mappen; covers_replay = "yes"/"no" setzen.

2. **Integration in CI:** `build_coverage_map.py` vor/nach Autopilot-Runs ausführen; QA_COVERAGE_MAP.json als Artefakt archivieren.

3. **Gap-Priorisierung:** severity aus Incident-Severity oder Strategy-Priority ableiten; high/medium/low verfeinern.

4. **Semantic Binding Gaps:** Knowledge Graph validated_by-Kanten regelmäßig gegen Inventar prüfen; bei Abweichung Warnung.

5. **Orphan-Review:** Periodische manuelle Prüfung von orphan_tests; Bereinigung oder Catalog-Eintrag.

6. **Keine Änderung:** Autopilot v3, Incidents, Replay, Regression Catalog, Test Strategy, Knowledge Graph bleiben unverändert.

---

## 6. Freigabe

Phase 2 ist **freigegeben** für:
- Produktive Nutzung des Coverage-Map-Generators
- Integration in CI
- Grundlage für Phase 3 (z.B. covers_replay, Gap-Priorisierung)

---

*Review erstellt am 15. März 2026.*
