# QA Coverage Map – Phase 2 Architektur

**Datum:** 15. März 2026  
**Phase:** 2 – Coverage Map  
**Status:** Architekturentwurf  
**Zweck:** Governance-Schicht für Coverage-Aggregation, Gap Detection und Qualitätsbewertung – auf Basis bestehender QA-Artefakte.

---

## 1. Input-Artefakte – Analyse

### 1.1 QA_TEST_INVENTORY.json

| Aspekt | Befund |
|--------|--------|
| **Struktur** | tests[], summary (by_subsystem, by_test_domain, by_test_type), test_count |
| **Pro Test** | test_id, pytest_nodeid, file_path, test_name, test_domain, test_type, subsystem, failure_classes, guard_types, covers_regression, covers_replay, manual_review_required, inference_sources, inference_confidence |
| **Belastbarkeit** | pytest_nodeid, file_path, test_domain: hoch. failure_classes: nur catalog_bound belastbar (26/550). subsystem: 204× unknown. covers_replay: immer unknown. |
| **Governance-Relevanz** | Single Source of Truth für Testlandschaft; Basis für alle Aggregationen |

### 1.2 QA_TEST_STRATEGY.json

| Aspekt | Befund |
|--------|--------|
| **Struktur** | guard_requirements[], recommended_focus_domains[], regression_requirements[], test_domains[], supporting_evidence |
| **Quellen** | QA_AUTOPILOT_V3, QA_CONTROL_CENTER |
| **regression_requirements** | incident_id, failure_class, subsystem, priority, reasons (z.B. "Binding status: open") |
| **guard_requirements** | failure_class, guard_type, subsystem, pilot_id |
| **test_domains** | domain, failure_classes[], subsystems[], priority, recommendation_count |
| **Governance-Relevanz** | Aggregierte Sicht auf Anforderungen; kann Coverage Map validieren (recommended_focus_domains vs. tatsächliche Tests) |

### 1.3 QA_KNOWLEDGE_GRAPH.json

| Aspekt | Befund |
|--------|--------|
| **Struktur** | nodes[], edges[] |
| **Node-Typen** | failure_class, incident, guard, regression_requirement, test_domain |
| **Edge-Typen** | incident_failure, recommended_test, requires_guard, requires_regression, validated_by |
| **validated_by** | failure_class → test_domain (z.B. ui_state_drift → async_behavior, contracts, regression) |
| **Governance-Relevanz** | Semantische Bindungen; failure_class ↔ test_domain; Prüfung von semantic_binding_gaps |

### 1.4 QA_AUTOPILOT_V3.json

| Aspekt | Befund |
|--------|--------|
| **Struktur** | recommended_test_backlog[], guard_gap_findings[], test_gap_findings[], translation_gap_findings[] |
| **recommended_test_backlog** | subsystem, failure_class, guard_type, test_domain, test_type, title |
| **translation_gap_findings** | incident_not_bound_to_replay, incident_not_bound_to_regression |
| **Governance-Relevanz** | Empfehlungen für fehlende Tests; Abgleich mit Inventar → Coverage |

---

## 2. Zielstruktur QA_COVERAGE_MAP.json

### 2.1 Top-Level

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-03-15T12:00:00Z",
  "generator": "coverage_map",
  "input_sources": [
    "docs/qa/QA_TEST_INVENTORY.json",
    "docs/qa/QA_TEST_STRATEGY.json",
    "docs/qa/QA_KNOWLEDGE_GRAPH.json",
    "docs/qa/QA_AUTOPILOT_V3.json"
  ],
  "inventory_snapshot": {
    "test_count": 550,
    "manual_review_required_count": 138,
    "generated_at": "2026-01-01T00:00:00Z"
  },
  "coverage_by_axis": {
    "failure_class": { ... },
    "guard": { ... },
    "test_domain": { ... },
    "regression_requirement": { ... },
    "replay_binding": { ... },
    "autopilot_recommendation": { ... }
  },
  "gaps": {
    "failure_class": [ ... ],
    "guard": [ ... ],
    "regression_requirement": [ ... ],
    "replay_binding": [ ... ]
  },
  "governance": {
    "orphan_tests": [ ... ],
    "semantic_binding_gaps": [ ... ],
    "manual_review_required": {
      "count": 138,
      "test_ids": [ ... ]
    }
  },
  "summary": {
    "total_tests": 550,
    "coverage_strength": { ... },
    "coverage_quality": { ... },
    "gap_count": { ... },
    "gap_types": { ... }
  }
}
```

### 2.2 Sektionsübersicht

| Sektion | Zweck |
|---------|-------|
| **coverage_by_axis** | Pro Dimension: welche Tests decken welche Werte ab |
| **gaps** | Maschinenlesbare Lücken pro Axis |
| **governance** | orphan_tests, semantic_binding_gaps, manual_review_required |
| **summary** | Aggregierte Metriken, coverage_strength, coverage_quality, gap_types |

---

## 3. Aggregationssichten

### 3.1 failure_class → tests

**Quelle:** QA_TEST_INVENTORY.tests[].failure_classes  
**Regel:** Nur `inference_sources.failure_class == "catalog_bound"` zählt.  
**Referenz:** VALID_FAILURE_CLASSES / REGRESSION_CATALOG.

### 3.2 guard → tests

**Quelle:** QA_TEST_INVENTORY.tests[].guard_types  
**Regel:** Aus test_type inferiert (GUARD_TYPE_MAP).  
**Guard-Typen:** failure_replay_guard, event_contract_guard, startup_degradation_guard.

### 3.3 test_domain → tests

**Quelle:** QA_TEST_INVENTORY.tests[].test_domain  
**Regel:** Direkt aus Pfad; discoverbar.

### 3.4 regression_requirement → tests

**Quelle:** QA_TEST_STRATEGY.regression_requirements, QA_AUTOPILOT_V3.translation_gap_findings (incident_not_bound_to_regression), incidents/*/bindings.json (regression_test).  
**Regel:** regression_test (path::test_name) → test_id; Abgleich mit Inventar.

### 3.5 replay_binding → tests

**Quelle:** incidents/*/bindings.json (regression_catalog.regression_test).  
**Regel:** Binding mit regression_test → test_id; rejected/archived ignorieren.

### 3.6 autopilot_recommendation → tests

**Quelle:** QA_AUTOPILOT_V3.recommended_test_backlog.  
**Regel:** Abgleich: test.subsystem == item.subsystem UND item.failure_class in test.failure_classes UND item.guard_type in test.guard_types.

---

## 4. Governance-Konzepte

### 4.1 manual_review_required

**Quelle:** QA_TEST_INVENTORY.tests[].manual_review_required  
**Regel:** Test erfordert manuelle Prüfung (root, helpers, generische unit-Namen, subsystem unknown).  
**Ausgabe:** governance.manual_review_required.count, governance.manual_review_required.test_ids  
**Einfluss:** coverage_quality = low wenn > 30 % manual_review_required.

### 4.2 orphan_tests

**Definition:** Tests, die keiner bekannten Anforderung zugeordnet sind.  
**Regel:** Test ist orphan wenn:  
- Kein failure_class (catalog_bound) UND  
- Kein regression_ids/replay_ids (wenn Bindings vorhanden) UND  
- test_domain ∈ {root, helpers, qa} (Meta-Tests)  
**Ausgabe:** governance.orphan_tests[] (test_id, reason)  
**Hinweis:** Nicht zwangsläufig schlecht – z.B. unit-Tests ohne Catalog-Eintrag.

### 4.3 semantic_binding_gaps

**Definition:** Inkonsistenzen zwischen Knowledge Graph und Inventar.  
**Quelle:** QA_KNOWLEDGE_GRAPH.edges (validated_by: failure_class → test_domain)  
**Regel:** failure_class X validiert_by test_domain Y, aber Inventar hat für X keine Tests in domain Y (catalog_bound).  
**Ausgabe:** governance.semantic_binding_gaps[] (failure_class, expected_test_domain, actual_test_count)  
**Governance:** Zeigt Lücken zwischen erwarteter und tatsächlicher Abdeckung.

### 4.4 gap_types

**Definition:** Kategorien von Lücken für maschinenlesbare Auswertung.  
**Werte:** siehe QA_COVERAGE_MAP_MAPPING_RULES.md.

---

## 5. Regeln (Übersicht)

| Regel | Dokument |
|-------|----------|
| coverage_strength | QA_COVERAGE_MAP_MAPPING_RULES.md §1 |
| coverage_quality | QA_COVERAGE_MAP_MAPPING_RULES.md §2 |
| manual_review_required | QA_COVERAGE_MAP_MAPPING_RULES.md §3 |
| gap_types | QA_COVERAGE_MAP_MAPPING_RULES.md §4 |
| orphan_tests | QA_COVERAGE_MAP_MAPPING_RULES.md §5 |
| semantic_binding_gaps | QA_COVERAGE_MAP_MAPPING_RULES.md §6 |

---

## 6. Governance-Prinzipien

| Prinzip | Beschreibung |
|---------|--------------|
| **Read-only** | Coverage Map liest nur; schreibt nur QA_COVERAGE_MAP.json |
| **Keine Mutation** | incidents/*, REGRESSION_CATALOG, Replay, Autopilot, Test Strategy, Knowledge Graph unverändert |
| **Determinismus** | sort_keys=True; sortierte Iteration; --timestamp |
| **Transparenz** | inference_sources/catalog_bound vs. inferred vs. unknown dokumentiert |
| **Kein Scope Creep** | Keine neuen Tests, kein Inventory-Redesign, keine Featureentwicklung |

---

## 7. Zusammenfassung: Inputs, Lücken, Regel-Sicherheit

### 7.1 Zwingend benötigte Inputs

| Input | Pflicht | Begründung |
|-------|---------|------------|
| **QA_TEST_INVENTORY.json** | **ja** | Basis für alle Aggregationen; ohne Abbruch |
| **REGRESSION_CATALOG.md** | **ja** | failure_class-Definition; VALID_FAILURE_CLASSES |
| **QA_TEST_STRATEGY.json** | nein | regression_requirements, recommended_focus; Fallback: leer |
| **QA_KNOWLEDGE_GRAPH.json** | nein | semantic_binding_gaps; Fallback: leer |
| **QA_AUTOPILOT_V3.json** | nein | autopilot_recommendation; Fallback: leer |
| **incidents/index.json** | nein | regression_requirement; Fallback: aus TEST_STRATEGY |
| **incidents/*/bindings.json** | nein | replay_binding; Fallback: leer |

### 7.2 Phase-1-Lücken, die Phase-2-Qualität begrenzen

| Lücke | Auswirkung | Mitigation |
|-------|------------|------------|
| **failure_class nur catalog_bound** | 26/550 Tests; Rest unbekannt | Coverage nur für catalog_bound; Gaps nur für definierte failure_classes |
| **covers_replay unknown** | Replay-Binding nicht aus Inventar | Bindings extern laden; regression_test → test_id |
| **subsystem 204× unknown** | Subsystem-Aggregation unvollständig | unknown als eigene Kategorie; keine Heuristik |
| **regression_ids/replay_ids leer** | Kein direkter Link zu Incidents | Phase 2: Bindings/Strategy als Brücke |
| **manual_review_required 138** | Qualitätsbewertung eingeschränkt | coverage_quality = low wenn Anteil hoch |

### 7.3 Mapping-Regeln: sicher vs. heuristisch

| Regel | Sicherheit | Begründung |
|-------|-----------|------------|
| **failure_class (catalog_bound)** | **sicher** | REGRESSION_CATALOG autoritativ |
| **test_domain** | **sicher** | Pfad-basiert; discoverbar |
| **covers_regression** | **sicher** | Marker/domain |
| **guard_types** | **heuristisch** | Aus test_type inferiert; GUARD_TYPE_MAP |
| **subsystem** | **heuristisch** | Dateiname/Testname; 204× unknown |
| **regression_requirement → test** | **sicher** | regression_test explizit in bindings |
| **replay_binding → test** | **sicher** | regression_test explizit |
| **autopilot_recommendation → test** | **heuristisch** | Abgleich subsystem + failure_class + guard; kann falsch-negativ |
| **orphan_tests** | **heuristisch** | Definition von „orphan“ abhängig von Kriterien |
| **semantic_binding_gaps** | **sicher** | Knowledge Graph validated_by; Inventar catalog_bound |

---

*Architektur erstellt am 15. März 2026. Governance-Schicht – keine Featureentwicklung.*
