# GUI-Devtools — Überblick

## Zweck

Interne Werkzeuge für Entwicklung und QA, die **nicht** zur normalen Produktiv-UX gehören. Sie hängen unter `app/gui/devtools/` bzw. nutzen gemeinsame Logik in `app/devtools/` (z. B. Theme-Visualizer-Widgets).

## Freischaltung

| Variable | Wirkung |
|----------|---------|
| `LINUX_DESKTOP_CHAT_DEVTOOLS=1` (oder `true`, `yes`, `on`) | Theme-Visualizer-Einträge in Runtime/Debug, Command-Palette-Befehl, optionaler Nav-Command in der Gui-`CommandRegistry` |
| nicht gesetzt oder `0` / `false` / `off` | Keine dieser Einträge — Endnutzer sehen den Theme-Visualizer nicht |

Es gibt **kein** separates Rollenmodell in der App; die Env-Variable ist die minimale, explizite Freigabe.

## Aktuelle Tools

| Tool | GUI-Pfad / Einstieg | Code |
|------|---------------------|------|
| **Theme Visualizer** | Runtime / Debug → Theme Visualizer; Ctrl+K → „Theme Visualizer öffnen“ | `theme_visualizer_launcher.py`, `theme_visualizer_workspace.py`, `app/devtools/theme_visualizer_window.py` |
| **Markdown Demo** | Runtime / Debug → Markdown Demo (ohne zusätzliches Env) | `markdown_demo_panel.py` |

## Siehe auch

- `docs/devtools/THEME_VISUALIZER.md` — Bedienung, CLI vs. eingebettet, Theme-Sandbox
- `THEME_VISUALIZER_APP_INTEGRATION_REPORT.md` (Repo-Root) — Integrationsdetails
