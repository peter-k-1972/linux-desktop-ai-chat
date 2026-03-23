# Regressionstest-Matrix (Auszug, nach Umsetzung)

Legende **Testart**: U = Unit, A = Architektur, I = Integration, UI = GUI-nah (Qt ohne pytest-qt), GP = Golden Path, CL = Cross-Layer.

| Bereich | Risiko | Testfall | Testart | Erwartetes Ergebnis |
|---------|--------|----------|---------|---------------------|
| Infrastruktur-Snapshot | Falsche Health-Anzeige | `test_sqlite_probe_*`, `test_probe_ollama_*`, `test_chroma_status_*` | U | Zustände OK / Keine Datei / Fehler / Modul fehlt / Kein Index passen zur Implementierung. |
| Infrastruktur-Snapshot | RAG-Zeile ignoriert Settings | `test_tool_snapshot_includes_rag_row_reflecting_settings` | U | Bei `rag_enabled=True` enthält RAG-Zeile „Aktiv“ (mit gemockter Infrastruktur). |
| Critic | Review aktiviert bricht Stream | `test_review_response_disabled_*` / `enabled` | U | Deaktiviert: Text unverändert; aktiviert: Warnung geloggt, Primärtext zurück. |
| Control-Center Agents | Rückfall auf Demo-Panels | `test_agents_workspace_uses_agent_manager_panel` | A | `_panel` ist `AgentManagerPanel`. |
| Control-Center Agents | Entfernte Dateien wieder da | `test_agents_panels_module_removed` | A | `agents_panels.py` fehlt; `__all__` ohne alte Agent-Panels. |
| Dashboard/CC-Panels | Leere/defekte Tabellen | `test_remediation_panels` (Tool/Data/System/QA/Prompt) | UI | Erwartete Zeilen/Refresh/Signale ohne Exception. |
| QA-Status-Panel | Falscher Adapter-Pfad | `test_qa_status_panel_loads_inventory_counts` | UI | Patch auf `app.qa.dashboard_adapter.QADashboardAdapter`; Anzeige enthält Test-Inventory-Zahl. |
| Prompt-Modell | CRUD bricht nach Schema-Erweiterung | `test_prompt_system*`, `test_prompt_repository`, `test_prompt_golden_path` | U / GP | Create/Get/Update/List/Duplicate mit `scope`/`project_id`. |
| PromptManager GUI | Speichern/Apply crashed | `test_prompt_manager_panel_*`, `test_prompt_ui_service_storage_roundtrip` | UI / I | Speichern, Liste, Editor, Apply-Signal; Editor liefert vollständiges `Prompt`. |
| Chat UI | Conversation/Composer/Header | `test_chat_ui.py` | UI | Sichtbarer Nachrichtentext; `send_requested` bei programmatischem Senden. |
| Chat ↔ Prompt | Einfügen/Menü | `test_chat_prompt_integration.py` | I | `_insert_prompt_text` und Menü-Pfad ohne Crash. |
| Cross-Layer Chat | Prompt im API-Request | `test_prompt_apply_affects_real_request` | CL | System-Content enthält Prompt-String; zweiter Apply nicht stale. |
| Legacy DB-Shape | Sidebar/Explorer bei Dict-Rows | `test_main_window_signal_connections` | I | MainWindow baut ohne `list_projects`-Unpack-Fehler. |
| RAG VectorStore | CI ohne chromadb | `test_vector_store_*` in `test_rag.py` | U | Skip, wenn `chromadb` fehlt; keine falschen Grün-Tests. |
