# Entwickler

Handbuch für Arbeit am Repository: Architektur-Anker, Erweiterungspunkte und Debugging. Pfade beziehen sich auf `app/` wie in `docs_manual/modules/` und `docs/ARCHITECTURE.md`.

## Relevante Module (gesamter Stack)

- [GUI](../../modules/gui/README.md) · [Chat](../../modules/chat/README.md) · [Kontext](../../modules/context/README.md) · [Settings](../../modules/settings/README.md)  
- [Provider](../../modules/providers/README.md) · [RAG](../../modules/rag/README.md) · [Agenten](../../modules/agents/README.md) · [Prompts](../../modules/prompts/README.md) · [Chains](../../modules/chains/README.md)

**Dokumentation:** [ARCHITECTURE.md](../../../docs/ARCHITECTURE.md) · [DEVELOPER_GUIDE.md](../../../docs/DEVELOPER_GUIDE.md) · [FEATURES/](../../../docs/FEATURES/)

## Aufgaben

- **Architektur** verstehen: GUI (`app/gui/`) → Services (`app/services/`) → Kontext (`app/chat/`, `app/context/`) → Settings (`app/core/config/`) → Provider (`app/providers/`), LLM (`app/llm/`), Agenten (`app/agents/`), RAG (`app/rag/`).
- **Features erweitern:** neue Settings-Kategorien, Slash-Commands, Workspaces, Services anbinden.
- **Fehler finden:** Chat-Pfad, Provider, RAG, Async/Signals, Replay/Repro für Kontext.
- **Tests ausführen:** `tests/README.md` — pytest mit Markern `unit`, `integration`, `live`, `ui`.

## Typische Workflows

### Repository lokal starten

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m app
```

Alternativen: `python main.py`, `python run_gui_shell.py` (`app/__main__.py` delegiert).

### Neuen Screen oder Workspace anbinden

1. Screen: Factory in `app/gui/bootstrap.py` bei `get_screen_registry().register(NavArea.…, …)` eintragen (`NavArea` in `app/core/navigation/nav_areas.py`).
2. Workspace innerhalb eines bestehenden Screens: analog zu `operations_screen.py` — Tuple `(workspace_id, WorkspaceClass)` zum `QStackedWidget` hinzufügen; Navigation in `*Nav` erweitern.
3. Breadcrumbs: `get_breadcrumb_manager().set_workspace` wird in den Screens bereits bei Workspace-Wechsel aufgerufen — gleiches Muster übernehmen.

### Settings-Kategorie ergänzen

1. Widget-Klasse unter `app/gui/domains/settings/categories/`.
2. In `settings_workspace.py`: `_category_factories["settings_<id>"] = YourCategory`.
3. In `navigation.py`: `register_settings_category` oder `DEFAULT_CATEGORIES` um Eintrag erweitern.
4. Keys in `AppSettings.load` / `save` (`app/core/config/settings.py`), wenn neue Persistenz nötig.

### Slash-Command hinzufügen

1. `app/core/commands/chat_commands.py`: in `parse_slash_command` verzweigen; ggf. `ROLE_COMMANDS` oder neue Verbzweigung.
2. `SLASH_COMMANDS` Liste aktualisieren.
3. Tests für Parser und Chat-Integration ergänzen.

### Kontext-Debugging

1. In der App: **Settings → Advanced** — `context_debug_enabled` aktivieren.
2. Code: `ChatService._resolve_context_configuration` (`app/services/chat_service.py`), Traces/`ChatContextResolutionTrace` (`app/chat/context_profiles.py`).
3. Headless: `python -m app.cli.context_replay <json>`, `python -m app.cli.context_repro_run <json>` (Quelle `linux-desktop-chat-cli/src/app/cli/`).
4. Explainability: `app/context/explainability/`, `app/services/context_explain_service.py`, `policy_chain` in `context_explanation_serializer.py`.

### Provider-/Modellprobleme eingrenzen

1. `app/providers/ollama_client.py` und `local_ollama_provider.py` / `cloud_ollama_provider.py`.
2. `app/services/chat_service.py` Sendepfad und Fehlerbehandlung.
3. Integrationstests unter `tests/integration/`, Chaos unter `tests/chaos/`.

### GUI-Pfade nicht mit Alt-Repo verwechseln

GUI liegt unter **`app/gui/`**. Verzeichnis **`app/ui/`** existiert im aktuellen Stand nicht (`docs/DOC_GAP_ANALYSIS.md`).

## Genutzte Module

| Modul | Dev-Fokus |
|-------|-----------|
| [gui](../../modules/gui/README.md) | `bootstrap.py`, `workspace_host`, Screen- und Workspace-IDs. |
| [chat](../../modules/chat/README.md) | `ChatService`, Guard, Streaming-Flag. |
| [context](../../modules/context/README.md) | Auflösung, Limits, Replay, Serializer. |
| [settings](../../modules/settings/README.md) | `AppSettings`, Backend, Panel-Bindings. |
| [providers](../../modules/providers/README.md) | Ollama-Clients. |
| [agents](../../modules/agents/README.md) | Planner, Delegation, Execution. |
| [rag](../../modules/rag/README.md) | Retriever, vector_store, pipeline. |
| [prompts](../../modules/prompts/README.md) | Repository, StorageBackend. |
| [chains](../../modules/chains/README.md) | Prioritäten, Pipelines, Delegation. |

Zusätzlich: **`docs/DEVELOPER_GUIDE.md`**, **`docs/ARCHITECTURE.md`**, **`tools/generate_system_map.py`** für aktuelle `docs/SYSTEM_MAP.md`.

## Risiken

- **Async/Qt:** Blocking-Calls in UI-Threads vermeiden; Muster in bestehenden Workspaces übernehmen.
- **Kontext-Änderungen ohne Tests:** Regression in Golden/QA-Tests (`tests/`, `docs/qa/`).
- **Settings-Drift:** Neuer Key ohne `save()` → Wert geht bei Neustart verloren.
- **Inspector-Stale-Content:** `content_token` / `prepare_for_setup` bei Inspector-Updates beachten (`OperationsScreen`, `RuntimeDebugScreen`).

## Best Practices

- Vor größeren GUI-Änderungen `pytest tests/ui` und relevante `integration`-Tests laufen lassen.
- Kontextänderungen mit Replay-JSON und Repro-Fällen absichern (`app/context/replay/`).
- Öffentliche Erweiterungspunkte nutzen: `register_settings_category_widget`, `register_all_screens`-Muster, CLI-Module als Referenz für deterministische Ausgaben.
- Nach Strukturänderungen `python3 tools/generate_system_map.py` ausführen und Diff prüfen.
