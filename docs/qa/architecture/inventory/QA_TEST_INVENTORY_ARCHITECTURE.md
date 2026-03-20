# QA Test Inventory – Architektur

**Datum:** 15. März 2026  
**Phase:** 1 – Learning-QA-Architektur  
**Status:** Entwurf  
**Zweck:** Grundlage für Coverage, Gap Detection und Governance – maschinenlesbares Testinventar.

---

## 1. Ziel des Artefakts

**QA_TEST_INVENTORY.json** ist das maschinenlesbare Inventar aller Tests im Projekt. Es dient als:

- **Single Source of Truth** für die Testlandschaft
- **Eingabe** für spätere Coverage-Map-Generatoren
- **Referenz** für Gap Detection (Autopilot v3, Test Strategy)
- **Governance-Basis** für Marker-Disziplin, Regression-Binding, Replay-Status

Das Inventar **beschreibt** Tests – es bewertet sie nicht. Es **katalogisiert** – es misst keine Coverage.

---

## 2. Abgrenzung zu Coverage Map

| Aspekt | QA_TEST_INVENTORY | QA_COVERAGE_MAP (später) |
|--------|-------------------|---------------------------|
| **Inhalt** | Liste aller Tests mit Metadaten | Abdeckung pro Subsystem/Failure-Class |
| **Quelle** | Discovery (pytest, Dateisystem) | Inventar + Code-Analyse |
| **Zweck** | Katalog, Referenz | Lückenanalyse, Priorisierung |
| **Phase** | 1 (jetzt) | 2 (später) |
| **Mutation** | Keine | Keine |

Das Inventar ist die **Voraussetzung** für die Coverage Map. Ohne Inventar keine sinnvolle Coverage-Berechnung.

---

## 3. Datenmodell

### 3.1 Top-Level-Struktur

```json
{
  "schema_version": "1.0",
  "generated_at": "ISO8601",
  "generator": "test_inventory",
  "input_sources": ["pytest", "REGRESSION_CATALOG.md", "..."],
  "test_count": 0,
  "tests": [...],
  "taxonomy": {...},
  "discovery_metadata": {...}
}
```

### 3.2 Test-Eintrag (Minimal)

```json
{
  "id": "tests/failure_modes/test_chroma_unreachable.py::test_rag_service_handles_chroma_unreachable",
  "file_path": "tests/failure_modes/test_chroma_unreachable.py",
  "test_name": "test_rag_service_handles_chroma_unreachable",
  "test_domain": "failure_modes",
  "test_type": "failure_mode",
  "markers": ["failure_mode", "asyncio"],
  "subsystem": "RAG",
  "failure_class": "rag_silent_failure",
  "guard_type": "failure_replay_guard",
  "covers_regression": false,
  "covers_replay": "unknown",
  "inference_status": {...}
}
```

### 3.3 inference_status (Transparenz)

Jedes Feld, das nicht 1:1 discoverbar ist, erhält einen Status:

```json
{
  "subsystem": "inferred",
  "failure_class": "catalog_bound",
  "guard_type": "inferred",
  "covers_regression": "discovered",
  "covers_replay": "unknown"
}
```

**Werte:** `discovered` | `inferred` | `catalog_bound` | `manual_review_required` | `unknown`

---

## 4. Felddefinitionen

| Feld | Typ | Ableitbarkeit | Beschreibung |
|------|-----|---------------|--------------|
| **id** | string | discovered | pytest nodeid: `path::test_name` |
| **file_path** | string | discovered | Relativer Pfad zur Testdatei |
| **test_name** | string | discovered | Name der Testfunktion |
| **test_domain** | string | discovered | Verzeichnis unter tests/ (z.B. `failure_modes`) |
| **test_type** | string | discovered/inferred | Kategorie: unit, contract, failure_mode, async_behavior, … |
| **markers** | string[] | discovered | pytest-Marker der Testfunktion |
| **subsystem** | string | inferred | Betroffenes Subsystem (QA_RISK_RADAR) |
| **failure_class** | string | catalog_bound/inferred | Fehlerklasse (REGRESSION_CATALOG) |
| **guard_type** | string | inferred | failure_replay_guard, event_contract_guard, startup_degradation_guard |
| **covers_regression** | boolean | discovered | true wenn @pytest.mark.regression oder tests/regression/ |
| **covers_replay** | string | unknown | "yes" | "no" | "unknown" – aus bindings.json wenn vorhanden |
| **inference_status** | object | – | Pro-Feld-Status für Nachvollziehbarkeit |

### 4.1 Erlaubte Werte

**test_domain:** async_behavior, chaos, contracts, cross_layer, failure_modes, golden_path, integration, live, meta, qa, regression, smoke, startup, state_consistency, ui, unit, helpers, (root)

**test_type:** unit, contract, failure_mode, async_behavior, integration, smoke, live, golden_path, regression, cross_layer, state_consistency, startup, chaos, ui, meta

**subsystem:** Agentensystem, Chat, Debug/EventBus, Metrics, Persistenz/SQLite, Prompt-System, Provider/Ollama, RAG, Startup/Bootstrap, Tools

**failure_class:** ui_state_drift, async_race, late_signal_use_after_destroy, request_context_loss, rag_silent_failure, debug_false_truth, startup_ordering, degraded_mode_failure, contract_schema_drift, metrics_false_success, tool_failure_visibility, optional_dependency_missing

**guard_type:** failure_replay_guard, event_contract_guard, startup_degradation_guard

---

## 5. Ableitungslogik

### 5.1 Automatisch discoverbar (ohne Heuristik)

| Feld | Methode |
|------|---------|
| id | pytest collection: `path::test_name` |
| file_path | Dateisystem |
| test_name | AST / pytest |
| test_domain | Pfad: `tests/<domain>/` → domain |
| markers | pytest: `item.iter_markers()` |
| covers_regression | `regression` in markers ODER test_domain == "regression" |

### 5.2 Heuristisch ableitbar

| Feld | Heuristik | Konflikt |
|------|-----------|----------|
| test_type | Primär: dominanter Marker (contract, failure_mode, …). Fallback: test_domain. | Mehrere Marker möglich → Priorität |
| subsystem | Dateiname/Testname: test_rag_* → RAG, test_chroma_* → RAG, test_ollama_* → Provider/Ollama, test_debug_* → Debug/EventBus, test_prompt_* → Prompt-System, test_agent_* → Agentensystem, test_chat_* → Chat | Mehrdeutig |
| guard_type | test_type: failure_mode → failure_replay_guard, contract → event_contract_guard, startup → startup_degradation_guard | Nur grobe Zuordnung |
| failure_class | REGRESSION_CATALOG.md Tabelle (Datei + Test) | Nur für dort eingetragene Tests |

### 5.3 Manuell / regelbasiert

| Feld | Quelle | Hinweis |
|------|--------|---------|
| failure_class | REGRESSION_CATALOG.md „Zuordnung“ | Autoritative Quelle – kein Raten |
| covers_replay | bindings.json.regression_catalog.regression_test | Nur wenn Incident-Replay-Binding existiert |
| subsystem | Bei Mehrdeutigkeit | manual_review_required |

---

## 6. Grenzen der Discovery

### 6.1 Was Phase 1 nicht leisten kann

- **covers_replay:** Ohne bindings.json oder replay.yaml nicht ableitbar → `unknown`
- **failure_class:** Nur für Tests in REGRESSION_CATALOG.md Tabelle → sonst `unknown` oder `manual_review_required`
- **subsystem:** Heuristik trifft bei generischen Namen (test_foo) nicht zu → `unknown`
- **Mehrere failure_classes pro Test:** REGRESSION_CATALOG erlaubt Komma-Liste – Inventar muss Liste unterstützen

### 6.2 Bekannte Lücken

- Tests ohne Marker (z.B. tests/unit/* ohne @pytest.mark.unit) → test_type aus test_domain
- Tests in tests/ (root) → test_domain = "root", test_type unsicher
- tests/qa/* → Meta-Tests, kein Produkt-Subsystem
- tests/helpers/* → Hilfsmodul, keine echten Tests

### 6.3 Governance-Regeln

1. **Keine Fake-Metadaten:** Wenn nicht ableitbar → `unknown` oder `manual_review_required`
2. **inference_status pflicht:** Jedes abgeleitete Feld muss seinen Ursprung dokumentieren
3. **REGRESSION_CATALOG ist autoritativ:** failure_class nur aus Catalog oder explizit `manual_review_required`
4. **Determinismus:** Gleiche Inputs → gleiches Inventar (sortierte Reihenfolge)

---

## 7. Integration mit bestehenden Artefakten

| Artefakt | Rolle für Inventar |
|----------|---------------------|
| REGRESSION_CATALOG.md | Autoritative failure_class-Zuordnung (Tabelle „Zuordnung“) |
| pytest.ini | Marker-Definitionen, testpaths |
| QA_RISK_RADAR.json | Subsystem-Liste (Validierung) |
| QA_AUTOPILOT_V3 | Konsument (später): Gap-Analyse gegen Inventar |
| QA_TEST_STRATEGY | Konsument: recommended_focus_domains vs. test_domains im Inventar |
| incidents/bindings.json | covers_replay (wenn regression_test gesetzt) |

---

## 8. Nächste Schritte (Phase 2)

- Generator `scripts/qa/generate_test_inventory.py`
- QA_COVERAGE_MAP.json (auf Basis Inventar)
- Autopilot v3: Gap Detection gegen Inventar
- Incident-Replay: covers_replay aus bindings befüllen

---

*Architektur erstellt am 15. März 2026. Phase 1 – keine Implementierung des Generators.*
