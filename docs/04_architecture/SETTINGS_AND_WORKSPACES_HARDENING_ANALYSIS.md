# Settings and Workspaces Hardening – Analyse

**Stand:** 2026-03-17  
**Ziel:** Vollausbau und Härtung von Settings und Workspaces ohne neue Großfeatures.

---

## 1. Settings-Bereiche – Übersicht

### 1.1 Architektur

| Komponente | Pfad | Beschreibung |
|------------|------|--------------|
| AppSettings | `app/core/config/settings.py` | Zentrales Modell, Qt-frei, Backend-injizierbar |
| SettingsBackend | `app/core/config/settings_backend.py` | Protocol: value/setValue |
| QSettingsBackendAdapter | `app/gui/qsettings_backend.py` | QSettings-Implementierung für Produktion |
| InMemoryBackend | `app/core/config/settings_backend.py` | Für Tests, keine Persistenz |
| init_infrastructure | `app/services/infrastructure.py` | Injiziert Backend; GUI-Bootstrap ruft mit QSettings auf |

### 1.2 Settings-Kategorien (SettingsWorkspace)

| Kategorie | Widget | Status | Persistenz | Wirkung |
|-----------|--------|--------|------------|---------|
| **settings_application** | ApplicationCategory | Platzhalter | — | Keine |
| **settings_appearance** | AppearanceCategory | **Funktional** | ❌ Theme nicht in AppSettings | ThemeManager.set_theme() |
| **settings_ai_models** | AIModelsCategory | Platzhalter "(In Entwicklung)" | ✓ AppSettings | — |
| **settings_data** | DataCategory | Platzhalter "(In Entwicklung)" | ✓ AppSettings | — |
| **settings_privacy** | PrivacyCategory | Platzhalter "(In Entwicklung)" | ✓ AppSettings | — |
| **settings_advanced** | AdvancedCategory | Platzhalter "(In Entwicklung)" | ✓ AppSettings | — |
| **settings_project** | ProjectCategory | EmptyStateWidget | — | Geplant |
| **settings_workspace** | WorkspaceCategory | EmptyStateWidget | — | Geplant |

### 1.3 Theme-Persistenz – Inkonsistenz

- **AppSettings.theme**: Werte `"light"` | `"dark"` (SettingsDialog)
- **ThemeManager**: IDs `"light_default"` | `"dark_default"`
- **run_gui_shell.py**: Lädt Theme aus CLI-Args / Env `LINUX_DESKTOP_CHAT_THEME`, **nicht** aus AppSettings
- **ThemeSelectionPanel**: Nutzt ThemeManager direkt, speichert **nicht** in AppSettings

**Folge:** Theme-Auswahl in Settings wird beim Neustart ignoriert.

### 1.4 SettingsDialog (Legacy MainWindow)

- Vollständig verdrahtet: Modell, Temperatur, Tokens, Think-Mode, Theme, RAG, Prompt, API-Key, Debug-Panel
- Speichert in AppSettings und ruft settings.save() auf
- Theme-Combo: `["light","dark"]` – **Mismatch** mit ThemeManager (`light_default`/`dark_default`)

### 1.5 ModelSettingsPanel

- Existiert in `app/gui/domains/settings/panels/model_settings_panel.py`
- Wird **nicht** von AIModelsCategory genutzt
- Wird in Control Center / Side-Panel verwendet
- Bindet an AppSettings, funktional

---

## 2. Workspaces – Übersicht

### 2.1 Screen-Registrierung (Bootstrap)

| area_id | Screen | Status |
|---------|--------|--------|
| command_center | DashboardScreen | Produktiv |
| project_hub | ProjectHubScreen | Produktiv |
| operations | OperationsScreen | Produktiv |
| control_center | ControlCenterScreen | Produktiv |
| qa_governance | QAGovernanceScreen | Produktiv |
| runtime_debug | RuntimeDebugScreen | Produktiv |
| settings | SettingsScreen | Produktiv |

### 2.2 Operations-Workspaces

| workspace_id | Status | Bemerkung |
|--------------|--------|-----------|
| operations_chat | Produktiv | Chat, Topics, Agents |
| operations_projects | Produktiv | Projektverwaltung |
| operations_knowledge | Produktiv | RAG, Knowledge Bases |
| operations_prompt_studio | Produktiv | Prompts, Library |
| operations_agent_tasks | Produktiv | Agent Tasks |

### 2.3 Control-Center-Workspaces

| workspace_id | Status | Bemerkung |
|--------------|--------|-----------|
| cc_models | Produktiv | Modelle, Ollama-Anbindung |
| cc_providers | Produktiv | Provider-Status |
| cc_agents | Produktiv | Agent-Verwaltung |
| cc_tools | Teilweise | Demo-Daten in tools_panels |
| cc_data_stores | Teilweise | Demo-Daten in data_stores_panels |

### 2.4 Demo-Daten / Platzhalter

| Ort | Inhalt |
|-----|--------|
| `control_center/panels/data_stores_panels.py` | "Demo-Daten", Dummy-Tabelle |
| `control_center/panels/agents_panels.py` | "Demo-Daten" |
| `control_center/panels/tools_panels.py` | "Demo-Daten" |

### 2.5 Inspector-Anbindung Settings

- SettingsWorkspace.setup_inspector speichert nur den Host
- **Keine** kategorie-spezifische Inspector-Aktualisierung beim Wechsel
- Inspectors (AppearanceInspector, ModelsSettingsInspector, etc.) existieren, werden aber nicht eingeblendet

---

## 3. Priorisierung

### Höchster Härtungsnutzen

1. **Theme-Persistenz**: Theme aus AppSettings beim Start laden; ThemeSelectionPanel → AppSettings speichern
2. **AI Models Category**: ModelSettingsPanel oder kompakte Variante einbinden
3. **Data Category**: RAG, Prompt-Speicherung, Prompt-Verzeichnis (aus SettingsDialog)
4. **Advanced Category**: Debug-Panel-Checkbox (debug_panel_enabled)
5. **Inspector pro Kategorie**: Beim Kategorie-Wechsel passenden Inspector anzeigen

### Mittlerer Nutzen

6. **Application Category**: Runtime-Status dynamisch (Ollama-Verbindung)
7. **Privacy Category**: API-Key-Sektion oder Verweis auf zentrale Einstellungen
8. **Demo-Daten**: data_stores, agents, tools – entweder echte Daten oder klar als "Vorschau" kennzeichnen

### Bewusst zurückgestellt

- Project/Workspace Categories: EmptyStateWidget bleibt (geplant für spätere Version)
- ComfyUI, Pipeline-Ausbau: explizit außerhalb dieses Tasks

---

## 4. Architektur-Konsistenz

- **Keine GUI→Provider-Kopplung**: Settings nutzen Services/Infrastructure ✓
- **Settings über Abstraktion**: AppSettings + Backend ✓
- **Keine parallelen Zustandsquellen**: AppSettings ist Single Source of Truth für persistierte Settings
- **Theme-Ausnahme**: ThemeManager ist aktuell zweite Quelle; soll mit AppSettings synchronisiert werden

---

## 5. Empfohlene Umsetzungsreihenfolge

1. Theme-Persistenz (Startup + ThemeSelectionPanel)
2. AI Models Category mit ModelSettingsPanel oder kompakter Variante
3. Data Category mit RAG/Prompt-Panels
4. Advanced Category mit Debug-Panel-Checkbox
5. Inspector pro Settings-Kategorie
6. Application Category: dynamischer Runtime-Status
7. Demo-Daten: Klarstellung oder Ersatz
