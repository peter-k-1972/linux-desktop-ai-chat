# QA Test Inventory – Mapping-Regeln

**Datum:** 15. März 2026  
**Phase:** 1 – Learning-QA-Architektur  
**Zweck:** Konkrete Abbildungsregeln von Testpfaden, -namen und -markern auf Inventar-Felder.

---

## 1. test_domain ← Verzeichnispfad

| Pfadmuster | test_domain | Anmerkung |
|------------|-------------|-----------|
| tests/async_behavior/* | async_behavior | 1:1 |
| tests/chaos/* | chaos | 1:1 |
| tests/contracts/* | contracts | 1:1 |
| tests/cross_layer/* | cross_layer | 1:1 |
| tests/failure_modes/* | failure_modes | 1:1 |
| tests/golden_path/* | golden_path | 1:1 |
| tests/integration/* | integration | 1:1 |
| tests/live/* | live | 1:1 |
| tests/meta/* | meta | 1:1 |
| tests/qa/autopilot_v3/* | qa | Unterordner ignorieren für domain |
| tests/qa/feedback_loop/* | qa | |
| tests/qa/generators/* | qa | |
| tests/qa/golden/* | qa | |
| tests/regression/* | regression | 1:1 |
| tests/smoke/* | smoke | 1:1 |
| tests/startup/* | startup | 1:1 |
| tests/state_consistency/* | state_consistency | 1:1 |
| tests/ui/* | ui | 1:1 |
| tests/unit/* | unit | 1:1 |
| tests/helpers/* | helpers | Keine echten Tests – optional ausschließen |
| tests/test_*.py | root | Root-Level, kein Unterordner |

**Regel:** `test_domain` = erstes Verzeichnis unter `tests/` (ohne `tests/`).  
**Ausnahme:** `tests/qa/autopilot_v3/` → domain = `qa`, nicht `autopilot_v3`.

---

## 2. test_type ← Marker und test_domain

### 2.1 Marker-Priorität (wenn mehrere Marker)

Reihenfolge für Dominanz (höchste Priorität zuerst):

1. regression
2. contract
3. failure_mode
4. chaos
5. async_behavior
6. cross_layer
7. state_consistency
8. startup
9. golden_path
10. integration
11. smoke
12. live
13. ui
14. unit

**Regel:** Erster gefundener Marker aus dieser Liste bestimmt test_type.  
**Fallback:** Wenn kein passender Marker → test_type = test_domain (snake_case).

### 2.2 test_type Werte

| Marker/Domain | test_type |
|---------------|-----------|
| regression | regression |
| contract | contract |
| failure_mode | failure_mode |
| chaos | chaos |
| async_behavior | async_behavior |
| cross_layer | cross_layer |
| state_consistency | state_consistency |
| startup | startup |
| golden_path | golden_path |
| integration | integration |
| smoke | smoke |
| live | live |
| ui | ui |
| unit | unit |
| (sonst) | = test_domain |

**Hinweis:** asyncio, slow, fast, full sind **technische** Marker, keine test_type-Kandidaten.

---

## 3. subsystem ← Dateiname / Testname (Heuristik)

| Muster (Datei oder Test) | subsystem | Konfidenz |
|--------------------------|-----------|-----------|
| *rag*, *chroma*, *embedding*, *retrieval* | RAG | inferred |
| *ollama*, *llm*, *model_router*, *provider* | Provider/Ollama | inferred |
| *debug*, *event_bus*, *event_store*, *event_type* | Debug/EventBus | inferred |
| *prompt* | Prompt-System | inferred |
| *agent* | Agentensystem | inferred |
| *chat*, *chatwidget*, *composer* | Chat | inferred |
| *metrics* | Metrics | inferred |
| *sqlite*, *db_*, *persistence* | Persistenz/SQLite | inferred |
| *tool*, *tools* | Tools | inferred |
| *startup*, *app_starts*, *main_window* | Startup/Bootstrap | inferred |
| (kein Treffer) | unknown | – |

**Regel:** Erster Regex-Treffer (case-insensitive). Bei Überlappung (z.B. test_rag_chat_*) → spezifischer gewinnt (rag vor chat wenn RAG-spezifisch).

**manual_review_required:** Wenn test_domain = "unit" oder generischer Name (test_foo, test_bar).

---

## 4. failure_class ← REGRESSION_CATALOG.md

**Autoritative Quelle:** Nur die Tabelle „Zuordnung: Tests → Fehlerklassen“ in REGRESSION_CATALOG.md.

| Bedingung | failure_class | inference_status |
|-----------|---------------|------------------|
| Eintrag in Catalog (Datei + Test) | Wert aus Tabelle | catalog_bound |
| Mehrere Klassen (Komma) | Liste: ["rag_silent_failure", "debug_false_truth"] | catalog_bound |
| Eintrag „–“ oder „-“ | null / leer | catalog_bound (explizit keine) |
| Kein Eintrag | unknown | unknown |

**Keine Heuristik für failure_class.** Ohne Catalog-Eintrag kein Raten.

**Datei-Matching:** Catalog nutzt Dateiname ohne .py (z.B. test_chroma_unreachable). Inventar muss exakt matchen.

---

## 5. guard_type ← test_type (Heuristik)

| test_type | guard_type | Anmerkung |
|-----------|------------|-----------|
| failure_mode | failure_replay_guard | Fault-Injection, Replay-Szenarien |
| chaos | failure_replay_guard | Chaos = erweiterte Failure-Injection |
| contract | event_contract_guard | Verträge, Schema, Events |
| startup | startup_degradation_guard | Startup, Degraded Mode |
| (sonst) | unknown | Keine sichere Zuordnung |

**Grenze:** async_behavior, cross_layer, regression können verschiedene Guard-Typen abdecken – nicht automatisch zuordenbar.

---

## 6. covers_regression ← Marker und Pfad

| Bedingung | covers_regression | inference_status |
|-----------|-------------------|------------------|
| @pytest.mark.regression | true | discovered |
| test_domain == "regression" | true | discovered |
| Beides | true | discovered |
| Weder | false | discovered |

**Deterministisch.** Keine Heuristik nötig.

---

## 7. covers_replay ← bindings.json

| Bedingung | covers_replay | inference_status |
|-----------|---------------|------------------|
| bindings.json mit regression_test = nodeid | "yes" | discovered |
| Incident mit Replay, aber kein Binding | "unknown" | unknown |
| Kein Incident-Replay-Kontext | "unknown" | unknown |

**Phase 1:** Praktisch immer `unknown`. Erst wenn Incident-Replay-Bindings flächendeckend existieren, wird dies discoverbar.

---

## 8. Manuell zu reviewende Fälle

### 8.1 Immer manual_review_required

- Tests in tests/ (root) ohne klaren Domain-Bezug
- Tests in tests/helpers/ (falls als Test gezählt)
- unit-Tests mit generischen Namen (test_parse, test_validate)
- Tests mit mehreren Subsystem-Kandidaten (z.B. test_chat_rag_integration → Chat oder RAG?)

### 8.2 Bei Konflikt

- Marker sagt „integration“, Domain sagt „failure_modes“ → test_type = failure_mode (Domain für fachliche Kategorie)
- Dateiname test_prompt_apply_* → Prompt-System, aber Cross-Layer-Aspekt → Subsystem bleibt Prompt-System, cross_layer ist test_type

### 8.3 Bekannte Ausnahmen

| Test/Datei | Besonderheit |
|------------|--------------|
| test_event_store_failure | Debug/EventBus (event_store), nicht Persistenz |
| test_llm_chunk_parsing_failure | contract_schema_drift, Subsystem Provider/Ollama |
| test_metrics_on_failed_chat_or_task | Metrics + Chat – Subsystem Metrics |
| test_chat_continues_when_rag_fails | RAG (RAG-Failure), Chat ist Kontext |

---

## 9. Namensmuster → failure_class (nur Hinweis)

**Nicht für automatische Zuordnung.** Nur als Review-Hilfe.

| Muster | Mögliche failure_class |
|--------|------------------------|
| *chroma*unreachable*, *rag*retrieval*fail* | rag_silent_failure |
| *signal*after*destroy*, *late*signal* | late_signal_use_after_destroy, async_race |
| *degraded*, *optional*depend*, *import*fail* | degraded_mode_failure, optional_dependency_missing |
| *startup*, *ollama*unreachable* | degraded_mode_failure, startup_ordering |
| *tool*exception*, *tool*fail* | tool_failure_visibility |
| *metrics*fail*, *task_failed* | metrics_false_success |
| *event*visible*, *timeline*, *debug*view* | debug_false_truth |
| *contract*, *schema*, *metadata* | contract_schema_drift |

Diese Muster **dürfen nicht** automatisch als failure_class gesetzt werden. Sie dienen nur der manuellen Prüfung.

---

*Mapping-Regeln erstellt am 15. März 2026.*
