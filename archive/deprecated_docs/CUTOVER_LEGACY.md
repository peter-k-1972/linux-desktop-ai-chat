# Cutover & Legacy – GUI-Übergang

## Standard-Startpfad (neue GUI)

Die Anwendung startet standardmäßig mit der **neuen GUI-Shell** (ShellMainWindow):

```bash
python main.py
# oder
python run_gui_shell.py
# oder
python -m app
```

Die neue GUI umfasst:
- TopBar, NavigationSidebar, WorkspaceHost, InspectorHost, BottomPanelHost
- Kommandozentrale, Operations, Control Center, QA & Governance, Runtime/Debug, Settings
- ThemeManager, IconManager, Command Palette, Breadcrumbs

## Legacy-GUI (deprecated)

Die **alte GUI** (MainWindow mit ChatWidget, SidebarWidget, CommandCenterView) ist deprecated:

```bash
python run_legacy_gui.py
```

Legacy-Komponenten:
- `app/main.py` – MainWindow, asyncio.main()
- `run_legacy_gui.py` – Einstiegspunkt für Legacy
- `app/chat_widget.py`, `app/sidebar_widget.py`, `app/ui/command_center/` – alte UI

Diese Teile bleiben vorerst im Repo, sind aber **nicht** der Standard-Startpfad.

## Umstellung (Cutover)

| Was | Status |
|-----|--------|
| main.py | Delegiert an run_gui_shell.main |
| python -m app | Delegiert an run_gui_shell.main |
| run_gui_shell.py | Standard-GUI-Start |
| run_legacy_gui.py | Legacy, explizit aufrufbar |
| app/main.py | Legacy, deprecated |

## Smoke-Tests

Die neue GUI ist durch Smoke-Tests abgesichert:

- `tests/smoke/test_shell_gui.py` – ShellMainWindow, WorkspaceHost, alle 6 Bereiche, Inspector, BottomPanel, Theme

```bash
pytest tests/smoke/test_shell_gui.py -v
```
