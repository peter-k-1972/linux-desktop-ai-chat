# QA Coverage Map – Mapping-Regeln

**Datum:** 15. März 2026  
**Status:** Verbindlich  
**Zweck:** Nachvollziehbare Regeln für coverage_strength, coverage_quality, gap_types, orphan_tests, semantic_binding_gaps.

**Referenz:** QA_COVERAGE_MAP_ARCHITECTURE.md

---

## 1. coverage_strength

### 1.1 Definition

`coverage_strength` bewertet pro Axis/Wert, ob eine Anforderung erfüllt ist.

### 1.2 Werte

| Wert | Bedeutung | Bedingung |
|------|-----------|-----------|
| **covered** | Voll abgedeckt | test_count ≥ expected_min |
| **partial** | Teilweise | 0 < test_count < expected_min |
| **gap** | Lücke | test_count = 0, obwohl expected_min > 0 |
| **n/a** | Nicht anwendbar | Keine Anforderung für diesen Wert |

### 1.3 Regeln pro Axis

| Axis | expected_min | Quelle |
|------|--------------|--------|
| **failure_class** | 1 | Jede in REGRESSION_CATALOG definierte failure_class erwartet ≥1 catalog_bound Test |
| **guard** | 1 | Jeder in PILOT_CONSTELLATIONS genannte guard_type erwartet ≥1 Test |
| **test_domain** | 0 | Keine Mindestanforderung; nur Zählung |
| **regression_requirement** | 1 pro Incident | regression_required=true → regression_test erwartet |
| **replay_binding** | 1 pro Replay | replay vorhanden → regression_test in bindings erwartet |
| **autopilot_recommendation** | 1 pro Backlog-Item | Empfehlung → passender Test erwartet |

### 1.4 Formel

```
coverage_strength(value) =
  if expected_min == 0: "n/a"
  elif test_count >= expected_min: "covered"
  elif test_count > 0: "partial"
  else: "gap"
```

---

## 2. coverage_quality

### 2.1 Definition

`coverage_quality` bewertet die Zuverlässigkeit der Aggregation pro Axis (nicht die Testqualität).

### 2.2 Werte

| Wert | Bedeutung | Bedingung |
|------|-----------|-----------|
| **high** | Belastbar | Alle Werte discovered oder catalog_bound |
| **medium** | Teilweise inferiert | Mix aus discovered/catalog_bound und inferred |
| **low** | Unsicher | > 30 % unknown oder manual_review_required |

### 2.3 Regeln pro Axis

| Axis | Quelle | Qualität |
|------|--------|----------|
| **failure_class** | inference_sources.failure_class | high (nur catalog_bound zählt) |
| **guard** | guard_types aus test_type | medium (inferiert) |
| **test_domain** | test_domain aus Pfad | high (discovered) |
| **regression_requirement** | bindings.regression_test | high (explizit) |
| **replay_binding** | bindings.regression_test | high (explizit) |
| **autopilot_recommendation** | Abgleich subsystem/failure_class/guard | medium (heuristisch) |

### 2.4 Formel (pro Axis)

```
quality(axis) =
  if all source in {discovered, catalog_bound}: "high"
  elif any source == "inferred" and unknown_share <= 0.3: "medium"
  else: "low"
```

### 2.5 Einfluss von manual_review_required

Wenn `manual_review_required_count / total_tests > 0.3`: Axis-Qualität maximal **medium**, auch wenn sonst high.

---

## 3. manual_review_required

### 3.1 Quelle

QA_TEST_INVENTORY.tests[].manual_review_required

### 3.2 Inventar-Regel (Phase 1)

Test erfordert manuelle Prüfung wenn:
- `test_domain in {root, helpers}` ODER
- `test_domain == "unit"` UND generischer Name (test_parse, test_validate, test_run, test_foo, test_bar) ODER
- `subsystem == null` UND `test_domain != "qa"`

### 3.3 Coverage-Map-Ausgabe

```json
"governance": {
  "manual_review_required": {
    "count": 138,
    "test_ids": ["tests_root_test_foo.py__test_bar", ...],
    "share_of_total": 0.25
  }
}
```

### 3.4 Einfluss auf summary

- `summary.manual_review_required_count`: Übernahme aus Inventar
- `coverage_quality` pro Axis: Reduktion auf medium/low wenn share > 0.3

---

## 4. gap_types

### 4.1 Definition

Kategorien von Lücken für maschinenlesbare Auswertung und Priorisierung.

### 4.2 Gap-Typen

| gap_type | axis | Bedeutung |
|----------|------|-----------|
| **failure_class_uncovered** | failure_class | failure_class in REGRESSION_CATALOG, kein catalog_bound Test |
| **guard_missing** | guard | Guard in Pilot/Strategy erwartet, kein Test |
| **regression_requirement_unbound** | regression_requirement | Incident regression_required, kein regression_test in bindings |
| **replay_unbound** | replay_binding | Replay vorhanden, kein regression_test in bindings |
| **autopilot_recommendation_uncovered** | autopilot_recommendation | Backlog-Item, kein passender Test |

### 4.3 Ausgabe

```json
"summary": {
  "gap_types": {
    "failure_class_uncovered": 3,
    "guard_missing": 1,
    "regression_requirement_unbound": 2,
    "replay_unbound": 2,
    "autopilot_recommendation_uncovered": 1
  }
}
```

### 4.4 Mapping gap → gap_type

| axis | gap_type |
|------|----------|
| failure_class | failure_class_uncovered |
| guard | guard_missing |
| regression_requirement | regression_requirement_unbound |
| replay_binding | replay_unbound |
| autopilot_recommendation | autopilot_recommendation_uncovered |

---

## 5. orphan_tests

### 5.1 Definition

Tests, die keiner bekannten Anforderung (failure_class, regression, replay, recommended_focus) zugeordnet sind.

### 5.2 Kriterien (OR – mindestens eines erfüllt)

| Kriterium | Bedingung |
|-----------|-----------|
| **kein_catalog_bound** | failure_classes leer ODER inference_sources.failure_class != "catalog_bound" |
| **kein_regression_binding** | regression_ids leer UND (kein bindings ODER regression_test fehlt) |
| **meta_domain** | test_domain in {root, helpers, qa} |
| **subsystem_unknown** | subsystem == null UND test_domain nicht in {failure_modes, contracts, async_behavior, ...} |

### 5.3 Einschränkung

**Nicht als orphan zählen:** Tests in test_domain {unit, integration, smoke, ui}, auch ohne failure_class. Diese können legitime Tests sein.

### 5.4 Ausgabe

```json
"governance": {
  "orphan_tests": [
    {
      "test_id": "tests_root_test_foo.py__test_bar",
      "reason": "test_domain=root, no catalog_bound failure_class"
    }
  ],
  "orphan_count": 42
}
```

### 5.5 Regel (operativ)

```
orphan(test) =
  (test_domain in {root, helpers, qa})
  OR
  (failure_classes leer AND inference_sources.failure_class != "catalog_bound"
   AND test_domain in {root, helpers})
```

---

## 6. semantic_binding_gaps

### 6.1 Definition

Inkonsistenzen zwischen QA_KNOWLEDGE_GRAPH (validated_by: failure_class → test_domain) und QA_TEST_INVENTORY.

### 6.2 Quelle

QA_KNOWLEDGE_GRAPH.edges mit `edge_type == "validated_by"`:
- source: `failure_class:X`
- target: `test_domain:Y`

Bedeutung: failure_class X wird typischerweise durch Tests in domain Y validiert.

### 6.3 Regel

Für jede validated_by-Kante (X → Y):
- Zähle Tests in Inventar mit `failure_classes` enthält X (catalog_bound) UND `test_domain == Y`
- Wenn count == 0: **semantic_binding_gap**

### 6.4 Ausgabe

```json
"governance": {
  "semantic_binding_gaps": [
    {
      "failure_class": "ui_state_drift",
      "expected_test_domain": "async_behavior",
      "actual_test_count": 0,
      "evidence": "Knowledge Graph validated_by: ui_state_drift → async_behavior; no catalog_bound test in async_behavior"
    }
  ],
  "semantic_binding_gap_count": 1
}
```

### 6.5 Abgrenzung

- **semantic_binding_gap** ≠ **failure_class gap**:  
  failure_class gap = X hat gar keinen Test.  
  semantic_binding_gap = X hat Tests, aber nicht in der vom Knowledge Graph erwarteten domain.

---

## 7. Übersicht: Regel-Sicherheit

| Regel | Sicher | Heuristisch | Begründung |
|-------|--------|-------------|------------|
| coverage_strength (failure_class) | ✓ | | expected_min aus REGRESSION_CATALOG |
| coverage_strength (guard) | | ✓ | Pilot-Konstellationen können sich ändern |
| coverage_quality | | ✓ | Abhängig von inference_sources; manual_review Anteil |
| orphan_tests | | ✓ | Definition von „orphan“ ist konfigurierbar |
| semantic_binding_gaps | ✓ | | validated_by explizit; catalog_bound belastbar |
| gap_types | ✓ | | 1:1 Mapping axis → gap_type |

---

*Mapping-Regeln verbindlich ab 15. März 2026.*
