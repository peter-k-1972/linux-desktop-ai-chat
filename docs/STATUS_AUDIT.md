# STATUS_AUDIT – Linux Desktop Chat

**Stand der Analyse:** 2026-03-20  
**Methode:** Code- und Durchsuchung der Codebasis (`app/`, `tests/`, `docs/`, `help/`), Abgleich mit bestehenden Reports (`docs/AUDIT_REPORT.md`, `docs/DOC_GAP_ANALYSIS.md`). **Keine Codeänderungen** im Rahmen dieser Aufgabe.

**Hinweis Umgebung:** Vollständiger `pytest --collect-only` im Analyse-Workspace brach mit **30 Collection-Errors** ab (siehe `docs/TEST_GAP_REPORT.md`). Aussagen zur Testlage stützen sich auf vorhandene Testdateien und Stichproben, nicht auf eine grüne Gesamtsuite.

---

## Executive Summary

Das Projekt ist **funktional weit fortgeschritten**: Chat-Pfad (GUI → `ChatService` → Provider), Kontext-Governance, Agenten-HR über `AgentManagerPanel` im Control Center, RAG-/Knowledge-UI, Prompt Studio, Settings mit acht Kategorien und umfangreiche QA-/Context-Tests sind im Repository angelegt.

**Harte Lücken** konzentrieren sich auf: (1) **Control Center → Tools / Data Stores** und Teile der **Kommandozentrale (Dashboard)** – sichtbar „fertige“ Oberflächen mit **statischer oder Dummy-Daten** statt Live-Backend; (2) **Settings → Project / Workspace** – bewusste **Empty States** ohne konkrete Formulare; (3) **Pipeline-Executors** für ComfyUI/Media – explizite Platzhalter mit Fehlermeldung; (4) **Dokumentationsdrift**: mehrere Architektur-/QA-Dokumente vom **2026-03-16** beschreiben den **Control-Center-Agents-Tab noch als reine Demo-Tabelle** – der **aktuelle Code** nutzt dort `AgentManagerPanel` mit `AgentService` (`agents_workspace.py`); (5) **Historische Pfade `app/ui/`** in älteren Reports – Verzeichnis **`app/ui/` existiert im Workspace nicht** (0 Dateien unter `app/ui/**`).

---

## Implementierungsstand

### Vollständig bzw. produktiv nutzbar (nach Codepfad, ohne E2E-Garantie)

| Bereich | Kurzbeleg |
|--------|-----------|
| Chat | `app/services/chat_service.py`, `app/gui/domains/operations/chat/`; Streaming/Thinking-Fallback in `chat_workspace.py` (siehe `docs/AUDIT_REPORT.md` §3.1) |
| Kontext | Modi, Limits, Explainability – `app/context/`, `app/services/chat_service.py`, Tests unter `tests/chat/`, `tests/context/` |
| Agenten (CRUD / Profile) | `AgentManagerPanel` + `AgentService` in `app/gui/domains/control_center/agents_ui/agent_manager_panel.py` |
| Agent Tasks (Operations) | `AgentTasksWorkspace` mit echtem `AgentRegistryPanel` unter `operations/agent_tasks/panels/agent_registry_panel.py` |
| Prompts | `app/prompts/`, Prompt-Studio unter `app/gui/domains/operations/prompt_studio/` |
| RAG / Knowledge | `app/rag/`, `app/services/knowledge_service.py`, Knowledge-Workspace |
| Settings (Application … Advanced) | Mehrere Kategorie-Panels unter `app/gui/domains/settings/` |
| Command Center (QA-Drilldowns) | `app/gui/domains/command_center/command_center_view.py` mit `QADashboardAdapter` u. a. |
| Runtime Debug / Markdown-Demo | `MarkdownDemoWorkspace` – **bewusst** intern (`runtime_debug_screen.py`) |
| CLI Context / Replay | `app/cli/` (Doku-Lücken siehe unten) |

### Teilweise / Platzhalter / irreführend wirkend

| Bereich | Befund |
|--------|--------|
| Control Center → **Tools** | `ToolRegistryPanel` mit `dummy_data`, statische Summary (`tools_panels.py`, `tools_workspace.py` – Text „7 Tools verfügbar …“) |
| Control Center → **Data Stores** | `dummy_data` in Tabellen, statische Health-Labels (`data_stores_panels.py`) |
| **Kommandozentrale Dashboard** | `SystemStatusPanel`, `ActiveWorkPanel`, `QAStatusPanel`, `IncidentsPanel` – Docstrings „Platzhalter-UI ohne Backend-Logik“ (`app/gui/domains/dashboard/panels/`) |
| **Settings Project / Workspace** | `ProjectCategory`, `WorkspaceCategory` – Empty State „wird in einer zukünftigen Version erweitert“ |
| **Knowledge** – Index/Retrieval-Status-Panels | Labels „(Platzhalter)“ (`index_overview_panel.py`, `retrieval_status_panel.py`) |
| **Prompt Studio** – Vorschau | `preview_panel.py`: „Vorschau, Test-Ausführung. (Platzhalter)“ |
| **Agent Tasks** – Status/Queue | `status_panel.py`, `queue_panel.py` mit Platzhalter-Texten |
| **Pipelines** | `PlaceholderComfyUIExecutor`, `PlaceholderMediaExecutor` geben `not yet implemented` zurück (`placeholder_executors.py`) |
| **`app/critic.py`** | Kommentar `# TODO: Implementierung wenn aktiviert` – unklar ob Feature aktiv genutzt |

### Referenziert, im Workspace nicht auffindbar / Drift

| Thema | Befund |
|--------|--------|
| Paket **`app.ui`** | Migration-Reports und `docs/04_architecture/COMMAND_CENTER_ARCHITECTURE.md` verweisen auf `app/ui/...` – **kein** `app/ui/` im aktuellen Tree; Guards in `tests/architecture/test_gui_does_not_import_ui.py` erwähnen Migration |
| **`app/gui/domains/control_center/panels/agents_panels.py`** | Enthält weiterhin **Demo-`AgentRegistryPanel`** – wird von **keinem Workspace** importiert; kanonisch ist `AgentManagerPanel` in `agents_workspace.py` |

---

## GUI-Gaps

- **Irreführende Daten:** Tools- und Data-Stores-Workspaces zeigen Tabellen mit festen Zeilen; Beschriftung „Vorschau (… bei Verbindung)“ mildert nur teilweise (Nutzer können trotzdem „Connected“ o. Ä. als Wahrheit lesen).
- **Dashboard:** Vier Karten ohne Anbindung an Live-Metriken/Incident-Feeds (explizit im Moduldocstring).
- **Bewusste leere Settings-Bereiche:** Project/Workspace sichtbar in der Navigationsstruktur, aber ohne editierbare Keys.
- **Subpanels mit „(Platzhalter)“:** Knowledge (Index/Retrieval-Übersicht), Prompt-Vorschau, Agent-Task-Status/Warteschlange.
- **Doppelnamen:** Zwei verschiedene Klassen `AgentRegistryPanel` (Control Center `agents_panels.py` vs Operations `agent_tasks/.../agent_registry_panel.py`) – erhöht Risiko für falsche Annahmen beim Lesen von Doku/Reports.

---

## Backend-Gaps

- **Tool-Registry / zentrale Tool-Verwaltung:** Keine evidenzbasierte Anbindung der CC-Tools-UI an einen Service (Tabelle hardcoded).
- **Data-Store-Übersicht:** Gleiches Muster – keine Live-Health aus `database_manager` / Chroma-Client in diesen Panels ersichtlich.
- **Pipeline-Schritte ComfyUI/Media:** Executors liefern bewusst Fehlschlag mit Platzhalter-Fehlertext.
- **`critic.py`:** Offenes TODO – End-to-End-Nutzung unklar ohne weitere Suche nach Aufrufern (hier: **unklar / verifizieren**).

---

## Dokumentations-Gaps

- **`docs/DOC_GAP_ANALYSIS.md` (Stand 2026-03-20):** Mehrere „BLOCKER“-Punkte sind **teilweise überholt**: Root-`README.md` existiert; Link in `docs/01_product_overview/introduction.md` zeigt auf `../02_user_manual/models.md`; `docs/04_architecture/SETTINGS_ARCHITECTURE.md` ist mit `settings_workspace.py` abgeglichen; `docs/SYSTEM_MAP.md` listiert kein `app/ui/` mehr im geprüften Ausschnitt; `help/settings/settings_chat_context.md` existiert.
- **Weiterhin relevant:** Historische Reports mit **`app/ui/`-Pfaden**; `docs/04_architecture/COMMAND_CENTER_ARCHITECTURE.md` mit **`app/ui/command_center/...`** widerspricht der Implementierung unter `app/gui/domains/command_center/`.
- **CLI / Repro-Registry:** `docs/DOC_GAP_ANALYSIS.md` – geringe Markdown-Abdeckung für `app/cli/` und neue Repro-Registry-Module; **Fundstelle:** keine systematische Vollverifikation aller `.md`-Dateien, stichprobenartig weiterhin lückenhaft.

---

## Doku-vs-Code-Widersprüche

| Dokument | Problem |
|----------|---------|
| `docs/qa/architecture/AGENT_UI_ARCHITECTURE_EVALUATION.md` | Behauptet `agents_workspace` nutze Demo-`AgentRegistryPanel` ohne `AgentService` – **widerspricht** `app/gui/domains/control_center/workspaces/agents_workspace.py` (nutzt `AgentManagerPanel`). |
| `docs/04_architecture/AGENTS_UI_ARCHITECTURE_AUDIT.md` | Gleiche veraltete Darstellung des Agents-Tabs. |
| `docs/04_architecture/COMMAND_CENTER_ARCHITECTURE.md` | Pfade `app/ui/command_center/...` – **kein** entsprechendes Paket im Tree; Code liegt unter `app/gui/domains/command_center/`. |
| Migrations-/Phase-Reports | Verweise auf `app/ui/agents` als aktiven Pfad – **Archiv/History**, nicht Ist-Dateisystem. |

Detailtabelle: `docs/DOC_PROMISE_MISMATCH_REPORT.md`.

---

## Platzhalter-Inventar

Siehe **`docs/PLACEHOLDER_INVENTORY.md`** (tabellarisch).

---

## Test- und QA-Lage

- **Breite Abdeckung in Dateien:** Hunderte Testmodule unter `tests/` (u. a. `unit/`, `integration/`, `smoke/`, `ui/`, `context/`, `chat/`, `architecture/`, `qa/`).
- **Lokale Collection:** `pytest --collect-only` **fehlgeschlagen** (30 Errors) – verhindert belastbare Aussage „alle Tests sammeln grün“ ohne Umgebungsfix.
- **Regressionsschwerpunkte** (laut vorhandener Struktur und `docs/AUDIT_REPORT.md`): Chat-Streaming, Kontext-Governance, Markdown-Pipeline, Architektur-Guards.

Detail: `docs/TEST_GAP_REPORT.md`.

---

## Architektur- und Konsistenzprobleme

- **Entferntes `app.ui` vs. Doku/Guards:** Tests erwähnen Übergangsphase; ältere Markdown-Reports nicht bereinigt.
- **Tote oder irreführende CC-Panels-Datei:** `agents_panels.py` (Demo) vs. reale `agents_ui`-Implementierung.
- **Namenskollision:** Zwei `AgentRegistryPanel`-Klassen in verschiedenen Paketen.
- **Dashboard vs. Command Center:** Zwei „Kommandozentrale“-artige Einstiege – Dashboard platzhalterisch, `CommandCenterView` datengetriebener; UX-Risiko der Erwartungssteuerung.

---

## Priorisierte Hauptrisiken

1. **Hohes UX-/Vertrauensrisiko:** Control Center Tools/Data Stores und Dashboard-Karten wirken produktiv, sind aber statisch bzw. ohne Backend – dokumentierte QA-Befunde in `docs/06_operations_and_qa/UX_DEFECTS_*` decken das konsistent ab.  
2. **Fehlentscheidungen durch veraltete Architektur-Doku:** Agents-Control-Center und `app/ui`-Pfade.  
3. **Wartbarkeit:** Doppelte `AgentRegistryPanel`-Namensgebung und unbenutzte `agents_panels`-Demo-Code.  
4. **Release-/CI-Risiko:** Wenn Test-Collection in CI ebenfalls fehlschlägt, ist die Gate-Qualität unklar – **verifizieren** in der echten Pipeline.  
5. **Pipeline-/Media-Erwartung:** Nutzer oder interne Definitionen könnten ComfyUI/Media-Schritte erwarten – Executors sind bewusst nicht implementiert.

---

## Nachtrag 2026-03-22 — Modell-Verbrauch, Quotas, lokale Assets

Dieser STATUS_AUDIT (Stichtag 2026-03-20) enthielt **keine** eigene Bewertung des **Model-Usage-/Quota-/Asset-Systems** (Phasen A–D). Die **aktuelle QA-Abnahme** dazu liegt in [`MODEL_USAGE_PHASE_E_QA_REPORT.md`](MODEL_USAGE_PHASE_E_QA_REPORT.md); technischer Audit-Auszug in [`AUDIT_REPORT.md`](AUDIT_REPORT.md) Abschnitt 11.

---

*Ende STATUS_AUDIT*
