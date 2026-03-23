# Feature-Status-Matrix — Linux Desktop Chat

**Datum:** 2026-03-22  
**Legende Reifegrad:** R5 produktionsreif · R4 weitgehend · R3 brauchbar, Lücken · R2 teilweise · R1 fragmentarisch · R0 nicht vorhanden  
**Legende Handlungsbedarf:** MUSS / SOLLTE / KANN (siehe Hauptaudit)

| Bereich | Feature / Modul | Nachweis im Code | GUI-seitig erreichbar | Teststatus | Doku-Status | Reifegrad | Befund | Handlungsbedarf |
|---------|-----------------|------------------|------------------------|------------|-------------|-----------|--------|-----------------|
| Shell | Hauptfenster / Areas | `app/gui/shell/main_window.py`, `bootstrap.py` | Ja (Sidebar) | Smoke `tests/smoke/test_shell_gui.py` | `README.md`, `USER_GUIDE.md` | R4 | Standardpfad klar | KANN |
| Navigation | Registry / Sidebar | `app/core/navigation/navigation_registry.py`, `sidebar_config.py` | Ja | Architektur-Guards | `ARCHITECTURE.md`, Help-Index | R4 | Single source of truth | SOLLTE (i18n) |
| Operations | Projekte | `ProjectsWorkspace`, `operations_screen.py` | Ja | u. a. `tests/test_projects_phase_a.py` | `help/operations/projects_overview.md`, `FEATURES` (implizit) | R4 | Stabil | KANN |
| Operations | Chat (Workspace) | `app/gui/domains/operations/chat/chat_workspace.py` | Ja | Unit/Verhalten teils; Golden Path **nicht** hier | `USER_GUIDE.md`, `help/operations/chat_overview.md` | R3 | Haupt-UI; Testfokus teils Legacy | **MUSS** (Tests) |
| Operations | Knowledge / RAG | `KnowledgeWorkspace`, `app/rag/`, `knowledge_service` | Ja | Integration/Live laut `tests/README.md` | `FEATURES/rag.md`, Help | R4 | Stark backend-lastig | SOLLTE (UI-E2E) |
| Operations | Prompt Studio | `prompt_studio_workspace.py` | Ja | `tests/ui/test_prompt_manager_ui.py` testet `PromptManagerPanel` (Domain) | Help `prompt_studio_overview.md` | R4 | `TEST_AUDIT_REPORT.md` veraltet (behauptet fehlende UI-Tests) | KANN (Doku bereinigen) |
| Operations | Workflows (DAG, Runs) | `app/workflows/`, `WorkflowsWorkspace` | Ja | Viele `tests/unit/workflows/` | `FEATURES/workflows.md`, Help | R4 | Release R3 erwähnt | KANN |
| Operations | Deployment (R4) | `deployment_workspace.py`, `app/core/deployment/` | Ja | `tests/unit/gui/test_deployment_workspace.py`, Service-Tests | `help/operations/deployment_workspace.md` | R4 | „Light“ laut Architektur | KANN |
| Operations | Betrieb (Audit, Incidents, Health) | `AuditIncidentsWorkspace`, `app/core/audit/` | Ja | u. a. `test_platform_health`, Release-Gate | `help/operations/operations_betrieb.md` | R4 | Mit Qt-Lifetime-Fixes dokumentiert | KANN |
| Operations | Agent Tasks | `AgentTasksWorkspace`, `app/agents/` | Ja | Agent-Tests, Golden Path Agent | `FEATURES/agents.md`, Help | R3–R4 | Komplexität hoch | SOLLTE |
| Control Center | Models / Providers / Agents | `control_center_screen.py` | Ja | diverse Unit/UI | Help `control_center/*` | R4 | Tools/Data Stores = lokale Snapshots (README) | KANN |
| QA & Governance | Inventar, Coverage, Gaps, Incidents, Replay | `qa_governance_screen.py`, `app/services` (QA) | Ja | Projekt-Tests + QA-Generatoren | `help/qa_governance/qa_overview.md` | R3–R4 | Datenabhängig von Testartefakten | SOLLTE (Erwartung klären) |
| Runtime / Debug | EventBus, Logs, LLM Calls, Metrics, … | `runtime_debug_screen.py` | Ja | `tests/ui/test_debug_panel_ui.py` u. a. | `help/runtime_debug/runtime_overview.md` | R3–R4 | Teilweise Inspektions-Charakter | KANN |
| Settings | 8 Kategorien | `settings_workspace.py`, `AppSettings` | Ja | Theme/Settings-Tests | `FEATURES/settings.md`, Help | R4 | README: Project/Workspace Lesemodus | KANN |
| CLI | Replay / Repro / Registry | `app/cli/` | **Nein** (ohne Terminal) | Tests für CLI (siehe `DEVELOPER_GUIDE.md`) | Dokumentiert als CLI | R4 | „Ohne Kommandozeile“ nur teilweise | SOLLTE (GUI-Brücke optional) |
| Context | Mode, Profile, Limits, Explain | `app/chat/`, `chat_service.py` | Teilweise über Settings + Chat | Viele Unit-Tests | `FEATURES/context.md` | R4 | Fachlich tief | KANN |
| Workbench | MainWorkbench, Explorer, Canvas | `app/gui/workbench/`, `run_workbench_demo.py` | **Nur separater Start** | Layout/Inspector Unit-Tests | **Nicht** gleichwertig in README wie Shell | R2 | Inspector-Stubs (`inspector_router.py`) | **SOLLTE** (Klärung) |
| Workbench | Command Palette (Workbench-Dialog) | `command_palette_dialog.py` | In Shell anderes Palette (`CommandPalette` aus `navigation/command_palette.py`) — **zwei Konzepte** | Nicht belastbar ohne alle Aufrufer | Englische UI-Strings | R3 | Begriff „Command Palette“ doppelt | SOLLTE |
| Legacy GUI | ChatWidget / archive | `app/gui/legacy/`, `archive/run_legacy_gui.py` | Nur Wartungspfad | Golden Path nutzt `ChatWidget` | README: Legacy unter `archive/` | R3 | Test↔Produkt-Verzug | **MUSS** (Alignment) |
| Designer Dummy | `gui_designer_dummy/` | Nur Struktur/Resourcen | **Nicht** klar als produktiver Pfad | Keine explizite Suite gefunden | Undokumentiert im README-Kern | R1–R2 | Potenziell verwirrend | KANN (Doku) |
| Packaging | Installer / Store | — | — | Nicht verifiziert | `RELEASE_ACCEPTANCE_REPORT.md` nennt Lücke | R1–R2 | Bewusst offen | SOLLTE (wenn 1.0) |

---

## Kurz-Zuordnung zu Feature-Reife (1–5 aus Auftrag)

1. **Vollständig:** Shell-Routing, Navigation Registry, Settings-Grundriss, Workflow-Engine-Kern (mit Testlast), Deployment/Betrieb-Kern (R4).  
2. **Weitgehend vollständig:** RAG-Pipeline, Agent-System, QA-Governance-Workspaces.  
3. **Teilweise:** Workbench-Produktreife (Stubs), Prompt-UI vs. alte Audit-Aussagen.  
4. **Vorbereitet / angedeutet:** Workbench-Inspector-Fähigkeiten als Text/Stubs.  
5. **Dokumentiert, nicht oder nicht vollständig:** „Command Palette“-Einheitlichkeit; konsistente „nur GUI“-Abdeckung für Replay; Packaging.

---

*Matrix basiert auf statischer Code- und Doku-Sicht; keine vollständige manuelle Click-Through-Abnahme.*
