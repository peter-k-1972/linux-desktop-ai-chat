# Phase 3 – Technische Dokumentation

**Datum:** 15. März 2026

---

## Teil 1: Orphan-Governance

### Konfiguration

`docs/qa/phase3_orphan_governance.json`:

- `orphan_whitelist_domains`: Tests in qa, helpers, meta sind nie orphan
- `orphan_exclusion_paths`: Pfade die nie als orphan zählen
- `orphan_candidate_domains`: Nur root wird auf orphan geprüft
- `treat_as`: "review_candidate"
- `ci_blocking`: false

### API

```python
from scripts.qa.coverage_map_rules import detect_orphan_tests, compute_orphan_breakdown

orphans = detect_orphan_tests(inventory, config=None, qa_dir=Path)
breakdown = compute_orphan_breakdown(inventory, orphans, config=None, qa_dir=Path)
```

---

## Teil 2: Gap-Priorisierung

### Konfiguration

`docs/qa/phase3_gap_prioritization.json`:

- `critical_subsystems`: Startup/Bootstrap, RAG, Chat, Provider/Ollama
- `severity_weights`: critical=40, high=30, medium=20, low=10
- `bonus_weights`: incident=25, strategy=15, autopilot=10, subsystem=10

### API

```python
from scripts.qa.gap_prioritization import compute_gap_priority, build_prioritized_gaps

enriched = compute_gap_priority(gap, context, config=None)
prioritized = build_prioritized_gaps(gaps, governance, context, config=None)
```

---

## Teil 3: CI-Integration

### Build-Reihenfolge

1. `pytest -m "not live and not slow"`
2. `python scripts/qa/build_test_inventory.py`
3. `python scripts/qa/enrich_replay_binding.py` (optional)
4. `python scripts/qa/build_coverage_map.py`
5. `python scripts/qa/generate_gap_report.py --format both`

### generate_gap_report.py

```
--format markdown|json|both
--output PATH
--coverage-map PATH
--top N
```

---

## Teil 4: Replay-Binding-Enrichment

### API

```python
from scripts.qa.enrich_replay_binding import enrich_inventory

enriched, trace = enrich_inventory(inventory, bindings_by_incident)
```

### CLI

```
python scripts/qa/enrich_replay_binding.py
python scripts/qa/enrich_replay_binding.py --dry-run
python scripts/qa/enrich_replay_binding.py --trace qa_replay_binding_trace.json
```

---

## Teil 5: Semantische Anreicherung

### Konfiguration

- `phase3_failure_class_hints.json`: file_patterns, test_name_patterns
- `phase3_guard_type_overrides.json`: overrides mit test_id_pattern → guard_types

### API

```python
from scripts.qa.semantic_enrichment import apply_semantic_enrichment

stats = apply_semantic_enrichment(inventory, qa_dir=Path)
# stats: {"failure_class_hints": n, "guard_type_overrides": n, "manual_review_reduced": n}
```

### Integration

Wird automatisch in `build_test_inventory` nach `output.to_dict()` aufgerufen.
