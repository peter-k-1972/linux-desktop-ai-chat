# Chat UI Phase 4 – Sidepanel-Analyse und Migrationsentscheidung

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Referenz:** CHAT_UI_PHASE3_MIGRATION_REPORT.md

---

## 1. Analyse von chat_side_panel.py

### 1.1 Zweck

**Datei:** `app/ui/sidepanel/chat_side_panel.py`

ChatSidePanel ist die rechte Seitenleiste im Chat-Bereich mit drei Tabs:

- **Tab 1 (Modelle):** ModelSettingsPanel – Modell-Einstellungen, Routing, Rollen, Provider
- **Tab 2 (Prompts):** PromptManagerPanel – Promptverwaltung, CRUD, „In Chat übernehmen“, „Als Systemprompt“, „In Composer einfügen“
- **Tab 3 (Debug):** AgentDebugPanel – Agenten-Debug-Ansicht (Activity, Timeline, Model Usage, Tool Execution, Task Graph)

### 1.2 Imports

| Import | Herkunft |
|--------|----------|
| PySide6.QtWidgets, QtCore, QtGui | extern |
| app.resources.styles.get_theme_colors | app |
| app.ui.sidepanel.model_settings_panel.ModelSettingsPanel | **ui** |
| app.ui.sidepanel.prompt_manager_panel.PromptManagerPanel, _PROMPTS_PANEL_FIXED_WIDTH | **ui** |
| app.ui.debug.agent_debug_panel.AgentDebugPanel | **ui** |
| app.debug.get_debug_store | app |
| app.prompts.PromptService | app (lazy in init_ui) |

### 1.3 Abhängigkeiten

```
ChatSidePanel
├── ModelSettingsPanel (ui.sidepanel)
├── PromptManagerPanel (ui.sidepanel)
│   └── _PROMPTS_PANEL_FIXED_WIDTH
├── AgentDebugPanel (ui.debug)
│   └── AgentActivityView, EventTimelineView, ModelUsageView, ToolExecutionView, TaskGraphView (alle ui.debug)
├── get_debug_store (app.debug)
└── PromptService (app.prompts)
```

### 1.4 Wer importiert ChatSidePanel?

| Datei | Herkunft | Art |
|-------|----------|-----|
| app/gui/legacy/chat_widget.py | gui | **einziger aktiver Konsument** |
| app/ui/sidepanel/__init__.py | ui | Re-Export |

### 1.5 Fachliche Zuordnung

- **Chat-Domain:** Ja – ChatSidePanel ist explizit die rechte Seitenleiste des ChatWidget (Conversation links, Sidepanel rechts).
- **Reine UI:** Nein – ChatSidePanel ist ein **Container** mit gemischter Verantwortung:
  - Orchestriert ModelSettingsPanel (Modell/Provider-Logik)
  - Orchestriert PromptManagerPanel (Prompt-CRUD, PromptService)
  - Orchestriert AgentDebugPanel (DebugStore, Event-Views)
- **Seiteneffekte:** Ja – Prompt-Panel emittiert Signale (prompt_apply_requested, prompt_as_system_requested, prompt_to_composer_requested), die ChatWidget verarbeitet.

---

## 2. Referenzprüfung

### 2.1 app.ui.sidepanel

| Datei | Import | Herkunft |
|-------|--------|----------|
| app/gui/legacy/chat_widget.py | chat_side_panel.ChatSidePanel | gui |
| app/ui/sidepanel/__init__.py | chat_side_panel, model_settings_panel, prompt_manager_panel | ui |
| app/ui/sidepanel/chat_side_panel.py | model_settings_panel, prompt_manager_panel | ui |
| app/ui/sidepanel/model_settings_panel.py | prompt_manager_panel._PROMPTS_PANEL_FIXED_WIDTH | ui |
| tests/ui/test_prompt_manager_ui.py | prompt_manager_panel.PromptManagerPanel | tests |
| tests/state_consistency/test_prompt_consistency.py | prompt_manager_panel.PromptManagerPanel | tests |

### 2.2 chat_side_panel / ChatSidePanel

| Datei | Verwendung |
|-------|------------|
| app/gui/legacy/chat_widget.py | Import + Instanziierung |
| app/ui/sidepanel/__init__.py | Re-Export |

**Ergebnis:** Nur `chat_widget` (gui) nutzt ChatSidePanel aktiv. Keine weiteren gui- oder produktiven Konsumenten.

---

## 3. Klassifikation: MANUAL_REVIEW

### 3.1 Entscheidungslogik

| Kriterium | Bewertung |
|-----------|-----------|
| Nur von chat_widget aktiv verwendet | ✓ Ja |
| Reine UI | ✗ Nein – Container mit Sub-Panels |
| Keine unklaren Seiteneffekte | ✗ Signale, Prompt-Service, Debug-Store |

### 3.2 Technischer Grund für MANUAL_REVIEW

**ChatSidePanel importiert app.ui.** Eine einfache Migration nach gui würde bedeuten:

- Neue Datei: `app/gui/domains/operations/chat/panels/chat_side_panel.py`
- Diese Datei müsste weiterhin importieren:
  - `app.ui.sidepanel.model_settings_panel`
  - `app.ui.sidepanel.prompt_manager_panel`
  - `app.ui.debug.agent_debug_panel`

**Folge:** Ein gui-Modul würde app.ui importieren → neuer oder verschobener Architektur-Verstoß. Die Violation würde von `chat_widget` auf `chat_side_panel` verlagert, nicht beseitigt.

### 3.3 Fazit

**Migration in diesem Scope nicht sinnvoll.** Die Verletzung kann nur beseitigt werden, wenn zuerst die Abhängigkeiten migriert werden:

1. ModelSettingsPanel → gui
2. PromptManagerPanel → gui (oder Prompt Studio)
3. AgentDebugPanel + ui.debug-Views → gui (oder Runtime/Debug-Domain)

Erst danach kann ChatSidePanel ohne ui-Imports nach gui migriert werden.

---

## 4. Falls migriert (nicht durchgeführt)

Keine Migration durchgeführt. Siehe Abschnitt 3.

---

## 5. Architektur-Guard-Status

| Status | Beschreibung |
|--------|--------------|
| Unverändert | KNOWN_GUI_UI_VIOLATIONS enthält weiterhin `gui/legacy/chat_widget.py` |
| Unverändert | chat_widget importiert app.ui.sidepanel.chat_side_panel.ChatSidePanel |

---

## 6. Teststatus

| Suite | Ergebnis |
|-------|----------|
| tests/architecture | 13 passed |
| tests/ui/test_chat_ui | 9 passed |
| tests/regression | 16 passed |
| tests/smoke/test_basic_chat | 4 passed |

Keine Änderungen am Code – Tests unverändert bestanden.

---

## 7. Risiken

| Risiko | Bewertung |
|--------|-----------|
| Voreilige Migration | Vermieden – keine Migration durchgeführt |
| Verstoß-Verschiebung | Würde bei einfacher Migration eintreten (gui→ui in neuem Modul) |
| Abhängigkeitskette | Tief – ModelSettingsPanel, PromptManagerPanel, AgentDebugPanel + 5 Debug-Views |

---

## 8. Nächste Schritte

### 8.1 Empfohlene Ziel-Domains

| Komponente | Empfohlene Domain | Begründung |
|------------|------------------|------------|
| ModelSettingsPanel | gui/domains/control_center oder gui/domains/settings | Modell-/Provider-Steuerung |
| PromptManagerPanel | gui/domains/operations/prompt_studio | Bereits Prompt Studio Workspace |
| AgentDebugPanel | gui/domains/runtime oder gui/debug | Debug/Runtime-Ansicht |
| ChatSidePanel | gui/domains/operations/chat/panels | Nach Migration der Sub-Panels |

### 8.2 Migrationsreihenfolge (Vorschlag)

1. **ModelSettingsPanel** nach gui migrieren (Control Center oder Settings)
2. **PromptManagerPanel** prüfen – evtl. bereits in Prompt Studio integrierbar
3. **AgentDebugPanel** und ui.debug-Views nach gui migrieren
4. **ChatSidePanel** nach gui migrieren, sobald alle Sub-Panels gui-Imports nutzen
5. **chat_widget** auf gui-Import umstellen, KNOWN_GUI_UI_VIOLATIONS bereinigen

### 8.3 manual_review_required

**Status:** manual_review_required

**Gründe:**
- ChatSidePanel hat tiefe ui-Abhängigkeiten
- Einfache Migration würde Verstoß nur verschieben
- Vorherige Migration der Sub-Panels erforderlich

---

**Hinweis:** Keine riskanten Änderungen durchgeführt. Nur Analyse und Dokumentation.
