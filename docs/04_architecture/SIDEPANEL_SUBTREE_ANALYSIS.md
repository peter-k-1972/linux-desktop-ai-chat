# Sidepanel-Subtree – Migrationsanalyse

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Referenz:** CHAT_UI_PHASE4_SIDEPANEL_REPORT.md

---

## Kontext

ChatSidePanel = MANUAL_REVIEW. Eine direkte Migration würde den gui→ui-Verstoß nur verschieben, da ChatSidePanel von ModelSettingsPanel, PromptManagerPanel und AgentDebugPanel abhängt.

Diese Analyse untersucht die Sub-Panels, um eine sichere Migrationsreihenfolge zu ermitteln.

---

## 1. app/ui/sidepanel/model_settings_panel.py

### Zweck

Modell-Einstellungen als Studio-Panel. Formular mit Sektionen:
- Modellzuweisung (Assistant, Thinking, Vision, Code, Overkill)
- Routing & Verhalten (Auto-Routing, Cloud, Websuche, Eskalation, Standardrolle)
- Rollen → Modell
- Provider & Status
- Erweitert (Temperatur, Top-p, Max Tokens, Timeout, Streaming, Retry)

Bindet an AppSettings und ModelOrchestrator. Emittiert `settings_changed`.

### Imports

| Import | Herkunft |
|--------|----------|
| PySide6.QtWidgets, QtCore, QtGui | extern |
| app.core.models.roles | app |
| app.resources.styles | app |
| app.ui.sidepanel.prompt_manager_panel._PROMPTS_PANEL_FIXED_WIDTH | **ui** (lazy in init_ui) |

### Abhängigkeiten

- **core:** ModelRole, get_role_display_name, all_roles, get_default_model_for_role
- **resources:** get_theme_colors
- **ui:** _PROMPTS_PANEL_FIXED_WIDTH (nur für Panel-Breite, Layout-Konsistenz mit PromptManagerPanel)

### Konsumenten

| Datei | Herkunft |
|-------|----------|
| app/ui/sidepanel/chat_side_panel.py | ui |
| app/ui/sidepanel/__init__.py | ui (Re-Export) |

### Empfohlene gui-Zieldomain

**app/gui/domains/settings/** oder **app/gui/domains/control_center/**

Begründung: Modellzuweisung, Routing, Provider-Status sind Settings-/Control-Center-Themen. Nicht Chat-spezifisch.

### Klassifikation

**MIGRATE**

### Begründung

- Reine UI mit Settings-Binding
- Einzige ui-Abhängigkeit: _PROMPTS_PANEL_FIXED_WIDTH (kann nach Migration von prompt_manager_panel aus gui importiert werden)
- Keine weiteren ui-Imports
- **Blockierend:** prompt_manager_panel muss zuerst migriert werden (oder _PROMPTS_PANEL_FIXED_WIDTH in gemeinsames Modul extrahiert)

---

## 2. app/ui/sidepanel/prompt_manager_panel.py

### Zweck

Promptverwaltung als Studio-Panel. Gestraffte UI:
- Suchfeld, Kategorie-Filter
- Aktionszeile (Neu, Laden, Speichern, Löschen, Duplizieren)
- Filterbare Prompt-Liste
- Editor (Titel, Kategorie, Typ, Beschreibung, Tags, Inhalt)
- Vorschau
- Anwendungsaktionen: „In Chat übernehmen“, „Als Systemprompt“, „In Composer einfügen“

Bindet an PromptService. Emittiert prompt_apply_requested, prompt_as_system_requested, prompt_to_composer_requested.

### Imports

| Import | Herkunft |
|--------|----------|
| PySide6.QtWidgets, QtCore, QtGui | extern |
| app.prompts (Prompt, PromptService, PROMPT_TYPES, PROMPT_CATEGORIES) | app |

### Abhängigkeiten

- **app.prompts:** Prompt, PromptService, PROMPT_TYPES, PROMPT_CATEGORIES
- Keine ui-Imports

### Konsumenten

| Datei | Herkunft |
|-------|----------|
| app/ui/sidepanel/chat_side_panel.py | ui |
| app/ui/sidepanel/model_settings_panel.py | ui (_PROMPTS_PANEL_FIXED_WIDTH) |
| app/ui/sidepanel/__init__.py | ui (Re-Export) |
| tests/ui/test_prompt_manager_ui.py | tests |
| tests/state_consistency/test_prompt_consistency.py | tests |

### Empfohlene gui-Zieldomain

**app/gui/domains/operations/prompt_studio/panels/**

Begründung: Prompt Studio existiert bereits unter gui/domains/operations/prompt_studio. PromptManagerPanel ist funktional verwandt (Prompt-CRUD, PromptService), aber anderes UI-Layout (kompaktes Single-Panel vs. Workspace mit Navigation). Kann als zusätzliches Panel „PromptManagerPanel“ oder „PromptSidePanel“ in prompt_studio/panels integriert werden. Die Chat-spezifischen Signale (prompt_apply_requested etc.) bleiben erhalten.

Alternative: **app/gui/domains/operations/chat/panels/** – wenn das Panel explizit Chat-Kontext behalten soll („In Chat übernehmen“).

### Klassifikation

**MIGRATE**

### Begründung

- Keine ui-Imports – **Leaf-Modul** im Sidepanel-Subtree
- Nur app.prompts und PySide6
- Kann zuerst migriert werden
- **Nicht blockierend** – keine Abhängigkeiten von anderen ui-Modulen

---

## 3. app/ui/debug/agent_debug_panel.py

### Zweck

Hauptpanel für Agenten-Debug. Bündelt 5 Tab-Views:
- Aktivität (AgentActivityView)
- Timeline (EventTimelineView)
- Task-Graph (TaskGraphView)
- Modelle (ModelUsageView)
- Tools (ToolExecutionView)

Polling alle 500ms aus DebugStore. Clear-Button zum Löschen der Debug-Daten.

### Imports

| Import | Herkunft |
|--------|----------|
| PySide6.QtWidgets, QtCore | extern |
| app.debug.debug_store | app |
| app.ui.debug.agent_activity_view | **ui** |
| app.ui.debug.event_timeline_view | **ui** |
| app.ui.debug.model_usage_view | **ui** |
| app.ui.debug.tool_execution_view | **ui** |
| app.ui.debug.task_graph_view | **ui** |

### Abhängigkeiten

- **app.debug:** DebugStore, get_debug_store
- **app.ui.debug:** 5 View-Module

### Konsumenten

| Datei | Herkunft |
|-------|----------|
| app/ui/sidepanel/chat_side_panel.py | ui |
| app/ui/debug/__init__.py | ui (Re-Export) |
| tests/ui/test_debug_panel_ui.py | tests |
| tests/cross_layer/test_debug_view_matches_failure_events.py | tests |
| tests/async_behavior/test_debug_clear_during_refresh.py | tests |

### Empfohlene gui-Zieldomain

**app/gui/domains/runtime_debug/panels/**

Begründung: runtime_debug existiert bereits (agent_activity_workspace, agent_activity_stream_panel, etc.). AgentDebugPanel mit DebugStore-Binding passt fachlich in runtime_debug.

### Klassifikation

**MIGRATE**

### Begründung

- Reine UI mit DebugStore-Binding
- **Blockierend:** 5 ui.debug-Views müssen zuerst migriert werden

---

## 4. app/ui/debug/agent_activity_view.py

### Zweck

Zeigt aktive Agenten mit Task und Status (Agent | Task | Status). Liest aus DebugStore.get_active_tasks().

### Imports

| Import | Herkunft |
|--------|----------|
| PySide6.QtWidgets, QtCore | extern |
| app.debug.debug_store | app |
| app.resources.styles | app |

### Abhängigkeiten

- Keine ui-Imports – **Leaf-Modul**

### Konsumenten

| Datei | Herkunft |
|-------|----------|
| app/ui/debug/agent_debug_panel.py | ui |

### Empfohlene gui-Zieldomain

**app/gui/domains/runtime_debug/panels/**

### Klassifikation

**MIGRATE**

### Begründung

- Leaf-Modul, keine ui-Abhängigkeiten
- Kann zuerst migriert werden

---

## 5. app/ui/debug/event_timeline_view.py

### Zweck

Chronologische Liste von Ereignissen (Zeit, Agent, Event). Liest aus DebugStore.

### Imports

| Import | Herkunft |
|--------|----------|
| datetime | stdlib |
| PySide6.QtWidgets, QtCore | extern |
| app.debug.agent_event | app |
| app.debug.debug_store | app |
| app.resources.styles | app |

### Abhängigkeiten

- Keine ui-Imports – **Leaf-Modul**

### Konsumenten

| Datei | Herkunft |
|-------|----------|
| app/ui/debug/agent_debug_panel.py | ui |

### Empfohlene gui-Zieldomain

**app/gui/domains/runtime_debug/panels/**

### Klassifikation

**MIGRATE**

### Begründung

- Leaf-Modul, keine ui-Abhängigkeiten

---

## 6. app/ui/debug/model_usage_view.py

### Zweck

Zeigt Modellnutzung: Modell, Aufrufe, Dauer. Tabellen-Ansicht aus DebugStore.

### Imports

| Import | Herkunft |
|--------|----------|
| PySide6.QtWidgets, QtCore | extern |
| app.debug.debug_store | app |
| app.resources.styles | app |

### Abhängigkeiten

- Keine ui-Imports – **Leaf-Modul**

### Konsumenten

| Datei | Herkunft |
|-------|----------|
| app/ui/debug/agent_debug_panel.py | ui |

### Empfohlene gui-Zieldomain

**app/gui/domains/runtime_debug/panels/**

### Klassifikation

**MIGRATE**

### Begründung

- Leaf-Modul, keine ui-Abhängigkeiten

---

## 7. app/ui/debug/tool_execution_view.py

### Zweck

Zeigt ausgeführte Tools mit Status. Liest aus DebugStore.

### Imports

| Import | Herkunft |
|--------|----------|
| PySide6.QtWidgets, QtCore | extern |
| app.debug.debug_store | app |
| app.resources.styles | app |

### Abhängigkeiten

- Keine ui-Imports – **Leaf-Modul**

### Konsumenten

| Datei | Herkunft |
|-------|----------|
| app/ui/debug/agent_debug_panel.py | ui |

### Empfohlene gui-Zieldomain

**app/gui/domains/runtime_debug/panels/**

### Klassifikation

**MIGRATE**

### Begründung

- Leaf-Modul, keine ui-Abhängigkeiten

---

## 8. app/ui/debug/task_graph_view.py

### Zweck

Vereinfachte Darstellung des Task-Graphen (Tasks mit Abhängigkeiten). Liest aus DebugStore.

### Imports

| Import | Herkunft |
|--------|----------|
| PySide6.QtWidgets, QtCore | extern |
| app.debug.debug_store | app |
| app.resources.styles | app |

### Abhängigkeiten

- Keine ui-Imports – **Leaf-Modul**

### Konsumenten

| Datei | Herkunft |
|-------|----------|
| app/ui/debug/agent_debug_panel.py | ui |

### Empfohlene gui-Zieldomain

**app/gui/domains/runtime_debug/panels/**

### Klassifikation

**MIGRATE**

### Begründung

- Leaf-Modul, keine ui-Abhängigkeiten

---

## 9. Referenzprüfung – Zusammenfassung

### ModelSettingsPanel

| Konsument | Herkunft |
|-----------|----------|
| chat_side_panel.py | ui |
| ui/sidepanel/__init__.py | ui |

### PromptManagerPanel

| Konsument | Herkunft |
|-----------|----------|
| chat_side_panel.py | ui |
| model_settings_panel.py | ui (_PROMPTS_PANEL_FIXED_WIDTH) |
| ui/sidepanel/__init__.py | ui |
| tests/ui/test_prompt_manager_ui.py | tests |
| tests/state_consistency/test_prompt_consistency.py | tests |

### AgentDebugPanel

| Konsument | Herkunft |
|-----------|----------|
| chat_side_panel.py | ui |
| ui/debug/__init__.py | ui |
| tests/ui/test_debug_panel_ui.py | tests |
| tests/cross_layer/test_debug_view_matches_failure_events.py | tests |
| tests/async_behavior/test_debug_clear_during_refresh.py | tests |

### Abhängigkeitsgraph

```
ChatSidePanel
├── ModelSettingsPanel
│   └── prompt_manager_panel._PROMPTS_PANEL_FIXED_WIDTH
├── PromptManagerPanel  [LEAF – keine ui-Abhängigkeiten]
└── AgentDebugPanel
    ├── AgentActivityView      [LEAF]
    ├── EventTimelineView      [LEAF]
    ├── ModelUsageView         [LEAF]
    ├── ToolExecutionView      [LEAF]
    └── TaskGraphView          [LEAF]
```

---

## 10. Empfohlene Migrationsreihenfolge

### Phase A: Leaf-Module (keine ui-Abhängigkeiten)

1. **prompt_manager_panel.py** → gui/domains/operations/prompt_studio/panels/ (oder chat/panels)
2. **agent_activity_view.py** → gui/domains/runtime_debug/panels/
3. **event_timeline_view.py** → gui/domains/runtime_debug/panels/
4. **model_usage_view.py** → gui/domains/runtime_debug/panels/
5. **tool_execution_view.py** → gui/domains/runtime_debug/panels/
6. **task_graph_view.py** → gui/domains/runtime_debug/panels/

### Phase B: Abhängige Panels

7. **model_settings_panel.py** → gui/domains/settings/ oder control_center/ (importiert _PROMPTS_PANEL_FIXED_WIDTH aus gui prompt_manager_panel)
8. **agent_debug_panel.py** → gui/domains/runtime_debug/panels/ (importiert 5 Views aus gui)

### Phase C: ChatSidePanel

9. **chat_side_panel.py** → gui/domains/operations/chat/panels/ (importiert alle Sub-Panels aus gui)

### Phase D: chat_widget

10. **chat_widget.py** – Import von ChatSidePanel auf gui umstellen, KNOWN_GUI_UI_VIOLATIONS bereinigen

---

## 11. Welche Datei zuerst migrieren?

**Erste Migration:** `app/ui/sidepanel/prompt_manager_panel.py`

Begründung:
- Leaf-Modul (keine ui-Imports)
- Wird von model_settings_panel für _PROMPTS_PANEL_FIXED_WIDTH benötigt
- Kann parallel zu den 5 Debug-Views migriert werden

**Alternative erste Migration:** Die 5 ui.debug-Views (agent_activity_view, event_timeline_view, model_usage_view, tool_execution_view, task_graph_view) – ebenfalls Leaf-Module. Können parallel zu prompt_manager_panel migriert werden.

---

## 12. Blockierende Abhängigkeiten

| Datei | Blockiert durch |
|-------|-----------------|
| model_settings_panel | prompt_manager_panel (_PROMPTS_PANEL_FIXED_WIDTH) |
| agent_debug_panel | 5 Debug-Views |
| chat_side_panel | ModelSettingsPanel, PromptManagerPanel, AgentDebugPanel |

---

## 13. ChatSidePanel danach sicher migrierbar?

**Ja**, sobald alle drei Sub-Panels migriert sind:

1. ModelSettingsPanel → gui
2. PromptManagerPanel → gui
3. AgentDebugPanel + 5 Views → gui

Dann kann ChatSidePanel nach gui migriert werden, ohne app.ui zu importieren. Der gui→ui-Verstoß in chat_widget wird beseitigt, indem chat_widget ChatSidePanel aus gui importiert.

---

## 14. Risiken

| Risiko | Bewertung |
|--------|-----------|
| _PROMPTS_PANEL_FIXED_WIDTH Zirkularität | Niedrig – prompt_manager_panel hat keine Abhängigkeit von model_settings_panel; Reihenfolge: prompt_manager zuerst |
| PromptManagerPanel vs. Prompt Studio | Mittel – unterschiedliche UI-Struktur; beide nutzen PromptService; keine funktionale Überschneidung, aber gleiche Domäne |
| runtime_debug Struktur | Niedrig – gui/domains/runtime_debug existiert; AgentDebugPanel + Views passen als neue Panels |
| Test-Anpassungen | Mittel – tests importieren direkt aus app.ui.sidepanel und app.ui.debug; müssen auf gui umgestellt werden |
