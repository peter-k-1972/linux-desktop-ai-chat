# CHANGELOG_REMEDIATION

**Zeitraum:** Umsetzung MASTER_REMEDIATION_PLAN / Audit-Gap-Schließung (2026-03-20)  
**Art:** Funktionale und dokumentarische Änderungen am Ist-Projekt.

---

## Phase 1 – Doku vs. Anwendung

**Umgesetzt**

- `docs/qa/architecture/AGENT_UI_ARCHITECTURE_EVALUATION.md` – Abschnitt **2a** (Ist-Stand CC Agents), historische Abschnitte gekennzeichnet.
- `docs/04_architecture/AGENTS_UI_ARCHITECTURE_AUDIT.md` – Executive Summary und Control-Center-Inventar an `AgentManagerPanel` / Entfernung `agents_panels` angepasst.
- `docs/04_architecture/COMMAND_CENTER_ARCHITECTURE.md` – Modulpfade auf `app/gui/domains/command_center/` korrigiert.
- `docs/DOC_GAP_ANALYSIS.md` – BLOCKER-Liste als erledigt/markiert; SETTINGS-Hinweis aktualisiert; Help-Kontext ergänzt.
- `README.md` – Control Center: Tools/Data Stores als Live-Snapshots beschrieben.

**Bewusst nicht umgesetzt**

- Vollständiges Durchforsten aller historischen `app/ui/`-Verweise in jedem Archiv-Report (nur priorisierte Kern-Dokus angepasst).

---

## Phase 2 – GUI-Platzhalter & tote Verzweigungen

**Umgesetzt**

- `app/gui/domains/control_center/panels/tools_panels.py` – echte Daten aus `build_tool_snapshot_rows()`, Refresh-Button, erklärender Banner.
- `app/gui/domains/control_center/panels/data_stores_panels.py` – SQLite-/RAG-/Chroma-Proben über `build_data_store_rows()`, Refresh.
- `app/gui/domains/control_center/workspaces/tools_workspace.py`, `data_stores_workspace.py` – ehrliche Detail-Hinweise; Inspector mit Snapshot-Zeile.
- `app/gui/domains/control_center/panels/agents_panels.py` – **gelöscht** (Demo-Duplikat).
- `app/gui/domains/control_center/panels/__init__.py` – Exporte bereinigt.
- `app/gui/domains/dashboard/*` – `SystemStatusPanel`, `QAStatusPanel`, `IncidentsPanel` mit `refresh()` und echten bzw. QA-JSON-Daten; `ActiveWorkPanel` mit klarem Nicht-Tracker-Hinweis; `dashboard_screen.py` mit `showEvent`-Refresh.
- `app/gui/domains/operations/prompt_studio/panels/preview_panel.py` – Live-Vorschau (readonly) des Editors.
- `app/gui/domains/operations/prompt_studio/prompt_studio_workspace.py` + `prompt_editor_panel.py` – Signal `editor_state_changed` / öffentliche Getter.
- `app/gui/domains/operations/knowledge/panels/index_overview_panel.py`, `retrieval_status_panel.py` – dünne Re-Exports auf kanonische Panels (Legacy-Pfade).
- `app/gui/domains/operations/agent_tasks/panels/status_panel.py`, `queue_panel.py` – **gelöscht** (ungenutzt).
- `app/gui/navigation/workspace_graph.py` – deutscher Platzhaltertext.
- `app/gui/domains/command_center/command_center_view.py` – Kommentar zum Subsystem-Detail präzisiert.

**Bewusst nicht umgesetzt**

- **Settings → Project / Workspace:** weiterhin Empty State (`ProjectCategory` / `WorkspaceCategory`) – keine neuen Keys ohne Produktentscheid.
- Navigationseinträge für CC Tools/Data Stores nicht entfernt (stattdessen echte Inhalte).

---

## Phase 3 – Backend & Kopplung

**Umgesetzt**

- **Neu:** `app/services/infrastructure_snapshot.py` – zentrale, GUI-freie Snapshots (SQLite RO-Probe, RAG-Basis + Chroma-Dateisuche, eingebaute Tool-Zeilen, synchrone Ollama-`/api/tags`-Probe für Dashboard).
- `app/critic.py` – bei `enabled=True` klares **Logging** statt stiller TODO-Zeile; Rückgabe der Primärantwort unverändert.

**Bewusst nicht umgesetzt**

- **Zentrale externe Tool-Registry** – existiert im Produkt nicht; CC-Tools zeigen nur eingebaute Pfade.
- **ComfyUI/Media-Pipeline-Executors** – weiterhin explizite Placeholder-Implementierung (`placeholder_executors.py`); kein neues Backend.
- **Critic-LLM-Review-Pipeline** – nicht implementiert (nur Transparenz).

---

## Phase 4 – Tests

**Umgesetzt**

- `tests/unit/test_infrastructure_snapshot.py` – Proben für SQLite, Tool- und Data-Store-Rows.

**Bewusst nicht umgesetzt**

- **`pytest --collect-only` gesamtes Repo** auf dem Analyse-Host weiterhin fehlerhaft, wenn `qasync` (und ggf. weitere Pakete) nicht in der **aktiven venv** installiert sind (PEP 668 / system-python). `requirements.txt` listet `qasync` bereits.

---

## Phase 5 – Doku-Konsolidierung

**Umgesetzt**

- `docs/05_developer_guide/CLI_CONTEXT_TOOLS.md` – CLI-Überblick.
- `docs/05_developer_guide/README.md` – Verlinkung.
- `app/gui_designer_dummy/DESIGNER_MAPPING.md` – Hinweis auf entferntes `agents_panels.py`.

**Bewusst nicht umgesetzt**

- Eigenständiges **Deployment-/Packaging-Handbuch** (DOC_GAP: weiter offen oder „out of scope“).
- Regenerierung von `docs/TRACE_MAP.md` / `app-tree.md` (verweisen ggf. noch auf entfernte Dateien).

---

## Phase 6 – QA / Freigabe

**Teilweise**

- QA-Matrix aus `docs/QA_ACCEPTANCE_MATRIX.md` wurde nicht als formelles Sign-off-Dokument ausgefüllt; technische Voraussetzungen für QA-01–QA-07 und QA-14 wurden überwiegend adressiert (siehe `REMAINING_GAPS_AFTER_IMPLEMENTATION.md`).

---

## Betroffene Dateien (Kernliste)

- Neu: `app/services/infrastructure_snapshot.py`, `tests/unit/test_infrastructure_snapshot.py`, `docs/05_developer_guide/CLI_CONTEXT_TOOLS.md`, `docs/CHANGELOG_REMEDIATION.md`, `docs/REMAINING_GAPS_AFTER_IMPLEMENTATION.md`
- Geändert: Control-Center-Panels/Workspaces, Dashboard-Screen/Panels, Prompt-Studio, `app/critic.py`, diverse `docs/**`, `README.md`, `DESIGNER_MAPPING.md`
- Gelöscht: `app/gui/domains/control_center/panels/agents_panels.py`, `app/gui/domains/operations/agent_tasks/panels/status_panel.py`, `app/gui/domains/operations/agent_tasks/panels/queue_panel.py`

---

## Offene Restrisiken

Siehe **`docs/REMAINING_GAPS_AFTER_IMPLEMENTATION.md`**.
