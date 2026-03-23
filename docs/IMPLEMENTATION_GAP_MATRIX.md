# IMPLEMENTATION_GAP_MATRIX – Linux Desktop Chat

**Stand:** 2026-03-20  
**Legende Status:** `fertig` = produktiver Codepfad erkennbar · `teilweise` = UI oder Backend unvollständig · `fehlt` = nicht gefunden · `Platzhalter` = expliziter Stub/Dummy · `unklar` = weitere Verifikation nötig

| Modul/Bereich | Erwartete Funktion | Status | GUI-seitig vorhanden? | Backend-seitig vorhanden? | Testabdeckung | Risiko | Empfehlung |
|---------------|-------------------|--------|------------------------|----------------------------|---------------|--------|------------|
| Chat | Senden, Sessions, Streaming, Guard | fertig | Ja (`operations/chat/`) | Ja (`chat_service.py`) | Stark (`tests/chat/`, `tests/unit/test_chat_*`, `tests/ui/`) | Mittel (Provider extern) | Live-Ollama-E2E nur gezielt (siehe AUDIT_REPORT) |
| Kontext | Modi, Limits, Injection, Explainability | fertig | Teilweise (Inspector/Debug) | Ja | Stark (`tests/context/`, `tests/chat/`) | Niedrig | — |
| Control Center – Models | Modellliste, Auswahl | teilweise/fertig | Ja (`models_workspace.py`, Panels) | unklar (Anbindung Provider-Service) | Ja (`tests/ui/`, Verträge) | Mittel | End-to-End-Anbindung dokumentieren |
| Control Center – Providers | Provider-Status/Konfiguration | teilweise | Ja | Ja (`provider_service`, `providers/`) | Ja (mehrere `tests/`) | Mittel | — |
| Control Center – Agents | HR-CRUD, Profile | fertig | Ja (`AgentManagerPanel`) | Ja (`AgentService`) | Ja (`tests/test_agent_hr.py`, `golden_path/test_agent_in_chat_golden_path.py`) | Niedrig | Doku zu `app/ui` bereinigen |
| Control Center – Tools | Tool-Registry, Permissions | Platzhalter | Ja (Tabelle) | **Nein** (hardcoded `dummy_data`) | unklar | **Hoch** | Service anbinden oder als „Preview“ kennzeichnen |
| Control Center – Data Stores | Store-Übersicht, Health | Platzhalter | Ja | **Nein** (hardcoded) | unklar | **Hoch** | Echte Health aus DB/Chroma |
| Dashboard (Kommandozentrale Screen) | System/QA/Incidents-Überblick | Platzhalter | Ja | Nein (Docstrings) | unklar | Hoch | Adapter wie `CommandCenterView` oder deaktivieren |
| Command Center (`command_center_view`) | QA-Drilldowns, KPIs | fertig/teilweise | Ja | Ja (`QADashboardAdapter`) | Ja (`tests/ui/test_command_center_dashboard.py`) | Mittel | Subsystem-Detail prüfen (Kommentar „placeholder“) |
| Settings – Application/Appearance/Models/Data/Privacy/Advanced | Editierbare Werte | fertig (je Panel) | Ja | Ja (`AppSettings`) | Ja (`tests/unit/test_settings_*`, smoke) | Niedrig | — |
| Settings – Project/Workspace | Projekt-/Workspace-Keys | Platzhalter | Ja (Nav + Empty State) | **fehlt** (keine Felder) | unklar | Mittel | Roadmap oder Keys definieren |
| Knowledge / RAG | Quellen, Index, Abfrage | teilweise/fertig | Ja (`knowledge_workspace.py`) | Ja (`knowledge_service`, `rag/`) | Ja (`tests/unit/test_rag.py`, Integration) | Mittel | Platzhalter-Panels (Index/Retrieval-Status) ausstatten |
| Prompt Studio | Listen, Editor, Test Lab | teilweise | Ja | Ja (`prompt_service`, `prompt_repository`) | Ja (`tests/unit/test_prompt_system.py`) | Mittel | `preview_panel` implementieren |
| Agent Tasks | Tasks ausführen, Liste | teilweise | Ja | Ja (AgentService, Runner – siehe Workspace) | Ja (verschiedene Agent-Tests) | Mittel | Status/Queue-Panels dynamisch machen |
| Pipelines | Schritt-Ausführung | teilweise | unklar (primär backend) | Ja Engine; Comfy/Media **Platzhalter** | Ja (`tests/unit/test_pipelines_*`) | Mittel | Erwartung in Doku/UI steuern |
| Runtime Debug – Markdown Demo | Rendering-Prüfung | fertig (Dev) | Ja | N/A (Samples aus `resources/demo_markdown`) | Ja (`tests/unit/test_markdown_*`) | Niedrig | Als Dev-only kommunizieren |
| QA Governance Workspaces | Gaps, Coverage, … | fertig | Ja (`qa_governance/`) | Ja (`QAGovernanceService` o. Ä.) | Ja (`tests/qa/`) | Niedrig | — |
| CLI Context Replay / Repro Registry | Headless Tools | fertig (Code vorhanden) | N/A | Ja (`app/cli/`, `app/context/replay/`) | Teilweise (`tests/cli/`, helpers) | Mittel | Entwickler-Doku ergänzen |
| Critic / Qualitätsbewertung | Nachrichtenbewertung? | unklar | unklar | `app/critic.py` mit TODO | unklar | Unklar | Aufrufer suchen; Feature aktivieren oder entfernen |
| Legacy `agents_panels.py` | — | redundant | Nein (nicht von Workspace importiert) | Nein | Nein | Niedrig | Entfernen oder intern nur Demo |

---

*Ende IMPLEMENTATION_GAP_MATRIX*
