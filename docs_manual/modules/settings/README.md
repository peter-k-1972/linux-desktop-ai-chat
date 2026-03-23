# Settings

## Verwandte Themen

- [Kontext](../context/README.md) · [Chat](../chat/README.md) · [Provider](../providers/README.md) · [RAG](../rag/README.md)  
- [GUI](../gui/README.md) · [Workflow: Einstellungen](../../workflows/settings_usage.md) · [Feature: Settings](../../../docs/FEATURES/settings.md)

## 1. Fachsicht

**Settings** bündelt **persistente Anwendungskonfiguration**: Modellparameter, Thema, RAG, Prompt-Speicher, Chat-Streaming, Kontext-Keys und weitere Flags. Die fachliche Logik liegt in **`AppSettings`** (`app/core/config/settings.py`) mit austauschbarem **`SettingsBackend`** (`app/core/config/settings_backend.py`, u. a. `InMemoryBackend`). Die **GUI** bietet einen Vollbild-Dialog mit **acht** linken Kategorien (`app/gui/domains/settings/navigation.py`, `settings_workspace.py`).

## 2. Rollenmatrix

| Rolle | Nutzung |
|-------|---------|
| **Fachanwender** | Sidebar → Settings; Kategorien durchklicken; Änderungen werden über die Panels gespeichert (`save()` auf `AppSettings`). |
| **Admin** | QSettings-Organisation `OllamaChat` / `LinuxDesktopChat` (siehe Hilfe `help/settings/settings_overview.md`); Backup der SQLite-/QSettings-Daten. |
| **Entwickler** | Keys in `AppSettings.load`/`save`; `register_settings_category_widget`, `register_settings_category`. |
| **Business** | „Konfiguration der Desktop-App“ ohne technische Schlüsselnamen-Pflicht. |

## 3. Prozesssicht

```
┌────────────────────────────────────────┐
│ User öffnet SettingsScreen              │
│ → SettingsWorkspace                     │
│   Links: SettingsNavigation (Kategorien) │
│   Mitte: Category-Widget (Stack)        │
│   Rechts: optional SettingsHelpPanel     │
└─────────────────┬──────────────────────┘
                  ▼
┌────────────────────────────────────────┐
│ Category-Panel liest/schreibt           │
│ get_infrastructure().settings           │
│ (AppSettings) → backend.setValue        │
└────────────────────────────────────────┘
```

**Legacy-Mapping:** `SettingsScreen.show_workspace` mappt alte IDs auf neue Kategorie-IDs (`app/gui/domains/settings/settings_screen.py`, `_WORKSPACE_TO_CATEGORY`).

## 4. Interaktionssicht

### 4.1 Acht Kategorien (IDs und UI-Titel)

Aus `DEFAULT_CATEGORIES` in `app/gui/domains/settings/navigation.py`, Widgets aus `_category_factories` in `settings_workspace.py`:

| ID | Titel (UI) | Widget-Klasse |
|----|-------------|---------------|
| `settings_application` | Application | `ApplicationCategory` |
| `settings_appearance` | Appearance | `AppearanceCategory` |
| `settings_ai_models` | AI / Models | `AIModelsCategory` |
| `settings_data` | Data | `DataCategory` |
| `settings_privacy` | Privacy | `PrivacyCategory` |
| `settings_advanced` | Advanced | `AdvancedCategory` |
| `settings_project` | Project | `ProjectCategory` |
| `settings_workspace` | Workspace | `WorkspaceCategory` |

**Hinweis:** Die generierte `docs/SYSTEM_MAP.md` kann unter Settings andere Workspace-Namen listen; die **Navigation + Registry im Code** oben sind die referenzierte Wahrheit für die **8** Kategorien.

### 4.2 Erweiterung (API)

- `register_settings_category_widget(category_id, widget_class)` — `settings_workspace.py`
- `register_settings_category(category_id, title, icon_name)` — `navigation.py`

### 4.3 Relevante Keys (Auszug aus `AppSettings`)

- Allgemein: `theme`, `theme_id`, `model`, `temperature`, `max_tokens`, `think_mode`, …
- Routing: `auto_routing`, `cloud_escalation`, `cloud_via_local`, `default_role`, `ollama_api_key`, …
- RAG: `rag_enabled`, `rag_space`, `rag_top_k`, `self_improving_enabled`, `chat_mode`, …
- Prompts: `prompt_storage_type`, `prompt_directory`, `prompt_confirm_delete`
- Chat: `chat_streaming_enabled`, `chat_context_mode`, `chat_context_detail_level`, `chat_context_include_*`, `chat_context_profile_enabled`, `chat_context_profile`
- Debug: `debug_panel_enabled`, `context_debug_enabled`, `chat_guard_ml_enabled`

Vollständige Liste: Methoden `load` und `save` in `app/core/config/settings.py`.

## 5. Fehler- / Eskalationssicht

| Problem | Ursache |
|---------|---------|
| Einstellung greift nicht | Höherpriore Runtime-Policy (Kontext) oder falscher Key; Backend nicht gespeichert. |
| Nur Context Mode sichtbar, Rest nicht | `chat_context_detail_level` / Includes / Profil haben **keine** separaten Felder in `app/gui/domains/settings/` (nur `chat_context_mode` in `AdvancedSettingsPanel`). |
| Falsche Kategorie nach Deep-Link | Alte `workspace_id`; Mapping in `settings_screen.py` prüfen. |

## 6. Wissenssicht

| Begriff | Ort |
|---------|-----|
| `AppSettings` | `app/core/config/settings.py` |
| `SettingsBackend`, `InMemoryBackend` | `app/core/config/settings_backend.py` |
| `SettingsWorkspace`, `_category_factories` | `app/gui/domains/settings/settings_workspace.py` |
| `SettingsNavigation`, `DEFAULT_CATEGORIES` | `app/gui/domains/settings/navigation.py` |
| `SettingsScreen` | `app/gui/domains/settings/settings_screen.py` |

## 7. Perspektivwechsel

| Perspektive | Fokus |
|-------------|--------|
| **User** | Acht Kategorien; Advanced für Kontextmodus und Debug-Checkboxen. |
| **Admin** | Persistenzpfade, Rechte auf Prompt-Verzeichnis, ChromaDB-Ort (RAG). |
| **Dev** | Neue Keys immer in `load`/`save`; Panel-Bindings; Tests mit `InMemoryBackend`. |
