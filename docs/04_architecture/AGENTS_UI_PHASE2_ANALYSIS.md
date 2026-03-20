# Agents UI Phase 2 – Analyse der verbleibenden Legacy-Module

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Referenz:** AGENTS_UI_PHASE1_MIGRATION_REPORT.md, AGENTS_UI_ARCHITECTURE_AUDIT.md

---

## Kontext

Phase 1 migrierte 7 Dateien nach `app/gui/domains/control_center/agents_ui/`.  
Control Center Agents nutzt nun `AgentManagerPanel` aus agents_ui.

Die folgenden 7 Dateien in `app/ui/agents/` wurden **nicht** migriert und werden hier analysiert.

---

## 1. agent_workspace.py

| Feld | Inhalt |
|------|--------|
| **Zweck** | Drei-Spalten-Workspace: Links Navigation (Agent Library, Runs, Activity, Skills), Mitte gestapelter Inhalt, rechts Inspector. Reagiert auf `project_context_changed`. |
| **Imports** | `PySide6.QtWidgets`, `PySide6.QtCore`, `app.ui.agents.agent_navigation_panel`, `app.ui.agents.agent_library_panel`, `app.ui.agents.agent_runs_panel`, `app.ui.agents.agent_activity_panel`, `app.ui.agents.agent_skills_panel`, `app.gui.events.project_events`, `app.agents.seed_agents`, `app.gui.inspector.agent_inspector` |
| **Abhängigkeiten** | AgentNavigationPanel, AgentLibraryPanel, AgentRunsPanel, AgentActivityPanel, AgentSkillsPanel. Nutzt `_placeholder_widget()` bei Import-Fehlern. |
| **Beziehung zu agents_ui** | Keine. Eigenständiger Workspace. Control Center nutzt `AgentsWorkspace` aus `gui/domains/control_center/workspaces/agents_workspace.py`, nicht diese Klasse. |
| **Klassifikation** | **REMOVE** |
| **Begründung** | Wird nirgends instanziiert. Nur in `app.ui.agents.__init__` exportiert. Control Center nutzt `gui/domains/control_center/workspaces/agents_workspace.AgentsWorkspace` (AgentManagerPanel). Toter Code. |

---

## 2. agent_navigation_panel.py

| Feld | Inhalt |
|------|--------|
| **Zweck** | Linke Navigationsleiste für AgentWorkspace. Sektionen: Agent Library, Agent Runs, Activity, Skills. Projekt-Header, `section_selected`-Signal. |
| **Imports** | `PySide6.QtWidgets`, `PySide6.QtCore`, `app.gui.icons`, `app.gui.events.project_events`, `app.core.context.project_context_manager` |
| **Abhängigkeiten** | Nur von `agent_workspace` verwendet. Keine Abhängigkeit zu agents_ui. |
| **Beziehung zu agents_ui** | Keine. |
| **Klassifikation** | **REMOVE** |
| **Begründung** | Ausschließlich von `agent_workspace` genutzt. Da AgentWorkspace tot ist, ist auch dieses Panel ungenutzt. |

---

## 3. agent_library_panel.py

| Feld | Inhalt |
|------|--------|
| **Zweck** | Kombiniert AgentListPanel (Liste) + AgentEditorPanel (Editor). Projektbezogene Agenten. Create Agent, Save, Refresh. |
| **Imports** | `PySide6.QtWidgets`, `app.agents.agent_profile`, `app.ui.agents.agent_list_panel`, `app.ui.agents.agent_editor_panel`, `app.core.context.project_context_manager`, `app.agents.agent_service` |
| **Abhängigkeiten** | AgentListPanel (Re-Export aus gui), AgentEditorPanel. Nutzt `list_panel`, `agent_selected`, `create_agent_requested`, `save_requested`. |
| **Beziehung zu agents_ui** | Nutzt `AgentListPanel` via ui-Re-Export (gui-Version). Nutzt `AgentEditorPanel` (nicht migriert, andere API als AgentProfilePanel). |
| **Klassifikation** | **REMOVE** |
| **Begründung** | Nur von `agent_workspace` verwendet. AgentWorkspace ist tot. Konzept (projektbezogene Liste + Editor) unterscheidet sich von AgentManagerPanel (HR-Liste + Profil). |

---

## 4. agent_editor_panel.py

| Feld | Inhalt |
|------|--------|
| **Zweck** | Agent-Konfigurations-Editor. Felder: Name, Modell, Prompt, Wissenssammlungen, Tools, Memory, Limits. `save_requested`-Signal, `load_profile()`, `to_profile()`. |
| **Imports** | `PySide6.QtWidgets`, `app.agents.agent_profile`, `app.gui.events.project_events`, `app.core.context.project_context_manager`, `app.services.knowledge_service` |
| **Abhängigkeiten** | Nur von `agent_library_panel` verwendet. |
| **Beziehung zu agents_ui** | Andere API als `AgentProfilePanel` / `AgentProfileForm`. AgentProfilePanel: Avatar, display_name, department, status, read-only/edit-Modus. AgentEditorPanel: Name, Model, Prompt, Knowledge, Tools, Memory, Limits – konfigurationsorientiert. |
| **Klassifikation** | **MANUAL_REVIEW** |
| **Begründung** | Unterschiedliches Konzept zu AgentProfileForm. Knowledge-Service-Integration, projektbezogene Collections. Könnte als alternative Editor-UI relevant sein oder in AgentProfileForm integriert werden. Architekturentscheidung nötig. |

---

## 5. agent_runs_panel.py

| Feld | Inhalt |
|------|--------|
| **Zweck** | Zeigt Agent-Runs aus DebugStore: Agent, Status, Startzeit, Dauer, Resultat. Polling alle 1,5 s. |
| **Imports** | `datetime`, `PySide6.QtWidgets`, `PySide6.QtCore`, `PySide6.QtGui`, `app.debug.debug_store` |
| **Abhängigkeiten** | Nur von `agent_workspace` verwendet. DebugStore-Integration. |
| **Beziehung zu agents_ui** | Keine. |
| **Klassifikation** | **MANUAL_REVIEW** |
| **Begründung** | Funktionale UI mit echter DebugStore-Anbindung. gui `runtime_debug` hat AgentActivityPanel mit Dummy-Daten. Diese Implementierung könnte nach runtime_debug migriert oder dort integriert werden. Architekturentscheidung: Wo gehört „Agent Runs“ hin? |

---

## 6. agent_activity_panel.py

| Feld | Inhalt |
|------|--------|
| **Zweck** | Event-Stream aus DebugStore: Model calls, Tool calls, Steps, Errors. Filter (All/Model/Tool/Step/Error). Polling alle 1,5 s. |
| **Imports** | `dataclasses`, `datetime`, `PySide6.QtWidgets`, `PySide6.QtCore`, `PySide6.QtGui`, `app.debug.agent_event`, `app.debug.debug_store` |
| **Abhängigkeiten** | Nur von `agent_workspace` verwendet. Echte DebugStore-Integration. |
| **Beziehung zu agents_ui** | Keine. gui hat `runtime_debug/panels/agent_activity_panels.AgentActivityPanel` – **Dummy-Daten**, keine DebugStore-Anbindung. |
| **Klassifikation** | **MANUAL_REVIEW** |
| **Begründung** | Diese Implementierung ist funktional (DebugStore, Event-History). gui runtime_debug nutzt Placeholder mit Hardcoded-Daten. Migration dieser Logik nach gui runtime_debug könnte den Placeholder ersetzen. Architekturentscheidung nötig. |

---

## 7. agent_skills_panel.py

| Feld | Inhalt |
|------|--------|
| **Zweck** | Tools pro Agent aktivieren/deaktivieren. Checkboxen für verfügbare Tools (knowledge_search, filesystem, calculator, …). Agent-Combo, Save. |
| **Imports** | `PySide6.QtWidgets`, `app.agents.agent_profile`, `app.gui.events.project_events`, `app.core.context.project_context_manager`, `app.agents.agent_service` |
| **Abhängigkeiten** | Nur von `agent_workspace` verwendet. `set_agent()` für externe Auswahl. |
| **Beziehung zu agents_ui** | AgentProfileForm hat `AgentCapabilitiesEditor` (capabilities) und `tools_edit` (QLineEdit, kommagetrennt). AgentSkillsPanel: Checkboxen mit Beschreibungen – andere UX. |
| **Klassifikation** | **MANUAL_REVIEW** |
| **Begründung** | Andere UX als AgentProfileForm (Checkboxen vs. Textfeld). Könnte in AgentProfileForm integriert oder als alternative Tool-Konfiguration genutzt werden. Unklare Verantwortlichkeit: agents_ui vs. eigenes Panel. |

---

## Zusammenfassung

| Datei | Klassifikation | Begründung |
|-------|----------------|------------|
| agent_workspace.py | REMOVE | Nie instanziiert, toter Code |
| agent_navigation_panel.py | REMOVE | Nur von AgentWorkspace, tot |
| agent_library_panel.py | REMOVE | Nur von AgentWorkspace, tot |
| agent_editor_panel.py | MANUAL_REVIEW | Andere API als AgentProfileForm, Knowledge-Integration |
| agent_runs_panel.py | MANUAL_REVIEW | Funktionale DebugStore-UI, Überlappung mit runtime_debug |
| agent_activity_panel.py | MANUAL_REVIEW | Funktionale DebugStore-UI, gui hat nur Dummy |
| agent_skills_panel.py | MANUAL_REVIEW | Andere UX als AgentProfileForm, Tool-Checkboxen |

---

## Abhängigkeitsgraph (Legacy-Branch)

```
agent_workspace
├── agent_navigation_panel
├── agent_library_panel
│   ├── agent_list_panel (Re-Export aus gui)
│   └── agent_editor_panel
├── agent_runs_panel
├── agent_activity_panel
└── agent_skills_panel
```

---

## Empfehlungen für Phase 2

1. **REMOVE (3 Dateien):** agent_workspace, agent_navigation_panel, agent_library_panel – nach Verifikation, dass keine Referenzen außer `__init__.py` existieren.

2. **MANUAL_REVIEW (4 Dateien):** agent_editor_panel, agent_runs_panel, agent_activity_panel, agent_skills_panel – vor Entfernung oder Migration Architekturentscheidungen treffen:
   - Soll agent_activity_panel-Logik nach gui runtime_debug migriert werden?
   - Soll agent_runs_panel in runtime_debug integriert werden?
   - Soll agent_skills_panel in AgentProfileForm/AgentCapabilitiesEditor integriert werden?
   - Soll agent_editor_panel als alternative Editor-UI erhalten oder mit AgentProfileForm vereinheitlicht werden?
