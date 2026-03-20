# Settings and Workspaces Hardening – Abschlussreport

**Stand:** 2026-03-17  
**Vorlage:** SETTINGS_AND_WORKSPACES_HARDENING_ANALYSIS.md

---

## 1. Analysierte Bereiche

| Bereich | Pfad | Ergebnis |
|---------|------|----------|
| Settings Core | `app/core/config/settings.py`, `settings_backend.py` | Vollständig, Backend-Abstraktion sauber |
| QSettings-Integration | `app/gui/qsettings_backend.py` | Verdrahtet, GUI-Bootstrap nutzt create_qsettings_backend() |
| Settings-Kategorien | `app/gui/domains/settings/categories/` | 8 Kategorien, davon 4 mit Platzhaltern |
| Settings-Panels | `app/gui/domains/settings/panels/` | ThemeSelectionPanel funktional, weitere ergänzt |
| Workspaces | `app/gui/domains/control_center/`, `operations/` | cc_models, cc_providers, cc_agents produktiv; data_stores, tools, agents mit Demo-Labels |
| Inspector | `app/gui/inspector/` | Kategorie-spezifische Inspectors für Settings ergänzt |

---

## 2. Umgesetzte Härtungen

### 2.1 Theme-Persistenz

- **AppSettings**: `theme_id` ergänzt (light_default, dark_default), Normalisierung von Legacy `theme` (light/dark)
- **ThemeSelectionPanel**: Persistiert Theme bei Änderung in AppSettings (`_persist_theme()`)
- **run_gui_shell.py**: Lädt Theme zuerst aus `infra.settings.theme_id`, Fallback auf CLI/Env

### 2.2 AI Models Category

- **AIModelsSettingsPanel**: Neues Panel mit Modell-Combo, Temperatur, Max Tokens, Think-Mode
- Asynchrones Laden der Modellliste über ModelService
- Automatisches Speichern bei Änderung

### 2.3 Data Category

- **DataSettingsPanel**: RAG (aktiv, Space, Top-K), Self-Improving, Prompt-Speicherart, Prompt-Verzeichnis, Löschbestätigung
- Vollständig an AppSettings gebunden, automatisches Speichern

### 2.4 Advanced Category

- **AdvancedSettingsPanel**: Debug-Panel-Checkbox (`debug_panel_enabled`)
- Entfernt: Platzhaltertexte „(In Entwicklung)“

### 2.5 Application Category

- Platzhaltertexte bereinigt: „Zukünftige Optionen“ → „System“, „Keine Backend-Verbindung“ → „Backend-Verbindung wird bei Bedarf hergestellt“

### 2.6 Privacy Category

- Text präzisiert: Hinweis auf API-Keys im Legacy-Dialog oder .env

### 2.7 Inspector pro Settings-Kategorie

- **SettingsWorkspace**: `_update_inspector(category_id)` bei Kategorie-Wechsel
- Inspectors für: settings_appearance (AppearanceInspector), settings_ai_models (ModelsSettingsInspector), settings_advanced (AdvancedSettingsInspector), settings_application (SystemSettingsInspector)

### 2.8 Control Center Demo-Labels

- „Demo-Daten“ → „Vorschau (Stores/Agenten/Tools bei Verbindung)“ in data_stores_panels, agents_panels, tools_panels

---

## 3. Bewusst nicht umgesetzt

| Punkt | Begründung |
|-------|------------|
| Project/Workspace Categories | EmptyStateWidget bleibt; geplant für spätere Version |
| Privacy: API-Key-UI in Kategorie | Vermeidung von Duplikation; API-Key bleibt im Legacy-SettingsDialog / .env |
| Echte Daten in Data Stores / Agents / Tools | Aufwand vs. Nutzen; Vorschau-Label klärt Erwartung |
| ComfyUI / Pipeline-Ausbau | Explizit außerhalb des Tasks |

---

## 4. Aktualisierte Tests

| Test | Beschreibung |
|------|--------------|
| `tests/unit/test_settings_theme_persistence.py` | theme_id Default, Normalisierung, Persistenz, Roundtrip |
| `tests/smoke/test_settings_workspace_smoke.py` | Import und Erstellung von SettingsWorkspace, AIModelsSettingsPanel, DataSettingsPanel, AdvancedSettingsPanel |
| `tests/test_model_settings_bindings.py` | Shared InMemoryBackend für korrekte Unit-Tests |
| `tests/test_app.py` | test_settings_storage mit shared Backend und theme_id |

---

## 5. Verbleibende Restpunkte

| Restpunkt | Priorität | Empfehlung |
|-----------|-----------|------------|
| Application Category: dynamischer Ollama-Status | Niedrig | Optional: QTimer + ModelService.get_models() für „Ollama verbunden“ |
| Privacy: API-Key-Verwaltung in Shell | Mittel | Falls Legacy-Dialog abgelöst wird |
| Project/Workspace Categories | Niedrig | Bei Projekt-/Workspace-Scoping |
| SettingsDialog (Legacy): Theme-Combo light/dark | Niedrig | Mapping zu light_default/dark_default bei Nutzung |

---

## 6. Architektur-Konsistenz

- Keine GUI→Provider-Kopplung
- Settings über AppSettings + Backend-Abstraktion
- Keine parallelen Zustandsquellen für persistierte Settings
- Theme: ThemeManager und AppSettings.theme_id synchron (ThemeSelectionPanel schreibt in beide Richtungen)

---

## 7. Empfohlene nächste fachliche Ausbauziele

1. **ComfyUI-Integration** (wenn Unterbau stabil)
2. **Project/Workspace-Scoping** für Settings
3. **API-Key-Verwaltung** in Shell-Settings (Ersatz für Legacy-Dialog)
4. **Dynamischer Runtime-Status** in Application Category
