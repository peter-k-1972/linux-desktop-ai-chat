# Sidepanel-Subtree – Phase A Migration Report

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Phase:** A – Leaf-Migration (6 Module)

---

## 1. Migration von prompt_manager_panel nach gui

### Durchgeführt

- **Neue Datei:** `app/gui/domains/operations/prompt_studio/panels/prompt_manager_panel.py`
- **Basis:** `app/ui/sidepanel/prompt_manager_panel.py` (Original)
- **Re-Export:** `app/ui/sidepanel/prompt_manager_panel.py` → `from app.gui.domains.operations.prompt_studio.panels.prompt_manager_panel import *`

### Änderungen

- Keine funktionalen Änderungen
- Keine Designänderungen
- Absolute Imports ab `app` (bereits vorhanden: `app.prompts`)
- Keine Imports aus `app.ui.*`
- Konstanten vollständig übernommen: `_PROMPTS_PANEL_FIXED_WIDTH`, `_BUTTON_WIDTH_IF_FIT`
- Signale unverändert: `prompt_apply_requested`, `prompt_as_system_requested`, `prompt_to_composer_requested`
- `__all__` ergänzt für Re-Export: `PromptManagerPanel`, `PromptListWidget`, `PromptEditorWidget`, `PromptPreviewWidget`, `_PROMPTS_PANEL_FIXED_WIDTH`

### Konsumenten

- `app/ui/sidepanel/__init__.py` – Re-Export PromptManagerPanel (unverändert)
- `app/ui/sidepanel/chat_side_panel.py` – Import über ui (Re-Export)
- `app/ui/sidepanel/model_settings_panel.py` – Import `_PROMPTS_PANEL_FIXED_WIDTH` über ui (Re-Export)

---

## 2. Migration der 5 Debug Leaf-Views nach gui

### Durchgeführt

| Original (ui) | Neu (gui) |
|---------------|-----------|
| `app/ui/debug/agent_activity_view.py` | `app/gui/domains/runtime_debug/panels/agent_activity_view.py` |
| `app/ui/debug/event_timeline_view.py` | `app/gui/domains/runtime_debug/panels/event_timeline_view.py` |
| `app/ui/debug/model_usage_view.py` | `app/gui/domains/runtime_debug/panels/model_usage_view.py` |
| `app/ui/debug/tool_execution_view.py` | `app/gui/domains/runtime_debug/panels/tool_execution_view.py` |
| `app/ui/debug/task_graph_view.py` | `app/gui/domains/runtime_debug/panels/task_graph_view.py` |

### Re-Exports

Jede ui-Datei wurde auf reinen Re-Export umgestellt:

```python
from app.gui.domains.runtime_debug.panels.<view> import *
```

### Änderungen pro Datei

- Keine funktionalen Änderungen
- Keine Designänderungen
- Absolute Imports ab `app` (bereits: `app.debug`, `app.resources`)
- Keine Imports aus `app.ui.*`
- `event_timeline_view`: `__all__` ergänzt für `_event_display_text` (wird von scripts/qa/checks.py, tests/meta/test_event_type_drift.py genutzt)

### Konsumenten

- `app/ui/debug/agent_debug_panel.py` – Import aller 5 Views über ui (Re-Export)
- `scripts/qa/checks.py` – `_event_display_text` über ui (Re-Export)
- `tests/meta/test_event_type_drift.py` – `_event_display_text` über ui (Re-Export)

---

## 3. Änderungen an Tests

### PromptManagerPanel

| Testdatei | Änderung |
|----------|----------|
| `tests/ui/test_prompt_manager_ui.py` | Import: `app.gui.domains.operations.prompt_studio.panels.prompt_manager_panel`; Patch-Pfad angepasst |
| `tests/state_consistency/test_prompt_consistency.py` | Import: gui-Pfad; Patch-Pfad angepasst |

### Debug-Views

| Testdatei | Änderung |
|----------|----------|
| `tests/ui/test_debug_panel_ui.py` | AgentActivityView, EventTimelineView: Import von gui |
| `tests/cross_layer/test_debug_view_matches_failure_events.py` | EventTimelineView: Import von gui |
| `tests/async_behavior/test_debug_clear_during_refresh.py` | EventTimelineView: Import von gui |

### Unverändert (Compatibility-Prüfung / AgentDebugPanel)

- `AgentDebugPanel` bleibt in ui – alle Tests, die das Panel prüfen, behalten ui-Import
- `scripts/qa/checks.py`, `tests/meta/test_event_type_drift.py` – behalten ui-Import für `_event_display_text` (Compatibility über Re-Export)

---

## 4. Verbleibende blockierende Module

Nicht migriert in Phase A (wie geplant):

| Modul | Grund |
|-------|-------|
| `chat_side_panel.py` | MANUAL_REVIEW, komplexe Abhängigkeiten |
| `model_settings_panel.py` | Abhängigkeit von PromptManagerPanel (jetzt via Re-Export gelöst) |
| `agent_debug_panel.py` | Container für migrierte Views, verbleibt in ui |
| `chat_widget.py` | gui/legacy, importiert ChatSidePanel (bekannte KNOWN_GUI_UI_VIOLATIONS) |

---

## 5. Teststatus

### Auszuführende Tests (manuell)

```bash
pytest tests/architecture
pytest tests/ui/test_prompt_manager_ui.py
pytest tests/state_consistency/test_prompt_consistency.py
pytest tests/ui/test_debug_panel_ui.py
pytest tests/cross_layer/test_debug_view_matches_failure_events.py
pytest tests/async_behavior/test_debug_clear_during_refresh.py
```

Optional:

```bash
pytest tests/regression
pytest
```

### Syntax-Check

- Alle migrierten Module: `python3 -m py_compile` erfolgreich
- Keine Linter-Fehler in den bearbeiteten Dateien

### Hinweis

Die Testumgebung (pytest, pytest-qt, PySide6) war im Ausführungskontext nicht verfügbar. Der Nutzer sollte die Tests lokal ausführen.

---

## 6. Risiken

| Risiko | Bewertung | Mitigation |
|--------|-----------|------------|
| Re-Export-Kette bricht | Niedrig | `import *` mit `__all__`; alle Konsumenten nutzen bestehende ui-Pfade |
| model_settings_panel verliert _PROMPTS_PANEL_FIXED_WIDTH | Niedrig | In gui `__all__` aufgenommen; ui Re-Export liefert Symbol |
| scripts/qa/checks, test_event_type_drift verlieren _event_display_text | Niedrig | In event_timeline_view `__all__` aufgenommen |
| Architekturtest schlägt fehl | Niedrig | Keine neuen gui→ui-Imports; KNOWN_GUI_UI_VIOLATIONS unverändert |

---

## 7. Nächste Schritte

1. **Tests lokal ausführen** – Bestätigung, dass alle genannten Test-Suites PASS
2. **Phase B (optional)** – model_settings_panel migrieren (nach Phase A abhängig von _PROMPTS_PANEL_FIXED_WIDTH aus gui)
3. **ChatSidePanel** – bleibt MANUAL_REVIEW; keine Änderung in Phase A
4. **agent_debug_panel** – kann in späterer Phase migriert werden, sobald ChatSidePanel geklärt ist

---

## Erfolgskriterien Phase A

| Kriterium | Status |
|-----------|--------|
| PromptManagerPanel unter gui/domains/operations/prompt_studio/panels/ | ✓ |
| 5 Debug-Views unter gui/domains/runtime_debug/panels/ | ✓ |
| ui-Originaldateien nur noch Re-Exports | ✓ |
| Direkte Tests nutzen bevorzugt gui-Imports | ✓ |
| Architekturtests (bei Ausführung) PASS | Erwartet |
| Keine funktionale Änderung | ✓ |
| Keine neue gui→ui-Verletzung | ✓ |
