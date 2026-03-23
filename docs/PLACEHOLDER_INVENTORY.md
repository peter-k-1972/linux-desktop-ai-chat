# PLACEHOLDER_INVENTORY – Linux Desktop Chat

**Stand:** 2026-03-20 · Inventar aus Code- und String-Suche (`PLACEHOLDER`, `Platzhalter`, `dummy_data`, `Vorschau`, Demo-Panels, explizite Docstrings). Keine vollständige semantische Analyse jedes `pass` in ABCs.

| Bereich | Datei | Klasse/Funktion | UI-Element | Art des Platzhalters | Aktueller Text / Verhalten | Erwartetes Zielverhalten (Soll aus Nutzersicht) | Priorität |
|---------|--------|-----------------|------------|----------------------|-----------------------------|-----------------------------------------------|-----------|
| Control Center – Tools | `app/gui/domains/control_center/panels/tools_panels.py` | `ToolRegistryPanel._setup_ui` | QLabel, QTableWidget | Statische Demo-Tabelle | Label „Vorschau (Tools bei Verbindung)“; feste 5 Zeilen (`dummy_data`) | Live-Tool-Liste aus Registry/Service, Verbindungsstatus echt | Hoch |
| Control Center – Tools | `app/gui/domains/control_center/workspaces/tools_workspace.py` | `ToolsWorkspace._setup_ui` | QLabel im Detail-Frame | Statischer Summary-Text | „7 Tools verfügbar · 5 Kategorien · Alle berechtigt“ | Aus echter Policy/Registry berechnen oder als Demo klar kennzeichnen | Hoch |
| Control Center – Data Stores | `app/gui/domains/control_center/panels/data_stores_panels.py` | `DataStoreOverviewPanel._setup_ui` | Tabelle | Demo-Zeilen | „Vorschau (Stores bei Verbindung)“; `dummy_data` SQLite/Chroma/File | Echte Verbindungs- und Health-Daten | Hoch |
| Control Center – Data Stores | `app/gui/domains/control_center/panels/data_stores_panels.py` | `DataStoreHealthPanel._setup_ui` | Labels | Statisch „Healthy“/„OK“ | Fest codierte grüne Status-Texte | Health-Checks gegen DB/Vector Store | Hoch |
| Control Center – Agents (Legacy-Panel) | `app/gui/domains/control_center/panels/agents_panels.py` | `AgentRegistryPanel` | QTableWidget | Demo-Daten | 3 feste Agenten-Zeilen | **Hinweis:** wird von Workspaces nicht importiert; kanonisch `AgentManagerPanel` | Mittel (toter Code / Verwirrung) |
| Control Center – Agents (Legacy-Panel) | `app/gui/domains/control_center/panels/agents_panels.py` | `AgentSummaryPanel` | QLabel-Zeilen | Statisch | „Research Agent“, feste Skills/Modell | Entfällt wenn Panel entfernt oder durch echte Daten ersetzt | Mittel |
| Dashboard | `app/gui/domains/dashboard/panels/system_status_panel.py` | `SystemStatusPanel` | Gesamtes Panel | Docstring: Platzhalter ohne Backend | Kurztext ohne Live-Daten | Systemmetriken (CPU, Ollama, DB, …) nach Produktziel | Hoch |
| Dashboard | `app/gui/domains/dashboard/panels/active_work_panel.py` | `ActiveWorkPanel` | — | Platzhalter-UI | Meta-Text | Echte „aktive Arbeit“-Aggregation | Hoch |
| Dashboard | `app/gui/domains/dashboard/panels/qa_status_panel.py` | `QAStatusPanel` | — | Platzhalter-UI | „Tests, Coverage, Gaps, Governance.“ | Anbindung an QA-Daten/Adapter wie Command Center | Hoch |
| Dashboard | `app/gui/domains/dashboard/panels/incidents_panel.py` | `IncidentsPanel` | — | Platzhalter-UI | — | Incident-Feed oder Link in echte QA-Views | Hoch |
| Settings | `app/gui/domains/settings/categories/project_category.py` | `ProjectCategory` | `EmptyStateWidget` | Bewusster Empty State | „Dieser Bereich wird in einer zukünftigen Version erweitert.“ | Projektspezifische Settings-Formulare | Mittel |
| Settings | `app/gui/domains/settings/categories/workspace_category.py` | `WorkspaceCategory` | `EmptyStateWidget` | Bewusster Empty State | „Dieser Bereich wird in einer zukünftigen Version erweitert.“ | Workspace-spezifische Settings | Mittel |
| Knowledge | `app/gui/domains/operations/knowledge/panels/index_overview_panel.py` | — | QLabel | Text-Platzhalter | „Embeddings, Chunks, Status. (Platzhalter)“ | Echte Index-Statistiken | Mittel |
| Knowledge | `app/gui/domains/operations/knowledge/panels/retrieval_status_panel.py` | — | QLabel | Text-Platzhalter | „Bereit. (Platzhalter)“ | Retrieval-/Indexer-Status | Mittel |
| Prompt Studio | `app/gui/domains/operations/prompt_studio/panels/preview_panel.py` | — | QLabel | Text-Platzhalter | „Vorschau, Test-Ausführung. (Platzhalter)“ | Vorschau/Test gegen Modell oder Stub | Mittel |
| Agent Tasks | `app/gui/domains/operations/agent_tasks/panels/status_panel.py` | — | QLabel | Text-Platzhalter | „Status: Bereit. (Platzhalter)“ | Echter Runner-/Queue-Status | Mittel |
| Agent Tasks | `app/gui/domains/operations/agent_tasks/panels/queue_panel.py` | — | QLabel | Text-Platzhalter | „Laufende Tasks, Warteschlange. (Platzhalter)“ | Live-Queue | Mittel |
| Command Center View | `app/gui/domains/command_center/command_center_view.py` | (Aufbau) | Subsystem-Detail | Kommentar-Platzhalter | Kommentar: „placeholder, wird bei Bedarf befüllt“ | Entweder befüllen oder UI vereinfachen | Niedrig–Mittel |
| Runtime Debug | `app/gui/devtools/markdown_demo_panel.py` | `MarkdownDemoWorkspace` | Gesamter Workspace | **Intentionale** Dev-/QA-UI | Banner, Demo-Samples | Kein Produktionsfeature – als intern kennzeichnen (bereits unter Runtime Debug) | Niedrig |
| Navigation Graph | `app/gui/navigation/workspace_graph.py` | — | QLabel | Leer-Zustand | „Hover over a workspace to see details“ (EN) | Optional: Lokalisierung/Konsistenz mit DE-UI | Niedrig |
| Chat / Formulare | diverse `setPlaceholderText(...)` | — | Eingabefelder | **Normale** UX-Platzhalter | z. B. „Nachricht eingeben...“ | — | — (kein Defekt) |
| Pipelines | `app/pipelines/executors/placeholder_executors.py` | `PlaceholderComfyUIExecutor`, `PlaceholderMediaExecutor` | — | Backend-Platzhalter | `error="... not yet implemented (placeholder)"` | Echte Executor-Integration oder UI deaktivieren | Mittel |
| Critic | `app/critic.py` | Modul | — | TODO-Kommentar | `# TODO: Implementierung wenn aktiviert` | **unklar / verifizieren** ob Feature produktiv | Unklar |

---

### Ergänzung: Streaming-„Platzhalter“ (kein UX-Stub)

| Bereich | Datei | Klasse/Funktion | Art | Hinweis |
|---------|--------|-----------------|-----|---------|
| Chat Streaming | `app/gui/domains/operations/chat/panels/conversation_panel.py` | `add_assistant_placeholder` | Technischer Platzhalter-Bubble | Legitimes Pattern bis Tokens eintreffen; getestet laut `docs/AUDIT_REPORT.md` |

---

*Ende PLACEHOLDER_INVENTORY*
