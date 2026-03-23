# Phase E – QA-Abnahme: Modell-/Provider-/Usage-/Asset-System

**Rolle:** Abschlussprüfung (technisch + fachlich)  
**Stand Code/Doku:** 2026-03-22  
**Keine Schönfärberei:** Dieser Bericht trennt belastbare Automatisierung von manuellen/CI-Lücken.

---

## 1. Soll-Ist gegenüber dem fachlichen Auftrag

| Kernpunkt | Bewertung | Kurzbegründung |
|-----------|-----------|----------------|
| Modelle online und offline nutzbar | **vollständig** (Routing) | `ModelOrchestrator` / Providerwahl; Cloud erfordert API-Key (Konfigurationsfehler wird separat erfasst). |
| Tokenverbrauch sichtbar und protokolliert | **teilweise** | **Ledger** `model_usage_records` + **Aggregationen** `model_usage_aggregate`; GUI über `ModelUsageGuiService` / Control-Center-Workspaces. **Kein** automatisierter pytest-Qt-Lauf für alle Anzeigepfade. |
| Limits /h, /Tag, /Woche, /Monat, /gesamt | **vollständig** (Backend) | `ModelQuotaService.evaluate_usage_against_quota` prüft alle gesetzten Fenster; Policies über DB. |
| Online-Limits aus API-Key/Provider-Kontext | **teilweise** | `QuotaScopeType.API_KEY` + `api_key_fingerprint` im `QuotaEvaluationContext`; **kein** Import echter Cloud-Kontingente von Ollama – Limits sind **app-seitige** Policies, nicht Provider-Telemetry. |
| Offline standardmäßig ohne Limits | **vollständig** | Seed-Policy `offline_default` / `mode=none` (Phase A); zusätzlich verifiziert: eigene `OFFLINE_DEFAULT`+`HARD_BLOCK` blockiert lokalen Lauf (`test_offline_hard_block_offline_default_policy`). |
| Offline konfigurierbare Limits | **vollständig** | Wie oben + globale/modellbezogene Policies gelten für lokale Provider (`is_online=False`). |
| `~/ai/` sauber eingebunden | **teilweise** | `ensure_user_ai_default_root`, `LocalModelScannerService`, `ModelAsset` ohne Nebenpersistenz – **korrekt**. **Matching** heuristisch/konservativ; keine Garantie fachlicher Modell↔Datei-Zuordnung bei komplexen Namen. |

**Bewusst vertagt / offen**

- **E2E mit live Ollama/Cloud** in CI: nicht Bestandteil der referenzierten Unit-/Service-Tests.
- **Vollständige GUI-Regression** (alle Chips/Badges in Chat-Details): nicht durch dedizierte E2E-Tests abgedeckt.
- **Preflight bei DB-/Quota-Ausnahme:** `model_chat_runtime` fällt auf `ALLOW` zurück und loggt (`Preflight quota evaluation failed`) – bewusst availability-first, aber **Risiko** „still ohne Limit“, wenn die DB beim Preflight ausfällt.

---

## 2. E2E-Testmatrix (Ist-Abdeckung)

Legende: **A** = automatisiert (pytest), **M** = manuell / nicht im referenzierten Lauf, **T** = Teilabdeckung.

| # | Szenario | Abdeckung | Nachweis / Bemerkung |
|---|-----------|-----------|----------------------|
| 1 | Online ohne Limitverletzung | **T** | Kein echter Cloud-Stream in CI; Runtime-Pfad mit Fake-Stream + exakten Tokens: `test_success_persists_exact_tokens_from_provider`. |
| 2 | Online Warnung `allow_with_warning` | **A** | `test_allow_with_warn_policy` (Preflight + `warning_active`). |
| 3 | Hard-Block | **A** | `test_preflight_block_no_provider_call` (kein Provider-Call, `BLOCKED`, Aggregation `blocked_count`). |
| 4 | Offline ohne Limit | **A** | Implizit in `test_success_*` mit lokalem Modell (`llama2` / lokaler Provider). |
| 5 | Offline mit Warn-/Block-Policy | **A** | `test_offline_hard_block_offline_default_policy` (Block); Warn analog global wie #2. |
| 6 | Providerfehler, kein Fake-Usage | **A** | `test_provider_error_no_fake_tokens` (`FAILED`, `total_tokens==0`). |
| 7 | Cancel/Abbruch | **A** | `test_cancel_mid_stream_single_cancelled_record` (ein `CANCELLED`-Ledger-Eintrag). |
| 8 | Lokales Asset vorhanden | **A** | `tests/unit/test_local_model_scanner_service.py` (Scan legt/aktualisiert `ModelAsset`). |
| 9 | Asset fehlt nach Re-Scan | **A** | `test_missing_file_marked_unavailable`. |
| 10 | Unassigned Asset | **A** | Matcher-Tests + manuelle Link-Integrität `test_manual_model_link_not_overwritten`. |
| 11 | Aggregationen h/d/w/m/total | **A** | `ModelUsageAggregationService.apply_record` in alle Perioden; `test_phase_a_orm_services` / erfolgreiche Runtime-Läufe erhöhen Buckets. **Rebuild:** `rebuild_from_ledger` in Phase-A-Tests. |
| 12 | Persistenz nach Reload | **T** | In-Memory-Tests belegen Konsistenz pro Engine; **SQLite-Datei + App-Neustart** nicht in dieser Matrix automatisiert. |

**Ausgeführter Testbundle-Lauf (Referenz):**  
`pytest tests/unit/test_phase_b_model_chat_runtime.py tests/unit/test_local_model_scanner_service.py tests/unit/test_model_invocation_display.py tests/unit/test_model_usage_gui_service.py tests/unit/test_phase_a_orm_services.py -q` → grün (`.venv-ci`).

---

## 3. Zustands- und Fehlersemantik (Audit)

| Zustand | Backend (`UsageStatus` / Outcome) | Chunk/DTO | GUI (`model_invocation_display`) | Doku |
|---------|-----------------------------------|-----------|----------------------------------|------|
| Erfolg | `SUCCESS` | `outcome=success`, `token_counts_exact` | Normal / complete | Help + Handbuch ergänzt |
| Warnung | (Preflight) `allow_with_warning` | `warning_active`, `preflight_message` | `style_hint=warn` | `cc_models.md` |
| Block (Quota) | `BLOCKED` | `error_kind=policy_block`, `outcome=policy_block` | `style_hint=block`, Titel mit Limit-Bezug | `cc_models.md` |
| Fehler Provider | `FAILED`, Tokens 0 | `error_kind=provider_error` | `style_hint=error` (nicht Block) | `cc_models.md` |
| Konfig (z. B. fehlender API-Key) | `FAILED` | `error_kind=config_error` | Konfigurations-Hinweis | `test_model_invocation_display` |
| Abbruch | `CANCELLED` | `outcome=cancelled` | Kein eigener Qt-E2E-Test | Phase-E (Chunk-Puffer dokumentiert) |
| Asset fehlt | — | — | `is_available=false`, Status „Fehlt / nicht erreichbar“ | `MODEL_USAGE_PHASE_D_REPORT.md` |
| Geschätzte Tokens | `estimated_tokens=True` | `token_counts_exact=False` | Nutzungsqualität im Bundle (`estimated_requests`) | `cc_models.md` |

**Mehrdeutigkeit:** Blockierung und technischer Fehler sind im **DTO** über `error_kind` und `outcome` trennbar; die GUI nutzt dafür `build_chat_invocation_view`. **Restrisiko:** ältere Chat-UI-Pfade müssen weiterhin `merge_model_invocation_payload` konsistent speisen (Unit-Tests vorhanden).

---

## 4. Datenkonsistenz (Kurzaudit)

| Thema | Urteil |
|-------|--------|
| Ledger als SoT | Ja; Aggregation wird pro Commit aus dem neuen `ModelUsageRecord` aktualisiert (`_commit_usage_record` → `apply_record`). |
| Rebuild | `rebuild_from_ledger` löscht Aggregate und spielt Ledger neu ein (Phase-A-Test). |
| Doppel-Commit | Erfolgs-/Fehlerpfade setzen `committed`, Cancel/Exception nur wenn `not committed`. |
| Doppelte Assets | `path_absolute` unique; Scan nutzt `upsert_asset_from_scan`. |
| GUI vs Backend | GUI liest über `ModelUsageGuiService`/`session_scope`, keine zweite Quelle für Usage-Zahlen. |
| Preflight-Ausfall | Siehe Risiko „ALLOW-Fallback“ oben. |

---

## 5. Dokumentation / Help (Änderungen Phase E)

| Datei | Änderung |
|-------|----------|
| `docs/MODEL_USAGE_PHASE_E_QA_REPORT.md` | **Neu** – dieser Bericht. |
| `help/control_center/cc_models.md` | Erweitert: Usage-Tracking, Quota, Unterscheidung Block/Fehler, lokale Assets/`~/ai`. |
| `docs/02_user_manual/models.md` | Erweitert: Verbrauch, Quotas, Speicherorte. |
| `docs/AUDIT_REPORT.md` | Abschnitt Modell-Usage/Quota/Assets (Stand 2026-03-22). |
| `docs/RELEASE_ACCEPTANCE_REPORT.md` | Verweis Phase E + Modellsystem-QA. |
| `help/README.md` | Link auf Phase-E-QA-Bericht. |

---

## 6. Risiken und Restmängel (ehrlich)

1. **Functional correctness:** Cloud-/Online-Szenarien ohne Live-API in CI.  
2. **Runtime robustness:** Preflight-Exception → `ALLOW`; Symlink/Permission-Ecken im Scanner nur teilweise abgebildet.  
3. **Data consistency:** Mehrere App-Instanzen auf derselben DB → klassisches SQLite-Thema (kein Scope dieser Phase).  
4. **UX clarity:** Chat-Details hängen an korrekter Propagation der `model_invocation`-Payload; kein vollständiger GUI-E2E-Nachweis.  
5. **Documentation drift:** Ältere QA-Dokumente unter `docs/qa/**` können ältere Befunde nennen – **maßgeblich** für Modell-Usage sind Phase-B/C/D/E-Berichte + dieser Report.  
6. **Local asset scan/matching:** Konservativ; falsche oder fehlende Zuordnungen möglich.  
7. **Provider variance:** Token-Felder variieren; ohne Provider-Usage → Schätzung (`estimated_tokens`).  
8. **estimated vs exact:** In UI als Qualitätshinweis, nicht als Abrechnungsgrad.

---

## 7. QA-Klassifikation

**Einstufung: `ACCEPTED_WITH_MINOR_FINDINGS`**

**Begründung**

- **Backend-Kern** (Preflight, Ledger, Aggregation, Block/Warn/Fail/Cancel, keine Fake-Tokens bei Providerfehler) ist durch **gezielte Unit-/Service-Tests** belegt; Scanner/Sync und ORM-Grundlagen ebenfalls.
- **Fachliche Lücken** betreffen vor allem **CI-/E2E-Abdeckung** (Live-Ollama/Cloud, vollständige Qt-Oberfläche, SQLite-Datei über App-Restart) und **betriebliche Randfälle** (Preflight-DB-Ausfall).
- **Dokumentation und Help** wurden an den realen Code angeglichen; verbleibende Drift in historischen QA-Artefakten ist bewusst dokumentiert.

**Nicht gewählt**

- `ACCEPTED`: würde Live-E2E und GUI-Regression implizit verhehlen.  
- `REJECTED`: würde den nachweisbaren Backend-Stand verkennen.

---

## 8. Abschlussliste (Deliverables Phase E)

**Neu**

- `docs/MODEL_USAGE_PHASE_E_QA_REPORT.md`

**Geändert**

- `tests/unit/test_phase_b_model_chat_runtime.py` (Cancel, Offline-Hard-Block)  
- `help/control_center/cc_models.md`  
- `docs/02_user_manual/models.md`  
- `docs/AUDIT_REPORT.md`  
- `docs/RELEASE_ACCEPTANCE_REPORT.md`  
- `help/README.md`

**Produktiv sinnvoll nutzbar:** Modellruntime mit Instrumentierung, Quota-Policies, Usage-Aggregation, lokale Asset-Registry inkl. Scan, GUI-Fassaden – unter den genannten Einschränkungen.

**Model-Usage-Gate (Nacharbeit umgesetzt):**

- **Marker:** `model_usage_gate` (registriert in `pytest.ini`).
- **Lokal:** `pytest -m model_usage_gate -q --tb=short` oder `./scripts/qa/run_model_usage_gate.sh`.
- **CI:** Workflow [`.github/workflows/model-usage-gate.yml`](../.github/workflows/model-usage-gate.yml) (Push/PR auf `main`/`develop`).
- **Inhalt (39 Tests):** `test_phase_b_model_chat_runtime` (Runtime/Preflight/Cancel/Offline-Block), `test_phase_a_orm_services` (ausgewählte Usage/Aggregation/Quota/Registry-Tests), `test_local_model_scanner_service`, `test_model_usage_gui_service`, `test_model_invocation_display`, plus **ein** SQLite-**Datei**-Test `tests/integration/test_model_usage_sqlite_file_gate.py` (Ledger + Aggregat nach `engine.dispose()` und Reopen).
- **Bewusst nicht im Gate:** Live-Ollama/Cloud, Qt-/GUI-E2E, volle pytest-Gesamtsuite, Alembic-Dateiexistenz-Check (`test_alembic_revision_file_exists`).
