# Feature-Registrar-Architektur (Phase 2)

## Kernentscheidung: Feature ≠ Paket

- **Python-Pakete** (`app/chat`, `app/rag`, …) liefern Code und Datenstrukturen. Sie kennen **keine** Edition und kein Produkt-Manifest.
- **Features** sind die **primäre vertikale Aktivierungseinheit**: Sie beschreiben, welche Teile der Shell (Screens, später Navigation/Commands/Services) zu einer fachlichen Einheit gehören.
- **Editionen** (später) schalten **Features** an oder aus, nicht Pakete direkt.

## Rolle von `FeatureDescriptor`

Reine Metadaten in `app/features/descriptors.py`: Name, `enabled_by_default`, informelle IDs für Screens/Nav/Commands/Services, optionale Abhängigkeits-Tags. Kein Qt, kein Import von `app.gui` in den Kernmodulen unter `app/features/` (außer dokumentierter Integrationspfad über `importlib` in `builtins.py`).

## Rolle von `FeatureRegistrar`

Vertrag in `app/features/registrar.py` (`FeatureRegistrar`):

- `get_descriptor()` — stabile Feature-Identität
- `register_screens(screen_registry)` — Eintrag in die globale `ScreenRegistry`
- `register_navigation` / `register_commands` / `register_services` — weiterhin meist no-op; **Navigationssichtbarkeit** und **`nav.*`-Commands** leiten sich aktuell aus `FeatureDescriptor.navigation_entries` / `commands` ab ([NAVIGATION_FEATURE_BINDING.md](NAVIGATION_FEATURE_BINDING.md))
- `is_available()` — später für optionale Extras; bei `False` wird der Registrar aus der „enabled“-Pipeline für Registrierung ausgelassen (ohne App-Abbruch)

**Konkrete Implementierungen** mit PySide6 und `gui.domains` liegen in `app/gui/registration/feature_builtins.py` (Integrationsgrenze).

## FeatureRegistry

`app/features/registry.py`:

- `register_registrar` / `get_registrar` / `list_registrars` / `list_enabled_registrars`
- Abwärtskompatibel: `register_feature(Descriptor)` für Tests/Legacy (Deskriptor-only ohne Screens)

Bootstrap-Hilfe: `apply_feature_screen_registrars(feature_registry, screen_registry)`.

## Bootstrap / Screens / Navigation

- `run_gui_shell` setzt nach `init_infrastructure` die Default-`FeatureRegistry` (alle eingebauten Registrare).
- `app/gui/bootstrap.register_all_screens()` ruft `apply_feature_screen_registrars` auf, falls eine Registry existiert; sonst Fallback `register_all_navigation_area_screens`.
- **Navigation:** zentrale `navigation_registry` + Filter über `nav_binding` / `sidebar_config` (siehe NAVIGATION_FEATURE_BINDING). **Commands:** `commands/bootstrap` filtert `nav.*` nach Deskriptor-`commands`.

## Aktuelle Phase

- **Keine** harte Edition und **kein** Entfernen von UI.
- Alle Standard-Registrare sind `enabled_by_default=True` und `is_available() == True`.
- Zusätzliche **Capability-Registrare** (z. B. `knowledge_rag`, `prompt_studio`, `workflow_automation`) liefern **Metadaten** ohne eigenen Top-Level-Screen (Workspaces liegen im Operations-Hub).

## Migrationsprinzip

- Evolutionär: bestehende `screen_registrar`-Hilfsfunktionen werden von den FeatureRegistraren aufgerufen.
- Rückwärtskompatibel: gleiche `NavArea`-Reihenfolge wie zuvor.
- Nächste Schritte: Navigation/Commands in Registrare ziehen; Edition-Manifest filtert `enabled`; `pyproject` extras koppeln an `is_available()`.

## Verweise

- [EDITION_AND_DEPENDENCY_MANIFESTS.md](EDITION_AND_DEPENDENCY_MANIFESTS.md) — Editionen & Dependency-Gruppen (Manifest-Schicht)
- `docs/architecture/FEATURE_SYSTEM.md` — Grundlagen Phase 1
- `tests/unit/features/` — Registry und Registrar
- `tests/architecture/test_feature_system_guards.py` — Isolation `app/features`
