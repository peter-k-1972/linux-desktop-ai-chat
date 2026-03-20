# QA Coverage Map – Generator-Dokumentation

**Datum:** 15. März 2026  
**Phase:** 2 – Learning-QA-Architektur  
**Status:** Implementiert

---

## 1. Übersicht

Der Coverage-Map-Generator liest QA-Artefakte, aggregiert Coverage, erkennt Gaps und schreibt `docs/qa/QA_COVERAGE_MAP.json`. Reine Read/Aggregation-Pipeline, keine Seiteneffekte.

---

## 2. Dateien

| Datei | Zweck |
|-------|-------|
| `scripts/qa/build_coverage_map.py` | CLI, Orchestrierung |
| `scripts/qa/coverage_map_loader.py` | Laden aller Input-Artefakte |
| `scripts/qa/coverage_map_rules.py` | Aggregation, Strength, Quality, Gaps, Orphans, Semantic Binding Gaps |

---

## 3. Verwendung

```bash
# Standard: schreibt docs/qa/QA_COVERAGE_MAP.json
python scripts/qa/build_coverage_map.py

# Dry-Run: Ausgabe auf stdout
python scripts/qa/build_coverage_map.py --dry-run

# stdout als Output
python scripts/qa/build_coverage_map.py --output -

# Reproduzierbarer Lauf
python scripts/qa/build_coverage_map.py --timestamp 2026-03-15T12:00:00Z

# Anderes qa-Verzeichnis
python scripts/qa/build_coverage_map.py --qa-dir /path/to/docs/qa
```

---

## 4. Inputs

| Input | Pflicht | Fallback bei Fehlen |
|-------|---------|---------------------|
| `docs/qa/QA_TEST_INVENTORY.json` | **ja** | Abbruch (FileNotFoundError) |
| `docs/qa/QA_TEST_STRATEGY.json` | nein | Leere regression_requirements, guard_requirements |
| `docs/qa/QA_KNOWLEDGE_GRAPH.json` | nein | Keine semantic_binding_gaps |
| `docs/qa/QA_AUTOPILOT_V3.json` | nein | Leere autopilot_recommendation |
| `docs/qa/incidents/index.json` | nein | Nicht verwendet (Strategy/Autopilot liefern regression_requirements) |
| `docs/qa/incidents/analytics.json` | nein | Nicht verwendet |
| `docs/qa/incidents/*/bindings.json` | nein | Leere replay_binding, regression_requirement (ohne regression_test) |

---

## 5. Annahmen

1. **Inventory ist autoritativ:** Alle Test-Referenzen (test_id, pytest_nodeid) kommen aus dem Inventar. Keine Halluzination von Tests.

2. **failure_class nur catalog_bound:** Nur Tests mit `inference_sources.failure_class == "catalog_bound"` zählen in der failure_class-Aggregation. Keine Raten.

3. **regression_test-Format:** `path::test_name` (z.B. `tests/failure_modes/test_foo.py::test_bar`). Wird zu test_id gemappt via `path.replace("/","_").replace("::","__")`.

4. **Bindings:** rejected/archived werden ignoriert. Nur bindings mit `regression_catalog.regression_test` fließen in replay_binding ein.

5. **Determinismus:** `sort_keys=True` bei JSON; sortierte Iteration über failure_classes, guard_types, test_domains.

6. **Orphan-Definition:** test_domain ∈ {root, helpers, qa} ODER (kein catalog_bound UND test_domain ∈ {root, helpers}).

7. **Semantic Binding Gaps:** Aus QA_KNOWLEDGE_GRAPH.edges (validated_by). failure_class X → test_domain Y, aber keine catalog_bound Tests für X in Y.

---

## 6. Output-Struktur

- **coverage_by_axis:** failure_class, guard, test_domain, regression_requirement, replay_binding, autopilot_recommendation
- **gaps:** failure_class, guard, regression_requirement, replay_binding
- **governance:** orphan_tests, semantic_binding_gaps, manual_review_required
- **summary:** total_tests, coverage_strength, coverage_quality, gap_count, gap_types

---

## 7. Governance

- **Read-only:** Liest nur; schreibt nur QA_COVERAGE_MAP.json (oder --output)
- **Keine Mutation:** Inventory, Strategy, Graph, Autopilot, Incidents unverändert
- **Transparenz:** inference_sources (catalog_bound, inferred, discovered) in Aggregationen
- **Summary-Counts:** Nachvollziehbar aus Aggregationen; keine geschätzten Werte

---

*Dokumentation erstellt am 15. März 2026.*
