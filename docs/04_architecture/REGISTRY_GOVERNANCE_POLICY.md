# Registry Governance Policy

**Projekt:** Linux Desktop Chat  
**Referenz:** `docs/architecture/REGISTRY_GOVERNANCE_ANALYSIS.md`  
**Tests:** `tests/architecture/test_registry_governance_guards.py`

---

## 1. Ziel

Runtime-Registries konsistent halten: keine Drift zwischen Registry-Einträgen, Services und Implementierungen.

---

## 2. Erlaubte Registrierungsorte

| Registry | Registrierungsort | Wer registriert |
|----------|-------------------|-----------------|
| Navigation Registry | `app/core/navigation/navigation_registry.py` | _build_registry() |
| Screen Registry | `app/gui/bootstrap.py` (Delegation nach `app/gui/registration/screen_registrar.py`) | `register_all_screens()` |
| Model Registry | `app/core/models/registry.py` | _load_defaults(), register() |
| Command Registry (Core) | `app/gui/commands/palette_loader.py` | `load_all_palette_commands()` (delegiert an `load_area_commands()`, `load_feature_commands()`, `load_help_commands()`, `load_system_commands()` u. a.) |
| Command Registry (GUI) | `app/gui/commands/bootstrap.py` | register_commands() |
| Agent Registry | `app/agents/agent_registry.py` | `register_profile()` (nach CRUD), Seed über `app/agents/seed_agents.py` (`ensure_seed_agents()`) |

---

## 3. Wer registrieren darf / darf NICHT

### 3.1 Dürfen registrieren

- **Bootstrap-Module:** gui/bootstrap, gui/commands/bootstrap, gui/commands/palette_loader
- **Core-Registries:** Eigene _load_defaults() / _build_registry()
- **Agent-Registry:** Agent CRUD-Flow, `ensure_seed_agents()`

### 3.2 Dürfen NICHT registrieren

- Beliebige Domain-Panels ohne zentrale Bootstrap-Integration
- Services (außer Agent register_profile nach CRUD)
- Provider, Tools, RAG, Prompts (keine direkte Registry-Registrierung außer definierten Orten)

---

## 4. Importregeln

| Registry-Modul | Darf importieren | Darf NICHT importieren |
|----------------|------------------|-------------------------|
| core/navigation/navigation_registry | core | gui, services, providers |
| core/models/registry | core | gui, services, providers |
| core/command_registry | stdlib | app.* |
| agents/agent_registry | agents | gui, services, providers |
| gui/workspace/screen_registry | gui, PySide6 | services, providers |
| gui/commands/registry | gui | — |

---

## 5. Lifecycle-Regeln

- **Navigation Registry:** Statisch; Änderungen nur in navigation_registry.py
- **Screen Registry:** Einmal bei Bootstrap; `register_all_screens()` vor `WorkspaceHost.register_from_registry()`
- **Model Registry:** Statisch; Änderungen in `registry._load_defaults()`
- **Command Registry:** Bei Bootstrap (`register_commands()`, `load_all_palette_commands()`)
- **Agent Registry:** Lazy; `refresh()` bei Bedarf; `register_profile()` nach Create/Update

---

## 6. Konsistenzregeln

### 6.1 Navigation ↔ Screen

- Jeder NavEntry.area mit workspace=None: Es existiert ein Screen für area.
- Jeder NavEntry mit workspace: Der Screen unterstützt show_workspace(workspace_id).
- ScreenRegistry enthält alle area_ids aus GUI_SCREEN_WORKSPACE_MAP.

### 6.2 Command Registry

- Jeder registrierte Command hat einen gültigen callback (oder dokumentierte Ausnahme).
- Command-IDs sind eindeutig.

### 6.3 Agent Registry

- AgentRegistry liest aus AgentRepository; AgentService nutzt dasselbe Repository.
- Seed-Agenten sind nach `ensure_seed_agents()` in `AgentRepository`.

### 6.4 Model Registry

- ModelEntry.provider ∈ {"local", "ollama_cloud"} (bekannte Provider-Strings).
- Keine doppelten model_ids.

### 6.5 Provider (implizit)

- ModelRegistry.provider-Strings sind auflösbar (local → LocalOllamaProvider, ollama_cloud → CloudOllamaProvider).

---

## 7. Ausnahmen

- Keine stillen Ausnahmen
- Neue Registrierungsorte nur nach Architektur-Review
