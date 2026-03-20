# UI Compatibility Cleanup Audit

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Kontext:** Nach Abschluss Agents-, Chat- und Sidepanel-Migration

---

## Scope

- `app/ui/agents/`
- `app/ui/chat/`
- `app/ui/sidepanel/`
- `app/ui/debug/`

---

## app/ui/agents/

### app/ui/agents/__init__.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export-Hub |
| **Inhalt** | Re-exportiert aus `app.gui.domains.control_center.agents_ui`: AgentManagerPanel, AgentManagerDialog, AgentListPanel, AgentListItem, AgentProfilePanel, AgentAvatarWidget, AgentProfileForm, AgentCapabilitiesEditor, AgentPerformanceTab |
| **Konsumenten** | Keine – kein produktiver Code, keine Tests importieren von `app.ui.agents` |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export-Hub ohne Konsumenten. main.py nutzt bereits `app.gui.domains.control_center.agents_ui` für AgentManagerDialog. Tests nutzen gui-Pfade. |

### app/ui/agents/agent_manager_panel.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Inhalt** | `from app.gui.domains.control_center.agents_ui.agent_manager_panel import AgentManagerPanel, AgentManagerDialog` |
| **Konsumenten** | Nur `app.ui.agents.__init__.py` (intern) |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

### app/ui/agents/agent_list_panel.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Nur `app.ui.agents.__init__.py` (intern) |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

### app/ui/agents/agent_profile_panel.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Nur `app.ui.agents.__init__.py` (intern) |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

### app/ui/agents/agent_avatar_widget.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Nur `app.ui.agents.__init__.py` (intern) |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

### app/ui/agents/agent_form_widgets.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Nur `app.ui.agents.__init__.py` (intern) |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

### app/ui/agents/agent_list_item.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Nur `app.ui.agents.__init__.py` (intern) |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

### app/ui/agents/agent_performance_tab.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Nur `app.ui.agents.__init__.py` (intern) |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

### app/ui/agents/legacy/__init__.py

| Attribut | Wert |
|----------|------|
| **Typ** | Dokumentation / leerer Hub |
| **Inhalt** | Nur Docstring, keine Exports |
| **Konsumenten** | Keine |
| **Klassifikation** | **MANUAL_REVIEW** |
| **Begründung** | Verweist auf legacy-Module. Kein aktiver Import. |

### app/ui/agents/legacy/agent_skills_panel.py

| Attribut | Wert |
|----------|------|
| **Typ** | Legacy mit eigener Logik |
| **Inhalt** | Vollständige UI-Implementierung (~240 Zeilen) |
| **Konsumenten** | Keine – nicht importiert |
| **Klassifikation** | **MANUAL_REVIEW** |
| **Begründung** | Toter Code aus altem AgentWorkspace. Deprecated, manual_review_required. Löschen nach Bestätigung. |

### app/ui/agents/legacy/agent_activity_panel.py

| Attribut | Wert |
|----------|------|
| **Typ** | Legacy mit eigener Logik |
| **Konsumenten** | Keine |
| **Klassifikation** | **MANUAL_REVIEW** |
| **Begründung** | Toter Code, deprecated. |

### app/ui/agents/legacy/agent_editor_panel.py

| Attribut | Wert |
|----------|------|
| **Typ** | Legacy mit eigener Logik |
| **Konsumenten** | Keine |
| **Klassifikation** | **MANUAL_REVIEW** |
| **Begründung** | Toter Code, deprecated. |

### app/ui/agents/legacy/agent_runs_panel.py

| Attribut | Wert |
|----------|------|
| **Typ** | Legacy mit eigener Logik |
| **Konsumenten** | Keine |
| **Klassifikation** | **MANUAL_REVIEW** |
| **Begründung** | Toter Code, deprecated. |

---

## app/ui/chat/

### app/ui/chat/__init__.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export-Hub (gemischt) |
| **Inhalt** | Aggregiert aus ui.chat.* und app.gui.* (chat_message_widget, topic_editor_dialog, topic_actions, chat_item_context_menu aus gui; chat_composer_widget, chat_header_widget, conversation_view, chat_list_item, chat_topic_section aus ui.chat) |
| **Konsumenten** | Keine – kein produktiver Code importiert von `app.ui.chat` |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | chat_widget, chat_workspace, chat_navigation_panel nutzen gui direkt. Package ungenutzt. |

### app/ui/chat/chat_composer_widget.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Nur `app.ui.chat.__init__.py` (intern) |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

### app/ui/chat/chat_header_widget.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Nur `app.ui.chat.__init__.py` (intern) |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

### app/ui/chat/conversation_view.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Nur `app.ui.chat.__init__.py` (intern) |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

### app/ui/chat/chat_topic_section.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Nur `app.ui.chat.__init__.py` (intern) |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

### app/ui/chat/chat_list_item.py

| Attribut | Wert |
|----------|------|
| **Typ** | Legacy mit eigener Logik |
| **Inhalt** | Eigene Implementierung von ChatListItemWidget und format_relative_time (~130 Zeilen). Gui-Version in app.gui.domains.operations.chat.panels.chat_list_item.py |
| **Konsumenten** | Nur `app.ui.chat.__init__.py` (intern) |
| **Klassifikation** | **MANUAL_REVIEW** |
| **Begründung** | Duplikat zur gui-Version. gui nutzt eigene chat_list_item. Kann nach Löschung von ui.chat.__init__ entfernt werden. |

### app/ui/chat/chat_message_widget.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Nur `app.ui.chat.__init__.py` (intern) |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

### app/ui/chat/chat_item_context_menu.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Nur `app.ui.chat.__init__.py` (intern) |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

### app/ui/chat/topic_actions.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Nur `app.ui.chat.__init__.py` (intern) |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

### app/ui/chat/topic_editor_dialog.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Nur `app.ui.chat.__init__.py` (intern) |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

---

## app/ui/sidepanel/

### app/ui/sidepanel/__init__.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export-Hub |
| **Inhalt** | Re-exportiert ChatSidePanel, ModelSettingsPanel, PromptManagerPanel aus ui.sidepanel.* |
| **Konsumenten** | Keine – chat_widget importiert direkt aus gui |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export-Hub ohne Konsumenten. |

### app/ui/sidepanel/chat_side_panel.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Inhalt** | `from app.gui.domains.operations.chat.panels.chat_side_panel import *` |
| **Konsumenten** | Nur `app.ui.sidepanel.__init__.py` (intern) |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

### app/ui/sidepanel/model_settings_panel.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Nur `app.ui.sidepanel.__init__.py` (intern) |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

### app/ui/sidepanel/prompt_manager_panel.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Nur `app.ui.sidepanel.__init__.py` (intern) |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

---

## app/ui/debug/

### app/ui/debug/__init__.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export-Hub |
| **Inhalt** | Re-exportiert AgentDebugPanel aus ui.debug.agent_debug_panel |
| **Konsumenten** | Keine – AgentDebugPanel wird überall aus gui importiert |
| **Klassifikation** | **KEEP_TEMP** |
| **Begründung** | Hub selbst ungenutzt, aber event_timeline_view wird von scripts/tests importiert. __init__ kann später entfernt werden. |

### app/ui/debug/agent_debug_panel.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Nur `app.ui.debug.__init__.py` (intern) |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

### app/ui/debug/agent_activity_view.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Keine (agent_debug_panel importiert aus gui) |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

### app/ui/debug/event_timeline_view.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | scripts/qa/checks.py, tests/meta/test_event_type_drift.py (importieren _event_display_text) |
| **Klassifikation** | **KEEP_TEMP** |
| **Begründung** | Re-Export, aber noch 2 Konsumenten. Nach Umstellung auf gui-Pfad → REMOVE_NOW. |

### app/ui/debug/model_usage_view.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Keine |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

### app/ui/debug/tool_execution_view.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Keine |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

### app/ui/debug/task_graph_view.py

| Attribut | Wert |
|----------|------|
| **Typ** | Re-Export |
| **Konsumenten** | Keine |
| **Klassifikation** | **REMOVE_NOW** |
| **Begründung** | Reiner Re-Export, keine externen Konsumenten. |

---

## Zusammenfassung

### 1. REMOVE_NOW Kandidaten

Diese Dateien sind reine Re-Exports ohne produktive Konsumenten und können nach Bestätigung entfernt werden:

**app/ui/agents/**
- `__init__.py`
- `agent_manager_panel.py`
- `agent_list_panel.py`
- `agent_profile_panel.py`
- `agent_avatar_widget.py`
- `agent_form_widgets.py`
- `agent_list_item.py`
- `agent_performance_tab.py`

**app/ui/chat/**
- `__init__.py`
- `chat_composer_widget.py`
- `chat_header_widget.py`
- `conversation_view.py`
- `chat_topic_section.py`
- `chat_message_widget.py`
- `chat_item_context_menu.py`
- `topic_actions.py`
- `topic_editor_dialog.py`

**app/ui/sidepanel/**
- `__init__.py`
- `chat_side_panel.py`
- `model_settings_panel.py`
- `prompt_manager_panel.py`

**app/ui/debug/**
- `agent_debug_panel.py`
- `agent_activity_view.py`
- `model_usage_view.py`
- `tool_execution_view.py`
- `task_graph_view.py`

### 2. KEEP_TEMP Kandidaten

Diese Dateien haben noch Konsumenten; nach Import-Umstellung → REMOVE_NOW:

| Datei | Konsumenten | Umstellung |
|-------|-------------|------------|
| `app/ui/debug/event_timeline_view.py` | scripts/qa/checks.py, tests/meta/test_event_type_drift.py | Import von `_event_display_text` auf `app.gui.domains.runtime_debug.panels.event_timeline_view` umstellen |
| `app/ui/debug/__init__.py` | Keine (nur intern) | Kann mit event_timeline_view-Umstellung entfernt werden |

### 3. KEEP_AS_COMPAT Kandidaten

Keine. Alle Compatibility-Entry-Points sind derzeit ungenutzt.

### 4. MANUAL_REVIEW Kandidaten

| Datei | Begründung |
|-------|------------|
| `app/ui/agents/legacy/__init__.py` | Leerer Hub für deprecated legacy-Module |
| `app/ui/agents/legacy/agent_skills_panel.py` | Toter Code, eigene Logik, deprecated |
| `app/ui/agents/legacy/agent_activity_panel.py` | Toter Code, deprecated |
| `app/ui/agents/legacy/agent_editor_panel.py` | Toter Code, deprecated |
| `app/ui/agents/legacy/agent_runs_panel.py` | Toter Code, deprecated |
| `app/ui/chat/chat_list_item.py` | Eigene Logik, Duplikat zu gui. Nur von ui.chat.__init__ genutzt. Nach Löschung von ui.chat entbehrlich. |

### 5. Empfohlene sichere Löschreihenfolge

1. **Phase 1 – app/ui/sidepanel/** (komplett)
   - Keine externen Konsumenten
   - chat_widget nutzt gui direkt

2. **Phase 2 – app/ui/agents/** (ohne legacy/)
   - Alle Re-Exports ohne Konsumenten
   - main.py, Tests nutzen gui

3. **Phase 3 – app/ui/chat/** (ohne chat_list_item)
   - Alle Re-Exports außer chat_list_item
   - chat_list_item: MANUAL_REVIEW (Duplikat)

4. **Phase 4 – app/ui/debug/** (nach Import-Umstellung)
   - Zuerst: scripts/qa/checks.py und tests/meta/test_event_type_drift.py auf gui umstellen
   - Dann: event_timeline_view, __init__, restliche Views

5. **Phase 5 – app/ui/agents/legacy/** (MANUAL_REVIEW)
   - Nach Bestätigung: agent_skills_panel, agent_activity_panel, agent_editor_panel, agent_runs_panel, __init__.py

6. **Phase 6 – app/ui/chat/chat_list_item.py** (MANUAL_REVIEW)
   - Nach Löschung von ui.chat.__init__

### 6. Empfohlene Reihenfolge für Import-Umstellungen vor Löschung

1. **scripts/qa/checks.py**
   - `from app.ui.debug.event_timeline_view import _event_display_text`
   - → `from app.gui.domains.runtime_debug.panels.event_timeline_view import _event_display_text`

2. **tests/meta/test_event_type_drift.py**
   - `from app.ui.debug.event_timeline_view import _event_display_text`
   - → `from app.gui.domains.runtime_debug.panels.event_timeline_view import _event_display_text`

Nach diesen zwei Umstellungen kann `app/ui/debug/` vollständig entfernt werden.

---

## Hinweise

- **app/ui/command_center/** und **app/ui/settings_dialog** sind nicht im Scope dieses Audits.
- main.py importiert weiterhin von app.ui.command_center und app.ui.settings_dialog.
- Die Löschung von REMOVE_NOW-Kandidaten sollte in separaten, kleinen Commits erfolgen, mit Testlauf nach jeder Phase.
