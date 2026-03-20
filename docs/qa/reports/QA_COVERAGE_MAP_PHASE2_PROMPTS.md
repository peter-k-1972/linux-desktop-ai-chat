# QA Coverage Map Phase 2 – Cursor-Prompts

**Zweck:** Copy-Paste-fähige Prompts für die schrittweise Umsetzung von Phase 2.  
**Referenz:** docs/qa/QA_COVERAGE_MAP_ARCHITECTURE.md

---

## Prompt 1: Grundgerüst

```
Erstelle scripts/qa/build_coverage_map.py und scripts/qa/coverage_map/ als Grundgerüst für Phase 2.

Anforderungen:
- docs/qa/QA_COVERAGE_MAP_ARCHITECTURE.md als Referenz
- Paket: coverage_map/ mit models.py, loader.py, aggregators.py, gap_detection.py, coverage_metrics.py
- CLI: --output, --dry-run, --inventory, --timestamp
- Liest QA_TEST_INVENTORY.json, REGRESSION_CATALOG.md
- Schreibt nur docs/qa/QA_COVERAGE_MAP.json (oder --output)
- Keine Änderung an incidents/*, REGRESSION_CATALOG, Replay
- Determinismus: sort_keys=True, --timestamp
```

---

## Prompt 2: Aggregatoren (Basis)

```
Implementiere scripts/qa/coverage_map/aggregators.py gemäß QA_COVERAGE_MAP_ARCHITECTURE.md Abschnitt 3.

Funktionen:
- aggregate_by_failure_class(inventory, valid_failure_classes) -> dict
- aggregate_by_guard(inventory) -> dict
- aggregate_by_test_domain(inventory) -> dict

Regeln:
- failure_class: nur Tests mit inference_sources.failure_class == "catalog_bound"
- guard: aus guard_types; inferiert
- test_domain: aus test_domain; discovered
- Alle Rückgabewerte: {value: {test_ids: [...], test_count: N, coverage_strength: str, source: str}}
```

---

## Prompt 3: Incident/Binding-Aggregation

```
Implementiere in scripts/qa/coverage_map/aggregators.py:

- aggregate_regression_requirement(inventory, incidents_index, bindings_by_incident) -> dict
- aggregate_replay_binding(inventory, bindings_by_incident) -> dict
- aggregate_autopilot_recommendation(inventory, autopilot_v3) -> dict

Regeln aus QA_COVERAGE_MAP_ARCHITECTURE.md Abschnitt 3.4–3.6.
- regression_test (path::test_name) zu test_id mappen (path:: -> tests_path__)
- Bindings mit status rejected/archived ignorieren
```

---

## Prompt 4: Gap Detection

```
Implementiere scripts/qa/coverage_map/gap_detection.py gemäß QA_COVERAGE_MAP_ARCHITECTURE.md Abschnitt 5.

Funktionen:
- detect_failure_class_gaps(coverage_by_failure_class, valid_failure_classes) -> list[Gap]
- detect_regression_requirement_gaps(regression_requirement_aggregate) -> list[Gap]
- detect_replay_binding_gaps(replay_binding_aggregate) -> list[Gap]
- detect_guard_gaps(coverage_by_guard, pilot_constellations) -> list[Gap]

Gap-Struktur: gap_id, axis, value, severity, expected, actual, evidence, mitigation_hint
```

---

## Prompt 5: Coverage Metrics

```
Implementiere scripts/qa/coverage_map/coverage_metrics.py:

- compute_coverage_strength(test_count, expected_min) -> "covered"|"partial"|"gap"|"n/a"
- compute_axis_quality(aggregate, source_counts) -> "high"|"medium"|"low"
- build_summary(coverage_by_axis, gaps) -> dict

Regeln aus QA_COVERAGE_MAP_ARCHITECTURE.md Abschnitt 4.
```

---

## Prompt 6: Integration

```
Vervollständige scripts/qa/build_coverage_map.py:

- Lade alle Inputs (loader.py)
- Rufe alle Aggregatoren auf
- Führe Gap Detection aus
- Berechne Summary
- Output: QA_COVERAGE_MAP.json Schema

Erstelle docs/qa/schemas/qa_coverage_map.schema.json (JSON Schema).
```

---

## Prompt 7: Tests

```
Erstelle pytest-Suite für coverage_map:

- tests/qa/test_coverage_map/test_aggregators.py
- tests/qa/test_coverage_map/test_gap_detection.py
- tests/qa/test_coverage_map/test_coverage_map_happy_path.py

Fixtures: minimal inventory, minimal incidents, minimal bindings.
Teste: failure_class aggregation, gap detection, determinismus, governance (keine Schreiboperationen außer Output).
```

---

## Reihenfolge (empfohlen)

1. Prompt 1 (Grundgerüst)
2. Prompt 2 (Basis-Aggregatoren)
3. Prompt 5 (Metrics)
4. Prompt 4 (Gap Detection)
5. Prompt 3 (Incident/Binding)
6. Prompt 6 (Integration)
7. Prompt 7 (Tests)
