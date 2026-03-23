# Theme Visualizer

## Zweck

Internes **Entwicklungs- und QA-Werkzeug** zur schnellen, konsistenten Prüfung von Themes: zentrale Design-Tokens als Farbfelder, grobe Kontrast-Hinweise, Live-Wechsel zwischen registrierten Themes und eine Vorschau typischer Qt-Komponenten unter dem **echten** Stylesheet (`load_stylesheet` / `ThemeManager`).

Dies ist **kein** Produktiv-Screen für Endnutzer. Es gibt zwei Startwege:

1. **Eigenständig** (`tools/theme_visualizer.py`): kein Shell-Start nötig; Theme-Wechsel wirkt **global** über `ThemeManager` (gesamte `QApplication`).
2. **Aus der GUI-Shell** (siehe unten): nur mit `LINUX_DESKTOP_CHAT_DEVTOOLS=1`; Theme-Wechsel im Visualizer-Fenster wirkt **nur auf dieses Fenster** (Sandbox), die Shell behält ihr Theme.

## Start (CLI)

Vom Repository-Root (virtuelle Umgebung mit PySide6 aktivieren):

```bash
python tools/theme_visualizer.py
```

Alternativ mit explizitem Interpreter:

```bash
.venv/bin/python tools/theme_visualizer.py
```

## Integration in die GUI-Shell

**Sichtbarkeit:** Setze `LINUX_DESKTOP_CHAT_DEVTOOLS=1` (oder `true` / `yes` / `on`). Ohne diese Variable sind Einträge ausgeblendet (sicheres Standardverhalten).

**Einstiege:**

| Ort | Aktion |
|-----|--------|
| **Runtime / Debug** (Seitenleiste) | Eintrag **Theme Visualizer** → Kurzseite mit Button „Theme Visualizer öffnen…“ |
| **Command Palette** (Ctrl+K) | Befehl **Theme Visualizer öffnen** (Kategorie Command) |
| **Gui CommandRegistry** (intern) | `nav.rd_theme_visualizer` — wird nur bei gesetztem Devtools-Env registriert |

**Fenster:** `app/gui/devtools/theme_visualizer_launcher.py` hält **eine** Instanz; erneutes Öffnen fokussiert das bestehende Fenster. Schließen setzt die Referenz zurück (`WA_DeleteOnClose`).

**Implementierung:** `ThemeVisualizerWindow(embed_in_app=True)` nutzt ein lokales `ThemeRegistry` + `setStyleSheet(load_stylesheet(theme))` nur auf dem Visualizer-Fenster — **kein** `ThemeManager.set_theme` für die ganze App.

Details zur Devtools-Steuerung: `docs/devtools/DEVTOOLS_OVERVIEW.md`.

## Abhängigkeiten

- Python 3.x wie im Projekt üblich
- **PySide6** (wie die GUI)
- Zugriff auf `app.gui.themes` (ThemeRegistry, ThemeManager, Loader, Token-Spec-Ableitung)

Keine zusätzlichen Pip-Pakete.

## Aufbau der Oberfläche

| Bereich | Inhalt |
|--------|--------|
| **Links** | Theme-Auswahl, QA-Checkboxen (Disabled/Fokus/Selektion/Debug), Kontrast-Liste (Pflicht-Paare), Token-Inspektor, Screenshot der Komponenten-Vorschau |
| **Mitte** | Token-Swatches gruppiert (Background, Foreground, Markdown, Chat, …) mit Kanon-Namen, Hex-Wert, grobem Kontrast-Hinweis |
| **Rechts** | Scrollbare Komponenten-Vorschau (Buttons, Inputs, Tabellen, Chat/Markdown-HTML, Badges, Menü, Tooltip-Ziel, ProgressBar, …) |

**Farbprofil-Dropdown:** Platzhalter (`—`), falls später `color_profile_id` eingeführt wird.

**Klick auf eine Token-Zeile:** Füllt den Inspektor und kopiert `Token<TAB>Wert` in die Zwischenablage.

## Typische Nutzung

1. Theme im Dropdown wählen — **CLI-Tool:** globales QSS via `ThemeManager.set_theme`. **Shell-Einbettung:** nur das Visualizer-Fenster erhält das gewählte QSS.
2. Token-Gruppen und Kontrast-Liste auf Auffälligkeiten prüfen (`OK` / `schlecht` / `kritisch`).
3. Rechte Vorschau mit Checkboxen für Disabled/Fokus/Selektion kombinieren.
4. Optional Screenshot der Komponenten-Spalte exportieren.

## Grenzen

- **Kein** WCAG-Audit-Tool: Kontrastlogik ist bewusst grob (siehe `app/gui/themes/contrast.py` und `docs/design/THEME_CONTRAST_RULES.md`).
- **Hover** an echten Qt-Widgets ist schwer isoliert darstellbar; für Buttons gibt es zusätzliche Zeilen mit Hover-/Pressed-Farben aus den Tokens.
- **Theme neu laden** aus dem Dateisystem ist nicht implementiert — Built-in-Themes kommen aus `ThemeRegistry` / semantischen Profilen; Code-Änderungen erfordern wie üblich einen Neustart des Tools.
- Token-Inspektor zeigt den **logischen** Ort der Definition (Registry / semantische Profile), keine einzelne JSON-Datei pro Token.

## Zusammenspiel mit Theme Guard und ThemeManager

- **ThemeManager** (`get_theme_manager()`): im **CLI-Modus** wendet er `load_stylesheet(theme)` auf die `QApplication` an. Im **eingebetteten** Modus bleibt der Singleton unverändert; Tokens kommen aus einer lokalen `ThemeDefinition` im Visualizer.
- **Theme Guard** (`tools/theme_guard.py`): statische Prüfung auf harte Farben außerhalb erlaubter Pfade. Der Visualizer verwendet **keine** parallelen Farbtabellen; programmatische Styles in `app/devtools/` nutzen nur Werte aus dem aktiven Theme.
- Konsistenz der Pflicht-Kontrast-Paare in CI bleibt Aufgabe der bestehenden Tests/Tools; der Visualizer ergänzt das für **manuelles** Sehen und Schnellcheck.

## Siehe auch

- `docs/04_architecture/THEME_ARCHITECTURE.md`
- `docs/design/THEME_TOKEN_SPEC.md`
- `docs/design/THEME_CONTRAST_RULES.md`
