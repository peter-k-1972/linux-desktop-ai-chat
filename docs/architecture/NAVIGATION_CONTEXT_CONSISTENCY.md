# Kontext-Navigation: Konsistenz mit Feature-/Edition-Filter

## Zweck

Neben Sidebar, `nav.*`-Commands und den bereits gefilterten Palette-Einträgen (`feature.open.*`, `nav.area.*`) nutzen **Breadcrumbs**, die **Runtime-/Debug-Subnav** und der **Theme-Visualizer** in der Palette dieselbe **erlaubte Nav-Menge** wie die Hauptnavigation.

## Datenquelle (eine Stelle)

| API | Modul | Bedeutung |
|-----|--------|-----------|
| `allowed_navigation_entry_ids()` | `app/gui/navigation/nav_context.py` | Delegiert zu `collect_active_navigation_entry_ids(get_feature_registry())`; `None` = kein Filter |
| `is_nav_entry_allowed(entry_id)` | `nav_context` | Prüfung für Workspace-/Entry-IDs |
| `is_area_visible_in_nav(area_id)` | `nav_context` | Mindestens ein erlaubter `NavEntry` mit dieser `area` |
| `collect_active_navigation_entry_ids` | `app/features/nav_binding.py` | Union der `FeatureDescriptor.navigation_entries` (Quelle der Wahrheit) |

`sidebar_config` und `palette_loader` verwenden für den Default-Pfad ebenfalls `allowed_navigation_entry_ids()` (bzw. weiterhin optional explizit `feature_registry=` in `get_sidebar_sections`).

## Was jetzt feature-/edition-aware ist

- **Breadcrumbs** (`BreadcrumbManager`): Bereiche und Workspaces nur, wenn die zugehörige Nav-Entry-ID aktiv ist; inaktiver Bereich → ein neutraler Krümel („App“); inaktiver Workspace bei sonst sichtbarem Bereich → Fallback auf **nur** den Bereichs-Krümel.
- **RuntimeDebugNav**: Listeneinträge nur für IDs in der erlaubten Menge; **Theme Visualizer**-Zeile nur bei DevTools **und** wenn `nav.rd_theme_visualizer` in den aktiven GUI-Kommandos liegt (wie in der Shell).
- **Palette `devtools.theme_visualizer`**: Registrierung nur, wenn dieselbe Bedingung wie oben erfüllt ist (kein exponierter Runtime-Pfad ohne Runtime-Feature).

## Fail-Soft bei „stalem“ Kontext

- **Versteckter Bereich** (`set_area`): Pfad = ein Element mit `id="_nav_fallback"`, Titel aus `neutral_breadcrumb_fallback_title()` (derzeit „App“), Aktion `DETAIL` (kein Navigationsziel).
- **Versteckter Workspace** (`set_workspace` / `set_path_with_detail`): wenn der **Bereich** noch sichtbar ist → `set_area(area_id)`; sonst neutraler Fallback.
- **Projekt-Kontext-Zeile** (Projektname als erster Krümel): nur wenn `command_center` in der erlaubten Nav-Menge liegt.

Kein Crash; keine leeren oder kaputten Qt-Strukturen.

## Bewusste Rest-Altpfade

- **Hilfe-**, **System-** und **Rebuild**-Palette-Befehle bleiben ungefiltert (kein Produktbereich).
- **`nav.workspace_graph`** bleibt global (zeigt bereits gefilterte Sidebar-Daten).
- **Help-Artikel** in der Palette (`help.open.*`) sind dokumentationsbezogen, nicht Nav-Registry-gespiegelt.
- **`register_navigation` auf FeatureRegistraren** weiterhin meist no-op; Metadaten bleiben in den Deskriptoren.

## Nächste Schritte (optional)

- Weitere kontextspezifische Listen (z. B. einzelne Domänen-Subnavs) an `allowed_navigation_entry_ids` anbinden, falls sie wieder ungefilterte IDs hardcoden.
- Breadcrumb-Fallback-Titel lokalisierbar machen.

## Verweise

- [NAVIGATION_FEATURE_BINDING.md](NAVIGATION_FEATURE_BINDING.md)
- [BOOTSTRAP_EDITION_ACTIVATION.md](BOOTSTRAP_EDITION_ACTIVATION.md)
- `app/gui/breadcrumbs/manager.py`, `app/gui/domains/runtime_debug/runtime_debug_nav.py`
