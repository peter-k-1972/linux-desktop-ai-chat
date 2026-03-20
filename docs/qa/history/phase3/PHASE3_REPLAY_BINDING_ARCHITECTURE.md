# Phase 3 – Replay-/Binding-Anreicherungsarchitektur

**Datum:** 15. März 2026  
**Status:** Architektur-Entwurf  
**Zweck:** Systematische Befüllung von `covers_replay` aus Bindings/Incident-Bezügen, ohne bestehende Artefakte umzuschreiben.

---

## 1. Kontext und Randbedingungen

### 1.1 Ist-Zustand

- **QA_TEST_INVENTORY:** `covers_replay` ist überwiegend `"unknown"` (keine explizite Replay-Bindung)
- **QA_COVERAGE_MAP:** `replay_binding`-Achse zeigt `bound_count: 0`, `total_replays: 0` (keine Replay-Szenarien vorhanden)
- **Incidents:** `replay_status`, `binding_status` in `incidents/index.json`; Bindings-Schema in `incidents/_schema/bindings.schema.json`
- **REGRESSION_CATALOG:** Zuordnung Test ↔ Fehlerklasse; keine Replay-IDs

### 1.2 Nicht ändern

- Keine Änderung an Incident-Dateien
- Keine Änderung an Replay-Dateien (falls vorhanden)
- Keine Änderung an REGRESSION_CATALOG
- Keine fachliche Rückwirkung auf die Coverage Map (keine Verfälschung bestehender Metriken)

---

## 2. Architektur: Anreicherungsschicht

### 2.1 Prinzip: Additive Enrichment

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ENRICHMENT LAYER (Phase 3)                                              │
│  Liest: incidents/index.json, Replay-Registry, Bindings                  │
│  Schreibt: NUR in QA_TEST_INVENTORY (covers_replay, replay_ids)           │
│            NUR in QA_COVERAGE_MAP (replay_binding-Aggregation)            │
└─────────────────────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
┌─────────────────────┐      ┌─────────────────────────────────────────┐
│  QA_TEST_INVENTORY  │      │  QA_COVERAGE_MAP                         │
│  (covers_replay,    │      │  coverage_by_axis.replay_binding          │
│   replay_ids)       │      │  gaps.replay_binding                     │
└─────────────────────┘      └─────────────────────────────────────────┘
```

### 2.2 Datenquellen für Replay-Bindung

| Quelle | Feld | Verwendung |
|--------|------|------------|
| `incidents/index.json` | `incident_id`, `replay_status`, `binding_status` | Identifikation von Incidents mit Replay |
| `incidents/{id}/bindings.json` | `incident_id`, `replay_id`, `regression_catalog.regression_test` | Replay-ID ↔ Test-Pfad |
| `QA_INCIDENT_REPLAY_SCHEMA` | `replay_szenario_id` (REPLAY-INC-*) | Format für Replay-IDs |
| `REGRESSION_CATALOG.md` | Zuordnung Test → Fehlerklasse | Indirekte Inferenz: Incident → Test über Fehlerklasse |

### 2.3 Inferenz-Regeln für covers_replay

| Regel | Bedingung | Ergebnis |
|-------|-----------|----------|
| **R1: Explizit gebunden** | Test in `regression_test` eines Bindings mit `replay_id` | `covers_replay: "yes"`, `replay_ids: [REPLAY-INC-*]` |
| **R2: Incident ohne Replay** | Incident hat `replay_status: null` oder `missing` | Kein Replay → kein covers_replay |
| **R3: Inferiert über Fehlerklasse** | Test catalog_bound für failure_class X; Incident mit X hat Replay | `covers_replay: "inferred"` (optional, niedrige Priorität) |
| **R4: Unbekannt** | Keine der obigen | `covers_replay: "unknown"` (bleibt) |

**Wichtig:** R3 ist heuristisch und sollte nur als Hinweis dienen, nicht als harte Bindung.

---

## 3. Implementierungsansatz

### 3.1 Neuer Enrichment-Script (additiv)

```
scripts/qa/enrich_replay_binding.py
```

**Inputs (read-only):**
- `docs/qa/incidents/index.json`
- `docs/qa/incidents/*/bindings.json` (falls vorhanden)
- `docs/qa/QA_TEST_INVENTORY.json` (wird gelesen und angereichert geschrieben)

**Outputs:**
- `docs/qa/QA_TEST_INVENTORY.json` (nur Felder `covers_replay`, `replay_ids` pro Test aktualisiert)
- Optional: `docs/qa/qa_replay_binding_trace.json` (Audit-Log: welche Tests wie angereichert)

### 3.2 Ablauf

1. Lade Inventory
2. Lade Incidents-Index
3. Für jeden Incident mit `replay_status` ≠ null:
   - Lade Bindings (falls vorhanden)
   - Extrahiere `regression_test` (pytest_nodeid) und `replay_id`
   - Finde Test im Inventory via `pytest_nodeid` oder `test_id`
   - Setze `covers_replay: "yes"`, `replay_ids: [replay_id]`
4. Schreibe Inventory zurück (nur diese Felder ändern)

### 3.3 Sichtbarkeit in Inventory

**Vor Enrichment:**
```json
{
  "test_id": "...",
  "covers_replay": "unknown",
  "replay_ids": []
}
```

**Nach Enrichment (wenn gebunden):**
```json
{
  "test_id": "...",
  "covers_replay": "yes",
  "replay_ids": ["REPLAY-INC-20260315-001"]
}
```

### 3.4 Sichtbarkeit in Coverage Map

Die Coverage Map wird von `build_coverage_map.py` erzeugt. Die `replay_binding`-Achse liest aus dem Inventory:

- `replay_binding.bound_count` = Anzahl Tests mit `covers_replay == "yes"`
- `replay_binding.total_replays` = Anzahl eindeutiger Replay-IDs aus Incidents
- `replay_binding.bindings` = Liste `{replay_id, test_id, incident_id}`

**Erweiterung in `coverage_map_rules.py` oder `build_coverage_map.py`:**

```python
def aggregate_replay_binding(inventory: dict, incidents_index: dict) -> dict:
    """replay_binding-Aggregation aus Inventory + Incidents."""
    tests = inventory.get("tests") or []
    bound = [t for t in tests if t.get("covers_replay") == "yes"]
    replay_ids = set()
    for t in bound:
        replay_ids.update(t.get("replay_ids") or [])
    bindings = [
        {"replay_id": rid, "test_id": t.get("test_id"), "incident_id": _replay_to_incident(rid)}
        for t in bound for rid in (t.get("replay_ids") or [])
    ]
    total = len(incidents_index.get("incidents") or [])  # oder: Replay-Registry
    return {
        "bindings": bindings,
        "bound_count": len(bound),
        "total_replays": max(total, len(replay_ids)),
        "coverage_strength": "covered" if len(bound) > 0 else "gap"
    }
```

---

## 4. Reihenfolge der Verarbeitung

1. **Inventory-Builder** (bestehend) → erzeugt Inventory mit `covers_replay: "unknown"`
2. **Enrichment-Script** (neu) → liest Inventory, Incidents, Bindings; schreibt `covers_replay`, `replay_ids` zurück
3. **Coverage-Map-Builder** (bestehend) → liest angereichertes Inventory; `replay_binding`-Achse nutzt neue Felder

---

## 5. Schema-Erweiterungen (ohne Schema-Bruch)

- **QA_TEST_INVENTORY:** `covers_replay` und `replay_ids` existieren bereits; keine Änderung nötig
- **QA_COVERAGE_MAP:** `replay_binding`-Struktur existiert; `bindings`-Array kann erweitert werden

---

## 6. Zusammenfassung

| Aspekt | Lösung |
|--------|--------|
| **Befüllung covers_replay** | Enrichment-Script liest Bindings/Incidents, schreibt nur in Inventory |
| **Sichtbarkeit Inventory** | `covers_replay`, `replay_ids` pro Test |
| **Sichtbarkeit Coverage Map** | `replay_binding.bindings`, `bound_count`, `total_replays` |
| **Artefakt-Änderungen** | Keine an Incidents, Replay, Regression |
| **Rückwirkung** | Keine Änderung an bestehenden Coverage-Map-Werten für andere Achsen |
