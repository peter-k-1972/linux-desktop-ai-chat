# Cutover-Zusammenfassung – neue GUI als Standard

## Was umgestellt wurde

| Bereich | Änderung |
|---------|----------|
| **main.py** | Delegiert an run_gui_shell.main (bereits vorher so) |
| **app/__main__.py** | Neu: `python -m app` startet neue GUI |
| **app/main.py** | Deprecation-Warnung bei Aufruf von main() |
| **run_legacy_gui.py** | Bereits als LEGACY gekennzeichnet |
| **ThemeSelectionPanel** | Fix: theme_changed-Callback robust gegen zerstörtes Widget |

## Ergänzte Tests

| Datei | Tests |
|-------|-------|
| **tests/smoke/test_shell_gui.py** | 9 Smoke-Tests für neue GUI |
| - test_shell_main_window_importable | Import prüfen |
| - test_run_gui_shell_importable | run_gui_shell prüfen |
| - test_app_main_module_runs_new_gui | python -m app prüfen |
| - test_nav_areas_defined | Alle 6 Hauptbereiche |
| - test_workspace_host_shows_all_areas | Workspace-Wechsel ohne Crash |
| - test_inspector_host_exists | InspectorHost |
| - test_bottom_panel_host_exists | BottomPanelHost |
| - test_theme_manager_available | ThemeManager |
| - test_shell_main_window_starts_with_mocked_infra | ShellMainWindow mit Mock-Infra |

## Verbleibende Legacy-Teile

| Komponente | Status |
|------------|--------|
| app/main.py (MainWindow) | LEGACY, deprecated |
| run_legacy_gui.py | LEGACY, explizit aufrufbar |
| app/chat_widget.py | Legacy-UI |
| app/sidebar_widget.py | Legacy-UI |
| app/ui/command_center/ | Legacy CommandCenterView |
| app/ui/agents/, app/ui/settings_dialog | Legacy-Dialoge |

Diese bleiben im Repo, sind aber nicht Teil des Standard-Startpfads.

## Startanweisung

```bash
# Standard (neue GUI)
python main.py

# Alternativ
python run_gui_shell.py
python -m app

# Legacy (deprecated)
python run_legacy_gui.py
```

## Smoke-Tests ausführen

```bash
pytest tests/smoke/test_shell_gui.py -v
```
