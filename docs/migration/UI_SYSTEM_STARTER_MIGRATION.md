# UI-System — Migrationsnotiz (Starter + Chat-Schnitt 1–5)

Technische Notiz zu `app/ui_contracts`, `app/ui_application`, `app/ui_runtime`, `app/ui_themes` und den vertikalen Chat-Schnitten.

## Erledigt: Chat vertikal (Schnitt 1)

- `**app/ui_application/ports/chat_operations_port.py**` — Qt-freier Port (Liste, Nachrichten, Stream-Iterator, Modellkatalog, Kontext/Projekt-Helfer, Contract-State-Mutatoren, Navigation/Menü-Helfer für das linke Panel).
- `**app/ui_application/adapters/service_chat_port_adapter.py**` — ein Adapter: delegiert an bestehende Services/Helper (keine neue Fachlogik). `cancel_generation` ist bewusst leer (kein Stream-Abort in `ChatService`).
- `**app/ui_application/presenters/chat_presenter.py**` — `run_send_async` für Send+Stream+Persistenz; Commands für Contract-State; `SendMessageCommand` über `attach_send_pipeline` → geplante Coroutine.
- `**app/ui_application/presenters/chat_stream_assembler.py**` — `append_stream_piece`, `extract_stream_display`.
- `**app/ui_application/presenters/chat_send_callbacks.py**` — UI-Hooks; optional `notify_send_session_completed` (Workspace synchronisiert `_current_chat_id` nach Send, z. B. nach Neuanlage).
- `**app/gui/domains/operations/chat/chat_workspace.py**` — `ChatWorkspaceChatSink` spiegelt Contract-State/Patches auf Widgets; Standard-Sendeinstieg über ChatPresenter (`attach_send_pipeline`), nicht die deprecated Env-Alternative unten.

### Legacy / Fallback Send

- Standard: **Presenter-Sendeinstieg** (`use_presenter_send_pipeline()`).
- **Deprecated:** `**LINUX_DESKTOP_CHAT_LEGACY_CHAT_SEND=1`** → `_run_send_legacy`: dieselbe `ChatOperationsPort`-Instanz und `consume_chat_model_stream` wie der Presenter, aber **ohne** Project Butler und **ohne** Contract-Streaming-Patches. Einmaliges `DeprecationWarning` beim ersten Check. Referenz: `**docs/04_architecture/CHAT_SEGMENT_CLOSEOUT.md**`.

### Legacy / Fallback Kontextmenüs, Topic-UI, Inspector

- Menüs / `**topic_actions`** / `**ChatContextInspector**`: optional `**chat_ops**` (`ChatOperationsPort`). **Ohne** Port: Legacy-Service-Zweige (Tests, externe Aufrufer).
- `**ChatWorkspace`** injiziert `**self._chat_port**` in Inspector, Navigation, Kontextleisten-Menü, Details.

## Erledigt: Chat Schnitt 2

- **Sink:** `ChatWorkspaceChatSink` — Fehlerzeile, Load/Streaming-Flags, Auswahl/Explorer, Konversation, Kontextleiste.
- **Send:** regulärer Pfad UI → `SendMessageCommand` → Presenter → `run_send_async` → Patches + Konversations-Callbacks.
- **Navigation:** `chat_navigation_panel.py` mit `nav_data` ohne `get_chat_service()` für Listen-Refresh.
- **Stop/Cancel:** `cancel_generation` ohne Backend-Hook; Docstring auf Port/Adapter.

## Erledigt: Chat Schnitt 3 (Details + Workspace)

- **Contract:** `ChatDetailsPanelState`, `ChatTopicOptionEntry`, Details in `ChatWorkspaceState` / `ChatStatePatch`.
- **Mapper** `chat_details_mapper.py` — u. a. `format_chat_details_timestamp` (wird auch im Workspace für Inspector-Zeitstempel genutzt).
- `**chat_details_panel.py`** — `details_ops`; `**apply_details_state**`.

## Erledigt: Chat Schnitt 4 (Kontextmenü + Topic-Aktionen)

- **Contract:** `ProjectListRow`.
- **Port:** u. a. `duplicate_chat`, `delete_chat`, `list_projects_for_chat_move`, `move_chat_to_project`, `set_active_project_id`, Topic-CRUD.
- `**chat_item_context_menu.py`**, `**topic_actions.py**`, Navigation mit `**chat_ops` / `chat_actions**`.

## Erledigt: Chat Schnitt 5 (Inspector + Projekt-Kontext im Workspace)

### Port

- `**set_active_project_selection(project_id: object | None)**` — durchgängige UI-Delegation zu `project_context_manager.set_active_project` (Switcher, `None` = leeren). `**set_active_project_id(int)**` ruft intern dieselbe Methode auf.

### ChatContextInspector

- Parameter `**chat_ops**`: Topic-Dropdown via `**list_topic_rows_for_project**`; Zuordnung via `**move_chat_to_topic**`. Ohne `**chat_ops**`: Legacy `get_topic_service` / `get_chat_service`.

### ChatWorkspace (kein `get_project_context_manager` mehr)

- Projekt-Switcher: `**self._chat_port.set_active_project_selection(project_id)**`.
- Letzte Session pro Projekt: `**self._chat_port.get_active_project_id()**`.
- Kontextleiste ohne Chat: aktiver Projektname über `**get_active_project_record()**` (Adapter liest weiter den Context-Manager — **eine** zentrale Stelle).
- Inspector-Aufbau: `**ChatContextInspector(..., chat_ops=self._chat_port)`**; letzte Aktivität mit `**format_chat_details_timestamp**` (kein Import von `_format_datetime` aus dem Inspector-Modul).

### Unverändert bewusst

- `**ContextInspectionPanel**` (Debug-Kontext) im Inspector-Container: weiter eigener Pfad; nicht Teil dieses Schnitts.
- `**subscribe_project_events**` / globale Projekt-Events: bleiben im Workspace (App-Integration).
- `**project_context_manager**`: weiter die **Implementierung** hinter `get_active_project_id` / `get_active_project_record` / `set_active_project_selection` im Adapter — nicht dupliziert im Workspace.

## Chat-Bereich: Migrationsreife

- **Operativer Chat-Stack** (Workspace, Navigation, Details, Menüs, Topic-Aktionen, Inspector-Hauptpfad, Send: Presenter-Einstieg vs. optional deprecated Workspace-Einstieg — **eine** Port-Instanz) ist **weitgehend** über `**ChatOperationsPort`** konsolidiert.
- **Legacy-Sende-Flag** ist deprecated (Diagnostik); Menü/Inspector ohne Port (`**chat_ops=None**`) bleibt separat für ältere Widget-Pfade relevant.
- **Rest außerhalb „rein Chat“:** globale DI, Themes, andere Workspaces, Debug-Panels.

## Noch offen (optional, nicht Chat-kern)

- `**cancel_generation`** — ehrlicher No-Op.
- Globale Port-DI (`run_gui_shell.py`), Theme-Cutover, `ContextInspectionPanel` auf Port.

## RuntimeWarning „coroutine was never awaited“ (Einordnung)

- Test-Fix: `scheduled[0].close()` im Presenter-Test.

## Tests

- `tests/unit/ui_application/test_chat_stream_assembler.py`
- `tests/unit/ui_application/test_chat_presenter_run_send.py`
- `tests/unit/ui_application/test_chat_details_mapper.py`
- `tests/unit/ui_application/test_chat_port_menu_actions.py` — Menü/Topic + `**set_active_project_selection**`
- `tests/unit/gui/test_chat_workspace_chat_sink.py`
- `tests/unit/gui/test_chat_navigation_panel_nav_data.py`
- `tests/unit/gui/test_chat_details_panel_contract.py`
- `tests/unit/gui/test_topic_actions_port_path.py`
- `tests/unit/gui/test_chat_item_context_menu_port.py`
- `tests/unit/gui/test_chat_context_inspector_port.py`
- `tests/contracts/test_chat_ui_contracts.py`
- `tests/smoke/test_chat_workspace_import.py`

## Erledigt: Settings Slice 1 (Appearance / Theme)

### Zielbild

- **UI** (`ThemeSelectionPanel`) → **Presenter** (`SettingsAppearancePresenter`) → **Port** (`SettingsOperationsPort`) → **Adapter** (`ServiceSettingsAdapter`) → Infrastructure / Theme-Metadaten.
- **State / Patch** (`AppearanceSettingsState`, `AppearanceStatePatch`) → **Sink** (`SettingsAppearanceSink`) → Liste + Fehlerzeile; **ThemeManager.set_theme** nur im Sink (GUI-Effekt).
- **Persistenz** (`settings.theme_id`, `settings.theme`, `save()`) nur im Adapter, nicht im Panel.

### Neue / geänderte Dateien


| Bereich        | Datei                                                                                                  |
| -------------- | ------------------------------------------------------------------------------------------------------ |
| Contract       | `app/ui_contracts/workspaces/settings_appearance.py`                                                   |
| Port           | `app/ui_application/ports/settings_operations_port.py`                                                 |
| Adapter        | `app/ui_application/adapters/service_settings_adapter.py`                                              |
| Presenter      | `app/ui_application/presenters/settings_appearance_presenter.py`                                       |
| Sink           | `app/gui/domains/settings/settings_appearance_sink.py`                                                 |
| Panel          | `app/gui/domains/settings/panels/theme_selection_panel.py` — `appearance_port=`; Legacy ohne Port      |
| Injektion      | `categories/appearance_category.py`, `workspaces/appearance_workspace.py` → `ServiceSettingsAdapter()` |
| Sink-Protokoll | `app/ui_application/view_models/protocols.py` — `SettingsAppearanceUiSink`                             |


### Bewusst Legacy (Slice 1)

- `**settings_dialog.py`** — **Modal:** Provider/Katalog + **`save_and_close`** über `SettingsOperationsPort.persist_legacy_modal_settings` (Abschnitt **„Settings — Modal-Dialog“**); Orchestrator-Cloud-Key weiter im Widget.
- `**ThemeSelectionPanel**` ohne `appearance_port` — ThemeManager für Liste/Wechsel; **`_persist_theme_legacy`** ruft nur noch **`ServiceSettingsAdapter().persist_theme_choice`** (kein `get_infrastructure` im Widget).
- Panels mit direktem `get_infrastructure().settings` (**AI Models**, **Data**, **Advanced**, …) — eigene Settings-Slices (2–4), nicht Slice 1.

### Status (Nachzieher Slice 1 — Guardrails)

- **Erledigt:** `theme_selection_panel.py` frei von `get_infrastructure(` / `get_*_service(`; Architekturtests `tests/architecture/test_theme_selection_panel_guardrails.py`; Sink-Tests `tests/unit/gui/test_settings_appearance_sink.py`.

### Technische Schuld

- **ThemeRegistry** wird im Adapter aus `app.gui.themes.registry` bezogen — Metadatenliste ist weiter an `gui` gebunden; mittelfristig Qt-freie oder `ui_contracts`-nahe Theme-Metadaten erwägen.

### Tests (Slice 1)

- `tests/contracts/test_settings_appearance_contracts.py`
- `tests/unit/ui_application/test_settings_appearance_presenter.py`
- `tests/unit/ui_application/test_service_settings_adapter.py` (inkl. Theme-Teil)
- `tests/unit/gui/test_theme_selection_panel_port_path.py`
- `tests/unit/gui/test_settings_appearance_sink.py`
- `tests/architecture/test_theme_selection_panel_guardrails.py`
- `tests/smoke/test_settings_slice1_import.py`

## Erledigt: Settings Slice 2 (Advanced / Debug)

### A. Bestandsanalyse der Kandidaten (kurz, codebasiert)


| Kandidat                          | Imports / Kopplung                                                                                                                                               | Async / Catalog / Cloud           | Eignung jetzt                                                           |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- | ----------------------------------------------------------------------- |
| `**ai_models_settings_panel.py`** | `get_infrastructure().settings`; `get_unified_model_catalog_service().build_catalog_for_chat` (async); `apply_catalog_to_combo`; `sqlalchemy` `OperationalError` | **Ja** (async Katalog, DB-Schema) | **Nein** — höchstes Risiko, schwer testbar ohne Event-Loop/DB           |
| `**data_settings_panel.py`**      | nur `get_infrastructure().settings`; viele Felder (RAG, Prompt-Pfad); `QFileDialog`                                                                              | Nein                              | **Möglich** — synchron, aber mehr Widgets/Zustände als Advanced         |
| `**advanced_settings_panel.py`**  | nur `get_infrastructure().settings`; 3 Felder (`debug_panel_enabled`, `context_debug_enabled`, `chat_context_mode`)                                              | **Nein**                          | **Ja (gewählt)** — kleinster vertikaler Schnitt, klarer State           |
| `**model_settings_panel.py`**     | injiziertes `settings`-Objekt + Orchestrator; `get_model_usage_gui_service`; viele Rollen-Combos / Cloud-Flags                                                   | Implizit cloud-lastig             | **Nein** — großes Panel, Studio-Pfad, nicht der nächste sichere Schritt |


**Entscheidung:** Slice 2 = **Advanced**, weil maximaler Architekturgewinn pro Zeile bei minimalem Risiko (kein Async, kein Unified Catalog, kein Provider).

### Zielbild

- **UI** (`AdvancedSettingsPanel`) → **Presenter** (`SettingsAdvancedPresenter`) → **Port** (Erweiterung `SettingsOperationsPort`) → **Adapter** (`ServiceSettingsAdapter`) → `AppSettings` + `save()`.
- **State / Patch** (`AdvancedSettingsState`, `AdvancedSettingsPatch`) → **Sink** (`SettingsAdvancedSink`).
- `**SettingsErrorInfo`** weiter aus `settings_appearance` (gemeinsame Fehler-DTO), domain-spezifisch `SettingsAdvancedPortError` in `settings_advanced`.

### Neue / geänderte Dateien


| Bereich   | Datei                                                                                                                |
| --------- | -------------------------------------------------------------------------------------------------------------------- |
| Contract  | `app/ui_contracts/workspaces/settings_advanced.py`                                                                   |
| Port      | `app/ui_application/ports/settings_operations_port.py` — `load_advanced_settings_state`, `persist_advanced_settings` |
| Adapter   | `app/ui_application/adapters/service_settings_adapter.py` — Advanced-Lese-/Schreibpfad                               |
| Presenter | `app/ui_application/presenters/settings_advanced_presenter.py`                                                       |
| Sink      | `app/gui/domains/settings/settings_advanced_sink.py`                                                                 |
| Panel     | `app/gui/domains/settings/panels/advanced_settings_panel.py` — `settings_port=`; Legacy ohne Port                    |
| Injektion | `categories/advanced_category.py` → `ServiceSettingsAdapter()`                                                       |
| Protokoll | `app/ui_application/view_models/protocols.py` — `SettingsAdvancedUiSink`                                             |


### Bewusst Legacy (Slice 2)

- `**settings_dialog.py`** — siehe Slice-1-Hinweis (Modal-Ports inkl. Persistenz).
- `**AdvancedSettingsPanel**` ohne `settings_port` — Lade-/Schreibpfad über **`ServiceSettingsAdapter`** (kein `get_infrastructure` im Widget).
- **AI Models** (vor Slice 4), `**model_settings_panel` (Studio)**, **Project** — weiter ohne neuen Port-Pfad (Data siehe Slice 3).

### Status (Nachzieher Guardrails Slice 2)

- `tests/architecture/test_settings_data_advanced_panel_guardrails.py` — `advanced_settings_panel.py` ohne `get_infrastructure` / `get_*_service`.

### Restschulden Settings (nach Slice 2)

- **AI Models:** async Katalog + Combo-Füllung — nach Slice 4 (skalar) verbleibender Brocken; siehe Slice 4b in der Slice-4-Sektion.
- `**SettingsOperationsPort`** wächst pro Slice — Einschätzung siehe Slice 3.

### Tests (Slice 2)

- `tests/contracts/test_settings_advanced_contracts.py`
- `tests/unit/ui_application/test_settings_advanced_presenter.py`
- `tests/unit/ui_application/test_service_settings_adapter.py` (Advanced-Teil)
- `tests/unit/gui/test_advanced_settings_panel_port_path.py`
- `tests/architecture/test_settings_data_advanced_panel_guardrails.py` (Advanced + Data)
- `tests/smoke/test_settings_slice2_import.py`

## Erledigt: Settings Slice 3 (Data / RAG / Prompt-Speicher)

### A. Bestandsanalyse (`data_settings_panel.py`)

- **Felder / Aktionen:** `rag_enabled`, `rag_space` (feste Einträge), `rag_top_k` (1–20), `self_improving_enabled`, `prompt_storage_type` (DB vs. Verzeichnis), `prompt_directory` (Text + Ordnerwahl), `prompt_confirm_delete`.
- **Legacy-Zugriffe (Stand Migration):** ohne Port nur noch **`ServiceSettingsAdapter`** (`load_data_settings_state` / `persist_data_settings`); kein `get_infrastructure` im Panel.
- **GUI-Effekt:** `QFileDialog.getExistingDirectory` — bleibt im **Panel**; nach OK im Hauptpfad nur noch `SetPromptDirectoryCommand(path)` (kein Dialog in Port/Adapter).
- **Schichten:** DTOs/Commands/Patches → **Presenter**; Lesen/Schreiben Settings → **Port/Adapter**; Widgets + Fehlerzeile + `blockSignals` → **Sink**; Dialog → **Panel**.

### Zielschnitt

- **Ein** vertikaler Schnitt für das komplette Panel (keine Teilung): synchron, ohne neue Fachlogik, gleiches Nutzerverhalten wie zuvor.

### Neue / geänderte Dateien


| Bereich   | Datei                                                                                                                        |
| --------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Contract  | `app/ui_contracts/workspaces/settings_data.py`                                                                               |
| Port      | `app/ui_application/ports/settings_operations_port.py` — `load_data_settings_state`, `persist_data_settings`                 |
| Adapter   | `app/ui_application/adapters/service_settings_adapter.py` — inkl. Coerce für unbekannte `rag_space` / `rag_top_k` beim Lesen |
| Presenter | `app/ui_application/presenters/settings_data_presenter.py`                                                                   |
| Sink      | `app/gui/domains/settings/settings_data_sink.py`                                                                             |
| Panel     | `app/gui/domains/settings/panels/data_settings_panel.py` — `settings_port=`; Legacy ohne Port                                |
| Injektion | `categories/data_category.py` → `ServiceSettingsAdapter()`                                                                   |
| Protokoll | `app/ui_application/view_models/protocols.py` — `SettingsDataUiSink`                                                         |


### Bewusst Legacy (Slice 3)

- `**DataSettingsPanel()`** ohne `settings_port` — `QFileDialog` im Panel; Persistenz über **Adapter** (wie Advanced Slice 2).
- `**settings_dialog.py`** — siehe Slice-1-Hinweis (Modal-Ports inkl. Persistenz).

### Status (Nachzieher Guardrails Slice 3)

- `data_settings_panel.py` in `test_settings_data_advanced_panel_guardrails.py` (gemeinsam mit Advanced).

### `SettingsOperationsPort` — bleibt er tragfähig?

- **Ja, derzeit:** eine Adapter-Klasse implementiert alle Methoden; für das Team noch überschaubar.
- **Wachstum:** ab mehreren unabhängigen Settings-Blöcken (z. B. 5+) kann eine **Aufteilung in kleinere Protocols** (oder ein klar benannter „Composer“) sinnvoll werden — bewusst **nicht** in diesem Slice umgesetzt, um keinen Big-Bang zu erzeugen.

### Tests (Slice 3)

- `tests/contracts/test_settings_data_contracts.py`
- `tests/unit/ui_application/test_settings_data_presenter.py`
- `tests/unit/ui_application/test_service_settings_adapter.py` (Data-Teil ergänzt)
- `tests/unit/gui/test_data_settings_panel_port_path.py`
- `tests/architecture/test_settings_data_advanced_panel_guardrails.py`
- `tests/smoke/test_settings_slice3_import.py`

## Erledigt: Settings Slice 4 (AI Models — skalarer Teilschnitt)

### A. Harte Bestandsanalyse (`ai_models_settings_panel.py`, Stand vor Teilschnitt)


| Aspekt                     | Konkret im Code                                                                                                                                                                                                                          |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Direkte Infrastructure** | `_get_settings()` → `get_infrastructure().settings` in `_load_from_settings`, allen `_on_*`-Persistenzpfaden, `_load_models`, `_sync_model_from_settings`, `_on_model_changed`.                                                          |
| **Async / Event-Loop**     | `_defer_load_models`: `asyncio.get_running_loop()`; bei fehlendem Loop `QTimer.singleShot(100, …)` Retry; `asyncio.create_task(self._load_models())`.                                                                                    |
| **Unified Model Catalog**  | `_load_models` importiert `get_unified_model_catalog_service().build_catalog_for_chat(s)` (async); Filter `chat_selectable`; `apply_catalog_to_combo` aus `app.gui.common.model_catalog_combo`.                                          |
| **DB / SQLAlchemy**        | `from sqlalchemy.exc import OperationalError` — eigener Zweig mit Platzhalter-Combo-Eintrag („Schema fehlt …“).                                                                                                                          |
| **Weitere Fehler**         | Generisches `except Exception` mit Logging; Heuristik `"no such table"` im Fehlertext.                                                                                                                                                   |
| **Zustands-/UI-Bereiche**  | (1) **Modell-Combo** — async gefüllt, UserRole-Daten, Persistenz `settings.model`. (2) **Skalare Widgets** — `temperature`, `max_tokens`, `think_mode`, `chat_streaming_enabled` — synchron aus Settings, sofortige Persistenz in Slots. |


**Unabhängigkeit:** Bereich (2) ist von (1) entkoppelt (kein gemeinsamer State außer dass der Katalog `settings` für `build_catalog_for_chat` liest). Bereich (1) ist der riskante Block (Async, DB, leerer Katalog, GUI-Helper `apply_catalog_to_combo`).

### B. Teilschnitt-Entscheidung

- **Gewählt:** Slice 4 = **nur skalare Parameter** (Temperatur, Max-Tokens, Thinking-Modus, Streaming) über **Presenter → `SettingsOperationsPort` → `ServiceSettingsAdapter` → AppSettings**.
- **Warum zuerst:** Gleiches Muster wie Data/Advanced: synchron, gut testbar, keine Event-Loop-/Fixture-Abhängigkeit für den Hauptpfad; Validierung und `save()`-Fehler werden sichtbar (Fehlerzeile), statt stillschweigendem `except` im Legacy-Widget-Pfad.
- **Warum nicht das ganze Panel:** `build_catalog_for_chat` + Combo-Befüllung + `OperationalError` erfordern entweder schwere Async-Test-Setups oder einen **eigenen Katalog-Port** mit Coroutine/Scheduling — das wäre ein zweiter vertikaler Schnitt (Slice 4b), nicht „noch eine Methode“ am gleichen Tag.
- **Bewusst Legacy:** **Standardmodell-Combo** komplett — `_defer_load_models`, `_load_models`, `_sync_model_from_settings`, `_on_model_changed` mit `get_unified_model_catalog_service`, `apply_catalog_to_combo`, direkter `settings.model` + `save()`.

### C. Contracts

- `**app/ui_contracts/workspaces/settings_ai_models.py`** — `AiModelsScalarSettingsState`, `AiModelsScalarSettingsPatch`, `AiModelsScalarWritePatch`, Commands (`LoadAiModelsScalarSettingsCommand`, `SetAiModelsTemperatureCommand`, …), `SettingsAiModelsPortError`, `merge_ai_models_scalar_state`, Konstanten `THINK_MODES`, Temperatur-/Token-Grenzen.

### D. Port

- `**SettingsOperationsPort**` erweitert um `load_ai_models_scalar_state` und `persist_ai_models_scalar` — **kein** zweites Protocol nötig: die Async-Katalog-API hat einen anderen Charakter; für Slice 4b ist eine **eigene** Port-Schnittstelle (z. B. `AiModelsCatalogPort` / coroutine-basiert) oder ein klar dokumentierter Adapter-Entry mit GUI-seitigem Scheduling wahrscheinlicher als „alles in `SettingsOperationsPort`“.

### E. Adapter

- `**ServiceSettingsAdapter`:** Lesen/Schreiben nur delegieren; **Coerce** für Temperatur/Max-Tokens (Clamp wie Spinbox-Ranges), unbekannter `think_mode` beim Lesen → `"auto"`; ungültiger `think_mode` beim Schreiben → `SettingsAiModelsPortError`.

### F. Presenter

- `**SettingsAiModelsPresenter`** — Commands, Client-Validierung (Range/Think-Mode), Port-Fehler → Patch mit `SettingsErrorInfo`, sonst Reload über Port.

### G. Sink / Panel

- `**SettingsAiModelsSink**` — `QDoubleSpinBox`, `QSpinBox`, Think-`QComboBox`, Streaming-`QCheckBox`, Fehler-`QLabel`.
- `**AIModelsSettingsPanel**` — `settings_port=` optional; mit Port: Initial `LoadAiModelsScalarSettingsCommand`; Slots für Skalare → Presenter; Modell-Combo: **Slice 4b** mit `catalog_port=` (siehe unten), sonst Legacy.
- `**categories/ai_models_category.py`** — `ServiceSettingsAdapter()` + `ServiceAiModelCatalogAdapter()` (Slice 4b).

### H. Tests

- `tests/contracts/test_settings_ai_models_contracts.py`
- `tests/unit/ui_application/test_settings_ai_models_presenter.py`
- `tests/unit/ui_application/test_service_settings_adapter.py` (AI-Models-skalar-Teil)
- `tests/unit/gui/test_ai_models_settings_panel_port_path.py`
- `tests/smoke/test_settings_slice4_import.py`

### I. Guardrails

- Wie zuvor: `ui_contracts` Qt-frei via `test_ui_layer_guardrails.py`.
- **Nachzieher:** Legacy-Skalare im Panel nur noch über **`ServiceSettingsAdapter`** — kein `get_infrastructure` im Widget (`tests/architecture/test_settings_ai_models_catalog_guardrails.py`).

### J. `SettingsOperationsPort` nach Slice 4

- **Weiter tragfähig** für synchron Settings-IO; bei Einführung eines **async Katalog-Ports** sollte dieser **nicht** als bloße `async def`-Methode am selben Protocol landen (Presenter/Widget-Scheduling), sondern als **getrennte** Schnittstelle oder dokumentierter „Catalog read model“-Port.

## Erledigt: Settings Slice 4b (AI Models — Unified Model Catalog / async)

### A. Harte Bestandsanalyse (Legacy-Pfad, vor Slice 4b)


| Baustein                                             | Rolle                                                                                                                                                                                    |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `**_defer_load_models`**                             | `asyncio.get_running_loop()` → `create_task(_load_models)`; ohne Loop `QTimer.singleShot(100, …)` (Retry).                                                                               |
| `**_load_models_legacy**` (Stand Nachzieher) | `ServiceAiModelCatalogAdapter.load_chat_selectable_catalog_for_settings` → `SettingsAiModelCatalogPresenter._outcome_to_state` → `SettingsAiModelCatalogSink` (kein direkter Catalog-Service im Panel). |
| `**_sync_model_from_settings**`                      | Nur Legacy: Abgleich `settings.model` mit `UserRole` und sichtbarem Text.                                                                                                                |
| `**_on_model_changed**`                              | `combo_current_selection_id` / `UserRole` → `settings.model` + `save()` (still `except`).                                                                                                |
| **Service-Helfer**                                   | `app.services.unified_model_catalog_service`, `app.gui.common.model_catalog_combo`.                                                                                                      |
| **qasync/Loop**                                      | Kein explizites qasync im Panel — nur stdlib-`asyncio` + Qt-Timer als Fallback.                                                                                                          |
| **OperationalError / leer**                          | Eigener Combo-Platzhalter („Alembic-Migration …“); generisches `Exception` mit `"no such table"`-Heuristik.                                                                              |
| **Zusammengehörig**                                  | Async-Laden, Fehlerklassifikation, Combo-Befüllung, Auswahl-Sync aus einem Lesezugriff auf `AppSettings.model`.                                                                          |
| **Rein GUI**                                         | `QComboBox`, `apply_catalog_to_combo`, `QTimer`/`create_task` — bleiben in Sink bzw. Panel-Scheduler.                                                                                    |


### B. Port-Entscheidung

- **Gewählt:** eigenes Protocol `**AiModelCatalogPort`** (`app/ui_application/ports/ai_model_catalog_port.py`) + `**UiCoroutineScheduler**` für den Event-Loop-Rand.
- **Begründung:** Async-Katalog + DB-Anfälligkeit gehören **nicht** auf `SettingsOperationsPort` (synchron, skalare Settings). Trennung hält Presenter und Tests lesbar; kein „Schein-async“ am zentralen Settings-Protocol.

### C. Contracts

- `**app/ui_contracts/workspaces/settings_ai_model_catalog.py`** — `AiModelCatalogEntryDto`, `AiModelCatalogPortLoadOutcome`, `AiModelCatalogState`, `CatalogLoadStatus`, Platzhalter-Konstanten (Legacy-Texte 1:1), Commands `LoadAiModelCatalogCommand`, `RetryAiModelCatalogCommand`, `PersistAiModelSelectionCommand`.

### D. Adapter

- `**app/ui_application/adapters/service_ai_model_catalog_adapter.py**` — kapselt `get_unified_model_catalog_service().build_catalog_for_chat`, DTO-Mapping, `OperationalError` / generische Fehler / `"no such table"` wie zuvor im Panel; `persist_default_chat_model_id` delegiert an `AppSettings` (Fehler werden geloggt, nicht geworfen — dokumentierte Legacy-Schuld).

### E. Presenter

- `**app/ui_application/presenters/settings_ai_model_catalog_presenter.py**` — Commands; `run_catalog_load_once` (await-bar in Tests); Loading → Port → Sink; Retry = erneuter Schedule.

### F. Sink / Panel

- `**app/gui/domains/settings/settings_ai_model_catalog_sink.py**` — `apply_full_catalog_state`: Loading-Platzhalter, Fehler/Leer-Platzhalter, sonst `apply_catalog_to_combo` + `_sync_model_from_settings_id` (Legacy-Parität).
- `**ai_models_settings_panel.py**` — mit `settings_port` **und** `catalog_port`: Catalog-Presenter + Panel implementiert `UiCoroutineScheduler.schedule`. **Nur** `settings_port` ohne `catalog_port`: **Legacy-Katalog** (`_load_models_legacy`) über **Catalog-Adapter** + Sink (wie oben).
- `**categories/ai_models_category.py`** — injiziert `ServiceSettingsAdapter()` und `ServiceAiModelCatalogAdapter()`.

### G. Modellauswahl / Persistenz

- **Mitgezogen in Slice 4b:** `PersistAiModelSelectionCommand` → `AiModelCatalogPort.persist_default_chat_model_id` — gleiche Semantik wie zuvor im Slot, aber nicht mehr als „Fachlogik“ im Widget.
- **Legacy:** ohne Catalog-Port **`ServiceAiModelCatalogAdapter.persist_default_chat_model_id`** (wie zuvor im Adapter, kein `settings`-Zugriff im Widget).

### H. Tests


| Test                                                                       | Pfad                                                                    |
| -------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Contracts                                                                  | `tests/contracts/test_settings_ai_model_catalog_contracts.py`           |
| Presenter (async Load, Retry, Persist)                                     | `tests/unit/ui_application/test_settings_ai_model_catalog_presenter.py` |
| Adapter (Happy, leer, OperationalError, no-such-table, generisch, Persist) | `tests/unit/ui_application/test_service_ai_model_catalog_adapter.py`    |
| Sink                                                                       | `tests/unit/gui/test_settings_ai_model_catalog_sink.py`                 |
| Panel (ohne/mit Catalog, async Load, Persist)                              | `tests/unit/gui/test_ai_models_settings_panel_port_path.py`             |
| Smoke                                                                      | `tests/smoke/test_settings_slice4b_import.py`                           |


### I. Guardrails

- `**tests/architecture/test_settings_ai_models_catalog_guardrails.py`** — Panel ohne `get_unified_model_catalog_service`, ohne `get_infrastructure`, ohne `get_*_service`; Legacy nutzt `ServiceAiModelCatalogAdapter`.
- `**ui_contracts**` weiter Qt-frei (`test_ui_layer_guardrails.py`).

### J. `SettingsOperationsPort` nach Slice 4b

- **Weiterhin** sinnvoll für **synchrone** Settings-Blöcke; **Katalog bleibt separat** (`AiModelCatalogPort`). Bei weiterem Wachstum optional kleinere Protocols oder ein Composer — bewusst kein Big-Bang.

## Erledigt: Settings — Modal-Dialog (`SettingsDialog`, Provider + Katalog)

- **Ziel:** Kein `get_provider_service()` / `get_unified_model_catalog_service()` im Dialog-Modul.
- **Ports:** `OllamaProviderSettingsPort` (`.env`-Key, async `validate_cloud_api_key`) + bestehendes `AiModelCatalogPort` für `update_models`.
- **Adapter:** `ServiceOllamaProviderSettingsAdapter`, Standard `ServiceAiModelCatalogAdapter`.
- **Konstruktor:** optional `ollama_provider_port=`, `catalog_port=`, `settings_operations_port=`; Standard = Service-Adapter.
- **Presenter:** `SettingsLegacyModalPresenter` — baut `SettingsLegacyModalCommit`, ruft `persist_legacy_modal_settings`; `refresh_model_catalog` delegiert Katalog-Mapping intern an `SettingsAiModelCatalogPresenter._outcome_to_state` + `SettingsAiModelCatalogSink` (Widget ohne DTO-Commit und ohne statischen Presenter-Aufruf).
- **Contract (Marker):** `app/ui_contracts/workspaces/settings_modal_ollama.py`.
- **Event-Loop:** Katalog-Laden und API-Key-Prüfung schedulen wie `AIModelsSettingsPanel` per `QTimer` + `get_running_loop()` / `create_task`, damit `__init__` ohne laufende asyncio-Schleife (z. B. pytest) nicht mit `RuntimeError` abbricht.
- **Technische Schuld:** `ServiceAiModelCatalogAdapter` importiert `sqlalchemy.exc.OperationalError` nur optional — Modul bleibt ohne installiertes SQLAlchemy importierbar.
- **Persistenz:** `save_and_close` → `SettingsLegacyModalPresenter.persist_from_ui(...)` → Port/Adapter (`ServiceSettingsAdapter`: ein `save()`). Orchestrator `._cloud.set_api_key` bleibt im Dialog nach erfolgreichem Presenter-Aufruf.
- **Contract:** `app/ui_contracts/workspaces/settings_legacy_modal.py` (`SettingsLegacyModalCommit`, `SettingsLegacyModalPortError`).
- **Tests:** `tests/architecture/test_settings_dialog_guardrails.py` (u. a. kein `SettingsLegacyModalCommit` / kein `SettingsAiModelCatalogPresenter` im Dialog-Modul), `tests/contracts/test_settings_modal_ollama_contracts.py`, `tests/contracts/test_settings_legacy_modal_contracts.py`, `tests/unit/ui_application/test_settings_legacy_modal_presenter.py`, `tests/unit/ui_application/test_service_settings_adapter.py`, `tests/smoke/test_settings_dialog_slice_import.py`.

### Korrekturpass: Settings Legacy Modal (Presenter-Schicht)

- **Ziel:** Kanonische Kette Widget → Presenter → Port; Widget nur Signale/Scheduler + Primitive an Presenter.
- **Umsetzung:** `app/ui_application/presenters/settings_legacy_modal_presenter.py`; `SettingsAiModelCatalogSink.sync_to_stored_model` für Auswahl nach Katalog-Load.

## Erledigt: Settings — ModelSettingsPanel (Routing / Assistant / skalare LLM-Felder)

- **Contract:** `app/ui_contracts/workspaces/settings_model_routing.py` — `ModelRoutingStudioState`, `ModelRoutingStudioWritePatch`, `LoadModelRoutingStudioCommand`, `ApplyModelRoutingStudioPatchCommand`.
- **Port:** `SettingsOperationsPort.load_model_routing_studio_state` / `persist_model_routing_studio`.
- **Adapter:** `ServiceSettingsAdapter` — Validierung `default_role` (Enum-Werte), Coerce Temperatur/Max-Tokens.
- **Presenter:** `SettingsModelRoutingPresenter`; **Sink:** `settings_model_routing_sink.py`.
- **Panel:** optional `model_routing_port=`; **Legacy** ohne Port: `ServiceSettingsAdapter` pro Handler (kein `self.settings.save()` im Widget).
- **Injektion:** `ChatSidePanel` → `model_routing_port=ServiceSettingsAdapter()`.
- **Tests:** `tests/contracts/test_settings_model_routing_contracts.py`, `tests/unit/ui_application/test_settings_model_routing_presenter.py`, `tests/unit/gui/test_settings_model_routing_sink.py`, `tests/unit/ui_application/test_service_settings_adapter.py` (Load/Persist), `tests/architecture/test_model_settings_panel_guardrails.py` (kein `self.settings.save()`).

## Erledigt: Settings — ProjectCategory (aktives Projekt, read-only)

- **Ziel:** `ProjectCategory` ohne `get_project_service()` / Kontext-Manager-Logik im Widget.
- **Pfad:** `ProjectCategory` → `SettingsProjectOverviewPresenter` → `SettingsProjectOverviewPort` → `ServiceSettingsProjectOverviewAdapter` → Context-Manager + `ProjectService`.
- **Contract:** `app/ui_contracts/workspaces/settings_project_overview.py` (`SettingsActiveProjectViewState`, `ActiveProjectSummaryDto`, `RefreshSettingsActiveProjectCommand`, `SettingsProjectCategoryBodyState`).
- **Sink:** `app/gui/domains/settings/settings_project_overview_sink.py`.
- **Optional:** `project_overview_port=` für Tests/Doppel-Injektion; Standard: `ServiceSettingsProjectOverviewAdapter()`.
- **Tests:** `tests/contracts/test_settings_project_overview_contracts.py`, `tests/unit/ui_application/test_settings_project_overview_presenter.py`, `tests/architecture/test_project_category_guardrails.py`, `tests/smoke/test_settings_project_overview_slice_import.py`.

## Erledigt: Chat Studio — ModelUsageSidebarHint (ModelSettingsPanel)

- **Ziel:** Hinweistext unter „Provider & Status“ ohne `get_model_usage_gui_service()` im Widget.
- **Pfad:** `ModelSettingsPanel` → `ModelUsageSidebarHintPresenter` → `ModelUsageGuiReadPort` → `ServiceModelUsageGuiAdapter` → `model_usage_gui_service`.
- **Contract:** `app/ui_contracts/workspaces/model_usage_sidebar.py` (`ModelUsageSidebarHintState`, `RefreshModelUsageSidebarHintCommand`).
- **Sink:** `app/gui/domains/settings/model_usage_sidebar_sink.py` — spiegelt auf `QLabel`.
- **Injektion:** `ChatSidePanel` setzt `usage_hint_port=ServiceModelUsageGuiAdapter()` auf `ModelSettingsPanel`.
- **Legacy:** `usage_hint_port=None` → `ServiceModelUsageGuiAdapter().quick_sidebar_hint()` direkt (kein Service-Getter im Panel).
- **Tests:** `tests/contracts/test_model_usage_sidebar_contracts.py`, `tests/unit/ui_application/test_model_usage_sidebar_presenter.py`, `tests/architecture/test_model_settings_panel_guardrails.py`, `tests/smoke/test_model_usage_sidebar_slice_import.py`.
- **Routing/Streaming/Assistant:** siehe Abschnitt **„Settings — ModelSettingsPanel (Routing …)“** (Presenter/Port; kein direktes `save()` im Panel).

### Settings-Bereich: Migrationsreife nach 4b

- **Appearance, Advanced, Data, AI Models (skalar + Katalog-Hauptpfad), ProjectCategory, SettingsDialog (Presenter + Ports), ModelSettingsPanel (Routing-Slice), ChatSidePanel-Injektion** sind über Ports/Adapter bzw. Standard-Injektion abgedeckt; verbleibendes **bewusstes Legacy**: weitere Kategorien (Privacy, Application, …).

### Prompt Studio — Guardrail-Erweiterung (ohne vollständige Portierung)

- **Ziel:** Weitere Panels behalten Legacy-Service-Zugriffe, aber **keine neuen** `get_*_service`-Aufrufe außerhalb der erlaubten Methoden (AST-Tests).
- **Tests:** `tests/architecture/test_prompt_studio_remaining_panels_guardrails.py` — u. a. `prompt_editor_panel`, `editor_panel`, `prompt_version_panel`, `library_panel`, `prompt_templates_panel`, `prompt_test_lab`, `prompt_studio_workspace`.

### Deployment — Dialog-Lesezugriff Projekte

- **Modul:** `deployment_project_combo_data.list_project_label_id_pairs()` — zentrale Projektliste für Combos.
- **Dialoge:** `TargetEditDialog` / `ReleaseEditDialog` mit `project_rows=` (UI-only auf Hauptpfad); Legacy `project_rows=None` → `_load_projects_legacy` mit `get_project_service`.
- **Panels:** `TargetsPanel` / `ReleasesPanel` laden Zeilen und übergeben sie an die Dialoge.
- **Tests:** `tests/unit/gui/test_deployment_project_combo_data.py`, `tests/architecture/test_deployment_edit_dialogs_project_service_guardrails.py`.
- **Einschätzung:** der **Kern** der häufig genutzten Settings-Workspaces ist **weitgehend migrationsreif**; Gesamt-„Settings fertig“ wäre übertrieben, solange weitere Kategorien auf Alt-Pfaden liegen.

## Geplante nächste Referenzdomäne: Deployment (Operations) — Domänenanalyse & Slice 1

**Hinweis:** Deployment Slice 1–4 sind **umgesetzt**. Die **aktuelle** Wahl der **nächsten** Referenzdomäne nach Deployment steht im Abschnitt **„Analyse und Wahl: Nächste Referenzdomäne nach Deployment“** (Ziel: **Agent Tasks**).

Domänenwahl und Vergleich unten (A–C) stammen aus der Vorbereitung. **Deployment Slice 1** (Targets read-only), **Slice 2** (Targets Neu/Bearbeiten), **Slice 3** (Releases read-only) und **Slice 4** (Rollouts read-only) sind **umgesetzt** — Details in den Abschnitten **„Erledigt: Deployment Slice 1–4“**. Chat und Settings bleiben das Muster (Contracts → Port → Adapter → Presenter → Sink, optional Legacy-Fallback).

### A. Kurzanalyse weiterer großer GUI-Domänen (harte Fakten aus dem Repo)


| Domäne                                         | Zentrale Einstiege                                                                                                              | Service-/Infra-Kopplung                                                                                                                                       | Async / besondere Risiken                                                                                                 | UI-Komplexität                                              | Erster vertikaler Slice (Eignung)                                                                                                                                          | Gewinn vs. Risiko                                                                         |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **Knowledge** (`operations_knowledge`)         | `knowledge_workspace.py` (~250 Zeilen), viele Panels unter `knowledge/panels/`                                                  | Überall `get_knowledge_service()`, Workspace importiert `app.rag.models.Chunk`                                                                                | `asyncio` + `create_task` im Workspace und z. B. `index_status_page`; RAG/Index/Chroma-Realität                           | Hoch (Explorer, Overview, Retrieval, Index, Collections, …) | Schwer klein zu schneiden ohne Projekt-/Space-Kontext; kleinster sinnvoller Schnitt wäre z. B. **nur Read-only-Liste** einer Teilfläche — trotzdem **DB/Vektor** im Rücken | Hoher fachlicher Nutzen, **hohes** technisches Risiko                                     |
| **Workflows** (`operations_workflows`)         | `workflow_workspace.py` (**~900+ Zeilen**), `panels/*`, `canvas/*` (Scene/View/Items)                                           | `get_workflow_service()` im Workspace-`__init__`, dazu `get_schedule_service()`, `project_service`; Domain-Modelle `WorkflowDefinition` / JSON-Serialisierung | `QThreadPool` + `QRunnable` für „Run now“; **QGraphicsView/Scene** — Zustand über Editor, Runs, Schedules **verschränkt** | Sehr hoch                                                   | Ein „dünner“ Slice ohne Canvas/Runs ist möglich (z. B. **nur Workflow-Liste**), führt aber schnell zu **Zweigleisigkeit** (Liste portgestützt, Rest direkt am Service)     | Großer langfristiger Gewinn, **höchstes** Risiko für Refactoring-Sumpf                    |
| **Deployment** (`operations_deployment`)       | `deployment_workspace.py` (**~35 Zeilen**), `panels/targets_panel.py`, `releases_panel.py`, `rollouts_panel.py`, wenige Dialoge | Ein dominanter Pfad: `deployment_operations_service.get_deployment_operations_service()`; Dialoge ziehen `get_project_service()` für Projektlisten            | **Synchrone** Service-API (`DeploymentOperationsService` → Repository + Audit); **kein** Pflicht-Async im Workspace       | Niedrig (Tab-Widget + Tabellen/Forms)                       | **Sehr gut:** z. B. **Targets: Liste laden + Anzeige** ohne sofort alle Mutationen/Dialoge zu portieren                                                                    | **Mittlerer** UX-Gewinn, **niedriges** technisches Risiko — beste **Schnitttauglichkeit** |
| **Prompt Studio** (`operations_prompt_studio`) | `prompt_studio_workspace.py`, viele Panels                                                                                      | `get_prompt_service()` überwiegend; **Test-Lab** zusätzlich `get_model_service`, `get_chat_service`                                                           | `asyncio` im **Prompt Test Lab**                                                                                          | Mittel–hoch (Editor, Versionen, Templates, Lab)             | Möglich, aber **Querschnitt** (Prompts + Modelle + Chat) im Lab                                                                                                            | Guter Produktnutzen, **mittleres** Risiko                                                 |
| **Agent Tasks** (`operations_agent_tasks`)     | `agent_tasks_workspace.py`, mehrere Task-Panels                                                                                 | Betrieb **Slice 1–2:** Lesepfade über Adapter/Port; `get_agent_operations_read_service` nur im Adapter bzw. Legacy-Detailfallback `_apply_ops_detail_legacy` | `asyncio.create_task` für laufende Agenten-Jobs (Tab **Aufgaben**, unverändert)                                         | Mittel (Tabs, Registry, Detail)                             | Betrieb-Tab **read-seitig** (Registry + Operations-Detail) migrationsreif; Laufzeitpfad bleibt heikel                                                                      | Mittleres Risiko durch **Live-Async** (nur Aufgaben-Tab)                                  |


### B. Vergleich (Kurz)


| Kriterium                                  | Knowledge | Workflows      | Deployment                               | Prompt Studio   | Agent Tasks      |
| ------------------------------------------ | --------- | -------------- | ---------------------------------------- | --------------- | ---------------- |
| Nutzen (Architektur-Klarheit)              | Hoch      | Sehr hoch      | Solide                                   | Mittel          | Mittel           |
| Migrations-/Technikrisiko                  | Hoch      | Sehr hoch      | **Niedrig**                              | Mittel          | Mittel–hoch      |
| Schnitttauglichkeit (kleiner erster Slice) | Schwach   | Schwach–mittel | **Stark**                                | Mittel          | Mittel           |
| Testbarkeit (ohne Canvas/Async-Dauerläufe) | Aufwendig | Aufwendig      | **Günstig**                              | Teilweise async | Async-Lauf nötig |
| Sumpf-Gefahr (halb portiert, halb Legacy)  | Hoch      | **Sehr hoch**  | **Gering** bei diszipliniertem Tab-Slice | Mittel          | Mittel           |


### C. Auswahl der nächsten Ziel-Domäne

**Gewählt: Deployment (`operations_deployment`).**

**Begründung:** Nicht die größte oder sichtbarste Domäne, sondern die **migrationssicherste**: kleiner Workspace, **eine** klare Service-Schicht, **synchrone** Aufrufe, keine Graphics-Scene, minimale Async-Abhängigkeit. Das erlaubt einen **ersten vertikalen Schnitt** im selben Stil wie Settings-Slices (lesen → Zustand → UI), ohne sofort Runtimes, Canvas und Mehr-Service-Orchestrierung mitzuziehen.

### D. Slice 1–4 — umgesetzt

Siehe **„Erledigt: Deployment Slice 1“** bis **„Slice 4“**.

### E. Guardrails (nach Slice 2)

- `**tests/architecture/test_deployment_targets_panel_guardrails.py`:** AST — `refresh`, `_on_new`, `_on_edit` ohne direkte Aufrufe von `get_deployment_operations_service`, `get_project_service`, `get_infrastructure` (nur Delegation zu Presenter bzw. `_on_*_legacy` / `_refresh_legacy`).
- **Direkter Service** nur noch: `**_refresh_legacy`**, `**_on_new_legacy**`, `**_on_edit_legacy**`, **Adapter**; **TargetEditDialog** lädt Projektliste weiter über `**get_project_service()`** (GUI, nicht Teil dieses Slices).
- **Releases** siehe **Deployment Slice 3**; **Rollouts** siehe **Deployment Slice 4**.
- **Fallback:** `TargetsPanel(..., deployment_targets_port=None)` → vollständiger Legacy-Pfad.

### F. Einordnung

- **Knowledge** und **Workflows** bleiben **wichtige Folgekandidaten** nach weiteren Deployment-Slices — oder mit **eigenem** Risiko-Review, wenn Produkt-Priorität sie vorgeht.
- **Prompt Studio** und **Agent Tasks** sind **nicht vergessen**, aber **Querschnitt** bzw. **Live-Async** erschweren den ersten sicheren Schnitt gegenüber Deployment.

## Erledigt: Deployment Slice 1 (Targets-Tab, read-only)

### A. Bestandsanalyse des Targets-Pfads (vor Migration)


| Aspekt                                    | Code                                                                                                                                                                                                                                                   |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `**deployment_workspace.py`**             | Erzeugt `TargetsPanel`, `ReleasesPanel`, `RolloutsPanel`; beim Start und bei Tab-Wechsel auf Index 0: `self._targets.refresh()`.                                                                                                                       |
| `**targets_panel.py` (Legacy `refresh`)** | `get_deployment_operations_service()` → `get_last_rollout_per_target()` **und** `list_targets()`; fünf Spalten: Name, Art, Projekt-ID, Letzter Rollout (`recorded_at` oder „—“), Ergebnis (`outcome` oder „—“); `UserRole` auf Spalte 0 = `target_id`. |
| **Leerer Zustand**                        | `setRowCount(0)` — keine explizite Meldung (Tabelle leer).                                                                                                                                                                                             |
| **Fehlerzustand**                         | Kein `try/except` um `refresh()` — Exceptions propagierten nach oben.                                                                                                                                                                                  |
| **Mutationen**                            | `Neu…` / `Bearbeiten…` → `TargetEditDialog` + `create_target` / `update_target` + erneutes `refresh()`.                                                                                                                                                |
| **Minimale Injektion**                    | Optionaler Parameter `deployment_targets_port=`; Workspace setzt `ServiceDeploymentTargetsAdapter()`.                                                                                                                                                  |


**Wichtig:** Der Lesepfad war **nicht** nur `list_targets`, sondern immer **+ `get_last_rollout_per_target`** — der Adapter spiegelt das 1:1.

### B.–F. Implementierung (Schichten)


| Bereich   | Datei                                                                                                                                                                                                                                 |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Contract  | `app/ui_contracts/workspaces/deployment_targets.py` — Slice 1: Tabellen-DTO, View-State, `LoadDeploymentTargetsCommand`; Slice 2: Write-DTOs, Editor-Snapshot, Create/Update-Commands, `DeploymentTargetsPortError`, `banner_message` |
| Port      | `app/ui_application/ports/deployment_targets_port.py` — `load_targets_view`, `get_target_editor_snapshot`, `create_target`, `update_target`                                                                                           |
| Adapter   | `app/ui_application/adapters/service_deployment_targets_adapter.py`                                                                                                                                                                   |
| Presenter | `app/ui_application/presenters/deployment_targets_presenter.py`                                                                                                                                                                       |
| Sink      | `app/gui/domains/operations/deployment/deployment_targets_sink.py`                                                                                                                                                                    |
| Panel     | `app/gui/domains/operations/deployment/panels/targets_panel.py` — Hauptpfad vs. `_refresh_legacy()`                                                                                                                                   |
| Workspace | `app/gui/domains/operations/deployment/deployment_workspace.py` — Injektion `ServiceDeploymentTargetsAdapter()`                                                                                                                       |
| Protokoll | `app/ui_application/view_models/protocols.py` — `DeploymentTargetsUiSink`                                                                                                                                                             |


### Bewusst Legacy (nach Slice 2 im Targets-Tab)

- `**_refresh_legacy**`, `**_on_new_legacy**`, `**_on_edit_legacy**` bei `deployment_targets_port=None`.
- `**releases_panel.py**` — Lesepfad **Deployment Slice 3**; Mutationen **Batch 4** über Port/Presenter (Legacy `_*_legacy` ohne Port).
- `**rollouts_panel.py**` — read-only-Hauptpfad siehe **Deployment Slice 4**; „Rollout protokollieren“ weiter direkt am Service.
- `**TargetEditDialog`:** Projekt-Dropdown weiter `**get_project_service()`** (bewusst nicht in den Port gezogen).

### Nächste sinnvolle Deployment-Slices

1. ~~**Slice 3:** **Releases**-Tab read-only~~ — **erledigt**.
2. ~~**Slice 4:** **Rollouts**-Tab read-only~~ — **erledigt** (siehe unten).
3. **Batch 4:** **Releases-Mutationen** über Port erledigt; **Rollouts-Mutationen** (z. B. protokollieren) weiterhin separat scoped.

### Tests (Deployment Targets, Slice 1–2)


| Test      | Pfad                                                                                           |
| --------- | ---------------------------------------------------------------------------------------------- |
| Contracts | `tests/contracts/test_deployment_targets_contracts.py`                                         |
| Presenter | `tests/unit/ui_application/test_deployment_targets_presenter.py`                               |
| Adapter   | `tests/unit/ui_application/test_service_deployment_targets_adapter.py`                         |
| Sink      | `tests/unit/gui/test_deployment_targets_sink.py`                                               |
| Panel     | `tests/unit/gui/test_targets_panel_port_path.py`, `tests/unit/gui/test_targets_panel_port_mutations.py` |
| Guardrail | `tests/architecture/test_deployment_targets_panel_guardrails.py`                               |
| Smoke     | `tests/smoke/test_deployment_slice1_import.py`, `tests/smoke/test_deployment_slice2_import.py` |


## Erledigt: Deployment Slice 2 (Targets Neu / Bearbeiten)

### A. Bestandsanalyse Mutationspfad (vor Slice 2)


| Aspekt                    | Code                                                                                                                                                          |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `**_on_new`**             | `TargetEditDialog` → `values()` → `get_deployment_operations_service().create_target(...)`; bei Exception `QMessageBox.warning`; bei Erfolg `self.refresh()`. |
| `**_on_edit**`            | `_selected_id()` → `QMessageBox` wenn leer → `svc.get_target(tid)` → Dialog mit `initial=t` (Record) → `update_target` + ggf. MessageBox + `refresh()`.       |
| **Dialog**                | `target_edit_dialog.py` — Felder Name/Art/Notizen/Projekt; `**_load_projects`** via `**get_project_service().list_projects()**` (bleibt im Dialog).           |
| **Refresh nach Mutation** | Immer `**self.refresh()`** (Legacy) bzw. nach Slice 1 im Hauptpfad **Presenter `LoadDeploymentTargetsCommand`** über Erfolgszweig in Presenter nach Mutation. |


### B.–F. Umsetzung

- **Contracts:** `DeploymentTargetCreateWrite`, `DeploymentTargetUpdateWrite`, `DeploymentTargetEditorSnapshotDto`, `CreateDeploymentTargetCommand`, `UpdateDeploymentTargetCommand`, `DeploymentTargetsPortError`, `DeploymentTargetsViewState.banner_message` (Mutation-Fehler ohne Tabelle zu leeren).
- **Port:** `get_target_editor_snapshot`, `create_target`, `update_target` (werfen `DeploymentTargetsPortError` bei Fehlern).
- **Adapter:** 1:1 Delegation an `DeploymentOperationsService`; `ValueError` → `DeploymentTargetsPortError("validation", …)`.
- **Presenter:** nach erfolgreicher Mutation `**_load_clearing_banner()`**; bei Fehler Reload + `**banner_message**`.
- **Sink:** bei `phase=ready` und gesetztem `**banner_message`** Feedback-Zeile sichtbar, Zeilen bleiben.
- **Panel:** Hauptpfad ohne direkten Deployment-Service; Legacy in `**_on_new_legacy`** / `**_on_edit_legacy**` ausgelagert (Guardrail-tauglich).

## Erledigt: Deployment Slice 3 (Releases-Tab, read-only)

### A. Bestandsanalyse des Releases-Pfads (vor Migration)

| Aspekt | Code |
|--------|------|
| **`releases_panel.py` — `refresh`** | `get_deployment_operations_service()` → `list_releases()`; fünf Spalten: Name, Version, Lifecycle, Artefakt, Projekt-ID; `UserRole` Spalte 0 = `release_id`; danach `_on_sel()`. |
| **`releases_panel.py` — `_on_sel`** | `get_release(rid)`; bei Treffer: Rich-Text-Detail (`display_name`, `version_label`, `lifecycle_status`, `artifact_ref`/`artifact_kind`); `list_rollouts(RolloutListFilter(release_id=rid, limit=200))` + `list_targets()` für Zielnamen in der Historientabelle; `UserRole` auf Run-ID-Spalte wenn gesetzt. |
| **Leer (Liste)** | Tabelle ohne Zeilen; ohne explizite Meldung (wie Targets Slice 1). |
| **Leer (Auswahl)** | Kein `release_id` oder Release nicht gefunden → Detail leer, Historie `setRowCount(0)`. |
| **Fehler** | Kein `try/except` um `refresh`/`_on_sel` — Exceptions propagierten. |
| **Mutationen** | `Neu…` / `Bearbeiten…` / `Archivieren` → Dialog bzw. Confirm + `create_release` / `update_release` / `archive_release` + `refresh()`. |
| **`deployment_workspace.py`** | Tab Index 1 → `self._releases.refresh()` (unverändert); keine Auto-Load beim Start für Releases. |
| **Minimale Injektion** | Optional `deployment_releases_port=`; Workspace setzt `ServiceDeploymentReleasesAdapter()`. |

### B.–G. Implementierung (Schichten)

| Bereich | Datei |
|---------|--------|
| Contract | `app/ui_contracts/workspaces/deployment_releases.py` — Tabellen-DTO, Detail-/Historien-DTOs, `DeploymentReleasesViewState`, `DeploymentReleaseSelectionState`, `LoadDeploymentReleasesCommand`, `LoadDeploymentReleaseSelectionCommand`, `deployment_releases_loading_state` |
| Port | `app/ui_application/ports/deployment_releases_port.py` — `load_releases_list_view`, `load_release_selection_state` |
| Adapter | `app/ui_application/adapters/service_deployment_releases_adapter.py` |
| Presenter | `app/ui_application/presenters/deployment_releases_presenter.py` — Liste cached für Auswahl-Merge |
| Sink | `app/gui/domains/operations/deployment/deployment_releases_sink.py` — Liste, Feedbackzeile, Detail, Historie |
| Panel | `app/gui/domains/operations/deployment/panels/releases_panel.py` — Hauptpfad vs. `_refresh_legacy` / `_on_sel_legacy` |
| Workspace | `deployment_workspace.py` — Injektion `ServiceDeploymentReleasesAdapter()` |
| Protokoll | `app/ui_application/view_models/protocols.py` — `DeploymentReleasesUiSink` |

### Bewusst Legacy (Slice 3)

- **`_refresh_legacy`**, **`_on_sel_legacy`** bei `deployment_releases_port=None`.
- **`_on_new`**, **`_on_edit`**, **`_on_archive`** — weiterhin direkt `get_deployment_operations_service()` (kein Write-Port in diesem Slice).
- **`ReleaseEditDialog`** — unverändert (GUI-only).
- **`rollouts_panel.py`** — read-only siehe **Deployment Slice 4**.

### Technische Schuld / Restpunkte

- **Auswahl lädt** jedes Mal `list_targets()` für Namensmapping — identisch zum früheren `_on_sel`, aber weiterhin O(n) pro Klick.
- **Fehler in `load_release_selection_state`:** Adapter fängt Exceptions ab und liefert leere Auswahl (mit Log) statt sie durchzureichen — weicht vom strikten Legacy-Verhalten ab, verhindert aber harte Abstürze bei Teilfehlern.
- **Nächster sinnvoller Slice:** **Rollouts read-only** ist in **Slice 4** umgesetzt; als Nächstes z. B. **Mutationen** (Releases / Rollouts) über Ports oder **Deployment-DI** zentralisieren.

### Tests (Deployment Releases, Slice 3)

| Test | Pfad |
|------|------|
| Contracts | `tests/contracts/test_deployment_releases_contracts.py` |
| Presenter | `tests/unit/ui_application/test_deployment_releases_presenter.py` |
| Adapter | `tests/unit/ui_application/test_service_deployment_releases_adapter.py` |
| Sink | `tests/unit/gui/test_deployment_releases_sink.py` |
| Panel | `tests/unit/gui/test_releases_panel_port_path.py` |
| Guardrail | `tests/architecture/test_deployment_releases_panel_guardrails.py` |
| Smoke | `tests/smoke/test_deployment_slice3_import.py` |

## Erledigt: Deployment Slice 4 (Rollouts-Tab, read-only)

### A. Bestandsanalyse des Rollouts-Pfads (vor Migration)

| Aspekt | Code |
|--------|------|
| **`rollouts_panel.py` — `_reload_filter_combos`** | `get_deployment_operations_service()` → `list_targets()` / `list_releases()`; Ziel-Combo „(alle Ziele)“ + Namen; Release-Combo „(alle Releases)“ + `f"{display_name} ({version_label})"`; Auswahl wird per `itemData`-Vergleich wiederhergestellt. |
| **`rollouts_panel.py` — `refresh`** | Ruft zuerst `_reload_filter_combos`, baut aus Combos + Zeitraum-Combo `since_iso`/`until_iso` (UTC, `timedelta` 7/30 Tage) oder beides `None`; `RolloutListFilter` mit `limit=800`; `list_rollouts(flt)`; erneut `list_targets()` / `list_releases()` für Anzeige-Namen; 7 Spalten; Spalte 5 `UserRole` = `workflow_run_id or ""`. |
| **Auswahl / Detail** | Keine separate Detailfläche; Auswahl nur für **`_goto_run`** (liest Run-ID aus Spalte-5-**Text**). |
| **Leer** | Keine explizite Empty-Message; leere Tabelle möglich. |
| **Fehler** | Kein `try/except` um `refresh` — Exceptions propagierten. |
| **Mutation** | **`_on_record`** → `RolloutRecordDialog` + `record_rollout` + `refresh()`. |
| **`deployment_workspace.py`** | Tab Index 2 → `self._rollouts.refresh()`. |
| **Minimale Injektion** | Optional `deployment_rollouts_port=`; Workspace setzt `ServiceDeploymentRolloutsAdapter()`. |

### B.–F. Implementierung (Schichten)

| Bereich | Datei |
|---------|--------|
| Contract | `app/ui_contracts/workspaces/deployment_rollouts.py` — `DeploymentRolloutsFilterSnapshot`, Option-/Tabellen-DTOs, `DeploymentRolloutsViewState`, `LoadDeploymentRolloutsCommand`, `deployment_rollouts_loading_state` |
| Port | `app/ui_application/ports/deployment_rollouts_port.py` — `load_rollouts_view(filter_snapshot)` |
| Adapter | `app/ui_application/adapters/service_deployment_rollouts_adapter.py` |
| Presenter | `app/ui_application/presenters/deployment_rollouts_presenter.py` |
| Sink | `app/gui/domains/operations/deployment/deployment_rollouts_sink.py` — Combos + Tabelle + Feedback |
| Panel | `app/gui/domains/operations/deployment/panels/rollouts_panel.py` — Hauptpfad vs. `_refresh_legacy` / `_reload_filter_combos_legacy` |
| Workspace | `deployment_workspace.py` — Injektion `ServiceDeploymentRolloutsAdapter()` |
| Protokoll | `app/ui_application/view_models/protocols.py` — `DeploymentRolloutsUiSink` |

### Bewusst Legacy (Slice 4)

- **`_refresh_legacy`**, **`_reload_filter_combos_legacy`** bei `deployment_rollouts_port=None`.
- **`_on_record`** — weiterhin direkt `get_deployment_operations_service()` für **`record_rollout`** nach dem Dialog; **Dialog-Combos** auf Hauptpfad mit Port: `Presenter.load_rollout_record_combo_options()` → injiziertes `RolloutRecordComboSnapshot`.
- **`RolloutRecordDialog`** — **Legacy:** Combos via `_reload_combos_legacy()` + Service; **Hauptpfad:** `combo_snapshot=` (UI-only). **`_goto_run`** / Navigation — unverändert im Panel.

### Technische Schuld / Restpunkte

- **Mehrfach-Lesungen** pro Refresh (Ziele/Releases für Combos + dieselben Daten implizit für Tabellen-Zuordnung) entspricht dem früheren Ablauf; kein neues Batching in der Service-API.
- **Fehler:** Adapter liefert `phase=error` mit leerer Tabelle statt Exception — Combos werden im Fehlerpfad vom Sink **nicht** neu gesetzt (kann veraltete Einträge zeigen bis zum nächsten erfolgreichen Load).
- **Zeitraum-Filter:** Berechnung von `since_iso`/`until_iso` bleibt im **Panel** (`_build_filter_snapshot`), identisch zur Legacy-Logik im Contract-Snapshot.

### Deployment: read-seitig migrationsreif?

- **Ja, eingeschränkt:** Alle drei Tabs (**Targets**, **Releases**, **Rollouts**) haben einen **read-only-Hauptpfad** über Contracts/Port/Adapter/Presenter/Sink mit Legacy-Fallback.
- **Nicht „fertig“:** Mutationspfade (Targets teilweise über Port, Releases/Rollouts größtenteils Legacy), globale DI, Dialoge mit eigenen Service-Zugriffen.

### Tests (Deployment Rollouts, Slice 4)

| Test | Pfad |
|------|------|
| Contracts | `tests/contracts/test_deployment_rollouts_contracts.py` |
| Presenter | `tests/unit/ui_application/test_deployment_rollouts_presenter.py` |
| Adapter | `tests/unit/ui_application/test_service_deployment_rollouts_adapter.py` |
| Sink | `tests/unit/gui/test_deployment_rollouts_sink.py` |
| Panel | `tests/unit/gui/test_rollouts_panel_port_path.py` |
| Guardrail | `tests/architecture/test_deployment_rollouts_panel_guardrails.py` |
| Smoke | `tests/smoke/test_deployment_slice4_import.py` |

## POST-CORRECTION — Batch 1 (erledigt)

### Slice 1 — Deployment: Rollout-Record-Dialog Combo-Injektion

| Status | **Erledigt** |
|--------|----------------|
| **Kurz** | Hauptpfad: Panel holt `RolloutRecordComboSnapshot` über `DeploymentRolloutsPresenter` → `DeploymentRolloutsPort.load_rollout_record_combo_options()` → Adapter (Ziele + nur `ready`-Releases). Dialog ohne Service, wenn `combo_snapshot` gesetzt. Legacy: `RolloutRecordDialog(parent)` lädt weiter über `_reload_combos_legacy()`. `record_rollout` bleibt im Panel auf Legacy-Service. |

**Geänderte / neue Dateien**

| Bereich | Datei |
|---------|--------|
| Contract | `app/ui_contracts/workspaces/deployment_rollouts.py` — `RolloutRecordComboRowDto`, `RolloutRecordComboSnapshot` |
| Port | `app/ui_application/ports/deployment_rollouts_port.py` — `load_rollout_record_combo_options` |
| Adapter | `app/ui_application/adapters/service_deployment_rollouts_adapter.py` — `rollout_record_combo_snapshot_from_records`, `load_rollout_record_combo_options` |
| Presenter | `app/ui_application/presenters/deployment_rollouts_presenter.py` — `load_rollout_record_combo_options` |
| Dialog | `app/gui/domains/operations/deployment/dialogs/rollout_record_dialog.py` |
| Panel | `app/gui/domains/operations/deployment/panels/rollouts_panel.py` — `_on_record` injiziert Snapshot bei Port-Pfad |

**Tests:** `tests/contracts/test_deployment_rollouts_contracts.py`, `tests/unit/ui_application/test_deployment_rollouts_presenter.py`, `tests/unit/ui_application/test_service_deployment_rollouts_adapter.py`, `tests/unit/gui/test_rollouts_panel_port_path.py`, `tests/unit/gui/test_rollout_record_dialog_combo_injection.py`, `tests/architecture/test_rollout_record_dialog_guardrails.py`

**Restschuld:** `record_rollout` und Legacy-Dialog-Öffnung ohne Port weiterhin direkt am Service; kein eigener Sink für den Dialog (Einmal-Lesepfad).

---

### Slice 2 — Settings: Modal Ollama Key-Validate über Presenter

| Status | **Erledigt** |
|--------|----------------|
| **Kurz** | `SettingsLegacyModalPresenter.validate_ollama_cloud_api_key` ruft `OllamaProviderSettingsPort.validate_cloud_api_key` auf und liefert `OllamaCloudApiKeyValidationResult` an `OllamaCloudApiKeyValidationSink`. `SettingsDialog._on_check_api_key_status` nur Scheduler + „Prüfe…“; `_OllamaApiKeyValidationSink` spiegelt Text/Stylesheet/Button. `.env`-Key-Lesen bleibt `get_ollama_api_key_from_env` am Port im Widget (nicht Teil dieses Slices). |

**Geänderte / neue Dateien**

| Bereich | Datei |
|---------|--------|
| Contract | `app/ui_contracts/workspaces/settings_modal_ollama.py` — `OllamaCloudApiKeyValidationResult`, `OllamaCloudApiKeyValidationKind` |
| Presenter | `app/ui_application/presenters/settings_legacy_modal_presenter.py` — `OllamaCloudApiKeyValidationSink`, `validate_ollama_cloud_api_key`, ctor `ollama_provider_port` |
| Sink (Widget-Helfer) | `app/gui/domains/settings/settings_dialog.py` — `_OllamaApiKeyValidationSink` |
| Dialog | `app/gui/domains/settings/settings_dialog.py` — `_on_check_api_key_status` |

**Tests:** `tests/contracts/test_settings_modal_ollama_contracts.py`, `tests/unit/ui_application/test_settings_legacy_modal_presenter.py`, `tests/unit/gui/test_settings_dialog_ollama_key_sink.py`, `tests/architecture/test_settings_dialog_guardrails.py` (`_on_check_api_key_status` ohne direkten `validate_cloud_api_key`-Aufruf)

**Restschuld:** Keine; optional später `.env`-Zeile ebenfalls über Presenter, falls gewünscht.

---

### Batch 1 — Zusammenfassung

| Kriterium | Stand |
|-----------|--------|
| Slices | 1–2 abgeschlossen |
| Tests | siehe Slice-Abschnitte |
| Guardrails | `test_rollout_record_dialog_guardrails.py`, erweitert `test_settings_dialog_guardrails.py` |
| Doku | dieser Abschnitt |

**Roadmap verbleibend (nicht Batch 1):** siehe **POST-CORRECTION — Batch 2** unten; danach Batch 3+.

---

## POST-CORRECTION — Batch 2 (erledigt): Prompt Studio — drei Lesepfade

### Slice A — Prompt Studio: Library panel read list

| Status | **Erledigt** |
|--------|----------------|
| **Kurz** | `PromptLibraryPanel` optional `prompt_studio_port`: **derselbe** `load_prompt_list` / `PromptStudioListPresenter` / `ServicePromptStudioAdapter` wie Slice 1; Sink `PromptStudioLibrarySink` → `apply_prompt_library_state`. Legacy: `_load_prompts_legacy`. Mutation `_on_delete_prompt` bleibt Service. |

| Bereich | Datei |
|---------|--------|
| Contract | `app/ui_contracts/workspaces/prompt_studio_library.py` — Aliasse zu `prompt_studio_list` (`LoadPromptLibraryCommand`, `PromptLibraryState`, …) |
| Port | kein neues Protokoll — `PromptStudioPort.load_prompt_list` (wiederverwendet) |
| Adapter | `service_prompt_studio_adapter.py` — unverändert für Library (nutzt bestehendes `load_prompt_list`) |
| Presenter | `prompt_studio_list_presenter.py` — wiederverwendet |
| Sink | `app/gui/domains/operations/prompt_studio/prompt_studio_library_sink.py` |
| Panel | `panels/library_panel.py` |

**Tests:** `tests/contracts/test_prompt_studio_library_contracts.py`, `tests/unit/gui/test_prompt_studio_library_sink.py`, `tests/unit/gui/test_library_panel_port_path.py`, `tests/architecture/test_prompt_library_panel_guardrails.py`, `test_prompt_studio_remaining_panels_guardrails.py` (Legacy-Name `_load_prompts_legacy`)

**Guardrails:** `refresh` / `apply_prompt_library_state` ohne `get_prompt_service`; erlaubt `_load_prompts_legacy`, `_on_delete_prompt`, `_add_prompt_item` (Legacy `count_versions`).

**Restschuld:** `PromptLibraryPanel` im Haupt-Workspace weiterhin nicht eingebunden (Export/Explorer); bei späterer Nutzung `prompt_studio_port=` setzen wie bei `PromptListPanel`.

---

### Slice B — Prompt Studio: Version panel read

| Status | **Erledigt** |
|--------|----------------|
| **Kurz** | `PromptStudioPort.load_prompt_versions` → Adapter mappt `list_versions` → `PromptVersionRowDto`; `PromptStudioVersionsPresenter` → `PromptStudioVersionsSink` → `apply_prompt_version_panel_state`. `set_prompt(..., versions=[...])` bleibt reines Dict-Rendering ohne Port. Workspace: `PromptInspectorPanel` / `PromptStudioInspector` reichen `prompt_studio_port` an `PromptVersionPanel` durch. |

| Bereich | Datei |
|---------|--------|
| Contract | `app/ui_contracts/workspaces/prompt_studio_versions.py` |
| Port | `prompt_studio_port.py` — `load_prompt_versions` |
| Adapter | `service_prompt_studio_adapter.py` — `load_prompt_versions` |
| Presenter | `prompt_studio_versions_presenter.py` |
| Sink | `prompt_studio_versions_sink.py` |
| Panel | `panels/prompt_version_panel.py` |
| Wiring | `prompt_inspector_panel.py`, `gui/inspector/prompt_studio_inspector.py`, `prompt_studio_workspace.py` |

**Tests:** `tests/contracts/test_prompt_studio_versions_contracts.py`, `tests/unit/ui_application/test_prompt_studio_versions_presenter.py`, `tests/unit/gui/test_prompt_version_panel_port_path.py`, `tests/architecture/test_prompt_version_panel_guardrails.py`, erweitert `test_service_prompt_studio_adapter.py`

**Guardrails:** `set_prompt` / `refresh` / `apply_prompt_version_panel_state` ohne direkten Service; Legacy nur `_load_versions_from_service`.

**Restschuld:** Keine für diesen Lesepfad; Inspector optional später rein presenter-getrieben (Slice 15 Roadmap).

---

### Slice C — Prompt Studio: Templates panel read

| Status | **Erledigt** |
|--------|----------------|
| **Kurz** | `load_prompt_templates` + `last_prompt_template_models`; `PromptStudioTemplatesPresenter` / `PromptStudioTemplatesSink`; `PromptTemplatesPanel` mit `prompt_studio_port=` (Workspace setzt Adapter). Create/Edit/Copy/Delete bleiben Legacy-Service. |

| Bereich | Datei |
|---------|--------|
| Contract | `app/ui_contracts/workspaces/prompt_studio_templates.py` |
| Port | `prompt_studio_port.py` — `load_prompt_templates` |
| Adapter | `service_prompt_studio_adapter.py` — `load_prompt_templates`, `last_prompt_template_models` |
| Presenter | `prompt_studio_templates_presenter.py` |
| Sink | `prompt_studio_templates_sink.py` |
| Panel | `panels/prompt_templates_panel.py` |
| Workspace | `prompt_studio_workspace.py` — Injektion `PromptTemplatesPanel(..., prompt_studio_port=...)` |

**Tests:** `tests/contracts/test_prompt_studio_templates_contracts.py`, `tests/unit/ui_application/test_prompt_studio_templates_presenter.py`, `tests/unit/gui/test_prompt_templates_panel_port_path.py`, `tests/architecture/test_prompt_templates_panel_guardrails.py`, `test_service_prompt_studio_adapter.py`

**Guardrails:** `refresh` / `apply_prompt_templates_state` ohne Service; Legacy `_load_templates_legacy` + Mutations-Methoden.

**Restschuld:** Template-Mutationen weiterhin direkt am Service (spätere Batch-Slices).

---

### Batch 2 — Zusammenfassung

| Kriterium | Stand |
|-----------|--------|
| Slices | Library read, Version read, Templates read |
| Tests | Contracts, Presenter, Adapter, Sink, Panel-Port-Pfad, AST-Guardrails, `tests/smoke/test_prompt_studio_batch2_import.py` |
| Protokoll | `app/ui_application/view_models/protocols.py` — `PromptStudioVersionsUiSink`, `PromptStudioTemplatesUiSink` |

**Roadmap verbleibend (nicht Batch 2):** Batch 3 (ModelSettingsPanel scalars, Editor save, Workspace new/open), …

## Analyse und Wahl: Nächste Referenzdomäne nach Deployment

Stand: Nach **Deployment Slice 1–4** ist die Operations-Deployment-Spalte **lesend** durchgängig portierbar; als **nächster Referenzblock** soll eine weitere GUI-Domäne den gleichen vertikalen Schnitt (Contracts → Port → Adapter → Presenter → Sink, Legacy-Fallback) erhalten.  
Ziel dieser Sektion: **eine** migrationssichere Wahl + **ein** erster Slice-Vorschlag — **ohne** Vollmigration und ohne neue Fachlogik.

### A. Domänenanalyse (projektreal, Datei-/Kopplungsfakten)

| Domäne | Zentrale Workspaces / Panels | Service- & Technikkopplung | UI-Komplexität | Kleinst denkbarer vertikaler Slice (Idee) | Architekturgewinn | Migrationsrisiko | Sumpf-Wahrscheinlichkeit |
|--------|------------------------------|----------------------------|----------------|-------------------------------------------|-------------------|------------------|---------------------------|
| **Knowledge** | `operations/knowledge/knowledge_workspace.py`; Panels u. a. `KnowledgeSourceExplorerPanel`, `KnowledgeOverviewPanel`, `RetrievalTestPanel`, `index_status_page`, `collection_panel`, … | Überwiegend `get_knowledge_service()`; Workspace importiert **`app.rag.models.Chunk`**; `asyncio` (`create_task`, Loop-Retry via `QTimer` in `_defer_refresh`); Indexierung/RAG-Pfade | Hoch (Splitter, Explorer, Overview, Retrieval, Collections, Chunk-Viewer) | Z. B. nur **Overview** oder nur **statische Liste** eines Teilbereichs | Mittel–hoch (sichtbare Entkopplung von RAG) | **Hoch** (Vektor/DB, async, viele Teilflächen) | **Hoch** — leicht halb portiert, halb Legacy |
| **Prompt Studio** | `operations/prompt_studio/prompt_studio_workspace.py` (~290+ Zeilen); `prompt_list_panel`, `prompt_editor_panel`, … | **`PromptListPanel`** **Slice 1**: Listen-Read über Port/Adapter; sonst weiter **`get_prompt_service()`** in Editor/Templates/Lab/Library | Mittel–hoch (3-Spalten, `QStackedWidget`, Navigation) | Slice 1 = **PromptListPanel read-only** (siehe **„Erledigt: Prompt Studio Slice 1“**) | Mittel | **Mittel** für Editor/Test-Lab | **Mittel** |
| **Agent Tasks** | `operations/agent_tasks/agent_tasks_workspace.py`; `AgentRegistryPanel`, `AgentOperationsDetailPanel`, `AgentTaskPanel`, … | Tab **Betrieb**: Registry **Slice 1** + Operations-Detail **Slice 2** (Port/Adapter/Presenter/Sink); Legacy nur `_apply_ops_detail_legacy` ohne Port-Registry; Tab **Aufgaben**: **`asyncio.create_task`** + `start_agent_task` (unverändert) | Mittel (Tabs, Splitter, Grid) | Slice 1–2 = **Betrieb read** (siehe **„Erledigt: Agent Tasks Slice 1/2“**) | Solide | **Niedrig** für **Inspector** (`setup_inspector` / `AgentTasksInspector`) | **Niedrig**, solange **Aufgaben-Tab/async** separat bleibt |
| **Workflows** | `operations/workflows/workflow_workspace.py` (**~900 Zeilen**); Editor, Run-, Schedule-Panels, viele Dialoge | **`get_workflow_service()`** im `__init__`; **`get_schedule_service()`**; **`QThreadPool`/`QRunnable`**; Domain **`WorkflowDefinition`**, Canvas/Editor-Kopplung | Sehr hoch | Theoretisch nur **Workflow-Liste** read-only — praktisch schnell an Canvas/Runs gebunden | Sehr hoch langfristig | **Sehr hoch** | **Sehr hoch** |
| **Weitere Kandidaten** | z. B. `operations/projects/projects_workspace.py` (Projekt-Lifecycle, viele Dialoge); Control-Center-Agents (`control_center/agents_ui/`) überschneidet sich fachlich mit **Agent Tasks** | jeweils eigene Service-Schichten, teils quer zu Operations | variiert | nicht klarer als Agent Tasks für *ersten* kleinen Slice | — | — | — |

### B. Vergleich (Kurz)

| Kriterium | Knowledge | Prompt Studio | Agent Tasks | Workflows |
|-----------|-----------|---------------|-------------|-----------|
| Nutzen (Architektur-Klarheit) | Hoch | Mittel | Solide | Sehr hoch (langfristig) |
| Risiko / Technikschuld | Hoch (RAG/Async) | Mittel | **Am niedrigsten** für Lese-Slice | Sehr hoch |
| Schnitttauglichkeit (kleiner erster Slice) | Schwach | Mittel | **Stark** (ein Panel, sync) | Schwach |
| Testbarkeit ohne Async/Canvas | Aufwendig | Gut | **Sehr gut** | Schlecht |
| Sumpf-Gefahr | Hoch | Mittel | **Gering** (bei Disziplin) | Sehr hoch |

### C. Auswahl — genau eine nächste Ziel-Domäne

**Gewählt: `operations_agent_tasks` (Agent Tasks).**

**Begründung (migrationssicher, nicht nach „Wichtigkeit“):**

- Der kleinste sinnvolle vertikale Einstieg war **`AgentRegistryPanel`** — **Slice 1 ist umgesetzt** (siehe unten); Lesepfad synchron über Adapter (`list_agents_for_project` + `list_summaries`).
- Kein Canvas, keine `QGraphicsScene`, kein Pflicht-Async für diesen Slice — im Gegensatz zu Knowledge (RAG/`Chunk`/Indexing-Retry) und Workflows (Editor/Pool/Definition).
- Prompt Studio ist **zweitbester** Kandidat (Listenpfad synchron), aber stärker mit **mehreren** Panels und **Workspace-Navigation** verwoben als die isolierte Registry-Liste.
- Workflows bleiben **bewusst zurückgestellt** bis zu einem separaten Risiko-Review.

### D. Erster Slice — umgesetzt: Agent Tasks Slice 1

Siehe **„Erledigt: Agent Tasks Slice 1“** direkt unter diesem Abschnitt.

### E. Guardrails (Slice 1–2 umgesetzt)

- **Architektur:** `tests/architecture/test_agent_registry_panel_guardrails.py` — `AgentRegistryPanel.refresh()` ohne direkten `get_agent_service`; Legacy nur in `_refresh_legacy`.
- **Architektur:** `tests/architecture/test_agent_tasks_workspace_guardrails.py` — `AgentTasksWorkspace._on_agent_selected` ohne direkten `get_agent_operations_read_service`; Legacy nur in `_apply_ops_detail_legacy`.
- **Registry-/Detail-Lesepfad:** `get_agent_service` / `get_agent_operations_read_service` für **Listen- und Detail-Lesen** nur im Adapter (bzw. Legacy-Fallback im Workspace); Hauptpfad: `LoadAgentTaskSelectionCommand` → `AgentTasksSelectionPresenter` → Port → Adapter → `AgentTasksSelectionSink`.
- **Fallback:** `AgentRegistryPanel(..., agent_tasks_registry_port=None)` → vollständiger Legacy-Pfad im Panel; Workspace erkennt `uses_port_driven_registry()==False` und nutzt `_apply_ops_detail_legacy` für die Detailspalte.
- **`ui_contracts`:** kein `AgentProfile` — Anzeige Registry als `list_item_text` + `agent_id`; Operations-Detail als `AgentTasksOperationsSummaryDto` / Issues-DTOs.

### F. Zweitwahl (kurz)

- **Prompt Studio:** **Slice 1 umgesetzt** (`PromptListPanel` read-only); nächste Schnitte z. B. Editor-Read oder Templates separat scoped.
- **Knowledge / Workflows:** erst nach klarer Scope-Begrenzung bzw. eigenem Architektur-Review.

---

**Deployment-Block:** gilt nach Slice 4 **read-seitig** als weitgehend migrationsreif. **Agent Tasks Slice 1–2** (Betrieb-Tab: Registry + Operations-Detail) sind umgesetzt; nächster sinnvoller Schritt siehe **„Erledigt: Agent Tasks Slice 2“** (Restpunkte / Slice 3).

## Erledigt: Agent Tasks Slice 1 (Registry im Betrieb-Tab, read-only)

### A. Bestandsanalyse (vor Migration)

| Aspekt | Code |
|--------|------|
| **`agent_tasks_workspace._refresh_agents`** | `get_project_context_manager().get_active_project_id()` → `_registry.refresh(project_id)` (Presenter/Adapter) → `last_registry_snapshot` → `_task_panel.set_agents(snap.agents)` (kein Workspace-Cache mehr). |
| **`AgentRegistryPanel.refresh` (Legacy)** | Ohne Projekt: ein nicht wählbares Item „Bitte Projekt auswählen“. Mit Projekt: `get_agent_service().list_agents_for_project(...)`; leer → ein Item „Keine Agenten – Seed ausführen?“; sonst pro `AgentProfile` mehrzeiliger Text (`effective_display_name`, `role`, `status`, `assigned_model`, optional `⚠ n Hinweis(e)` aus `summaries_by_id[profile.id].issues`); `UserRole` = `AgentProfile`. Exception → ein Item „Agenten konnten nicht geladen werden“. |
| **`select_agent_by_id`** | Iteriert Liste, vergleicht `AgentProfile.id`, emittiert `agent_selected`. |
| **Minimale Injektion** | Optional `agent_tasks_registry_port=` am Panel; Workspace hält `ServiceAgentTasksRegistryAdapter()` und übergibt dieselbe Instanz; ein **`last_registry_snapshot`** nach erfolgreichem Registry-Load (Slice 2b). |

### B.–F. Implementierung

| Bereich | Datei |
|---------|--------|
| Contract | `app/ui_contracts/workspaces/agent_tasks_registry.py` |
| Port | `app/ui_application/ports/agent_tasks_registry_port.py` |
| Adapter | `app/ui_application/adapters/service_agent_tasks_registry_adapter.py` |
| Presenter | `app/ui_application/presenters/agent_tasks_registry_presenter.py` |
| Sink | `app/gui/domains/operations/agent_tasks/agent_tasks_registry_sink.py` |
| Panel | `app/gui/domains/operations/agent_tasks/panels/agent_registry_panel.py` |
| Workspace | `agent_tasks_workspace.py` — Injektion, `_refresh_agents` ohne direkten Agent-/Read-Service für die Registry |
| Protokoll | `app/ui_application/view_models/protocols.py` — `AgentTasksRegistryUiSink` |

### Technische Schuld / Restpunkte

- **`ServiceAgentTasksRegistryAdapter`** setzt nach `load_registry_view` genau ein **`AgentTasksRegistrySnapshot`** (`agents`, `profiles_by_id`, `summaries_by_id`) — **Slice 2b** konsolidiert die früheren drei Sidecar-Felder. Der Workspace liest nur noch `last_registry_snapshot` für `AgentTaskPanel.set_agents` und (Legacy) `summaries_by_id` für `_apply_ops_detail_legacy`. Selection nutzt `snapshot.summaries_by_id` (`get_summary` nur bei Cache-Miss mit Projekt).
- **Presenter (Registry)** übergibt `AgentProfile`-Tupel an den Sink **nur** für `UserRole` und `agent_selected` — bleibt GUI-Schicht, nicht Contract.
- **Aufgaben-Tab / `asyncio` / `start_agent_task` / `AgentSummaryPanel.set_agent(AgentProfile)` / `ensure_seed_agents` / `setup_inspector`:** weiterhin Legacy bzw. unangetastet (Slice-2-Scope nur Betrieb-Detailspalte).

### Tests (Agent Tasks Slice 1)

| Test | Pfad |
|------|------|
| Contracts | `tests/contracts/test_agent_tasks_registry_contracts.py` |
| Presenter | `tests/unit/ui_application/test_agent_tasks_registry_presenter.py` |
| Adapter | `tests/unit/ui_application/test_service_agent_tasks_registry_adapter.py` |
| Sink | `tests/unit/gui/test_agent_tasks_registry_sink.py` |
| Panel | `tests/unit/gui/test_agent_registry_panel_port_path.py` |
| Guardrail | `tests/architecture/test_agent_registry_panel_guardrails.py` |
| Smoke | `tests/smoke/test_agent_tasks_slice1_import.py` |

## Erledigt: Agent Tasks Slice 2 (Selection / Operations-Detail im Betrieb-Tab)

### A. Bestandsanalyse (Detail-Pfad, Codebezug)

| Aspekt | Code / Verhalten |
|--------|------------------|
| **`AgentTasksWorkspace._on_agent_selected`** | Signal `AgentRegistryPanel.agent_selected` liefert `AgentProfile`. Bisher (pre-Slice-2): `AgentSummaryPanel.set_agent(profile)` und `AgentTaskPanel.set_selected_agent` (Aufgaben-Tab); für **Betrieb-Detail** wurde `self._summaries_by_id.get(profile.id)` genutzt, bei Miss + gesetztem Projekt **`get_agent_operations_read_service().get_summary(profile.id, project_id)`**, dann `AgentOperationsDetailPanel.set_summary(s)`. Ohne Profil: `set_summary(None)`. |
| **`AgentOperationsDetailPanel`** | `set_summary(AgentOperationsSummary \| None)` rendert HTML-Body (Slug, Status, Modell, Issues, Workflow-IDs); Deep-Link-Buttons. Keine Service-Aufrufe. |
| **`get_summary`** | `AgentOperationsReadService.get_summary` lädt Profil via `get_agent_service().get_agent`, prüft Sichtbarkeit im Projekt, baut Summary wie `list_summaries` (Metrics, Issues, Workflow-Refs). |
| **GUI-only** | `AgentSummaryPanel` bleibt profilbasiert (Aufgaben-Tab); `AgentTasksInspector` / `_refresh_inspector` unverändert. |
| **Cache / Snapshot** | **Slice 2b:** nur noch `adapter.last_registry_snapshot` — kein `_summaries_by_id` im Workspace. |

### B.–G. Implementierung (Slice 2)

| Bereich | Datei / Ergänzung |
|---------|-------------------|
| Contract | `app/ui_contracts/workspaces/agent_tasks_registry.py` — `AgentTasksOperationsIssueDto`, `AgentTasksOperationsSummaryDto`, `AgentTasksSelectionViewState`, `LoadAgentTaskSelectionCommand`, `agent_tasks_selection_idle_state` |
| Port | `app/ui_application/ports/agent_tasks_registry_port.py` — `load_agent_task_selection_detail` |
| Adapter | `service_agent_tasks_registry_adapter.py` — `load_agent_task_selection_detail` (Cache-Treffer → DTO; sonst `get_summary`; Fehler → `phase=error`) |
| Presenter | `app/ui_application/presenters/agent_tasks_selection_presenter.py` |
| Sink | `app/gui/domains/operations/agent_tasks/agent_tasks_selection_sink.py` (DTO → `AgentOperationsSummary` für bestehendes Panel) |
| Protokoll | `app/ui_application/view_models/protocols.py` — `AgentTasksSelectionUiSink` |
| Panel | `agent_operations_detail_panel.py` — `set_read_error` für Read-Fehler |
| Workspace | `agent_tasks_workspace.py` — `_on_agent_selected` → Presenter bei `uses_port_driven_registry()`; `_apply_ops_detail_legacy` sonst |
| Registry-Panel | `uses_port_driven_registry()` für Workspace-Entscheid |

**Betrieb-Tab:** read-seitig (Liste + Detail) über einen durchgängigen UI-Pfad testbar; **Legacy** bleibt für Kombinationen ohne Port-Registry.

### Technische Schuld / ehrliche Restpunkte

- **Slice 2b:** Adapter hält nur noch **`last_registry_snapshot`** statt dreier Felder; kein Workspace-Mirror mehr.
- `AgentTasksSelectionSink` mappt DTOs zurück auf `AgentOperationsSummary`, damit `AgentOperationsDetailPanel` unverändert bleibt (bewusster GUI-Grenz-Mapper).
- Legacy-Detail (`_apply_ops_detail_legacy`) nutzt `last_registry_snapshot.summaries_by_id`, wenn vorhanden.

### Nächster sinnvoller Slice (Agent Tasks)

- **Slice 3 ist umgesetzt** (siehe unten). **Slice 4 (Idee):** Aufgaben-Tab/async nur nach separatem Scope-Review; alternativ **Prompt Studio**-Listenpfad als nächste Referenzdomäne.

### Tests (Agent Tasks Slice 2)

| Test | Pfad |
|------|------|
| Contracts | `tests/contracts/test_agent_tasks_registry_contracts.py` (Slice-2-Teil) |
| Presenter | `tests/unit/ui_application/test_agent_tasks_selection_presenter.py` |
| Adapter | `tests/unit/ui_application/test_service_agent_tasks_registry_adapter.py` (Selection-Tests) |
| Sink | `tests/unit/gui/test_agent_tasks_selection_sink.py` |
| Workspace | `tests/unit/gui/test_agent_tasks_workspace_selection_path.py` |
| Guardrail | `tests/architecture/test_agent_tasks_workspace_guardrails.py` |
| Smoke | `tests/smoke/test_agent_tasks_slice2_import.py` |

## Erledigt: Agent Tasks Slice 3 (Inspector Read-Pfad)

### Kurz

- **Contract:** `app/ui_contracts/workspaces/agent_tasks_inspector.py` — `AgentTasksInspectorState`, `AgentTasksInspectorPatch`, `LoadAgentTasksInspectorCommand`, `AgentTasksInspectorReadDto`, `INSPECTOR_SECTION_SEP`.
- **Port:** `load_agent_tasks_inspector_state(agent_id, project_id)` auf `AgentTasksRegistryPort`.
- **Adapter:** `load_agent_tasks_inspector_state` — Snapshot-Cache oder `get_agent_operations_read_service().get_summary`, Abbild auf `AgentTasksInspectorReadDto`.
- **Presenter:** `agent_tasks_inspector_presenter.py` — merged Operations-Texte mit Task-Sektionen aus dem Workspace (`_inspector_task_sections`).
- **Sink:** `agent_tasks_inspector_sink.py` — `AgentTasksInspector(port_driven_body=…)` / Fehler-Styling.
- **Workspace:** `_refresh_inspector` → `LoadAgentTasksInspectorCommand` + Presenter bei Port-Registry; `_refresh_inspector_legacy` unverändertes `AgentTaskResult`-Widget. `_inspector_focus_agent_id` bei Agentenauswahl. `setup_inspector` erzeugt Sink/Presenter.
- **Legacy:** ohne `uses_port_driven_registry()` weiter direktes Inspector-Widget.

### Tests (Agent Tasks Slice 3)

| Test | Pfad |
|------|------|
| Contracts | `tests/contracts/test_agent_tasks_inspector_contracts.py` |
| Presenter | `tests/unit/ui_application/test_agent_tasks_inspector_presenter.py` |
| Adapter | `tests/unit/ui_application/test_service_agent_tasks_registry_adapter.py` (Inspector-Tests) |
| Sink | `tests/unit/gui/test_agent_tasks_inspector_sink.py` |
| Workspace | `tests/unit/gui/test_agent_tasks_workspace_inspector_path.py` |
| Guardrail | `tests/architecture/test_agent_tasks_inspector_guardrails.py` |
| Smoke | `tests/smoke/test_agent_tasks_slice3_import.py` |

## Erledigt: Prompt Studio Slice 1 (`PromptListPanel` read-only)

### Kurz

- **Contract:** `app/ui_contracts/workspaces/prompt_studio_list.py` — `PromptListEntryDto`, `PromptStudioListState`, `LoadPromptStudioListCommand`, `prompt_studio_list_loading_state`.
- **Port:** `app/ui_application/ports/prompt_studio_port.py` — `load_prompt_list(project_id, filter_text)`.
- **Adapter:** `service_prompt_studio_adapter.py` — `list_project_prompts` + `list_global_prompts` + `count_versions` (wie vorher im Panel); Sidecar `last_prompt_list_models` für `PromptListItem`.
- **Presenter:** `prompt_studio_list_presenter.py`
- **Sink:** `prompt_studio_list_sink.py`
- **Panel:** `prompt_list_panel.py` — `prompt_studio_port=None` → `_load_prompts_legacy`; sonst `refresh()` → Command/Presenter.
- **Workspace:** `ServicePromptStudioAdapter` injiziert in `PromptListPanel`.

### Tests (Prompt Studio Slice 1)

| Test | Pfad |
|------|------|
| Contracts | `tests/contracts/test_prompt_studio_list_contracts.py` |
| Presenter | `tests/unit/ui_application/test_prompt_studio_list_presenter.py` |
| Adapter | `tests/unit/ui_application/test_service_prompt_studio_adapter.py` |
| Sink | `tests/unit/gui/test_prompt_studio_list_sink.py` |
| Panel | `tests/unit/gui/test_prompt_list_panel_port_path.py` |
| Guardrail | `tests/architecture/test_prompt_list_panel_guardrails.py` |
| Smoke | `tests/smoke/test_prompt_studio_slice1_import.py` |

## Erledigt: Batch 3 — POST-CORRECTION UI (drei Slices)

### Slice 1 — Settings: ModelSettingsPanel erweiterte Skalare (Top-p, Timeout, Retry)

**Kurz:** `ModelRoutingStudioState` / `ModelRoutingStudioWritePatch` um `top_p`, `llm_timeout_seconds`, `retry_without_thinking` ergänzt; Adapter persistiert auf `AppSettings`; Sink spiegelt in `top_p_spin`, `timeout_spin`, `retry_check`; Panel-Handler nutzen den bestehenden Presenter-/Port-Pfad (kein `self.settings.save()`, kein direktes `self.settings` in Routing-Handlern). Legacy bleibt: Panel ohne `model_routing_port` → `ServiceSettingsAdapter` über `_legacy_routing_adapter()`.

| Bereich | Dateien |
|---------|---------|
| Contract | `app/ui_contracts/workspaces/settings_model_routing.py` |
| Port / Adapter / Presenter / Sink | `settings_operations_port.py` (bestehend), `service_settings_adapter.py`, `settings_model_routing_presenter.py`, `settings_model_routing_sink.py` |
| Panel | `app/gui/domains/settings/panels/model_settings_panel.py` |
| Settings | `app/core/config/settings.py` — `top_p`, `llm_timeout_seconds` in load/save |

**Tests:** `tests/contracts/test_settings_model_routing_contracts.py`, `tests/unit/gui/test_settings_model_routing_sink.py`, `tests/unit/ui_application/test_settings_model_routing_presenter.py`, `tests/unit/ui_application/test_service_settings_adapter.py` (inkl. `test_persist_model_routing_studio_scalars_top_p_timeout_retry`).

**Guardrails:** `tests/architecture/test_model_settings_panel_guardrails.py` — erweitert um AST-Prüfung: Routing-Handler (`_on_top_p_changed`, `_on_timeout_changed`, `_on_retry_changed`, …) ohne `self.settings`.

**Restschuld:** Rollen-Combos (`_on_role_model_changed`) weiterhin ohne Port-Persistenz; Provider-/Orchestrator-Hinweise unverändert.

---

### Slice 2 — Prompt Studio: Editor-Speichern (Mutation)

**Kurz:** `Widget → PromptStudioEditorPresenter → PromptStudioPort → ServicePromptStudioAdapter`. Contracts: `prompt_studio_editor.py` (`SavePromptVersionEditorCommand`, `UpdatePromptMetadataEditorCommand`, `PromptEditorSaveResultState`, …). Legacy: `prompt_studio_port=None` → `_on_save_legacy` (bzw. voller Editor: gleiches Muster).

| Bereich | Dateien |
|---------|---------|
| Contract | `app/ui_contracts/workspaces/prompt_studio_editor.py` |
| Port | `app/ui_application/ports/prompt_studio_port.py` — `persist_prompt_editor` |
| Adapter | `app/ui_application/adapters/service_prompt_studio_adapter.py` — `persist_prompt_editor` |
| Presenter | `app/ui_application/presenters/prompt_studio_editor_presenter.py` |
| Sink | `app/gui/domains/operations/prompt_studio/prompt_studio_editor_sink.py` |
| Protokoll | `app/ui_application/view_models/protocols.py` — `PromptStudioEditorUiSink` |
| Panels | `panels/prompt_editor_panel.py`, `panels/editor_panel.py` |
| Workspace | `prompt_studio_workspace.py` — `PromptEditorPanel(..., prompt_studio_port=...)` |

**Tests:** `tests/contracts/test_prompt_studio_editor_contracts.py`, `tests/unit/ui_application/test_prompt_studio_editor_presenter.py`, `tests/unit/ui_application/test_service_prompt_studio_adapter.py` (persist), `tests/unit/gui/test_prompt_studio_editor_sink.py`, `tests/unit/gui/test_prompt_editor_panel_port_path.py`.

**Guardrails:** `tests/architecture/test_prompt_studio_remaining_panels_guardrails.py` — `get_prompt_service` nur noch in `_on_save_legacy` (beide Editor-Panels).

**Restschuld:** Test Lab, Template-Mutationen, Inspector breit — bewusst nicht Batch 3.

---

### Slice 3 — Prompt Studio: Workspace „Neu“ + `open_with_context`

**Kurz:** `PromptStudioWorkspacePresenter` (dünn) → Port → Adapter: `create_user_prompt_for_studio`, `open_prompt_snapshot_for_studio`. Contract `PromptStudioWorkspaceOpResult` in `prompt_studio_workspace.py`. Legacy: `prompt_studio_workspace_flow=False` oder explizite `_on_new_prompt_legacy` / `_open_with_context_legacy`.

| Bereich | Dateien |
|---------|---------|
| Contract | `app/ui_contracts/workspaces/prompt_studio_workspace.py` |
| Port / Adapter | `prompt_studio_port.py`, `service_prompt_studio_adapter.py` |
| Presenter | `app/ui_application/presenters/prompt_studio_workspace_presenter.py` |
| Workspace | `app/gui/domains/operations/prompt_studio/prompt_studio_workspace.py` |

**Tests:** `tests/contracts/test_prompt_studio_workspace_contracts.py`, `tests/unit/ui_application/test_prompt_studio_workspace_presenter.py`, `tests/unit/ui_application/test_service_prompt_studio_adapter.py` (create/open), `tests/unit/gui/test_prompt_studio_workspace_batch3.py`.

**Guardrails:** `test_prompt_studio_remaining_panels_guardrails.py` — `get_prompt_service` nur in `_on_new_prompt_legacy`, `_open_with_context_legacy`.

**Restschuld:** Weitere Workspace-Hilfen mit direktem Service-Zugriff außerhalb dieses Flusses unverändert.

**Smoke (Batch 3):** `tests/smoke/test_prompt_studio_batch3_import.py`.

## Erledigt: Batch 4 — Deployment-Mutationen (Targets + Releases)

### Slice 1 — Deployment: Targets-Mutation Port-Vollständigkeit

**Kurz:** Hauptpfad war bereits Presenter → `DeploymentTargetsPort` → `ServiceDeploymentTargetsAdapter`; Batch 4 schärft AST-Guardrails (`get_project_service`, `get_infrastructure` zusätzlich verboten in `refresh` / `_on_new` / `_on_edit`) und ergänzt Panel-Test `test_targets_panel_port_mutations.py` für Command-Dispatch.

| Bereich | Dateien (Audit / ergänzt) |
|---------|---------------------------|
| Contracts / Port / Adapter / Presenter / Sink | `deployment_targets.py`, `deployment_targets_port.py`, `service_deployment_targets_adapter.py`, `deployment_targets_presenter.py`, `deployment_targets_sink.py`, `targets_panel.py` |

**Tests:** bestehende Contracts/Presenter/Adapter/Sink-Tests; neu `tests/unit/gui/test_targets_panel_port_mutations.py`.

**Guardrails:** `tests/architecture/test_deployment_targets_panel_guardrails.py` — `get_deployment_operations_service`, `get_project_service`, `get_infrastructure` nur in `_*_legacy` / `_refresh_legacy`.

**Restschuld:** keine funktionale Lücke für Target Create/Update auf dem injizierten Pfad; Rollouts-Tab unverändert.

---

### Slice 2 — Deployment: Releases-Mutationen über Port

**Kurz:** `CreateDeploymentReleaseCommand` / `UpdateDeploymentReleaseCommand` / `ArchiveDeploymentReleaseCommand`, `DeploymentReleasesViewState.banner_message`, Port-Methoden `create_release` / `update_release` / `archive_release` / `get_release_editor_snapshot`; Presenter lädt nach Erfolg Liste + Auswahl neu, bei Fehler Banner; `ReleasesPanel` delegiert bei injiziertem Port; Legacy in `_on_*_legacy`.

| Bereich | Dateien |
|---------|---------|
| Contract | `app/ui_contracts/workspaces/deployment_releases.py` |
| Port | `app/ui_application/ports/deployment_releases_port.py` |
| Adapter | `app/ui_application/adapters/service_deployment_releases_adapter.py` |
| Presenter | `app/ui_application/presenters/deployment_releases_presenter.py` |
| Sink | `app/gui/domains/operations/deployment/deployment_releases_sink.py` — Banner bei Mutation-Fehler |
| Panel | `app/gui/domains/operations/deployment/panels/releases_panel.py` |

**Tests:** erweitert `test_deployment_releases_contracts.py`, `test_deployment_releases_presenter.py`, `test_service_deployment_releases_adapter.py`, `test_deployment_releases_sink.py`, `test_releases_panel_port_path.py`.

**Guardrails:** `test_deployment_releases_panel_guardrails.py` — `refresh`, `_on_sel`, `_on_new`, `_on_edit`, `_on_archive` ohne `get_deployment_operations_service` / `get_project_service` / `get_infrastructure` (nur `_*_legacy`).

**Restschuld:** Rollout-Aufzeichnung/Mutation bewusst nicht Teil dieses Batches.

**Smoke (Batch 4):** `tests/smoke/test_deployment_batch4_import.py`.

## Erledigt: Batch 5 — Prompt Studio Test Lab read + Agent Tasks Operations-Summary read

### Slice 1 — Prompt Studio: Test Lab read

**Kurz:** Prompt-/Versions- und Modell-Combos im Test Lab laden über `PromptStudioTestLabPresenter` → `PromptStudioPort` → `ServicePromptStudioAdapter`; Run/Stream (`_run_prompt`, `get_chat_service`) unverändert. Ohne injizierten Presenter bleiben `_*_legacy`-Methoden mit direktem Prompt-/Model-Service.

| Bereich | Dateien |
|---------|---------|
| Contract | `app/ui_contracts/workspaces/prompt_studio_test_lab.py` |
| Port | `app/ui_application/ports/prompt_studio_port.py` — `load_prompt_test_lab_prompts` / `load_prompt_test_lab_versions` / `async load_prompt_test_lab_models` |
| Adapter | `app/ui_application/adapters/service_prompt_studio_adapter.py` |
| Presenter | `app/ui_application/presenters/prompt_studio_test_lab_presenter.py` |
| Sink | `app/gui/domains/operations/prompt_studio/prompt_studio_test_lab_sink.py` |
| Panel / Workspace | `panels/prompt_test_lab.py`, `prompt_studio_workspace.py` |
| Protocol | `app/ui_application/view_models/protocols.py` — `PromptStudioTestLabUiSink` |

**Tests:** `tests/contracts/test_prompt_studio_test_lab_contracts.py`, `tests/unit/ui_application/test_prompt_studio_test_lab_presenter.py`, `tests/unit/ui_application/test_service_prompt_studio_adapter.py` (Test-Lab-Methoden), `tests/unit/gui/test_prompt_studio_test_lab_sink.py`, `tests/unit/gui/test_prompt_test_lab_port_path.py`.

**Guardrails:** `tests/architecture/test_prompt_test_lab_panel_guardrails.py` — `_load_prompts_async`, `_load_models_async`, `_on_prompt_changed` ohne `get_prompt_service` / `get_model_service`; `_*_legacy` und `_run_prompt` (Chat) explizit erlaubt. `test_prompt_studio_remaining_panels_guardrails.py` enthält `PromptTestLab` nicht mehr (eigener Guard).

**Restschuld:** (Batch 6 erledigt) Test-Lab Run/Streaming über Port/Adapter; keine Editor/Library/Templates/Versions-Mutationen in Batch 5/6.

**Smoke (Batch 5):** `tests/smoke/test_prompt_studio_batch5_import.py`.

---

### Slice 2 — Agent Tasks: Operations-Summary read (Workspace)

**Kurz:** Die Betrieb-Detailspalte (Operations-Summary) wird bei gesetztem `AgentTasksSelectionPresenter` **immer** über `LoadAgentTaskSelectionCommand` → Presenter → Port → Adapter geladen — unabhängig davon, ob die Registry-Liste selbst noch den Legacy-Pfad nutzt. `get_agent_operations_read_service` bleibt nur im Adapter und in `_apply_ops_detail_legacy` (wenn kein Selection-Presenter).

| Bereich | Dateien |
|---------|---------|
| Workspace | `app/gui/domains/operations/agent_tasks/agent_tasks_workspace.py` — `_on_agent_selected` |
| Port / Adapter / Presenter / Contracts | unverändert erweitert; kein paralleles Summary-Modell |

**Tests:** `tests/unit/gui/test_agent_tasks_workspace_selection_path.py` (`test_selection_presenter_used_even_when_registry_not_port_driven`); bestehende Adapter-/Presenter-/Sink-Tests.

**Guardrails:** `tests/architecture/test_agent_tasks_workspace_guardrails.py` — ergänzt: `_refresh_agents` ohne direkten `get_agent_operations_read_service`; `_on_agent_selected` und `_apply_ops_detail_legacy` wie zuvor.

**Restschuld:** Start-Task / Runtime-Async unverändert; Inspector-Pfad unverändert.

## Erledigt: Batch 6 — Prompt Studio Test Lab run/stream + Agent Tasks Start-Task async

### Slice 1 — Prompt Studio: Test Lab run / chat stream

**Kurz:** Chat-Stream läuft über `PromptStudioTestLabPresenter.handle_run_async` → `PromptStudioPort.stream_prompt_test_lab_run` → `ServicePromptStudioAdapter` → `get_chat_service().chat`; Sink spiegelt `PromptTestLabRunPatch` (Text, Scroll, Run-Button). Ohne injizierten Presenter bleibt `_run_prompt_legacy` mit direktem Chat-Service.

| Bereich | Dateien |
|---------|---------|
| Contract | `prompt_studio_test_lab.py` — `RunPromptTestLabCommand`, `PromptTestLabStreamChunkDto`, `PromptTestLabRunPatch`, `PromptTestLabRunState` |
| Port | `prompt_studio_port.py` — `stream_prompt_test_lab_run` |
| Adapter | `service_prompt_studio_adapter.py` |
| Presenter | `prompt_studio_test_lab_presenter.py` |
| Sink / Panel | `prompt_studio_test_lab_sink.py`, `panels/prompt_test_lab.py` |
| Protocol | `protocols.py` — `PromptStudioTestLabUiSink.apply_run_patch` |

**Tests:** `test_prompt_studio_test_lab_contracts.py` (Run-DTOs), `test_prompt_studio_test_lab_presenter.py` (Stream/Fehler), `test_service_prompt_studio_adapter.py` (Stream), `test_prompt_studio_test_lab_sink.py` (Run-Patch), `test_prompt_test_lab_run_path.py`.

**Guardrails:** `test_prompt_test_lab_panel_guardrails.py` — `_on_run` / `_run_via_presenter` ohne `get_chat_service`; `_run_prompt_legacy` mit Chat-Service.

**Restschuld:** keine funktionale Lücke für den injizierten Test-Lab-Pfad; Editor/Library/Templates/Versionen unverändert.

**Smoke (Batch 6):** `tests/smoke/test_batch6_import.py`.

---

### Slice 2 — Agent Tasks: Start task async port

**Kurz:** `AgentTasksWorkspace._run_task` ruft bei gesetztem `AgentTasksRuntimePresenter` `StartAgentTaskCommand` auf; `ServiceAgentTasksRuntimeAdapter.start_agent_task_runtime` kapselt `get_agent_service().start_agent_task`; `AgentTasksRuntimeSink` mappt DTO → `AgentTaskResult` fürs Result-Panel. Legacy: `_run_task_legacy` mit direktem Service + Inspector-Refresh wie zuvor.

| Bereich | Dateien |
|---------|---------|
| Contract | `app/ui_contracts/workspaces/agent_tasks_runtime.py` |
| Port | `app/ui_application/ports/agent_tasks_runtime_port.py` |
| Adapter | `app/ui_application/adapters/service_agent_tasks_runtime_adapter.py` |
| Presenter | `app/ui_application/presenters/agent_tasks_runtime_presenter.py` |
| Sink | `app/gui/domains/operations/agent_tasks/agent_tasks_runtime_sink.py` |
| Workspace | `agent_tasks_workspace.py` |

**Tests:** `test_agent_tasks_runtime_contracts.py`, `test_service_agent_tasks_runtime_adapter.py`, `test_agent_tasks_runtime_presenter.py`, `test_agent_tasks_runtime_sink.py`, `test_agent_tasks_workspace_runtime_path.py`.

**Guardrails:** `test_agent_tasks_workspace_runtime_guardrails.py` — `_run_task` ohne direkten `.start_agent_task`-Aufruf; `_run_task_legacy` mit Aufruf.

**Restschuld:** breitere Runtime-Orchestrierung/Inspector-Redesign bewusst out of scope; `_refresh_inspector(None)` bleibt im `finally` wie zuvor.

## Erledigt: Batch 7 — Deployment Rollout-Record + Prompt Studio Library-Delete + Template-Mutationen

### Slice 1 — Deployment: Rollout protokollieren über Port

**Kurz:** Nach Batch-1-Combo-Injektion ruft der Hauptpfad `RecordDeploymentRolloutCommand` über `DeploymentRolloutsPresenter.handle_record_rollout` → `DeploymentRolloutsPort.record_deployment_rollout` → `ServiceDeploymentRolloutsAdapter` → `record_rollout`. Bei Erfolg wie zuvor Refresh über `LoadDeploymentRolloutsCommand`. Ohne Port bleibt `_on_record_legacy` mit direktem `get_deployment_operations_service`.

| Bereich | Dateien |
|---------|---------|
| Contract | `app/ui_contracts/workspaces/deployment_rollouts.py` — `RecordDeploymentRolloutCommand`, `DeploymentRolloutRecordMutationResult` |
| Port | `deployment_rollouts_port.py` — `record_deployment_rollout` |
| Adapter | `service_deployment_rollouts_adapter.py` |
| Presenter | `deployment_rollouts_presenter.py` |
| Panel | `panels/rollouts_panel.py` — `_on_record` / `_on_record_legacy` |

**Tests:** `test_deployment_rollouts_contracts.py`, `test_deployment_rollouts_presenter.py`, `test_service_deployment_rollouts_adapter.py`, `test_rollouts_panel_port_path.py` (Record + Refresh).

**Guardrails:** `test_deployment_rollouts_panel_guardrails.py` — `refresh` und `_on_record` ohne `get_deployment_operations_service`; nur `_on_record_legacy` / `_refresh_legacy` / `_reload_filter_combos_legacy`.

**Restschuld:** Run-Link / weitere Rollout-Workflows unverändert out of scope.

---

### Slice 2 — Prompt Studio: Library-Panel Delete über Port

**Kurz:** `DeletePromptLibraryCommand` → `PromptStudioListPresenter.handle_delete_library_prompt` → `PromptStudioPort.delete_prompt_library_entry` → Adapter → `get_prompt_service().delete`; bei Erfolg Listen-Reload. Legacy: `_on_delete_prompt_legacy`.

| Bereich | Dateien |
|---------|---------|
| Contract | `prompt_studio_library.py` — `DeletePromptLibraryCommand`, `PromptLibraryMutationResult` |
| Port | `prompt_studio_port.py` |
| Adapter | `service_prompt_studio_adapter.py` |
| Presenter | `prompt_studio_list_presenter.py` |
| Panel | `panels/library_panel.py` |

**Tests:** `test_prompt_studio_library_contracts.py`, `test_prompt_studio_list_presenter.py`, `test_service_prompt_studio_adapter.py`, `test_library_panel_port_path.py`.

**Guardrails:** `test_prompt_library_panel_guardrails.py` — `_on_delete_prompt` ohne `get_prompt_service`; `_on_delete_prompt_legacy` mit Service.

**Restschuld:** (Batch 8 erledigt) siehe Batch 8 — Library `version_count`.

---

### Slice 3 — Prompt Studio: Templates-Panel Kern-Mutationen über Port

**Kurz:** Create / Update / Copy-to-Prompt / Delete über `PromptStudioTemplatesPresenter` und `PromptStudioPort`-Methoden; Adapter kapselt Prompt-Service. Legacy-Methoden `_on_*_legacy` behalten direkten Service.

| Bereich | Dateien |
|---------|---------|
| Contract | `prompt_studio_templates.py` — `Create/Update/Copy/Delete*Command`, `PromptTemplateMutationResult` |
| Port | `prompt_studio_port.py` |
| Adapter | `service_prompt_studio_adapter.py` |
| Presenter | `prompt_studio_templates_presenter.py` |
| Panel | `panels/prompt_templates_panel.py` |

**Tests:** `test_prompt_studio_templates_contracts.py`, `test_prompt_studio_templates_presenter.py`, `test_service_prompt_studio_adapter.py`, `test_prompt_templates_panel_port_path.py`.

**Guardrails:** `test_prompt_templates_panel_guardrails.py` — `_on_create`, `_on_edit`, `_on_copy_to_prompt`, `_on_delete` ohne `get_prompt_service`; `_*_legacy` mit Service.

**Restschuld:** Editor-/Versions-Mutationen weiter wie zuvor; Test Lab / Agent Tasks unberührt. (Batch 8 erledigt) Snapshot-Mapping ausgelagert nach `prompt_snapshot_ui.py` ohne lazy Import.

**Smoke (Batch 7):** `tests/smoke/test_batch7_import.py`.

## Erledigt: Batch 8 — Versionen-Audit, Library version_count, Snapshot-Helper

### Slice 1 — Prompt Studio: Versionen-Panel Kern-Mutationen (Audit)

**Kurz:** Im aktuellen `PromptVersionPanel` existieren keine nutzerseitigen Versions-Mutationen (kein Anlegen/Löschen/Umbenennen im Panel). Zeilenwahl löst nur `version_selected` mit bereits geladenen Daten aus; Persistenz bleibt beim Editor (out of scope). Es wurden keine neuen Port-/Presenter-Mutations-APIs eingeführt. Vertragsmodul-Dokumentation und AST-Guardrails wurden ergänzt (`_on_version_clicked`, `_add_version_item` ohne Service; Legacy nur `_load_versions_from_service`).

| Bereich | Dateien |
|---------|---------|
| Contract | `prompt_studio_versions.py` — Modulhinweis Batch 8 |
| Guardrails | `test_prompt_version_panel_guardrails.py` |

**Tests:** bestehend `test_prompt_studio_versions_contracts.py`, `test_prompt_studio_versions_presenter.py`, `test_prompt_version_panel_port_path.py`.

**Restschuld:** Falls später CRUD für Versionen im Panel gewünscht, eigener Batch mit Commands/Port-Methoden.

---

### Slice 2 — Prompt Studio: Library `version_count` auf injiziertem Pfad

**Kurz:** Adapter setzte `version_count` bereits pro Zeile; das Library-Panel ruft auf dem Port-Pfad kein `get_prompt_service().count_versions` mehr auf — Fallback nur noch in `_version_count_from_service_legacy` für Legacy-Listenaufbau.

| Bereich | Dateien |
|---------|---------|
| Contract-Doku | `prompt_studio_library.py` |
| Panel | `panels/library_panel.py` — `_version_count_from_service_legacy`, `_add_prompt_item` |
| Adapter | unverändert (weiterhin `count_versions` im Adapter) |

**Tests:** `test_service_prompt_studio_adapter.py` (Zeilen `version_count >= 1`), `test_library_panel_port_path.py` (Refresh mit kaputtem globalem `get_prompt_service`).

**Guardrails:** `test_prompt_library_panel_guardrails.py` — `_add_prompt_item` ohne Service; `_version_count_from_service_legacy` mit Service.

**Restschuld:** keine für dieses Slice.

---

### Slice 3 — Prompt Studio: gemeinsamer Snapshot-Helper

**Kurz:** `prompt_from_snapshot` liegt in `app/gui/domains/operations/prompt_studio/prompt_snapshot_ui.py` (nur `Prompt` + `PromptStudioPromptSnapshotDto`). Workspace und Templates-Panel importieren den Helper direkt — kein lazy Import, kein Zyklus workspace ↔ templates panel.

| Bereich | Dateien |
|---------|---------|
| Helper | `prompt_snapshot_ui.py` |
| Workspace | `prompt_studio_workspace.py` |
| Panel | `prompt_templates_panel.py` |

**Tests:** `tests/unit/gui/test_prompt_snapshot_ui.py`, `tests/smoke/test_batch8_import.py`.

**Guardrails:** Import-Disziplin über Smoke; keine neuen Panel-Methoden.

**Restschuld:** keine.

**Smoke (Batch 8):** `tests/smoke/test_batch8_import.py`.

## Architektur-Guardrails

- Unverändert: `tests/architecture/arch_guard_config.py` / `test_ui_layer_guardrails.py` (neue Contract-Dateien unter `ui_contracts` fallen unter die bestehende Qt-frei-Prüfung).
- Zusätzlich: `test_settings_ai_models_catalog_guardrails.py` (Unified-Catalog-Import nur im Legacy-Zweig des AI-Models-Panels).
- Zusätzlich (Batch 4): `test_deployment_targets_panel_guardrails.py` — `refresh`, `_on_new`, `_on_edit` ohne `get_deployment_operations_service` / `get_project_service` / `get_infrastructure` (Legacy nur in `_*_legacy` / `_refresh_legacy`).
- Zusätzlich (Batch 4): `test_deployment_releases_panel_guardrails.py` — `refresh`, `_on_sel`, `_on_new`, `_on_edit`, `_on_archive` ohne dieselben direkten Aufrufe (Legacy nur in `_*_legacy` / `_refresh_legacy` / `_on_sel_legacy`).
- Zusätzlich: `test_deployment_rollouts_panel_guardrails.py` — `RolloutsPanel.refresh()` und `_on_record` ohne direkten `get_deployment_operations_service`-Aufruf (Batch 7: Mutation über Port/Presenter; Legacy nur `_on_record_legacy` / `_refresh_legacy` / `_reload_filter_combos_legacy`).
- Zusätzlich (Batch 7): `test_prompt_library_panel_guardrails.py` — `_on_delete_prompt` ohne `get_prompt_service` (Legacy `_on_delete_prompt_legacy`).
- Zusätzlich (Batch 8): dieselbe Datei — `_add_prompt_item` ohne `get_prompt_service`; `count_versions` nur in `_version_count_from_service_legacy`.
- Zusätzlich (Batch 8): `test_prompt_version_panel_guardrails.py` — `_on_version_clicked` / `_add_version_item` ohne `get_prompt_service`; Legacy nur `_load_versions_from_service`.
- Zusätzlich (Batch 7): `test_prompt_templates_panel_guardrails.py` — Hauptpfad-Mutationen `_on_create` / `_on_edit` / `_on_copy_to_prompt` / `_on_delete` ohne `get_prompt_service` (Legacy `_*_legacy`).
- Zusätzlich: `test_agent_registry_panel_guardrails.py` — `AgentRegistryPanel.refresh()` ohne direkten `get_agent_service`-Aufruf (Legacy nur in `_refresh_legacy`).
- Zusätzlich: `test_agent_tasks_workspace_guardrails.py` — `AgentTasksWorkspace._on_agent_selected` ohne direkten `get_agent_operations_read_service`-Aufruf (Legacy nur in `_apply_ops_detail_legacy`); `_refresh_agents` ebenfalls ohne diesen Aufruf (Batch 5).
- Zusätzlich (Batch 5): `test_prompt_test_lab_panel_guardrails.py` — Test-Lab-Lesepfad ohne `get_prompt_service` / `get_model_service` (Legacy nur `_*_legacy`).
- Zusätzlich (Batch 6): dieselbe Datei — Hauptpfad-Run (`_on_run`, `_run_via_presenter`) ohne `get_chat_service` (Legacy nur `_run_prompt_legacy`).
- Zusätzlich (Batch 6): `test_agent_tasks_workspace_runtime_guardrails.py` — `_run_task` ohne direkten `start_agent_task`-Aufruf (Legacy nur `_run_task_legacy`).
- Zusätzlich: `test_agent_tasks_inspector_guardrails.py` — `AgentTasksWorkspace._refresh_inspector` ohne direkten `get_agent_operations_read_service`-Aufruf (Read nur Adapter).
- Zusätzlich: `test_prompt_list_panel_guardrails.py` — `PromptListPanel.refresh()` ohne direkten `get_prompt_service`-Aufruf (Legacy nur `_load_prompts_legacy`).
- Zusätzlich (Batch 3): `test_model_settings_panel_guardrails.py` — erweitert: Routing-/Skalar-Handler ohne `self.settings`; weiterhin kein `self.settings.save()` / kein `get_infrastructure` im Panel.
- Zusätzlich (Batch 3): `test_prompt_studio_remaining_panels_guardrails.py` — `get_prompt_service` nur in `_on_save_legacy` (Editor-Panels), nur in `_on_new_prompt_legacy` / `_open_with_context_legacy` (Workspace).
- Kein zusätzlicher AST-Guard für `get_infrastructure` in Advanced/Data/**AI-Models**-Panels: der Legacy-Pfad behält den direkten Zugriff bewusst; der neue Hauptpfad läuft nur mit Injektion (Skalare Slice 4; Katalog Slice 4b mit `catalog_port`).

