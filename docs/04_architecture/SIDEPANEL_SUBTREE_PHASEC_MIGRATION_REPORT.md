# Sidepanel-Subtree – Phase C Migration Report

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Phase:** C – Container-Migration (ChatSidePanel)

---

## 1. Migration von ChatSidePanel nach gui

### Durchgeführt

- **Neue Datei:** `app/gui/domains/operations/chat/panels/chat_side_panel.py`
- **Basis:** `app/ui/sidepanel/chat_side_panel.py` (Original)
- **Re-Export:** `app/ui/sidepanel/chat_side_panel.py` → `from app.gui.domains.operations.chat.panels.chat_side_panel import *`

### Änderungen

- Keine funktionalen Änderungen
- Keine Designänderungen
- Absolute Imports ab `app`
- Keine Imports aus `app.ui.*`

### Direkte gui-Imports der Sub-Panels

| Komponente | Import-Pfad |
|------------|-------------|
| ModelSettingsPanel | `app.gui.domains.settings.panels.model_settings_panel` |
| PromptManagerPanel, _PROMPTS_PANEL_FIXED_WIDTH | `app.gui.domains.operations.prompt_studio.panels.prompt_manager_panel` |
| AgentDebugPanel | `app.gui.domains.runtime_debug.panels.agent_debug_panel` |

### Beibehalten

- `app.debug.get_debug_store` – unverändert
- `PromptService` lazy loading in `init_ui` – unverändert
- Signale: `settings_changed`, `prompt_apply_requested`, `prompt_as_system_requested`, `prompt_to_composer_requested` – unverändert

---

## 2. Re-Export in ui/sidepanel/chat_side_panel.py

- **Inhalt:** Reiner Re-Export, keine Logik
- **Code:** `from app.gui.domains.operations.chat.panels.chat_side_panel import *`

---

## 3. ui/sidepanel/__init__.py

- **Status:** Unverändert
- **Import:** `from app.ui.sidepanel.chat_side_panel import ChatSidePanel` – funktioniert über Re-Export
- ChatSidePanel bleibt für Legacy-Konsumenten erreichbar

---

## 4. Umstellung von gui/legacy/chat_widget.py

### Durchgeführt

- **Import geändert von:** `from app.ui.sidepanel.chat_side_panel import ChatSidePanel`
- **Import geändert nach:** `from app.gui.domains.operations.chat.panels.chat_side_panel import ChatSidePanel`
- Keine weitere Umstrukturierung
- Keine Featureänderung

---

## 5. Änderungen an Tests

- **Keine Teständerungen nötig**
- Kein Test importiert ChatSidePanel direkt
- `test_chat_ui.py` nutzt ChatWidget (app.gui.legacy) – ChatWidget erhält ChatSidePanel nun aus gui
- Alle relevanten Tests (ChatWidget, Prompt-Apply, etc.) laufen über die bestehende Kette

---

## 6. Guard-/Violation-Status

### tests/architecture/test_gui_does_not_import_ui.py

- **KNOWN_GUI_UI_VIOLATIONS:** Von `{"gui/legacy/chat_widget.py"}` auf `frozenset()` reduziert
- **Ergebnis:** Keine bekannte gui→ui-Verletzung mehr
- **chat_widget:** Importiert ChatSidePanel nun aus gui

---

## 7. Teststatus

### Auszuführende Tests (manuell)

```bash
pytest tests/architecture
pytest tests/ui/test_chat_ui.py
pytest tests/ui/test_prompt_manager_ui.py
pytest tests/state_consistency/test_prompt_consistency.py
pytest tests/ui/test_debug_panel_ui.py
pytest tests/cross_layer/test_debug_view_matches_failure_events.py
pytest tests/async_behavior/test_debug_clear_during_refresh.py
pytest tests/smoke/test_basic_chat.py
pytest tests/regression
```

Optional: `pytest`

### Syntax-Check

- Alle migrierten Module: `python3 -m py_compile` erfolgreich

---

## 8. Risiken

| Risiko | Bewertung | Mitigation |
|--------|-----------|------------|
| Re-Export-Kette bricht | Niedrig | ui/sidepanel/__init__ importiert weiterhin über ui |
| ChatWidget verliert ChatSidePanel | Niedrig | Direktimport aus gui |
| Zirkuläre Imports | Niedrig | ChatSidePanel importiert nur gui; keine Rückabhängigkeit |

---

## 9. Nächste Schritte

1. **Tests lokal ausführen** – Bestätigung, dass alle genannten Test-Suites PASS
2. **Sidepanel-Subtree abgeschlossen** – Alle Komponenten (ChatSidePanel, ModelSettingsPanel, PromptManagerPanel, AgentDebugPanel + 5 Views) liegen in gui
3. **ui/sidepanel** – Verbleibt als reiner Compatibility Layer (Re-Exports)
4. **Optional:** ui/sidepanel kann langfristig deprecation-hinweise erhalten, wenn alle Konsumenten auf gui umgestellt sind

---

## Erfolgskriterien Phase C

| Kriterium | Status |
|-----------|--------|
| ChatSidePanel unter gui/domains/operations/chat/panels/ | ✓ |
| app/ui/sidepanel/chat_side_panel.py nur noch Re-Export | ✓ |
| ChatSidePanel importiert keine app.ui.* | ✓ |
| gui/legacy/chat_widget.py importiert ChatSidePanel aus gui | ✓ |
| KNOWN_GUI_UI_VIOLATIONS geleert | ✓ |
| Architekturtests (bei Ausführung) PASS | Erwartet |
| Keine funktionalen Änderungen | ✓ |
