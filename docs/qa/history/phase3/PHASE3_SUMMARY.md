# Phase 3 – Zusammenfassung und Roadmap

**Datum:** 15. März 2026  
**Status:** Architektur-Entwurf abgeschlossen

---

## Erstellte Dokumente

| Dokument | Inhalt |
|----------|--------|
| [PHASE3_REPLAY_BINDING_ARCHITECTURE.md](./PHASE3_REPLAY_BINDING_ARCHITECTURE.md) | Replay-/Binding-Anreicherung; covers_replay aus Bindings |
| [PHASE3_SEMANTIC_ENRICHMENT_PLAN.md](./PHASE3_SEMANTIC_ENRICHMENT_PLAN.md) | failure_class, guard_types, manual_review_required |
| [PHASE3_ORPHAN_REVIEW_GOVERNANCE.md](./PHASE3_ORPHAN_REVIEW_GOVERNANCE.md) | orphan_tests als Review-Kandidaten; False-Positive-Reduktion |
| [PHASE3_CI_INTEGRATION_PLAN.md](./PHASE3_CI_INTEGRATION_PLAN.md) | Build-Zeitpunkt; blockierende vs. nicht blockierende Checks |
| [PHASE3_GAP_PRIORITIZATION.md](./PHASE3_GAP_PRIORITIZATION.md) | Severity-Regeln; Priorisierung nach Incident, Strategy, Subsystem |

---

## Kurzfristig möglich (ohne explizite Annotationen)

| Maßnahme | Aufwand | Wirkung |
|----------|---------|---------|
| **Orphan-Governance** | Konfigurationsdatei + Anpassung detect_orphan_tests | Reduktion von 296 auf ~40–80 Orphans; weniger False Positives |
| **Replay-Binding-Enrichment** | Script, das Bindings liest und Inventory anreichert | covers_replay von "unknown" auf "yes" wo Bindings existieren |
| **CI-Integration** | Build-Schritte in CI; Gap-Report als Artefakt | Sichtbarkeit; keine neuen Annotationen nötig |
| **Gap-Priorisierung** | Prioritäts-Score aus bestehenden Daten | Bessere Fokussierung; nutzt Incident/Strategy/Autopilot |
| **failure_class Hints** | Konfigurationsdatei mit Datei-/Testname-Patterns | Erweiterung catalog_bound ohne REGRESSION_CATALOG-Änderung |
| **guard_type Overrides** | Konfigurationsdatei mit test_id_pattern → guard_types | Explizite guard_types ohne Code-Änderung |

---

## Mittelfristig: Explizite Annotationen nötig

| Maßnahme | Was braucht es | Nutzen |
|----------|----------------|--------|
| **failure_class catalog_bound** | Manuelle Einträge in REGRESSION_CATALOG | Belastbare Coverage; 26 → 50+ Tests |
| **guard_types explizit** | pytest-Marker @pytest.mark.guard_type(...) oder Override-Pflege | coverage_quality: medium → high |
| **Replay-Szenarien** | Incident → Replay-YAML; Bindings mit regression_test | Replay-Binding überhaupt befüllbar |
| **Regression-Bindings** | Bindings.json pro Incident mit regression_test | regression_requirement_unbound schließen |

---

## Größter QA-Reifegewinn

| Priorität | Maßnahme | Begründung |
|-----------|----------|------------|
| **1** | **Orphan-Governance** | Sofort umsetzbar; reduziert Rauschen; verbessert Akzeptanz der Metrik |
| **2** | **CI-Integration** | Gap-Reports sichtbar; kontinuierliche Feedback-Schleife |
| **3** | **Gap-Priorisierung** | Fokussierung auf Incident-nähe und kritische Subsysteme |
| **4** | **failure_class Hints** | Schneller Gewinn ohne manuelle Catalog-Pflege |
| **5** | **Replay-Binding-Enrichment** | Vorbereitung; wirkt sobald Replays/Bindings existieren |

---

## Randbedingungen (unverändert)

- Keine Änderung an bestehenden QA-Artefakten (fachlich)
- Keine Änderung an Incidents, Replay, Regression
- Keine Coverage-Map-Verfälschung rückwirkend
