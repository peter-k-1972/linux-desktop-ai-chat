# Agents UI Phase 3 – Stabilisierung

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Referenz:** AGENTS_UI_PHASE2_EXECUTION.md, ARCHITECTURE_GUARD_RULES.md

---

## 1. main.py Import-Fix

| Vorher | Nachher |
|--------|---------|
| `from app.ui.agents.agent_manager_panel import AgentManagerDialog` | `from app.gui.domains.control_center.agents_ui import AgentManagerDialog` |

**Ziel erreicht:** main.py importiert nun direkt aus gui statt über ui-Re-Export.

```
main → gui (agents_ui)
```

---

## 2. Gefundene ui.agents Imports

| Modul | Import | Status |
|-------|--------|--------|
| app/main.py | AgentManagerDialog | **gefixt** → gui |
| app/ui/agents/* | interne Re-Exports | erlaubt |
| tests/* | — | keine app.ui.agents Imports (bereits in Phase 1 auf gui umgestellt) |

**Ergebnis:** Keine weiteren app.ui.agents Imports außerhalb der erlaubten Bereiche.

---

## 3. Neuer Architekturtest

**Datei:** `tests/architecture/test_gui_does_not_import_ui.py`

**Test:** `test_gui_layer_does_not_import_ui_layer`

**Funktion:** Prüft, dass kein Modul unter `app/gui/` etwas aus `app/ui/` importiert.

**Implementierung:**
- Scan aller Python-Dateien unter `app/gui/`
- AST-basierte Extraktion von Importen
- Fehlschlag bei `app.ui.*`-Imports

**Bekannte Ausnahmen (Legacy, Chat-Migration ausstehend):**
- `gui/legacy/chat_widget.py` – app.ui.chat, app.ui.sidepanel
- `gui/domains/operations/chat/panels/chat_navigation_panel.py` – app.ui.chat.chat_topic_section

Diese Dateien sind in `KNOWN_GUI_UI_VIOLATIONS` hinterlegt. Nach Chat-Migration entfernen.

---

## 4. Teststatus

| Suite | Ergebnis |
|-------|----------|
| tests/architecture/ | **13/13 PASS** ✓ |
| tests/ui/test_agent_hr_ui.py | 7 passed ✓ |
| tests/regression/test_agent_delete_removes_from_list.py | 3 passed ✓ |
| tests/state_consistency/test_agent_consistency.py | 2 passed ✓ |
| tests/ui/test_ui_behavior.py | 3 passed ✓ |
| tests/ui/test_agent_performance_tab.py | 1 passed ✓ |

**Gesamt:** 29 Tests passed.

---

## 5. Risiken

| Risiko | Bewertung | Maßnahme |
|--------|-----------|----------|
| gui/legacy/chat_widget importiert ui | **bekannt** | KNOWN_GUI_UI_VIOLATIONS; Chat-Migration geplant |
| chat_navigation_panel importiert chat_topic_section | **bekannt** | KNOWN_GUI_UI_VIOLATIONS; Chat-Migration geplant |
| ui/agents Compatibility Layer | **niedrig** | Nur Re-Exports; main.py nutzt gui direkt |

---

## 6. Durchgeführte Änderungen

| # | Änderung |
|---|----------|
| 1 | main.py: Import von ui.agents → gui.agents_ui |
| 2 | tests/architecture/test_gui_does_not_import_ui.py: neuer Guard-Test |
| 3 | app/ui/agents/__init__.py: Compatibility-Layer-Header ergänzt |
| 4 | app/ui/agents/legacy/__init__.py: deprecated-Header ergänzt |

---

## 7. Ziel nach Phase 3

| Schicht | Status |
|---------|--------|
| gui | Einzige aktive UI-Schicht (agents_ui kanonisch) |
| ui | Reine Compatibility (Re-Exports) |
| legacy | Isolierter Altcode (ui/agents/legacy/) |
| main.py | Importiert AgentManagerDialog direkt aus gui |
