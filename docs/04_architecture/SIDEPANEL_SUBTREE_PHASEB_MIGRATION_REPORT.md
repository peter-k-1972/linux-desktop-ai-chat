# Sidepanel-Subtree – Phase B Migration Report

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Phase:** B – Abhängige Panels (ModelSettingsPanel, AgentDebugPanel)

---

## 1. Migration von model_settings_panel nach gui

### Durchgeführt

- **Neue Datei:** `app/gui/domains/settings/panels/model_settings_panel.py`
- **Basis:** `app/ui/sidepanel/model_settings_panel.py` (Original)
- **Re-Export:** `app/ui/sidepanel/model_settings_panel.py` → `from app.gui.domains.settings.panels.model_settings_panel import *`

### Änderungen

- Keine funktionalen Änderungen
- Keine Designänderungen
- Absolute Imports ab `app`
- **Import von _PROMPTS_PANEL_FIXED_WIDTH:** Jetzt direkt aus `app.gui.domains.operations.prompt_studio.panels.prompt_manager_panel` (nicht mehr aus ui)
- Keine Imports aus `app.ui.*`
- Signal `settings_changed` unverändert
- `SectionCard` mit migriert (interner Helper der Panel-Datei)

### Ziel-Domain

`app/gui/domains/settings/panels/` – konsistent mit bestehender settings-Domain (ThemeSelectionPanel, etc.)

### Konsumenten

- `app/ui/sidepanel/__init__.py` – Re-Export ModelSettingsPanel (unverändert)
- `app/ui/sidepanel/chat_side_panel.py` – Import über ui (Re-Export)

---

## 2. Migration von agent_debug_panel nach gui

### Durchgeführt

- **Neue Datei:** `app/gui/domains/runtime_debug/panels/agent_debug_panel.py`
- **Basis:** `app/ui/debug/agent_debug_panel.py` (Original)
- **Re-Export:** `app/ui/debug/agent_debug_panel.py` → `from app.gui.domains.runtime_debug.panels.agent_debug_panel import *`

### Änderungen

- Keine funktionalen Änderungen
- Keine Designänderungen
- Absolute Imports ab `app`
- **Imports der 5 Debug-Views:** Jetzt direkt aus gui:
  - `app.gui.domains.runtime_debug.panels.agent_activity_view`
  - `app.gui.domains.runtime_debug.panels.event_timeline_view`
  - `app.gui.domains.runtime_debug.panels.model_usage_view`
  - `app.gui.domains.runtime_debug.panels.tool_execution_view`
  - `app.gui.domains.runtime_debug.panels.task_graph_view`
- Keine Imports aus `app.ui.*`

### Konsumenten

- `app/ui/debug/__init__.py` – Re-Export AgentDebugPanel (unverändert)
- `app/ui/sidepanel/chat_side_panel.py` – Import über ui (Re-Export)

---

## 3. Änderungen an Imports

### model_settings_panel

| Vorher | Nachher |
|--------|---------|
| `from app.ui.sidepanel.prompt_manager_panel import _PROMPTS_PANEL_FIXED_WIDTH` | `from app.gui.domains.operations.prompt_studio.panels.prompt_manager_panel import _PROMPTS_PANEL_FIXED_WIDTH` |

### agent_debug_panel

| Vorher | Nachher |
|--------|---------|
| `from app.ui.debug.agent_activity_view import AgentActivityView` | `from app.gui.domains.runtime_debug.panels.agent_activity_view import AgentActivityView` |
| `from app.ui.debug.event_timeline_view import EventTimelineView` | `from app.gui.domains.runtime_debug.panels.event_timeline_view import EventTimelineView` |
| `from app.ui.debug.model_usage_view import ModelUsageView` | `from app.gui.domains.runtime_debug.panels.model_usage_view import ModelUsageView` |
| `from app.ui.debug.tool_execution_view import ToolExecutionView` | `from app.gui.domains.runtime_debug.panels.tool_execution_view import ToolExecutionView` |
| `from app.ui.debug.task_graph_view import TaskGraphView` | `from app.gui.domains.runtime_debug.panels.task_graph_view import TaskGraphView` |

---

## 4. Änderungen an Tests

### AgentDebugPanel

| Testdatei | Änderung |
|----------|----------|
| `tests/ui/test_debug_panel_ui.py` | Import: `app.gui.domains.runtime_debug.panels.agent_debug_panel` |
| `tests/cross_layer/test_debug_view_matches_failure_events.py` | Import: gui-Pfad |
| `tests/async_behavior/test_debug_clear_during_refresh.py` | Import: gui-Pfad |

### ModelSettingsPanel

- Keine direkten Komponenten-Tests gefunden – keine Teständerungen nötig

---

## 5. Verbleibende Blocker

| Modul | Status |
|-------|--------|
| `chat_side_panel.py` | Unverändert, MANUAL_REVIEW |
| `chat_widget.py` (gui/legacy) | Bekannte KNOWN_GUI_UI_VIOLATIONS – importiert ChatSidePanel aus ui |
| ChatSidePanel-Migration | Erst nach Phase B sicher migrierbar |

---

## 6. Teststatus

### Auszuführende Tests (manuell)

```bash
pytest tests/architecture
pytest tests/ui/test_debug_panel_ui.py
pytest tests/cross_layer/test_debug_view_matches_failure_events.py
pytest tests/async_behavior/test_debug_clear_during_refresh.py
```

Optional:

```bash
pytest tests/ui/test_prompt_manager_ui.py
pytest tests/state_consistency/test_prompt_consistency.py
pytest tests/regression
pytest
```

### Syntax-Check

- Alle migrierten Module: `python3 -m py_compile` erfolgreich

---

## 7. Risiken

| Risiko | Bewertung | Mitigation |
|--------|-----------|------------|
| Re-Export-Kette bricht | Niedrig | chat_side_panel importiert weiterhin über ui |
| Zirkularer Import (model_settings ↔ prompt_manager) | Niedrig | prompt_manager_panel hat keine Abhängigkeit von model_settings |
| Architekturtest schlägt fehl | Niedrig | Keine neuen gui→ui-Imports; KNOWN_GUI_UI_VIOLATIONS unverändert |

---

## 8. Nächste Schritte

1. **Tests lokal ausführen** – Bestätigung, dass alle genannten Test-Suites PASS
2. **Phase C: ChatSidePanel** – Nach Phase B ist ChatSidePanel migrierbar; alle Sub-Panels (ModelSettingsPanel, PromptManagerPanel, AgentDebugPanel) liegen in gui
3. **chat_widget** – Nach ChatSidePanel-Migration kann gui/legacy/chat_widget auf gui-Import umgestellt werden

---

## Erfolgskriterien Phase B

| Kriterium | Status |
|-----------|--------|
| ModelSettingsPanel unter gui/domains/settings/panels/ | ✓ |
| AgentDebugPanel unter gui/domains/runtime_debug/panels/ | ✓ |
| ui-Originaldateien nur noch Re-Exports | ✓ |
| model_settings_panel importiert _PROMPTS_PANEL_FIXED_WIDTH aus gui | ✓ |
| agent_debug_panel importiert 5 Views aus gui | ✓ |
| Architekturtests (bei Ausführung) PASS | Erwartet |
| Keine neue gui→ui-Verletzung | ✓ |
| chat_side_panel unverändert | ✓ |
