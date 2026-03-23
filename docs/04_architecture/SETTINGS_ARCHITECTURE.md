# Settings – Architektur (aktuell)

Stand: abgeglichen mit `app/gui/domains/settings/settings_workspace.py` und `navigation.py`.

## Überblick

Der Settings-Bereich ist ein **Vollbild-Workspace**: linke Kategorienliste, zentraler Inhalt pro Kategorie, optional rechte Hilfe (`SettingsHelpPanel`).

## Kategorien (fest registriert)

Reihenfolge und IDs entsprechen `DEFAULT_CATEGORIES` in `app/gui/domains/settings/navigation.py`:

| ID | Anzeigename (UI) |
|----|------------------|
| `settings_application` | Application |
| `settings_appearance` | Appearance |
| `settings_ai_models` | AI / Models |
| `settings_data` | Data |
| `settings_privacy` | Privacy |
| `settings_advanced` | Advanced |
| `settings_project` | Project |
| `settings_workspace` | Workspace |

Widget-Klassen pro ID: `_category_factories` in `settings_workspace.py` (`ApplicationCategory`, `AppearanceCategory`, `AIModelsCategory`, `DataCategory`, `PrivacyCategory`, `AdvancedCategory`, `ProjectCategory`, `WorkspaceCategory`).

## Erweiterung

- **Neues Panel:** `register_settings_category_widget(category_id, QWidget-Klasse)` in `settings_workspace.py`.  
- **Navigationseintrag:** `register_settings_category(category_id, title, icon_name)` in `navigation.py`.

## Screen-Integration

`SettingsScreen` (`settings_screen.py`) hostet `SettingsWorkspace` und mappt **Legacy-Workspace-IDs** auf Kategorie-IDs (`_WORKSPACE_TO_CATEGORY`), damit Deep-Links aus älterer Navigation weiter funktionieren.

## Persistenz

Inhaltliche Werte kommen aus `AppSettings` (`app/core/config/settings.py`) über das injizierte `SettingsBackend` (in der GUI typischerweise Qt/QSettings). Die Settings-UI liest/schreibt über die jeweiligen Category-Panels.

## Verwandte Dokumentation

- [`docs/FEATURES/settings.md`](../FEATURES/settings.md)  
- [`docs/USER_GUIDE.md`](../USER_GUIDE.md) § Settings  
- [`help/settings/settings_overview.md`](../../help/settings/settings_overview.md)
