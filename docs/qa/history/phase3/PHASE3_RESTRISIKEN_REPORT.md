# Phase 3 – Offener Restrisiken-Report

**Datum:** 15. März 2026

---

## 1. Restrisiken

| Risiko | Beschreibung | Mitigation |
|--------|--------------|------------|
| **R1: failure_class Hints zu breit** | Pattern wie `test_chroma_*` könnten falsche Tests matchen | Hints explizit halten; bei False Positives Pattern verfeinern |
| **R2: guard_type Overrides veralten** | Bei Umbenennung von Tests stimmen Patterns nicht mehr | Overrides bei Refactorings prüfen |
| **R3: orphan_breakdown excluded_by_path** | Zählt Tests in tests/qa/, tests/helpers/, tests/meta/ – könnte von whitelisted überlappen | Beide Metriken sind informativ; Überschneidung akzeptabel |
| **R4: Replay-Binding ohne Bindings** | Wenn keine bindings.json existieren, bleibt covers_replay überall "unknown" | Erwartetes Verhalten; Enrichment ist additiv |
| **R5: manual_review_reduced** | _recompute_manual_review setzt false nur wenn alle sources ≠ unknown; viele Tests haben weiterhin unknown | Reduktion begrenzt; mittelfristig explizite Annotationen nötig |
| **R6: Coverage Map Schema** | `prioritized_gaps` ist neues Top-Level-Feld; bestehende Schema-Definitionen könnten es nicht erwarten | Schema ist flexibel (additionalProperties); keine Validierungsfehler |
| **R7: CI-Integration** | generate_gap_report erwartet prioritized_gaps; ältere Coverage Maps haben es nicht | Script prüft `coverage_map.get("prioritized_gaps") or []` – graceful fallback |

---

## 2. Bekannte Einschränkungen

- **catalog_bound aus Hints:** confidence=high setzt inference_sources.failure_class="catalog_bound" – das erhöht die offizielle Coverage. Architektur erlaubt das für "aus REGRESSION_CATALOG abgeleitete" Hints.
- **Orphan-Definition:** Nur root ohne catalog_bound; 130 Orphans (vorher 296). Domain "root" kann Tests aus verschiedenen Pfaden enthalten.
- **Gap-Priorisierung:** incident_bonus + strategy_bonus können sich addieren; Score kann 100 erreichen. Keine Obergrenze außer min(100, score).

---

## 3. Empfohlene Follow-ups

1. **Schema-Validierung:** Optionalen Check für Inventory/Coverage Map gegen JSON-Schema in CI
2. **Hints erweitern:** Weitere file_patterns aus REGRESSION_CATALOG ableiten
3. **Orphan-Review:** Periodische manuelle Prüfung der 130 Review-Kandidaten
4. **Replay-Bindings:** Bei neuen Incidents bindings.json mit regression_test anlegen
