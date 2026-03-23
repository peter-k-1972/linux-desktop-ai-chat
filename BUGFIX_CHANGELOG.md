# Bugfix Changelog — Stabilität (Linux Desktop Chat)

**Datum:** 2026-03-21  
**Bezug:** `TEST_EXECUTION_REPORT.md`, `TEST_STABILITY_REPORT.md`

---

## 1. QA-Governance-Tests: falsche Pfade zu Artefakten

| | |
|--|--|
| **Fehler** | Fünf Tests in `test_coverage_map_governance.py` und ein Test in `test_inventory_governance.py` wurden per `pytest.skip` übersprungen, obwohl die Dateien im Repo existieren. |
| **Ursache** | Die Pfade wiesen auf `docs/qa/QA_*.json` bzw. `docs/qa/REGRESSION_CATALOG.md`. Tatsächliche Ablage: `docs/qa/artifacts/json/` und `docs/qa/governance/REGRESSION_CATALOG.md` (vgl. `scripts/qa/qa_paths.py`, `build_test_inventory.py`). |
| **Lösung** | Tests auf die kanonischen Pfade umgestellt (`_ARTIFACTS_JSON`, `governance/REGRESSION_CATALOG.md`). |

**Dateien:** `tests/qa/coverage_map/test_coverage_map_governance.py`, `tests/qa/test_inventory/test_inventory_governance.py`

---

## 2. Nicht geschlossene `aiohttp.ClientSession` (Ollama / Infrastruktur)

| | |
|--|--|
| **Fehler** | Nach der Suite: `ResourceWarning` / „Unclosed client session“; Risiko für instabile CI-Logs und Ressourcenlecks unter Last. |
| **Ursache** | (a) `OllamaClient.close()` setzte `_session` nach `close()` nicht zurück; (b) Live-Hilfsfunktion `_ollama_available()` schloss weder Client noch Loop sauber; (c) `TestOllamaLive` hielt pro Test eine Session ohne garantiertes Teardown; (d) der Infrastruktur-Singleton wurde in Tests ausgetauscht, ohne den bisherigen `OllamaClient` zu schließen; (e) bei laufender Event-Loop musste `close` per Task eingeplant werden, Mock-Clients dürfen kein `asyncio.run` auf Nicht-Coroutinen erhalten. |
| **Lösung** | `OllamaClient.close()` leert die Session-Referenz; `set_infrastructure()` schließt den alten Client best-effort (Awaitable-Prüfung, `asyncio.run` vs. `loop.create_task`); `reset_provider_service()` bei Infra-Wechsel; `pytest_sessionfinish` schließt den Singleton-Client am Session-Ende; Live-Tests: `_ollama_available` mit `finally` + `client.close()`, async-Fixture `ollama_live_client` mit `await client.close()`; analog `test_agent_execution.py`. |

**Dateien:** `app/providers/ollama_client.py`, `app/services/infrastructure.py`, `app/services/provider_service.py`, `tests/conftest.py`, `tests/live/test_ollama.py`, `tests/live/test_agent_execution.py`

---

## 3. Flaky UI-Test: Scrollposition nach Streaming

| | |
|--|--|
| **Fehler** | `test_conversation_scroll_bottom_after_streaming_update` schlug unter Volllast gelegentlich fehl (`sb.value() != sb.maximum()`). |
| **Ursache** | Festes `qtbot.wait(80)` reichte nicht, bis Layout/Scrollbar den Endzustand erreicht hatten. |
| **Lösung** | `qtbot.waitUntil(..., timeout=5000)` mit Bedingung „Maximum gesetzt und Wert am Ende“. |

**Dateien:** `tests/ui/test_chat_message_rendering.py`

---

## 4. Bekannte Rest-Beobachtung (Ausnahme)

| | |
|--|--|
| **Phänomen** | Unter einer vollen Suite erscheint am Prozessende weiterhin **eine** „Unclosed client session“-Meldung (reproduzierbar ~1× pro Lauf), ohne Test-Failures. |
| **Einschätzung** | Vermutlich verbleibende aiohttp-Session außerhalb des Infrastruktur-Singletons oder Finalisierung nach Pytest-Event-Loop-Shutdown; nicht als Regression der obigen Fixes gewertet, aber transparent dokumentiert in `FINAL_TEST_STATUS.md`. |

---

## 5. Keine Code-Änderung (bewusste Ausnahme)

| Thema | Grund |
|-------|--------|
| **PEP 668 / System-Python ohne venv** | Verhalten der Distribution, kein Anwendungsdefekt. Empfehlung: `.venv` + `pip install -r requirements.txt` (wie CI mit isoliertem Python-Prefix). |
