# Technischer Audit-Bericht – Linux Desktop Chat

**Stand:** 20. März 2026  
**Typ:** Architektur- und QA-Referenz

---

## 1. SYSTEMÜBERBLICK

- **Linux Desktop Chat** – lokale Chat-Anwendung für Entwickler
- **Lokale Modelle** via Ollama (kein Cloud-Zwang)
- **PySide6 GUI** – WorkspaceHost, Domains, Navigation
- **Modulare Backend-Architektur** – Chat, Agents, RAG, LLM, Prompts, Provider getrennt

---

## 2. ARCHITEKTURSTATUS

### 2.1 Schichten

| Schicht | Verantwortung |
|---------|---------------|
| **UI** (PySide6) | Darstellung, User-Input, Settings-Persistenz |
| **Services** | ChatService, AgentService, PromptService – Orchestrierung |
| **Context-System** | Kontextfragment-Erzeugung, keine Settings-Logik |
| **Settings** | Konfiguration liefern, keine Kontextentscheidung |
| **Provider** (Ollama) | Completion, erhält fertige Messages |

Klare Trennung bestätigt. Kein UI→Provider-Leak.

---

## 3. CHAT-SYSTEM

- **Stabiler Sendepfad:** UI → ChatService → Provider
- **Chat Guard** vorhanden – Doppelsendung, Streaming-Konflikte abgefangen
- **Streaming** optional (Toggle)
- Keine Kontextlogik im Provider

### 3.1 Validierung: Ollama-Streaming / Thinking-Fallback (Abschluss)

**Ergebnis:** `PASS_WITH_GUARDS` (fokussierter Testlauf, kein Release-Gate der Gesamtcodebasis).

#### Ursprüngliche Ursache

- Ollama lieferte sichtbaren Text in `message.thinking`, während `message.content` leer blieb.
- Die Anzeige-Pipeline wertete primär den extrahierten Anzeige-Text aus `content` aus → im Chat erschien teils nichts oder nicht der vom Nutzer erwartete Fließtext.

#### Umgesetzter Fix

- **Thinking-Fallback** in `ChatWorkspace._extract_content` (`app/gui/domains/operations/chat/chat_workspace.py`): Ist `message.content` leer (bzw. nur Whitespace), wird der Rohwert von `message.thinking` als Anzeige-Text verwendet; bei nicht-leerem `content` bleibt **echtes `content` vorrangig**.
- **Regression:** Overlap-/Append-Pfad und kumulative Duplikat-Unterdrückung werden in `tests/unit/test_chat_extract_content_streaming.py` abgedeckt; NDJSON-Byte-Splits und Aggregation ohne Live-Ollama in `tests/unit/test_ollama_ndjson_stream.py` und `tests/unit/test_ollama_stream_chat_simulation.py`.
- **Platzhalter:** Ersetzen des leeren Platzhalters beim ersten sinnvollen Update ist in denselben Unit-Tests abgesichert.

#### Teststatus (fokussierter Lauf)

| Metrik | Wert |
|--------|------|
| Ergebnis | **25 / 25 PASS** |
| Dateien | `test_chat_extract_content_streaming.py` (11), `test_ollama_ndjson_stream.py` (3), `test_ollama_stream_chat_simulation.py` (6), `test_completion_status_integration.py` (5) |

**Kernfälle (kurz):** Thinking-only und Thinking→Content-Sequenzen; Priorität von `content` über Thinking; `done` ohne nutzbaren Text; Fehler-Chunks; Overlap/Append und partieller Prefix-Overlap; Platzhalter-Erstupdate; NDJSON über TCP-ähnliche Byte-Grenzen (inkl. UTF-8-Multibyte-Split); defekte/leere Zeilen im Strom; `completion_status`-Persistenz und Schema-Rückwärtskompatibilität; `_extract_content`-Kontrakt (vier Tuple-Werte, `done`, Fehlerpfad).

#### Bekannte Guards / Restgrenzen

- Kein **Live-Ollama-E2E** in diesem Lauf (kein Netzwerk, kein echtes Modell).
- Keine **vollständige pytest-qt-Gesamtsuite** in diesem Lauf.
- Stream endet mit **`done` ohne extrahierten Anzeige-Text:** bewusstes Verhalten – es wird **keine** Assistant-Message persistiert (nicht als Fehlbefund).
- **Overlap** an exotischen Token-/Chunk-Grenzen bleibt **modell- und API-abhängiger Guard**; aktuell kein reproduzierter Fehlbefund in den genannten Tests.

---

## 4. CONTEXT-SYSTEM

### 4.1 Fähigkeiten

- **Kontextmodus:** off, neutral, semantic
- **Detail-Level:** minimal, standard, full
- **Field-Control:** project, chat, topic (project_chat = project + chat)

### 4.2 Architektur

- Settings steuern (chat_context_mode, chat_context_detail_level, include_*)
- ChatService entscheidet, ob injiziert wird
- Context-Modul rendert Fragmente – kein Settings-Import

### 4.3 Compression und Budgeting

- **Render Limits** – feste Kürzungsregeln (max_project_chars, max_chat_chars, max_topic_chars, max_total_lines)
- **Policy Budgets** – ARCHITECTURE (größer), DEBUG (klein), EXPLORATION/DEFAULT (mittel)
- **Failsafe Compression** – Header-only/Marker-only verworfen, sinnlose Felder weggelassen
- **Traceability für Limits** – ChatContextResolutionTrace enthält limits_source, max_*_chars, max_total_lines

→ `docs/04_architecture/CHAT_CONTEXT_GOVERNANCE.md` §9, `docs/qa/CHAT_CONTEXT_COMPRESSION_CHECKLIST.md`

### 4.4 Governance

→ `docs/04_architecture/CHAT_CONTEXT_GOVERNANCE.md`

- Keine Heuristik, keine LLM-Entscheidung, keine UI-Logik
- Änderungen nur mit Tests, QA-Vergleich und Doku-Update

### 4.5 Default (ADR)

- semantic, standard, project_chat (Governance §4, ADR_CHAT_CONTEXT_DEFAULT.md)

---

## 5. QA-ARCHITEKTUR

- **Strukturierte Tests:** Unit, Integration, Smoke, Regression, Meta
- **Kontextmodus-Tests:** test_context_mode_comparison, test_chat_context_injection
- **Vergleichstests:** Matrix-Experimente (6 Cases)
- **Governance-Regressionstests:** test_context_governance_regressions.py

---

## 6. EXPERIMENT-PIPELINE

- **run_context_matrix.py** – erzeugt context_matrix_001.json (6 Cases)
- **Review-Sheet** – context_review_sheet.csv, manuelle Bewertung
- **Evaluation Template** – CHAT_CONTEXT_EVALUATION_TEMPLATE.md
- **Aggregation Script** – evaluate_context_reviews.py → context_review_summary.json

→ `docs/qa/CHAT_CONTEXT_EVALUATION_MATRIX.md`

---

## 7. TOKEN-DISZIPLIN

- **Metriken:** chars, lines, nonempty_lines (keine echte Tokenmessung – bewusst)
- Modellabhängige Tokenisierung würde externe Abhängigkeit einführen
- Strukturvergleich reicht für Kontextvarianten

→ `docs/qa/CHAT_CONTEXT_TOKEN_DISCIPLINE.md`

---

## 8. PRODUKTIONSREIFE

→ `docs/qa/CHAT_CONTEXT_PRODUCTION_CHECKLIST.md`

- **Deterministisch** – Settings-gesteuert, reproduzierbar
- **Testbar** – Regressionstests, Matrix-Experimente
- **Reproduzierbar** – gleiche Settings → gleicher Kontext
- **Konfigurierbar** – kein Hardcoding

---

## 9. CONTEXT EXPLAINABILITY & OBSERVABILITY (IST-STAND)

### 9.1 Implementierungsstatus pro Komponente

| Komponente | Pfad | Status | Klassifikation |
|------------|------|--------|----------------|
| **Explanation-Strukturen** | `app/context/explainability/context_explanation.py` | Implementiert | deterministic, read-only |
| **Extended Trace** | `app/chat/context_profiles.py` (ChatContextResolutionTrace) | Implementiert | deterministic, read-only |
| **Budget-Accounting** | ContextExplanation, ContextSourceEntry (budget_allocated/used/dropped) | Implementiert | deterministic, read-only |
| **Dropped-Context-Sichtbarkeit** | ContextDroppedEntry, dropped_by_source, dropped_reasons | Implementiert | deterministic, read-only |
| **Ignored-Inputs-Sichtbarkeit** | ContextIgnoredInputEntry, ignored_inputs | Implementiert | deterministic, read-only |
| **Explanation-Serializer** | `app/context/explainability/context_explanation_serializer.py` | Implementiert | deterministic, read-only |
| **Inspection-Serializer** | `app/context/explainability/context_inspection_serializer.py` | Implementiert | deterministic, read-only |
| **Debug-Formatter** | `app/context/debug/context_debug.py` | Implementiert | deterministic, read-only |
| **Payload-Preview** | `app/context/explainability/context_payload_preview.py` | Implementiert | deterministic, read-only |
| **Inspection-Service** | `app/services/context_inspection_service.py` | Implementiert | read-only, non-invasive |
| **Inspection-CLI** | `scripts/dev/context_inspect.py` | Implementiert | debug-only, read-only |
| **Explain-CLI** | `scripts/dev/context_explain.py`, `preview_context_fragment.py` | Implementiert | debug-only, read-only |
| **Request-Fixtures** | `tests/fixtures/context_requests/` (7 JSON) | Implementiert | deterministic |
| **Fixture-Loader** | `app/context/devtools/request_fixture_loader.py` | Implementiert | deterministic |
| **Snapshot-Coverage** | `tests/context/expected/` (10 Szenarien × 3 Surfaces + budget/resolution/CLI) | Implementiert | deterministic |
| **Debug-Gating** | `app/context/debug/context_debug_flag.py` | Implementiert | debug-only |
| **Request-Capture** | `app/context/devtools/request_capture.py` | Implementiert | debug-only, non-invasive |
| **UI-neutraler Adapter** | `app/context/inspection/context_inspection_view_adapter.py` | Implementiert | read-only, non-invasive |
| **Debug-Panel** | `app/gui/domains/debug/context_inspection_panel.py` | Implementiert | debug-only, read-only |
| **CI-Integration** | `.github/workflows/context-observability.yml` | Implementiert | runtime-neutral |

### 9.2 Erklärungsschema (implementierte Dataclasses)

- **ContextExplanation:** sources, decisions, resolved_settings, compressions, warnings, ignored_inputs, budget-Felder, dropped_by_source, dropped_reasons, empty_result, failsafe_triggered
- **ContextSourceEntry:** source_type, identifier, included, chars/budget_allocated/used/dropped, selection_order, reason
- **ContextResolvedSettingEntry:** setting_name, final_value, winning_source, candidates (ContextSettingCandidate), fallback_used
- **ContextIgnoredInputEntry:** input_name, input_source, raw_value, reason, resolution_effect
- **ContextDroppedEntry:** source_type, reason, dropped_tokens, source_id
- **ContextWarningEntry:** warning_type, message, source_type, source_id, effect, dropped_tokens

### 9.3 Resolver-Integration

- **ChatService** (`app/services/chat_service.py`): `get_context_explanation()` liefert Trace mit Explanation; `_inject_chat_context` ruft bei jeder Auflösung Explanation-Erzeugung auf; `_explanation_with_budget`, `_build_resolved_settings`, `_build_dropped_context_report` integriert.
- **Request-Capture:** `capture()` im Sendepfad (`chat_service.py` Zeile 406–415), nur bei CONTEXT_DEBUG_ENABLED.
- **ContextExplainService:** `preview`, `preview_with_trace`, `preview_with_trace_and_fragment` – delegiert an ChatService.

### 9.4 Debug-Panel-Integration

- **ChatWorkspace** (`app/gui/domains/operations/chat/chat_workspace.py`): ContextInspectionPanel im Chat-Inspector, nur sichtbar wenn `is_context_debug_enabled()`.
- **IntrospectionWorkspace** (`app/gui/domains/runtime_debug/workspaces/introspection_workspace.py`): „Inspect Last Context“-Button (Dev-Modus), öffnet Dialog mit ContextInspectionPanel für zuletzt erfassten Request.

### 9.5 Test-Coverage (context_observability-Marker)

| Testdatei | Abdeckung |
|-----------|-----------|
| `test_context_explainability.py` | Decisions, sources, compressions, failsafe warnings, formatted snapshot |
| `test_context_explainability_budget.py` | Budget-Felder, available_budget-Konsistenz, per-source accounting |
| `test_context_resolution_chain_explainability.py` | winning_source, candidates, skipped_reason, ignored_inputs, fallback_used, JSON-Determinismus |
| `test_context_explainability_snapshots.py` | 10 Szenarien × 3 Surfaces (formatted, inspection, json) |
| `test_context_inspection_service.py` | inspect(), inspect_as_dict(), Determinismus |
| `test_context_inspection_view_adapter.py` | to_view_model, Snapshot |
| `test_context_inspect_cli.py` | CLI Snapshot für minimal_default, explicit_policy_architecture, invalid_policy_fallback |
| `test_context_debug_flag.py` | is_context_debug_enabled, capture/get_last_request gating |

Hinweis: `test_request_capture.py` und `test_context_failsafe_limits.py` haben keinen context_observability-Marker.

### 9.6 CI-Gate

- **Workflow:** `.github/workflows/context-observability.yml` – push/PR auf main, develop
- **Befehl:** `pytest -m context_observability -v --tb=short`
- **Regeln:** Keine flaky Tests, keine zeitbasierten Assertions, keine Netzwerk-/Provider-Abhängigkeit

### 9.7 Bekannte Einschränkungen

- Schema-Dokumentation (`docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md`) manuell gepflegt
- Kein HTTP/API-Endpoint für `get_context_explanation` (nur lokaler Service)
- DB-abhängig: Fixtures benötigen existierende Chat/Project/Topic in DB
- Keine Persistenz: Inspection-Ergebnisse werden nicht gespeichert
- CLI (`context_inspect.py`, `context_explain.py`): erfordert CONTEXT_DEBUG_ENABLED; bei Deaktivierung Exit 0 mit Hinweis, keine Inspection-Ausgabe

### 9.8 Bekannte Non-Goals

- Echte Tokenmessung (chars/lines als Proxy)
- Persistenz von Inspection-Ergebnissen
- HTTP/API-Exposition der Explainability

### 9.9 Restrisiken

| Risiko | Bewertung |
|--------|-----------|
| Performance-Impact | Gering – Explanation bei jeder Auflösung, aber nur Trace-Struktur; Capture/CLI/Panel gated |
| Breaking Changes | Keine – Erweiterung bestehender Strukturen |
| Abhängigkeiten | Keine neuen |

### 9.10 Klassifikation pro Attribut

| Attribut | Status |
|----------|--------|
| **Deterministisch** | Gleiche Inputs → gleiche Explanation; Serializer/Formatter ohne Zufall, feste Feldreihenfolge |
| **Read-only** | Keine Mutation von DB, Settings oder UI; Inspection nur Lesen |
| **Debug-only** | Request-Capture, CLI, Panel nur bei CONTEXT_DEBUG_ENABLED; keine UI-Anzeige in Produktion |
| **Non-invasive** | Keine Änderung der Failsafe-Policy; nur Instrumentierung/Trace |
| **Runtime-neutral** | CI-Tests ohne Netzwerk/Provider; keine Laufzeitabhängigkeit |

### 9.11 Governance

- **Keine Runtime-Entscheidungsgewalt in Tooling/UI:** Kontext-Entscheidungen liegen ausschließlich im Resolver (ChatService).
- **Keine versteckten Heuristiken:** Erklärung basiert ausschließlich auf Resolver-Output und dokumentierten Feldern.

---

## 10. RISIKEN (REALISTISCH)

| Risiko | Auswirkung |
|--------|------------|
| Overcontext | semantic + full → Ablenkung, Tokenlast |
| Undercontext | neutral + minimal → zu wenig Steuerung |
| Falsche Default-Wahl | Nutzererfahrung, Nachjustierung nötig |
| Governance-Verwässerung | Heuristik/LLM später eingeschleust |
| Überkürzung / Informationsverlust | Limits zu streng → relevanter Kontext fehlt |
| Policy-Budget-Mismatch | Policy erwartet mehr Kontext als Budget zulässt |

---

## 11. MODELL-USAGE, QUOTA, LOKALE ASSETS (2026-03-22)

**Laufzeit:** `app/services/model_chat_runtime.py` – Preflight (`ModelQuotaService`), Provider-Stream, einmaliger Commit über `ModelUsageService` + `ModelUsageAggregationService`. Ledger-Tabelle `model_usage_records` ist die Source of Truth; `model_usage_aggregate` ist daraus ableitbar (`rebuild_from_ledger`).

**Konfiguration:** Quota-Richtlinien in der DB (`ModelQuotaPolicy`); Offline-Standard ohne Limit über Seed `offline_default`; zusätzliche Policies (global, Modell, API-Key-Fingerprint, …) nach `ModelQuotaService`.

**Lokale Artefakte:** `ModelStorageRoot` / `ModelAsset`; Scan/Sync `LocalModelScannerService`; optionaler Default-Root `~/ai` (`ensure_user_ai_default_root`). Keine dateibasierte Nebenpersistenz für Assets.

**Fehler-/Zustandstrennung:** `BLOCKED` (Quota) vs `FAILED` (Provider/Konfig) vs `CANCELLED` vs `SUCCESS` – DTO über `error_kind` / `outcome`; GUI-Aggregation in `model_invocation_display`. Details und QA-Matrix: [`MODEL_USAGE_PHASE_E_QA_REPORT.md`](MODEL_USAGE_PHASE_E_QA_REPORT.md).

**Testrealität:** Backend-Pfade werden durch Unit-Tests mit In-Memory-SQLite abgedeckt; **kein** Ersatz für Live-Ollama/Cloud oder vollständige Qt-E2E in diesem Audit-Abschnitt.

---

**Systemstatus: STABIL / KONTROLLIERBAR / EVALUATIONSBEREIT**
