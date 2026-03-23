# Qt Designer Dummy-Bibliothek

## Zweck

Diese Dummy-Bibliothek bildet die **visuelle Architektur** der Linux Desktop Chat PySide6-GUI in Qt Designer-faehigen .ui-Dateien ab. Sie dient als:

- **Blueprint** fuer visuelle Nachbearbeitung
- **Referenz** fuer Layout und Zonenaufteilung
- **Basis** fuer spaetere Designer-basierte Views

**Nicht enthalten:** Businesslogik, Signal/Slot-Verbindungen, dynamische Daten, Services.

---

## Struktur

```
gui_designer_dummy/
  README_DESIGNER_DUMMY.md
  DESIGNER_MAPPING.md
  shell/                    # App-Rahmen
    shell_main_window.ui
    workspace_host.ui
    inspector_host.ui
    bottom_panel_host.ui
    breadcrumbs_bar.ui
  screens/                  # Domain-Screens
    dashboard_screen.ui
    operations_screen.ui
    control_center_screen.ui
    qa_governance_screen.ui
    runtime_debug_screen.ui
    settings_screen.ui
    settings_workspace.ui
    command_center_view.ui
    audit_operations_view.ui
    governance_view.ui
    incident_operations_view.ui
    qa_drilldown_view.ui
    qa_operations_view.ui
    review_operations_view.ui
    runtime_debug_view.ui
    subsystem_detail_view.ui
  workspaces/               # Domain-Workspaces
    chat/
    knowledge/
    projects/
    prompt_studio/
    agent_tasks/
    control_center/
  panels/                   # Wiederverwendbare Panels
    sidebar.ui
    top_bar.ui
    breadcrumb_bar.ui
    inspector_host.ui
    bottom_panel_host.ui
    system_status_panel.ui
    active_work_panel.ui
    qa_status_panel.ui
    incidents_panel.ui
    context_inspection_panel.ui
    agent_debug_panel.ui
    introspection_workspace.ui
  dialogs/
  widgets/
```

---

## .ui-Dateien in Qt Designer oeffnen

### Voraussetzungen

- Qt Designer (`designer` oder `pyside6-designer`)

### Oeffnen

```bash
# Main Shell
designer app/gui_designer_dummy/shell/shell_main_window.ui

# Einzelner Screen
designer app/gui_designer_dummy/screens/dashboard_screen.ui

# Workspace
designer app/gui_designer_dummy/workspaces/chat/chat_workspace.ui
```

---

## Datei-Kategorien

### Main Shell

| Datei | Beschreibung |
|-------|--------------|
| shell/shell_main_window.ui | QMainWindow mit Header, Breadcrumb, Workspace, Docks (Nav, Inspector, Bottom) |
| shell/workspace_host.ui | QStackedWidget mit Platzhaltern fuer alle Screens |
| shell/inspector_host.ui | Inspector mit Kontext/Auswahl/Details |
| shell/bottom_panel_host.ui | QTabWidget: Logs, Events, Metriken, Agent-Aktivitaet, LLM-Trace |
| shell/breadcrumbs_bar.ui | Breadcrumb-Leiste |

### Screens

Domain-Screens: dashboard, operations, control_center, qa_governance, runtime_debug, settings, command_center. Zusaetzlich: audit, governance, incident, qa, review, runtime_debug, subsystem_detail Views.

### Panels

Dashboard-Panels (system_status, active_work, qa_status, incidents), Shell-Panels (sidebar, top_bar), Debug-Panels (context_inspection, agent_debug, introspection_workspace).

### Workspaces

- **chat:** chat_workspace, chat_navigation_panel, conversation_panel, input_panel, chat_side_panel, chat_header_widget, chat_context_bar, chat_details_panel
- **knowledge:** knowledge_workspace + 14 Panels
- **projects:** projects_workspace + 7 Panels
- **prompt_studio:** prompt_studio_workspace + 10 Panels
- **agent_tasks:** agent_tasks_workspace + 9 Panels
- **control_center:** control_center_nav, 5 Workspaces, 5 Agent-Panels, 5 Domain-Panels

### Dialoge

command_palette, project_switcher_dialog, new_project_dialog, topic_create/rename/delete_confirm, create/rename_collection, assign_sources, new_prompt_dialog, template_edit_dialog, agent_manager_dialog, settings_dialog, workspace_graph_dialog.

---

## Was ist nur visuell approximiert

- **BreadcrumbBar:** Pfad-Items werden dynamisch erzeugt; Dummy zeigt festen Platzhalter
- **NavigationSidebar:** Sektionen aus Registry; Dummy mit festen Sektionen
- **InspectorHost:** Inhalt je nach Screen; Dummy mit Standard-Platzhalter
- **WorkspaceGraphDialog:** Graph-Visualisierung; Dummy mit Platzhalter
- **Command Center Views:** Audit, Governance, Incident, QA, Review, Runtime, Subsystem – Tabellen/Listen dynamisch; Dummy mit Platzhalter-Struktur
- **Icons:** Werden ueber IconManager geladen; in .ui nur Text

---

## Produktive Nutzung

### 1. Layout-Anpassung

.ui-Dateien in Qt Designer oeffnen, Margins, Spacing, Proportionen anpassen.

### 2. Code-Generierung

```bash
pyside6-uic shell/shell_main_window.ui -o ui_shell_main_window.py
```

### 3. Laufzeit-Loading

```python
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

loader = QUiLoader()
file = QFile("shell/shell_main_window.ui")
file.open(QFile.OpenModeFlag.ReadOnly)
window = loader.load(file)
```

### 4. Integration in bestehende Architektur

- Generierte `setupUi()` in Subklassen aufrufen
- Signale/Slots in Python verbinden
- Dynamische Inhalte (Inspector, Listen, Tabs) weiterhin per Python befuellen

---

## Technische Regeln

- **Format:** Qt Designer XML (.ui), Version 4.0
- **Encoding:** UTF-8, ASCII in Platzhaltertexten
- **Layouts:** QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter, QFormLayout
- **Keine** absoluten Positionen
- **objectName:** camelCase (z.B. workspaceHost, chatNavigationPanel)
