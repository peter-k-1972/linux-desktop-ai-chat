# Phase 3 – Semantische Anreicherung

**Datum:** 15. März 2026  
**Status:** Architektur-Entwurf  
**Zweck:** failure_class-Bindung verbessern, guard_types explizit machen, manual_review_required reduzieren – ohne bestehende Artefakte fachlich umzuschreiben.

---

## 1. Ist-Zustand und Unsicherheiten

| Aspekt | Aktuell | Problem |
|--------|---------|---------|
| **failure_class** | 26/550 Tests catalog_bound | 524 Tests ohne explizite Bindung; viele haben plausible Inferenz |
| **guard_types** | inferiert; coverage_quality = medium | Keine explizite Annotation; Heuristik fehleranfällig |
| **manual_review_required** | 138 Tests | Hoher Anteil; viele könnten durch bessere Inferenz reduziert werden |

---

## 2. failure_class-Bindung verbessern

### 2.1 Strategie: Kaskadierte Anreicherung

```
Stufe 1: REGRESSION_CATALOG (bestehend)
         → catalog_bound für Tests mit expliziter Zuordnung

Stufe 2: Erweiterte Catalog-Matching-Regeln (Phase 3)
         → Dateiname + Testname-Pattern gegen REGRESSION_CATALOG
         → Beispiel: test_chroma_unreachable* → rag_silent_failure

Stufe 3: Heuristische Inferenz (niedrige Priorität)
         → test_domain + subsystem + Marker → plausible failure_class
         → inference_sources.failure_class = "inferred" (nicht catalog_bound)
```

### 2.2 Erweiterte Catalog-Matching-Regeln

**Neue Konfigurationsdatei (additiv):** `docs/qa/phase3_failure_class_hints.json`

```json
{
  "schema_version": "1.0",
  "file_patterns": [
    {
      "pattern": "test_chroma_*",
      "failure_class": "rag_silent_failure",
      "confidence": "high",
      "notes": "REGRESSION_CATALOG Zuordnung"
    },
    {
      "pattern": "test_rag_retrieval_failure*",
      "failure_class": "rag_silent_failure",
      "confidence": "high"
    },
    {
      "pattern": "test_prompt_apply*",
      "failure_class": "request_context_loss",
      "confidence": "medium"
    }
  ],
  "test_name_patterns": [
    {
      "pattern": "*chroma*unreachable*",
      "failure_class": "rag_silent_failure"
    },
    {
      "pattern": "*streaming*clean*",
      "failure_class": "ui_state_drift"
    }
  ]
}
```

**Regel:** Nur anwenden, wenn Test noch kein `catalog_bound` hat. Nach Anwendung: `inference_sources.failure_class = "catalog_bound"` nur wenn `confidence == "high"` und Pattern aus REGRESSION_CATALOG stammt; sonst `"inferred"`.

### 2.3 Manuelle Review-Kandidaten priorisieren

- Tests mit `manual_review_required: true` und `inference_sources.failure_class == "unknown"` zuerst
- Autopilot/Strategy kann priorisierte Liste ausgeben: "Top 20 Tests für failure_class-Review"
- Nach manueller Zuordnung: Eintrag in REGRESSION_CATALOG; nächster Inventory-Build wird catalog_bound

### 2.4 Keine Rückwirkung auf Coverage Map

- Coverage Map zählt nur `catalog_bound` für failure_class-Aggregation
- `inferred` erhöht nicht die offizielle Coverage; dient nur der Transparenz und Vorbereitung für manuelle Bestätigung

---

## 3. guard_types: Von inferiert zu explizit

### 3.1 Aktuelle Inferenz (coverage_map_rules.py)

- `failure_replay_guard`: Tests in chaos/startup mit degraded/failure
- `event_contract_guard`: Tests in contracts mit Event-Struktur
- `startup_degradation_guard`: Tests in startup mit optional dependencies

### 3.2 Explizite Annotation: Marker und Konfiguration

**Option A: pytest-Marker (empfohlen)**

```python
@pytest.mark.guard_type("event_contract_guard")
def test_debug_event_contract(...):
    ...
```

**Option B: Konfigurationsdatei (ohne Code-Änderung)**

`docs/qa/phase3_guard_type_overrides.json`:

```json
{
  "overrides": [
    {
      "test_id_pattern": "tests_contracts_test_debug_event_contract*",
      "guard_types": ["event_contract_guard"]
    },
    {
      "test_id_pattern": "tests_chaos_test_startup_partial_services*",
      "guard_types": ["failure_replay_guard"]
    }
  ]
}
```

**Priorität:** Explizite Annotation (Marker oder Override) überschreibt Inferenz. `inference_sources.guard_type` = "explicit" vs "inferred".

### 3.3 Migrationspfad

1. **Phase 3a:** Override-Datei einführen; Inventory-Builder liest Overrides, setzt `guard_types` explizit
2. **Phase 3b:** Nach und nach Marker in Tests einfügen (optional)
3. **Coverage Map:** `source: "explicit"` für guard_types verbessert `coverage_quality`

---

## 4. manual_review_required reduzieren

### 4.1 Ursachen für manual_review_required

- `inference_sources.* == "unknown"` für eines der Felder (failure_class, subsystem, test_type)
- Keine Zuordnung aus REGRESSION_CATALOG
- Keine Zuordnung aus Subsystem-Inferenz (Dateipfad)

### 4.2 Reduktionsstrategie

| Maßnahme | Wirkung | Aufwand |
|----------|---------|---------|
| Erweiterte Catalog-Matching-Regeln (§2.2) | failure_class: unknown → inferred/catalog_bound | Niedrig |
| Subsystem-Inferenz verbessern | subsystem: unknown → inferred (aus Pfad) | Niedrig |
| test_type aus test_domain ableiten | test_type: unknown → inferred | Niedrig |
| guard_type Overrides (§3.2) | guard_types explizit | Mittel |
| Manuelle Review-Batches | Kandidaten priorisiert abarbeiten | Manuell |

### 4.3 Automatische Herabstufung

**Regel:** Wenn alle `inference_sources` ≠ "unknown" (mindestens inferred), dann `manual_review_required: false`.

**Ausnahme:** Tests mit `inference_confidence.* == "low"` können weiterhin `manual_review_required: true` bleiben, bis manuell bestätigt.

---

## 5. Implementierungsreihenfolge

| Schritt | Artefakt | Aktion |
|---------|----------|--------|
| 1 | `phase3_failure_class_hints.json` | Neu anlegen; Pattern aus REGRESSION_CATALOG ableiten |
| 2 | `build_test_inventory.py` | Erweiterung: Hints lesen, anwenden (nur bei unknown) |
| 3 | `phase3_guard_type_overrides.json` | Neu anlegen; aus bestehender Inferenz-Logik ableiten |
| 4 | `build_test_inventory.py` | Erweiterung: Overrides lesen, guard_types setzen |
| 5 | `test_inventory_rules.py` | manual_review_required-Logik verfeinern |

---

## 6. Metriken und Erfolg

| Metrik | Vorher | Ziel (Phase 3) |
|--------|--------|----------------|
| catalog_bound failure_class | 26 | 35+ (durch Hints + manuelle Reviews) |
| guard_types source=explicit | 0 | 10+ (durch Overrides) |
| manual_review_required | 138 | < 100 |
| coverage_quality (guard) | medium | medium → high (bei expliziten guard_types) |

---

## 7. Randbedingungen

- **REGRESSION_CATALOG:** Keine Änderung; Hints sind additive Konfiguration
- **QA_TEST_INVENTORY:** Nur Anreicherung; keine Löschung bestehender catalog_bound-Werte
- **QA_COVERAGE_MAP:** Nutzt weiterhin nur catalog_bound für failure_class; inferred bleibt transparent
