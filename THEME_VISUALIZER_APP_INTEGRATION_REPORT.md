# Theme Visualizer — App-Integrationsbericht

## Neue Dateien

| Datei | Rolle |
|-------|--------|
| `app/gui/devtools/devtools_visibility.py` | `is_theme_visualizer_available()` anhand `LINUX_DESKTOP_CHAT_DEVTOOLS` |
| `app/gui/devtools/theme_visualizer_launcher.py` | Single-Instance-Öffnen, `WA_DeleteOnClose`, Fokus bei erneutem Aufruf |
| `app/gui/devtools/theme_visualizer_workspace.py` | Runtime/Debug-Workspace mit Button zum Öffnen des Fensters |
| `app/gui/devtools/theme_visualizer_window.py` | Re-Export der Implementierung aus `app.devtools` (klarer GUI-Import-Pfad) |
| `tests/unit/gui/test_theme_visualizer_integration.py` | Sichtbarkeit, Launcher, eingebettetes Theme vs. global |
| `docs/devtools/DEVTOOLS_OVERVIEW.md` | Kurzüberblick Devtools + Env-Steuerung |

## Geänderte Dateien

| Datei | Änderung |
|-------|----------|
| `app/devtools/theme_visualizer_window.py` | `embed_in_app`-Modus: `_EmbeddedPreviewContext` (lokales `ThemeRegistry` + Fenster-QSS) vs. `_ManagerPreviewContext` (Singleton); Combo-Sync mit App-Theme |
| `app/devtools/theme_preview_widgets.py` | `SupportsThemeColors`-Protocol statt fester `ThemeManager`-Typ |
| `app/gui/domains/runtime_debug/runtime_debug_nav.py` | Dynamische Workspace-Liste mit optionalem `rd_theme_visualizer` |
| `app/gui/domains/runtime_debug/runtime_debug_screen.py` | Optionaler Stack-Eintrag `ThemeVisualizerEntryWorkspace` |
| `app/gui/icons/nav_mapping.py` | Icon `rd_theme_visualizer` → `APPEARANCE` |
| `app/gui/commands/bootstrap.py` | `_maybe_register_theme_visualizer_nav_command` (nur bei Env) |
| `app/gui/commands/palette_loader.py` | `load_theme_visualizer_palette_command` + Aufruf aus `load_all_palette_commands` |
| `docs/devtools/THEME_VISUALIZER.md` | Abschnitt Shell-Integration, Sandbox-Verhalten |

## Gewählter Einstiegspunkt

- **Primär:** Bereich **Runtime / Debug** (gleiche Kategorie wie Markdown-Demo), Eintrag nur bei `LINUX_DESKTOP_CHAT_DEVTOOLS=1`.
- **Sekundär:** **Command Palette** (`devtools.theme_visualizer`), ebenfalls gated.
- **Ergänzend:** Gui-`CommandRegistry`-Eintrag `nav.rd_theme_visualizer` für konsistente Navigation mit anderen `nav.rd_*`-Befehlen (nur bei Env).

Kein zusätzlicher Top-Bar-Button — vermeidet Produktiv-Oberflächen-Noise.

## Sichtbarkeitslogik

- `LINUX_DESKTOP_CHAT_DEVTOOLS` explizit positiv → sichtbar.
- Unset oder negativ → keine Nav-Einträge, kein Palette-Befehl, kein `nav.rd_theme_visualizer`.

## Fenster- / Lifecycle-Konzept

- Modulglobale Referenz `_instance` im Launcher.
- Beim ersten Öffnen: `ThemeVisualizerWindow(embed_in_app=True)`, `Window`-Flag, `WA_DeleteOnClose`, `destroyed` → Referenz `None`.
- Zweiter Aufruf: `show` / `raise_` / `activateWindow` auf bestehender Instanz.

## Theme-Kopplung (Sandbox)

- **Eingebettet:** `load_stylesheet(theme)` nur auf dem Visualizer-`QWidget`; Token-Daten aus `ThemeDefinition.get_tokens_dict()` — **ohne** `ThemeManager.set_theme`.
- **CLI (`tools/theme_visualizer.py`):** unverändert global über `ThemeManager`.

## Testergebnis

```bash
pytest tests/tools/test_theme_visualizer_smoke.py tests/unit/gui/test_theme_visualizer_integration.py -q
```

→ **8 passed** (Stand: lokaler Lauf nach Integration).

## Bekannte Restrisiken

- Andere Tests oder Prozesse, die `LINUX_DESKTOP_CHAT_DEVTOOLS` setzen, aktivieren die Einträge global in derselben Umgebung.
- Ein sehr großes `setStyleSheet` auf dem Visualizer-Fenster kann bei Qt-Grenzfällen mit vererbten Styles interagieren; bisher keine Sonderfälle gemeldet.
