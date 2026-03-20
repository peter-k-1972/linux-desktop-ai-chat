# GUI Cutover – neue Shell als Standard

**Datum:** 2026-03-15  
**Status:** Abgeschlossen

## Standard-Startpunkt

Die Anwendung startet standardmäßig mit der **neuen GUI-Shell**:

```bash
python main.py
# oder
.venv/bin/python main.py
```

Die neue Shell bietet:
- **MainWindow** mit TopBar, NavigationSidebar, WorkspaceHost, InspectorHost, BottomPanelHost
- **6 Hauptbereiche:** Kommandozentrale, Operations, Control Center, QA & Governance, Runtime/Debug, Settings
- ThemeManager, IconManager, Command Palette (Ctrl+Shift+P), Breadcrumb-Navigation

## Alternative Einstiegspunkte

| Skript | Beschreibung |
|--------|--------------|
| `main.py` | **Standard** – neue GUI-Shell |
| `run_gui_shell.py` | Direkter Start der Shell (ohne Backend, identisch zu main.py) |
| `run_legacy_gui.py` | **Legacy** – alte Chat-Oberfläche mit Ollama-Backend |

## Legacy-GUI

Die alte GUI (ChatWidget, SidebarWidget, CommandCenterView) ist deprecated und wird über `run_legacy_gui.py` gestartet:

```bash
python run_legacy_gui.py
```

**Legacy-Dateien:**
- `app/main.py` – alter App-Einstieg (MainWindow, ChatWidget, etc.)
- `app/chat_widget.py`
- `app/sidebar_widget.py`
- `app/ui/command_center/`
- Weitere Chat-/Backend-Module

## Gefixte Probleme

- Cutover: main.py startet neue GUI
- Breadcrumb-Manager: Null-Check bei get_breadcrumb_manager()
- Legacy klar als deprecated markiert

## Ergänzte Elemente

- Keine neuen Screens erforderlich – alle 6 Hauptbereiche waren bereits implementiert
- run_legacy_gui.py für Rückwärtskompatibilität
