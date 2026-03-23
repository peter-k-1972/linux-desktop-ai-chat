# TEST_GAP_REPORT – Linux Desktop Chat

**Stand:** 2026-03-20

## Umgebungsbefund (Collection)

| Befund | Detail |
|--------|--------|
| Befehl | `python3 -m pytest --collect-only -q` (Repo-Root) |
| Ergebnis | **Abbruch: 30 errors during collection** |
| Konsequenz | Gesamtanzahl „grün sammelbarer“ Tests in dieser Umgebung **nicht** belastbar; CI-Zustand **separat verifizieren** |

Stichprobe: `python3 -m pytest tests/unit/test_markdown_pipeline.py --collect-only -q` → **OK** (7 Tests).

---

## Inventar (orientierend)

| Metrik | Wert (orientierend) |
|--------|---------------------|
| Testdateien `tests/**/test_*.py` | ca. **220+** Dateien (Glob-Stand Analyse) |
| Schwerpunkte | `unit/`, `integration/`, `smoke/`, `ui/`, `context/`, `chat/`, `architecture/`, `qa/`, `failure_modes/`, `chaos/`, `golden_path/` |

---

## Tabellarische Lücken (kritische Use Cases)

| Bereich | Kritischer Use Case | Vorhandene Tests (Beispiele, nicht exhaustiv) | Fehlende / schwache Absicherung | Risiko bei Nichtbehebung |
|---------|--------------------|-----------------------------------------------|----------------------------------|---------------------------|
| Chat Streaming + Thinking-Fallback | Korrekte Anzeige bei `content` leer, NDJSON-Splits | `tests/unit/test_chat_extract_content_streaming.py`, `test_ollama_ndjson_stream.py`, `test_ollama_stream_chat_simulation.py` (siehe `docs/AUDIT_REPORT.md`) | **Live-Ollama** E2E in CI meist fehlend | Regressions nur mit Mock-Stream; API-Drift unentdeckt |
| Control Center Tools/Data Stores | Keine falschen Live-Daten anzeigen | **Keine** dedizierten Tests in Stichprobe für `dummy_data`-Panels | UI-Contract-Tests (Preview vs Live), Snapshot/Label-Tests | Nutzer vertrauen auf falsche Verbindungsdaten |
| Dashboard-Panels | Statuskarten reflektieren System | Keine Tests gefunden für `SystemStatusPanel` / `QAStatusPanel` etc. | Widget-Tests oder Feature-Flag bis implementiert | Falsche Sicherheit im Operations-Überblick |
| Settings Project/Workspace | Persistenz projektbezogener Keys | unklar | Tests wenn Felder eingeführt werden | Datenverlust oder Scope-Fehler |
| Pipeline Comfy/Media Steps | Klare Fehlermeldung, kein stiller Erfolg | Executor-Logik in `placeholder_executors.py` | Integrationstest: Schritt ausführen → erwarteter `StepResult` | Falsche Erwartung in Automatisierungs-Workflows |
| GUI-Gesamtsuite | Regressions in Shell/Navigation | `tests/smoke/`, `tests/ui/`, Architektur-Guards | **Volle** Collection muss in CI grün sein | Ungewissheit über Release-Qualität |
| Doku-generierte Maps | SYSTEM_MAP/FEATURE_REGISTRY aktuell | `tests/architecture/` (Drift-Radar, Map-Contract) | Abgleich mit manuell veralteten Reports | Onboarding-Fehler |
| Agent-Duplikat-Panels | Keine Verwechslung CC-Demo vs Operations-Liste | Operations: `agent_tasks` mit echtem Service; CC: ManagerPanel | Test, dass `agents_panels.AgentRegistryPanel` nicht in Shell gemountet wird (optional) | Wartungsfehler bei Refactors |

---

## Regressionsschwerpunkte (aus bestehender Projekt-Doku)

Aus `docs/AUDIT_REPORT.md` und Ordnerstruktur abgeleitet – weiterhin **zusätzliche** Tests sinnvoll für:

1. **Chat-Guard** (Doppel-Send, Stream-Konflikt) – vorhandene Tests ergänzen bei neuer UI.  
2. **Kontext-Governance** – bestehende Regressionssuite (`test_context_governance_regressions.py` etc.) bei Settings-Änderungen pflegen.  
3. **Markdown-Rendering** – Pipeline + UI-Fallback (`test_markdown_*`).  
4. **Architektur-Imports** – `test_gui_does_not_import_ui.py`, Package-Guards.

---

*Ende TEST_GAP_REPORT*
