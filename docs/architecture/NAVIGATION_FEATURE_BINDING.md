# Navigation ↔ Features / Editionen

## Zweck

Die **sichtbare** Sidebar-Struktur und die **nav.\***-Hauptbefehle (sowie relevante Palette-„Open …“-Einträge) folgen der **aktiven Feature-Menge** aus der `FeatureRegistry` (Edition → `apply_active_feature_mask` → enabled + `is_available()`).

Die zentrale **`navigation_registry`** (`app/core/navigation/navigation_registry.py`) bleibt die **kanonische Liste** von IDs, Titeln und Bereichen; es gibt **keinen** Ersatz dieser Registry, nur eine **Filter-Schicht**.

## Datenfluss

1. **Quelle der Aktivierung:** `FeatureDescriptor.navigation_entries` und `FeatureDescriptor.commands` pro `FeatureRegistrar` (eingebaut: `app/gui/registration/feature_builtins.py`).
2. **Aggregation:** `app/features/nav_binding.py`
   - `collect_active_navigation_entry_ids(registry)` — Union der `navigation_entries`
   - `collect_active_gui_command_ids(registry)` — Union der `commands` (für `nav.*` im Command-Bootstrap)
3. **GUI-Einstieg:** `app/gui/navigation/nav_context.py` — `allowed_navigation_entry_ids()` usw. (eine Stelle für Sidebar, Palette, Breadcrumbs, Subnav; siehe [NAVIGATION_CONTEXT_CONSISTENCY.md](NAVIGATION_CONTEXT_CONSISTENCY.md))
4. **Konsumenten:**
   - `app/gui/navigation/sidebar_config.get_sidebar_sections()` — filtert Registry-Einträge; leere Sektionen werden ausgelassen
   - `app/gui/commands/bootstrap.register_commands()` — `_register_nav_command` pro `nav.*`
   - `app/gui/commands/palette_loader` — `load_feature_commands` / `load_area_commands` / Theme-Visualizer-Gate
   - `app/gui/breadcrumbs/manager.py` — Breadcrumb-Pfade
   - `app/gui/domains/runtime_debug/runtime_debug_nav.py` — Runtime-Subnav

## Ohne globale FeatureRegistry

Ist `get_feature_registry()` **None** (Legacy/Tests), verhalten sich Sidebar, Nav-Commands, Breadcrumbs und Runtime-Subnav wie zuvor (**kein** Filter).

## Operations-Hub und Capabilities

Der **Operations-Hub** deklariert nur **gemeinsame** Operations-Workspaces (Projekte, Chat, Agent Tasks, Deployment, Betrieb). **Knowledge**, **Prompt Studio** und **Workflows** hängen an den Capability-Features `knowledge_rag`, `prompt_studio`, `workflow_automation`. So bleiben Navigation und (über die gleichen Deskriptoren) **Editionen** wie `minimal` / `standard` konsistent.

## Unavailable (fail-soft)

Feature **enabled**, aber `is_available() == False`: **kein** Beitrag zu Nav-IDs oder Nav-Commands; **Warnung** im Log (siehe `nav_binding`).

## Bewusst nicht oder nur teilweise feature-gekoppelt

| Bereich | Stand |
|--------|--------|
| **Workspace Graph** | Nutzt gefilterte `get_sidebar_sections()` — gleiche Datenbasis wie Sidebar |
| **Breadcrumbs / Runtime-Subnav** | An `nav_context` / erlaubte Nav-Menge angebunden — siehe [NAVIGATION_CONTEXT_CONSISTENCY.md](NAVIGATION_CONTEXT_CONSISTENCY.md) |
| **Hilfe / System-Palette-Commands** | Unverändert (kein Produkt-Schnitt) |

## Nächste Schritte

- `register_navigation` auf den Registraren nutzen, wenn Metadaten aus den Deskriptoren in dynamischere Registrierung wandern sollen
- Weitere Domänen-Subnavs prüfen, falls wieder hartcodierte Workspace-Listen entstehen

## Verweise

- [BOOTSTRAP_EDITION_ACTIVATION.md](BOOTSTRAP_EDITION_ACTIVATION.md)
- [FEATURE_REGISTRAR_ARCHITECTURE.md](FEATURE_REGISTRAR_ARCHITECTURE.md)
- `app/features/nav_binding.py`
