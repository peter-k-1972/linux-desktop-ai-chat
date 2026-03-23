# EXECUTION_BACKLOG – Gap-Schließung Linux Desktop Chat

**Stand:** 2026-03-20  
**Legende Aufwand:** S ≤ ca. 0,5 PT · M ≤ ca. 2 PT · L > 2 PT (indikativ, Team-abhängig)  
**Legende Priorität:** P0 kritisch · P1 hoch · P2 mittel · P3 niedrig  
**Quelle:** A = STATUS_AUDIT · P = PLACEHOLDER_INVENTORY · D = DOC_PROMISE_MISMATCH · M = IMPLEMENTATION_GAP_MATRIX · T = TEST_GAP_REPORT

| ID | Bereich | Aufgabe | Quelle | Priorität | Aufwand | Risiko | Abhängigkeiten | DoD |
|----|---------|---------|--------|-----------|---------|--------|-----------------|-----|
| R-DOC-01 | Doku | `AGENT_UI_ARCHITECTURE_EVALUATION.md`: CC Agents = `AgentManagerPanel` + `AgentService`; kein fiktiver Demo-Only-Tab | D, A | P0 | M | Niedrig | — | Review gegen `agents_workspace.py`; keine widersprüchlichen Tabellen |
| R-DOC-02 | Doku | `AGENTS_UI_ARCHITECTURE_AUDIT.md`: gleiche Korrektur oder Archiv-Banner + Datum | D, A | P0 | M | Niedrig | — | Wie R-DOC-01 |
| R-DOC-03 | Doku | `COMMAND_CENTER_ARCHITECTURE.md`: Pfade `app/gui/domains/command_center/...` statt `app/ui/...` oder Archiv | D, A | P0 | S | Niedrig | — | `rg app/ui/command_center` im Dokument = 0 oder erklärt |
| R-DOC-04 | Doku | `DOC_GAP_ANALYSIS.md`: überholte BLOCKER/HIGH (README, intro-Link, SETTINGS, help context, SYSTEM_MAP-Stichprobe) bereinigen | D, A | P0 | S | Niedrig | — | Abschnitt 2/3 reflektiert Ist; verbleibende Lücken explizit |
| R-DOC-05 | Doku | Root `README.md`: CC-Zeile präzisieren (Tools/Data Stores Demo vs. Live) | D, A | P0 | S | Niedrig | Entscheid R-GUI-01/02 oder temporäre Fußnote | README widerspricht nicht PLACEHOLDER_INVENTORY |
| R-GUI-01 | GUI / Produkt | **Entscheid** CC Tools: Live verdrahten / Demo-Banner / Nav ausblenden | P, A, M | P0 | S | Mittel | — | Schriftlich 1 Seite; verlinkt in Ticket |
| R-GUI-02 | GUI / Produkt | **Entscheid** CC Data Stores: analog R-GUI-01 | P, A, M | P0 | S | Mittel | — | Wie R-GUI-01 |
| R-GUI-03 | GUI / Produkt | **Entscheid** Dashboard (`DashboardScreen`): verlinken / Empty State / aus Nav | P, A, M, T | P0 | S | Mittel | — | UX-Erwartung dokumentiert |
| R-GUI-04 | GUI | CC `tools_panels.py` / `tools_workspace.py`: Umsetzung gemäß R-GUI-01 | P, M | P0/P1 | M–L | Hoch | R-GUI-01 | Kein unmarkiertes `dummy_data` als Live |
| R-GUI-05 | GUI | CC `data_stores_panels.py` / Workspace: Umsetzung gemäß R-GUI-02 | P, M | P0/P1 | M–L | Hoch | R-GUI-02 | Keine falschen „Connected“ ohne Datenbasis |
| R-GUI-06 | GUI | Dashboard-Panels: Umsetzung gemäß R-GUI-03 | P, T | P0/P1 | M | Mittel | R-GUI-03 | Docstring/UI konsistent |
| R-GUI-07 | Code-Struktur | `agents_panels.py` + `control_center/panels/__init__.py`: entfernen, umbenennen oder isolieren; Namenskollision `AgentRegistryPanel` auflösen | A, P, M, T | P1 | M | Mittel | `rg`/CI keine unbeabsichtigten Imports | Architektur-Guards grün |
| R-GUI-08 | GUI | `index_overview_panel.py` / `retrieval_status_panel.py`: Platzhaltertext ersetzen (Daten oder ehrlicher Empty State) | P, M | P2 | M | Niedrig | Optional R-BE-04 | Kein irreführendes „(Platzhalter)“ ohne Kontext |
| R-GUI-09 | GUI | `preview_panel.py` (Prompt Studio): Vorschau anbinden oder Empty State | P, M | P2 | M | Niedrig | Optional R-BE-05 | Wie R-GUI-08 |
| R-GUI-10 | GUI | `status_panel.py` / `queue_panel.py` (Agent Tasks): dynamisch oder ehrlicher Text | P, M | P2 | M | Niedrig | Optional R-BE-06 | Wie R-GUI-08 |
| R-GUI-11 | GUI | `command_center_view.py`: Subsystem-Detail-Kommentar „placeholder“ auflösen (befüllen oder entfernen) | P, A | P3 | S | Niedrig | — | Code/Doku ohne toten Kommentar-Widerspruch |
| R-GUI-12 | GUI | `workspace_graph.py`: EN-Platzhaltertext lokalisieren (optional) | P | P3 | S | Niedrig | — | Konsistent mit Hauptsprache oder i18n-Regel |
| R-BE-01 | Backend | CC Tools: Service/Registry-Anbindung **falls** R-GUI-01 = Live | M, A | P1 | L | Hoch | R-GUI-04 | Fehlerpfad + leere Liste definiert |
| R-BE-02 | Backend | CC Data Stores: Health aus SQLite/Chroma/File **falls** R-GUI-02 = Live | M, A | P1 | L | Hoch | R-GUI-05 | Keine hardcodierten Health-Strings ohne Check |
| R-BE-03 | Backend / Settings | Project/Workspace: erste persistierte Keys **oder** Nav-Reduktion + Doku | M, P | P2 | L | Mittel | R-DOC-04 | Kein leerer Bereich ohne erklärende Doku |
| R-BE-04 | Backend | Knowledge-Metriken für Index/Retrieval-Panels **falls** UI Live | M | P2 | M | Niedrig | R-GUI-08 | Datenquelle in Docstring |
| R-BE-05 | Backend | Prompt-Preview: Anbindung Test-Lab oder Renderer **falls** UI Live | M | P2 | M | Niedrig | R-GUI-09 | Wie R-BE-04 |
| R-BE-06 | Backend | Agent-Task Status/Queue: Anbindung Runner/DebugStore **falls** UI Live | M | P2 | M | Niedrig | R-GUI-10 | Wie R-BE-04 |
| R-BE-07 | Backend | `PlaceholderComfyUIExecutor` / `PlaceholderMediaExecutor`: Verhalten dokumentiert; ggf. Registry-Warnung | P, M, T | P2 | S | Niedrig | — | Doku + Test (R-TEST-05) |
| R-BE-08 | Backend | `critic.py`: Aufrufer analysieren; implementieren, entfernen oder feature-flaggen | A, M | P3 | M | Unklar | — | Kein offenes TODO ohne Ticket |
| R-TEST-01 | QA | `pytest --collect-only` Fehlerursachen beheben oder markers/skip-Policy | T, A | P1 | L | Hoch | — | Referenz-CI collect exit 0 |
| R-TEST-02 | Test | CC Tools/UI: Contract-Test gemäß R-GUI-01 (Demo-Banner sichtbar **oder** Live-Daten-Mock) | T, P | P1 | M | Mittel | R-GUI-04 | Test grün |
| R-TEST-03 | Test | CC Data Stores: analog R-TEST-02 | T, P | P1 | M | Mittel | R-GUI-05 | Test grün |
| R-TEST-04 | Test | Dashboard: Smoke/Widget nach R-GUI-06 | T | P1 | S | Niedrig | R-GUI-06 | Test grün |
| R-TEST-05 | Test | PlaceholderExecutors: `StepResult` success=False + Message | T | P2 | S | Niedrig | R-BE-07 | Test grün |
| R-TEST-06 | Test | Architektur: nach R-GUI-07 Guards + ggf. Import-Test | T, A | P1 | S | Mittel | R-GUI-07 | `test_gui_does_not_import_ui` o. Ä. grün |
| R-TEST-07 | Test | Regression Chat/Kontext/Markdown bei Änderungen an geteilten Modulen | A, T | P1 | M | Mittel | relevante PRs | Bestehende Suites ungebrochen |
| R-TEST-08 | Test | Optional: Guard „agents_workspace importiert AgentManagerPanel“ | T, D | P3 | S | Niedrig | R-DOC-01 | Test grün |
| R-DOC2-01 | Doku | Developer-Guide: CLI `app/cli/*`, Repro-Registry, erwartete Artefakte | A, D | P2 | M | Niedrig | — | Neue/aktualisierte Seite verlinkt |
| R-DOC2-02 | Doku | Weitere `docs/**` mit `app/ui/`: Archiv-Banner oder Batch-Fix (priorisiert nach Einlinks) | D, A | P2 | L | Niedrig | R-DOC-03 | Top-N Links bereinigt |
| R-DOC2-03 | Doku | SYSTEM_MAP/FEATURE_REGISTRY: Regenerationsanleitung + Verantwortlichkeit | D | P2 | S | Niedrig | — | Im Developer-Guide nachlesbar |
| R-DOC2-04 | Doku | Deployment/Packaging: Minimaldoc oder „out of scope“ | D | P3 | S | Niedrig | — | DOC_GAP aktualisiert |
| R-QA-01 | QA | Abschluss: `QA_ACCEPTANCE_MATRIX.md` blockierende Zeilen + Sign-off | `MASTER_REMEDIATION_PLAN` §8 | P0 | S | Niedrig | R-TEST-01, relevante Phasen | Matrix vollständig; Release-Note |

---

## Mapping Backlog → Phase

| Phase | Backlog-IDs |
|-------|-------------|
| 1 | R-DOC-01 – R-DOC-05 |
| 2 | R-GUI-01 – R-GUI-07, R-GUI-08 – R-GUI-12 (08–12 nach Kapazität) |
| 3 | R-BE-01 – R-BE-08 (nur wenn Live/Scope) |
| 4 | R-TEST-01 – R-TEST-08 |
| 5 | R-DOC2-01 – R-DOC2-04 |
| 6 | R-QA-01 |

---

*Ende EXECUTION_BACKLOG*
