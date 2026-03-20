# Registry Governance – Abschlussreport

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Status:** Registry-Governance aktiv

---

## 1. Gefundene Registries

| Registry | Pfad | Typ | Governance-relevant |
|----------|------|-----|---------------------|
| Navigation Registry | app/core/navigation/navigation_registry.py | Statisch | Ja |
| Screen Registry | app/gui/workspace/screen_registry.py | Dynamisch | Ja |
| Model Registry | app/core/models/registry.py | Statisch | Ja |
| Command Registry (Core) | app/core/command_registry.py | Klassen-Registry | Ja |
| Command Registry (GUI) | app/gui/commands/registry.py | Klassen-Registry | Ja |
| Agent Registry | app/agents/agent_registry.py | Cache/Repository | Ja |
| Icon Registry | app/gui/icons/registry.py | Konstanten | Nein (UI-Detail) |
| Theme Registry | app/gui/themes/registry.py | Dynamisch | Nein |
| Settings Category | app/gui/domains/settings/navigation.py | Dict | Nein |

**Keine formale Registry:** Provider (implizit über ModelRegistry.provider), Tools (keine Registry).

---

## 2. Erkannte Risiken

| Risiko | Bewertung | Maßnahme |
|--------|-----------|----------|
| Screen existiert nicht | Niedrig | Bootstrap registriert nur importierbare Klassen; Guards prüfen |
| NavEntry ohne Screen | Niedrig | test_navigation_registry_screens_exist |
| Command ohne Handler | Niedrig | test_gui_command_registry_commands_have_handlers, test_palette_command_registry_commands_have_handlers |
| Ungültige ModelEntry.provider | Niedrig | test_model_registry_provider_strings_valid |
| Doppelte model_ids | Niedrig | test_model_registry_ids_unique |
| Core-Registry importiert gui/services/providers | Niedrig | test_core_registries_do_not_import_gui_services_providers |
| AgentRegistry importiert gui/services/providers | Niedrig | test_agent_registry_does_not_import_gui_services_providers |

---

## 3. Implementierte Guards

| Guard | Datei | Regel |
|-------|-------|-------|
| test_navigation_registry_screens_exist | test_registry_governance_guards.py | GUI_SCREEN_WORKSPACE_MAP area_ids haben Screens in Bootstrap |
| test_registered_screens_inherit_base_screen | test_registry_governance_guards.py | Screen-Klassen erben von BaseScreen |
| test_gui_command_registry_commands_have_handlers | test_registry_governance_guards.py | GUI-Commands haben callback |
| test_palette_command_registry_commands_have_handlers | test_registry_governance_guards.py | PaletteCommands haben callback |
| test_model_registry_provider_strings_valid | test_registry_governance_guards.py | ModelEntry.provider ∈ {"local", "ollama_cloud"} |
| test_model_registry_ids_unique | test_registry_governance_guards.py | Keine doppelten model_ids |
| test_agent_registry_importable_and_consistent | test_registry_governance_guards.py | AgentRegistry und AgentService funktionieren |
| test_model_provider_strings_resolvable | test_registry_governance_guards.py | Provider-Strings auflösbar |
| test_core_registries_do_not_import_gui_services_providers | test_registry_governance_guards.py | Core-Registries ohne gui/services/providers |
| test_agent_registry_does_not_import_gui_services_providers | test_registry_governance_guards.py | AgentRegistry ohne gui/services/providers |

---

## 4. Gefixte Inkonsistenzen

- **Keine** – Alle Registries waren bereits konsistent.
- **Keine** – Import-Drift war nicht vorhanden (Core-Registries importieren nur core).

---

## 5. Verbleibende Risiken

| Risiko | Bewertung | Maßnahme |
|--------|-----------|----------|
| Tool Registry (fehlt) | Niedrig | ToolRegistryPanel zeigt Demo-Daten; keine formale Registry. Kein Guard nötig. |
| Provider Registry (implizit) | Niedrig | ModelRegistry.provider-Strings werden geprüft; Provider sind fest verdrahtet. |
| Zwei Command-Registries (core + gui) | Architektur | Bewusst: Core für Command Palette (PaletteCommand), GUI für ältere Commands (Command). Beide werden geprüft. |

---

## 6. Konfiguration

- **arch_guard_config.py:** `KNOWN_MODEL_PROVIDER_STRINGS = {"local", "ollama_cloud"}`

---

## 7. Validierung

```
54 architecture tests passed (inkl. 10 Registry-Guards)
```

---

## 8. Freigabe

**Registry-Governance ist aktiv.**

- 10 neue Guards in `test_registry_governance_guards.py`
- Policy dokumentiert in `docs/architecture/REGISTRY_GOVERNANCE_POLICY.md`
- Analyse in `docs/architecture/REGISTRY_GOVERNANCE_ANALYSIS.md`
- Keine funktionalen Änderungen, keine UI-Änderungen
