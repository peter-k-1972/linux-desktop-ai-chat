# Registry Governance Analysis

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16

---

## 1. Gefundene Registries

### 1.1 Navigation Registry

| Attribut | Wert |
|----------|------|
| **Pfad** | `app/core/navigation/navigation_registry.py` |
| **Typ** | Statische Definition (NavEntry, NavSectionDef) |
| **Lookup** | `get_all_entries()`, `get_entry(id)`, `get_sidebar_sections()` |
| **Registrierung** | `_build_registry()` – hartcodierte Liste |
| **Nutzer** | Sidebar, Command Palette, Workspace Graph, palette_loader |
| **Imports** | core.navigation (nav_areas, icon_ids) – keine gui, services, providers |

### 1.2 Screen Registry

| Attribut | Wert |
|----------|------|
| **Pfad** | `app/gui/workspace/screen_registry.py` |
| **Typ** | Dynamische Registry (area_id → Factory) |
| **Lookup** | `get_factory(area_id)`, `create_screen(area_id)`, `list_areas()` |
| **Registrierung** | `register(area_id, factory, title)` – via `app/gui/bootstrap.register_all_screens()` |
| **Nutzer** | WorkspaceHost |
| **Imports** | PySide6.QtWidgets – GUI-Modul |

### 1.3 Model Registry

| Attribut | Wert |
|----------|------|
| **Pfad** | `app/core/models/registry.py` |
| **Typ** | Statische Registry (ModelEntry) |
| **Lookup** | `get(model_id)`, `get_models_for_role()`, `list_all()` |
| **Registrierung** | `register(entry)` – `_load_defaults()` |
| **Nutzer** | ModelOrchestrator, EscalationManager, GUI (model_settings, settings_dialog) |
| **Imports** | core.models.roles – keine gui, services, providers |
| **Provider-Referenz** | ModelEntry.provider: "local" | "ollama_cloud" |

### 1.4 Command Registry (Core)

| Attribut | Wert |
|----------|------|
| **Pfad** | `app/core/command_registry.py` |
| **Typ** | Klassen-Registry (PaletteCommand) |
| **Lookup** | `get(id)`, `search(query)`, `all_commands()`, `execute(id)` |
| **Registrierung** | `CommandRegistry.register(PaletteCommand)` |
| **Nutzer** | palette_loader (load_all_palette_commands, load_feature_commands) |
| **Imports** | Keine app.* – nur stdlib |

### 1.5 Command Registry (GUI)

| Attribut | Wert |
|----------|------|
| **Pfad** | `app/gui/commands/registry.py` |
| **Typ** | Klassen-Registry (Command) |
| **Lookup** | `get(id)`, `search(query)`, `all_commands()`, `execute(id)` |
| **Registrierung** | `CommandRegistry.register(Command)` – via `gui/commands/bootstrap.register_commands()` |
| **Nutzer** | Command Palette (ShellMainWindow) |
| **Imports** | app.gui.commands.model |

### 1.6 Agent Registry

| Attribut | Wert |
|----------|------|
| **Pfad** | `app/agents/agent_registry.py` |
| **Typ** | Cache über AgentRepository (DB) |
| **Lookup** | `get(id)`, `get_by_slug()`, `get_by_name()`, `list_active()`, `list_all()` |
| **Registrierung** | `register_profile()` nach Create/Update; Seed via `seed_agents.ensure_seed_agents()` |
| **Nutzer** | AgentService (services + agents), chat_widget, agent_manager_panel |
| **Imports** | agents (agent_profile, agent_repository, departments) – keine gui, services |

### 1.7 Icon Registry

| Attribut | Wert |
|----------|------|
| **Pfad** | `app/gui/icons/registry.py` |
| **Typ** | Konstanten (Icon-IDs) |
| **Lookup** | IconRegistry.CHAT, IconRegistry.ADD, … |
| **Registrierung** | Statisch |
| **Nutzer** | GUI-Komponenten |

### 1.8 Theme Registry

| Attribut | Wert |
|----------|------|
| **Pfad** | `app/gui/themes/registry.py` |
| **Typ** | Dynamische Registry (ThemeDefinition) |
| **Lookup** | `get(id)`, `list_themes()` |
| **Registrierung** | `register(theme)` |
| **Nutzer** | ThemeManager |

### 1.9 Settings Category Registry

| Attribut | Wert |
|----------|------|
| **Pfad** | `app/gui/domains/settings/navigation.py` |
| **Typ** | Dict (category_id → (title, icon)) |
| **Registrierung** | `register_settings_category()` |
| **Nutzer** | SettingsWorkspace |

---

## 2. Keine formale Registry

| Komponente | Beschreibung |
|------------|--------------|
| **Provider** | Keine Provider-Registry. ModelOrchestrator nutzt LocalOllamaProvider, CloudOllamaProvider direkt. ModelRegistry.provider = "local" \| "ollama_cloud". |
| **Tools** | Keine Tool-Registry. app/tools exportiert FileSystemTools, web_search. ToolRegistryPanel zeigt Demo-Daten. |

---

## 3. Drift-Risiken

| Risiko | Registry | Beschreibung |
|--------|-----------|--------------|
| Screen existiert nicht | Screen Registry | Bootstrap registriert area_id → Factory; Factory könnte auf nicht existierende Klasse verweisen |
| NavEntry ohne Screen | Navigation | NavEntry.area/workspace referenziert Screen, der nicht in ScreenRegistry |
| Command ohne Handler | Command Registry | PaletteCommand/Command mit callback=None |
| Agent in Registry, Service kennt ihn nicht | Agent Registry | AgentRegistry liest aus AgentRepository; AgentService nutzt dasselbe Repository – konsistent |
| Modell in Registry, Provider liefert nicht | Model Registry | ModelEntry.provider = "local" \| "ollama_cloud"; Provider sind fest verdrahtet |
| Doppelte IDs | Alle | Keine doppelten Keys/IDs |

---

## 4. Import-Drift (Registries)

| Registry | Importiert | Bewertung |
|----------|------------|-----------|
| navigation_registry | core | OK |
| models/registry | core | OK |
| command_registry (core) | — | OK |
| agent_registry | agents | OK |
| screen_registry | PySide6 | GUI-Modul, OK |
| gui/commands/registry | gui | OK (GUI-intern) |

**Keine Registries importieren:** gui (außer screen_registry, gui/commands), services, konkrete Provider.
