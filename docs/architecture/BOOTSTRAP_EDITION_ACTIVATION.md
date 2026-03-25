# Bootstrap: Edition-Aktivierung (erster Schritt)

## Zweck

Die laufende Desktop-App wählt beim Start eine **Edition**; daraus wird die **aktive Feature-Menge** für die `FeatureRegistry` abgeleitet. Nur **aktive und verfügbare** `FeatureRegistrar` registrieren Screens.

**Noch nicht:** Release-Splitting, `pyproject`-extras, User-Edition-Switcher in der UI.

**Navigation:** Sidebar, `nav.*`-Commands und zugehörige Palette-Einträge sind **feature-gefiltert** — siehe [NAVIGATION_FEATURE_BINDING.md](NAVIGATION_FEATURE_BINDING.md).

## Aktive Edition bestimmen

Reihenfolge (erste gültige gewinnt):

1. CLI: ``python run_gui_shell.py --edition standard``
2. Umgebung: ``LDC_EDITION=minimal``
3. Default: **``full``** — entspricht der bisherigen vollen Feature-Fläche (kein versehentliches „Amputieren“).

Unbekannte Namen: **Warnung** im Log, dann nächste Quelle bzw. Default — **kein** Prozess-Abbruch.

## Von Edition zu Features

1. ``resolve_active_edition_name(...)`` → Edition-Name (String).
2. ``build_feature_registry_for_edition(name)`` lädt ``EditionDescriptor``, bildet ``effective_edition_features`` (``enabled_features \\ disabled_features``).
3. Alle eingebauten Registrare werden registriert; ``apply_active_feature_mask`` setzt ``enabled`` pro Feature-Name exakt nach dieser Menge.

## Screens

``register_all_screens()`` → ``apply_feature_screen_registrars``: nur Registrare mit ``enabled`` und ``is_available()``.

## Unavailable (fail-soft)

Ist ein Feature laut Edition **aktiv**, der Registrar liefert aber ``is_available() == False``: **Warnung** im Log, ``register_screens`` wird übersprungen — **kein** Crash.

## Navigation

Die **zentrale** `navigation_registry` bleibt die ID-Quelle; **Sichtbarkeit** leitet sich von aktiven Features ab ([NAVIGATION_FEATURE_BINDING.md](NAVIGATION_FEATURE_BINDING.md)). Verbleibende Drift (z. B. Breadcrumbs) ist dokumentiert.

## Warum nur dieser Schritt

- Minimale invasive Kopplung: ein Pfad in ``run_gui_shell`` + bestehende Registry-Maske.
- Produktiv-Default **full** bleibt vertraut.
- Später: QSettings/UX für Edition, Manifest-Dateien, CI-Matrix, pip-extras.

## Verweise

- [EDITION_AND_DEPENDENCY_MANIFESTS.md](EDITION_AND_DEPENDENCY_MANIFESTS.md)
- [FEATURE_REGISTRAR_ARCHITECTURE.md](FEATURE_REGISTRAR_ARCHITECTURE.md)
- ``app/features/edition_resolution.py``
