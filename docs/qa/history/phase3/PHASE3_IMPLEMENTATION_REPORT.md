# Phase 3 – Implementierungsbericht

**Datum:** 15. März 2026  
**Status:** Implementierung abgeschlossen

---

## 1. Neue Dateien

| Datei | Zweck |
|-------|-------|
| `docs/qa/phase3_orphan_governance.json` | Orphan-Governance-Konfiguration (Whitelist, Exclusion, Candidate-Domains) |
| `docs/qa/phase3_gap_prioritization.json` | Gap-Priorisierung (Severity-Weights, Bonus-Weights, kritische Subsysteme) |
| `docs/qa/phase3_ci_config.json` | CI-Konfiguration (blocking, warnings, output_paths) |
| `docs/qa/phase3_failure_class_hints.json` | failure_class-Hints für semantische Anreicherung |
| `docs/qa/phase3_guard_type_overrides.json` | guard_type-Overrides |
| `docs/qa/phase3_ci_build_order.md` | Build-Reihenfolge und CI-Snippets |
| `scripts/qa/gap_prioritization.py` | Priorisierungslogik (priority_score, escalation_factors) |
| `scripts/qa/generate_gap_report.py` | Gap-Report-Generator (Markdown, JSON) |
| `scripts/qa/enrich_replay_binding.py` | Replay-Binding-Enrichment für Inventory |
| `scripts/qa/semantic_enrichment.py` | failure_class-Hints, guard_type-Overrides, manual_review |
| `tests/qa/coverage_map/test_gap_prioritization.py` | Tests für Gap-Priorisierung |
| `tests/qa/test_enrich_replay_binding.py` | Tests für Replay-Binding-Enrichment |
| `tests/qa/test_semantic_enrichment.py` | Tests für semantische Anreicherung |

---

## 2. Geänderte Dateien

| Datei | Änderung |
|-------|----------|
| `scripts/qa/coverage_map_rules.py` | `detect_orphan_tests` mit Phase-3-Governance (Whitelist, Exclusion); `compute_orphan_breakdown`; `_load_orphan_governance_config` |
| `scripts/qa/build_coverage_map.py` | Import `compute_orphan_breakdown`, `build_prioritized_gaps`; governance mit `orphan_breakdown`; `prioritized_gaps` im Output |
| `scripts/qa/build_test_inventory.py` | Aufruf `apply_semantic_enrichment` nach `output.to_dict()` |
| `tests/qa/coverage_map/test_coverage_map_gaps.py` | Orphan-Tests angepasst: `test_detect_orphan_tests_meta_domains_whitelisted`, `test_detect_orphan_tests_root_without_catalog_bound_is_orphan` |

---

## 3. Bewusst nicht geänderte Artefakte

| Artefakt | Begründung |
|----------|------------|
| `docs/qa/incidents/*` | Keine Änderung an Incidents |
| `docs/qa/incidents/*/bindings.json` | Keine Änderung an Bindings (nur gelesen) |
| Replay-Dateien | Keine Änderung |
| `docs/qa/REGRESSION_CATALOG.md` | Keine Änderung |
| `docs/qa/QA_COVERAGE_MAP.json` (Schema) | prioritized_gaps ist additive Erweiterung |
| `docs/qa/QA_TEST_INVENTORY.json` (Schema) | covers_replay, replay_ids existieren bereits |

---

## 4. Technische Doku je Teilbereich

### Teil 1: Orphan-Governance

- **Konfiguration:** `phase3_orphan_governance.json`
- **Logik:** `detect_orphan_tests()` liest Config; Whitelist (qa, helpers, meta); Exclusion-Pfade; nur root ohne catalog_bound = orphan
- **Output:** `governance.orphan_breakdown`, `orphan_treat_as`, `orphan_ci_blocking`

### Teil 2: Gap-Priorisierung

- **Konfiguration:** `phase3_gap_prioritization.json`
- **Logik:** `compute_gap_priority()` pro Gap; Eskalation: incident, strategy, autopilot, critical_subsystem
- **Output:** `prioritized_gaps` (sortiert nach priority_score)

### Teil 3: CI-Integration

- **Build-Reihenfolge:** pytest → build_test_inventory → enrich_replay_binding (optional) → build_coverage_map → generate_gap_report
- **Blockierend:** pytest; Schema-Validierung (optional)
- **Nicht blockierend:** Gap-Schwellen, orphan backlog

### Teil 4: Replay-Binding-Enrichment

- **Input:** Inventory, bindings_by_incident
- **Output:** Inventory mit `covers_replay`, `replay_ids` (nur wo Binding mit regression_test+replay_id)

### Teil 5: Semantische Anreicherung

- **Hints:** `phase3_failure_class_hints.json` – file_patterns, test_name_patterns
- **Overrides:** `phase3_guard_type_overrides.json` – test_id_pattern → guard_types
- **Integration:** `apply_semantic_enrichment()` in build_test_inventory

---

## 5. pytest-Absicherung

- 241 QA-Tests bestanden
- Neue Tests: test_gap_prioritization (4), test_enrich_replay_binding (3), test_semantic_enrichment (4)
- Bestehende Orphan-Tests angepasst
