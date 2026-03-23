# Phase B – Modellruntime: Usage, Quota, Abschlussbericht

## Neue Dateien

| Datei | Zweck |
|--------|--------|
| `app/runtime/__init__.py` | Paketmarker |
| `app/runtime/model_invocation.py` | DTO `ModelInvocationChunkPayload`, `ModelInvocationOutcome`, Chunk-Helfer `attach_model_invocation` (`model_invocation`-Key) |
| `app/services/token_usage_estimation.py` | Zentrale Heuristik (Zeichen/4) für Preflight-Obergrenze und Offline-Fallback |
| `app/services/provider_usage_normalizer.py` | Auszug/normalisierte Finalzählung aus Stream-/Final-Chunks (`prompt_eval_count`/`eval_count`, `usage`-Dict) |
| `app/services/model_orchestrator_service.py` | Singleton `get_model_orchestrator()` mit gemeinsamem `OllamaClient` aus `get_infrastructure()` |
| `app/services/model_chat_runtime.py` | Preflight (Quota), Provider-Stream, einmaliger Ledger-Commit + Aggregation |
| `tests/unit/test_phase_b_model_chat_runtime.py` | Tests: Block, Erfolg exakt/geschätzt, Provider-Fehler, Warn-Preflight |

## Geänderte Dateien

| Datei | Änderung |
|--------|-----------|
| `app/core/models/orchestrator.py` | `stream_raw_chat()` = uninstrumentierter Provider-Stream; `chat()` ruft `stream_instrumented_model_chat` (optional `chat_id`, `usage_type`) |
| `app/services/chat_service.py` | Produktiver Chat über `get_model_orchestrator().chat` statt direkt `ollama_client.chat`; optionale Parameter `cloud_via_local`, `usage_type` |
| `app/services/infrastructure.py` | Bei `set_infrastructure`: `reset_model_orchestrator()` |
| `app/core/config/settings.py` | `model_usage_tracking_enabled` (Default: True), Persistenz in `save()`/`load()` |
| `app/agents/agent_task_runner.py` | `usage_type=agent_run` für Agent-Läufe |
| `tests/test_chat_streaming_toggle.py` | Infra-Patch auf `app.services.infrastructure.get_infrastructure`, Tracking aus, Orchestrator-Reset |
| `tests/unit/test_chat_guard.py` | Tracking aus, Orchestrator-Reset vor Infra-Setup |

## Instrumentierte Runtime-Pfade

1. **Chat (GUI, Skripte, Prompt-Lab)**  
   `ChatService.chat` → `ModelOrchestrator.chat` → `stream_instrumented_model_chat`.

2. **Agenten**  
   `AgentTaskRunner` → `ChatService.chat(..., usage_type=agent_run)`.

3. **Direkter Orchestrator** (z. B. Legacy `MainWindow` mit injiziertem `ModelOrchestrator`)  
   `ModelOrchestrator.chat` ist instrumentiert; `stream_raw_chat` bleibt der Rohpfad (nur für die Runtime-Schicht).

Kein paralleler „alter“ Chat-Pfad über `ChatService` → `ollama_client` mehr.

## Provider / Ollama: wo Usage exakt ist

- **Lokal & Cloud (Ollama-API-NDJSON):** Auswertung über Chunk-Felder `prompt_eval_count`, `eval_count` sowie verschachteltes `usage` mit gängigen Schlüsseln (`prompt_tokens`/`completion_tokens`, `input`/`output` etc.) in `provider_usage_normalizer`.
- **Liefern die Chunks keine Usage:** `finalize_token_counts` nutzt die zentrale Schätzung (`token_usage_estimation`); `estimated_tokens=true` im Ledger, `token_counts_exact=false` im Chunk.

## Blockierung & Fehlersemantik

- **Quota hard_block:** Kein Aufruf von `stream_raw_chat`; Ledger `blocked`, Chunk mit `error_kind=policy_block`, `model_invocation.outcome=policy_block`.
- **Fehlender API-Key bei direktem Cloud-Modell:** Kein Cloud-Request; Ledger `failed`, Chunk `error_kind=config_error`, `outcome=config_error`.
- **Provider-Fehlerchunk (`error` im Stream):** Nach Stream `failed`, Token 0; zusätzlicher Abschlusschunk mit `outcome=provider_error` und `usage_record_id`.
- **Abbruch (`asyncio.CancelledError`):** Ledger `cancelled`, Token aus State + Schätzung falls nötig; kein zweiter Success-Commit (Flag `committed`).

## Quota (Online vs. Offline)

- **Online** (Cloud-Provider, nicht `cloud_via_local`): `QuotaEvaluationContext.is_online=True`, `api_key_fingerprint` aus Settings-Key; Policies `API_KEY` / `GLOBAL` / `MODEL` / … wie in Phase A.
- **Offline** (`local` oder Cloud über lokales Ollama): `is_online=False`; `offline_default`-Policies aus der DB greifen, sobald vorhanden – kein implizites „Offline ignoriert alles“.

Aggregat-Schlüssel für Snapshot/Preflight/Commit: `scope_type=global`, `scope_ref=""`, `provider_id` wie im Datensatz.

## Aggregation

Nach jedem Commit: `ModelUsageAggregationService.apply_record` innerhalb derselben `session_scope`-Transaktion wie `create_record` → konsistente Buckets (hour/day/week/month/total).

## Einstellung

- **`model_usage_tracking_enabled`:** `False` = kein Preflight/Ledger, nur `stream_raw_chat` (z. B. Tests oder Notfall).

## Offen für Phase C/D

- Feinere Scopes (z. B. `project`/`chat`) durchgängig mit Quota-Snapshot und Ledger abgleichen; aktuell nur globales Aggregat-Keying, Metadaten in `raw_request_meta_json` (`chat_id`, …).
- Explizite Modell-Offline-Verfügbarkeitsprüfung vor Request (eigener `config_error`-Pfad).
- GUI-gestützte Warnungen aus `model_invocation` / Policy-Text.
- Strikte Tokenizer-basierte Schätzung statt Zeichen/4.
- Dedizierte Tests für Streaming-Cancel ohne Doppel-Commit (manueller `athrow`).

## Tests

`tests/unit/test_phase_b_model_chat_runtime.py` (In-Memory-SQLite, gepatchtes `session_scope`) sowie angepasste Chat-Streaming-/Guard-Tests. Gesamte `tests/unit/` lokal grün (Stand: Ausführung mit Projekt-`.venv-ci`).

Voraussetzung Produktion: Alembic-Migration Phase A auf derselben DB wie `LINUX_DESKTOP_CHAT_DATABASE_URL` / Standard-`chat_history.db`.
