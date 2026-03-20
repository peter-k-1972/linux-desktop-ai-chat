# Agents UI Phase 1 – Validierung und Stabilisierung

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Referenz:** AGENTS_UI_PHASE1_MIGRATION_REPORT.md, ARCHITECTURE_GUARD_RULES.md

---

## 1. Import-Audit Ergebnis

### Regel

Module außerhalb von `app/ui/agents/*`, `app/main.py`, `chat_widget.py` dürfen **nicht** `app.ui.agents` importieren. Stattdessen: `app.gui.domains.control_center.agents_ui`.

### Gefundene app.ui.agents Imports

| Modul | Import | Status |
|-------|--------|--------|
| app/main.py | `from app.ui.agents.agent_manager_panel import AgentManagerDialog` | **erlaubt** (main.py in Whitelist) |
| app/ui/agents/* | interne Imports (agent_workspace, agent_library_panel, etc.) | **erlaubt** (intern) |
| tests/state_consistency/test_agent_consistency.py | `from app.ui.agents.agent_manager_panel import AgentManagerPanel` | **gefixt** → gui |
| tests/ui/test_agent_hr_ui.py | agent_manager_panel, agent_profile_panel, agent_list_panel | **gefixt** → gui |
| tests/ui/test_ui_behavior.py | agent_manager_panel, agent_profile_panel, agent_list_panel | **gefixt** → gui |
| tests/regression/test_agent_delete_removes_from_list.py | agent_manager_panel | **gefixt** → gui |
| tests/ui/test_agent_performance_tab.py | agent_performance_tab | **gefixt** → gui |

### chat_widget.py

- **app/gui/legacy/chat_widget.py** importiert **kein** `app.ui.agents`.
- Keine Änderung nötig.

---

## 2. Fixes durchgeführt

| Datei | Änderung |
|-------|----------|
| tests/ui/test_agent_hr_ui.py | `app.ui.agents.*` → `app.gui.domains.control_center.agents_ui.*` |
| tests/ui/test_ui_behavior.py | `app.ui.agents.*` → `app.gui.domains.control_center.agents_ui.*` |
| tests/regression/test_agent_delete_removes_from_list.py | `app.ui.agents.agent_manager_panel` → `app.gui.domains.control_center.agents_ui.agent_manager_panel` |
| tests/ui/test_agent_performance_tab.py | `app.ui.agents.agent_performance_tab` → `app.gui.domains.control_center.agents_ui.agent_performance_tab` |
| tests/state_consistency/test_agent_consistency.py | `app.ui.agents.agent_manager_panel` → `app.gui.domains.control_center.agents_ui.agent_manager_panel` |

---

## 3. Compatibility Layer Prüfung

### app/ui/agents/ – 7 migrierte Dateien

| Datei | Inhalt | Status |
|-------|--------|--------|
| agent_manager_panel.py | Re-Export von AgentManagerPanel, AgentManagerDialog | ✓ nur Re-Export |
| agent_list_panel.py | Re-Export von AgentListPanel | ✓ nur Re-Export |
| agent_list_item.py | Re-Export von AgentListItem | ✓ nur Re-Export |
| agent_profile_panel.py | Re-Export von AgentProfilePanel | ✓ nur Re-Export |
| agent_avatar_widget.py | Re-Export von AgentAvatarWidget | ✓ nur Re-Export |
| agent_form_widgets.py | Re-Export von AgentProfileForm, AgentCapabilitiesEditor | ✓ nur Re-Export |
| agent_performance_tab.py | Re-Export von AgentPerformanceTab | ✓ nur Re-Export |

**Keine Logik, keine Widgets, keine Services** in den 7 Dateien. Nur `from app.gui.domains.control_center.agents_ui.* import ...`.

### app/ui/agents/__init__.py

- Migrierte Komponenten: Import aus `app.gui.domains.control_center.agents_ui`
- Nicht migrierte: Import aus `app.ui.agents.*` (agent_workspace, agent_navigation_panel, etc.)
- **Keine Änderung** – korrekt für Compatibility Layer.

### Nicht migrierte Dateien (remove_later / manual_review)

- agent_workspace.py, agent_navigation_panel.py, agent_library_panel.py, agent_editor_panel.py, agent_runs_panel.py, agent_activity_panel.py, agent_skills_panel.py
- Enthalten **eigene Logik** – nicht Teil des Compatibility Layers für die 7 migrierten Dateien.
- **manual_review_required:** Nein – außerhalb des Phase-1-Scopes.

---

## 4. Workspace Integration

### app/gui/domains/control_center/workspaces/agents_workspace.py

```python
from app.gui.domains.control_center.agents_ui import AgentManagerPanel
```

- Import aus **gui**, nicht aus ui ✓
- Keine Änderung nötig.

---

## 5. Patch Targets in Tests

| Test | Patch Target | Status |
|------|--------------|--------|
| test_agent_hr_ui.py | `app.gui.domains.control_center.agents_ui.agent_manager_panel.ensure_seed_agents` | ✓ bereits gui |
| test_agent_hr_ui.py | `app.gui.domains.control_center.agents_ui.agent_manager_panel.QMessageBox.question` | ✓ bereits gui |
| test_ui_behavior.py | `app.gui.domains.control_center.agents_ui.agent_manager_panel.ensure_seed_agents` | ✓ bereits gui |
| test_agent_delete_removes_from_list.py | `app.gui.domains.control_center.agents_ui.agent_manager_panel.*` | ✓ bereits gui |
| test_agent_consistency.py | `app.gui.domains.control_center.agents_ui.agent_manager_panel.*` | ✓ bereits gui |

**Keine** Patch-Targets mit `app.ui.agents.*` gefunden. Bereits in Phase 1 migriert.

---

## 6. Teststatus

| Suite | Ergebnis |
|-------|----------|
| tests/architecture/ | **12/12 PASS** ✓ |
| tests/ui/test_agent_hr_ui.py | 7 passed ✓ |
| tests/regression/test_agent_delete_removes_from_list.py | 3 passed ✓ |
| tests/state_consistency/test_agent_consistency.py | 2 passed ✓ |
| tests/ui/test_ui_behavior.py | 3 passed ✓ |
| tests/ui/test_agent_performance_tab.py | 1 passed ✓ |

**Gesamt:** 28 Tests passed.

---

## 7. Risiken

| Risiko | Bewertung | Maßnahme |
|--------|-----------|----------|
| main.py nutzt weiterhin ui.agents (AgentManagerDialog) | **niedrig** | Erlaubt – main.py in Whitelist. Legacy-Einstieg; Migration von main.py außerhalb Phase 1. |
| ui/agents/__init__.py exportiert noch nicht migrierte Klassen | **niedrig** | Bewusst – AgentWorkspace etc. sind remove_later/manual_review. |
| agent_library_panel importiert agent_list_panel (Re-Export) | **keins** | agent_list_panel re-exportiert aus gui; funktioniert korrekt. |

---

## 8. manual_review_required

**Keine** Punkte. Alle Änderungen sind reine Import-Korrekturen. Keine komplexen Refactorings, keine neuen Architekturentscheidungen.

---

## 9. Architekturregeln – Verifikation

| Regel | Status |
|-------|--------|
| core darf nichts über gui oder ui wissen | ✓ |
| gui ist kanonische UI-Schicht | ✓ agents_ui unter gui |
| ui nur Compatibility Layer | ✓ 7 Dateien nur Re-Exports |
| gui darf niemals ui importieren | ✓ agents_workspace importiert aus gui |
| absolute imports ab "app" | ✓ |
| tests/architecture 12/12 PASS | ✓ |
