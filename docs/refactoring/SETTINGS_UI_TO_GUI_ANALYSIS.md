# Settings-Subsystem: UI → GUI Migration – Ist-Analyse

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Phase:** 1 – Ist-Analyse

---

## 1. Ausgangslage

### 1.1 Legacy-Bereiche

| Pfad | Typ | Inhalt |
|------|-----|--------|
| `app/ui/settings/` | Verzeichnis | Re-Exports aus `app.gui.domains.settings` |
| `app/ui/settings_dialog.py` | Modul | `SettingsDialog` – modal Dialog für Legacy MainWindow |

### 1.2 Bereits migriert (kanonisch unter gui)

- `app/gui/domains/settings/` – vollständige Implementierung:
  - `settings_screen.py` – SettingsScreen (Full-page)
  - `settings_workspace.py` – SettingsWorkspace
  - `navigation.py` – SettingsNavigation
  - `settings_nav.py` – SettingsNav
  - `categories/` – ApplicationCategory, AppearanceCategory, AIModelsCategory, etc.
  - `panels/` – ModelSettingsPanel, ThemeSelectionPanel
  - `workspaces/` – BaseSettingsWorkspace, ModelsWorkspace, etc.

---

## 2. Analyse `app/ui/settings/`

### 2.1 Enthaltene Dateien

| Datei | Inhalt | Klassifikation |
|-------|--------|----------------|
| `__init__.py` | Re-Export: SettingsWorkspace, SettingsNavigation | REMOVE_DEAD |
| `settings_navigation.py` | Re-Export aus gui navigation | REMOVE_DEAD |
| `settings_workspace.py` | Re-Export aus gui settings_workspace | REMOVE_DEAD |
| `categories/__init__.py` | Re-Export aus gui categories | REMOVE_DEAD |
| `categories/base_category.py` | Re-Export BaseSettingsCategory | REMOVE_DEAD |
| `categories/*_category.py` | Re-Exports (8 Dateien) | REMOVE_DEAD |

### 2.2 Externe Konsumenten

**Keine.** Kein produktiver Code importiert `app.ui.settings` oder Untermodule.

- `app.gui.bootstrap` importiert `SettingsScreen` aus `app.gui.domains.settings`
- `app.gui.domains.settings.settings_screen` importiert direkt aus gui
- Tests nutzen `host.widget(...)` – kein direkter Import von app.ui.settings

---

## 3. Analyse `app/ui/settings_dialog.py`

### 3.1 Inhalt

- **Klasse:** `SettingsDialog(QDialog)`
- **Zweck:** Modal-Dialog für Einstellungen (Modell, Temperatur, Tokens, Theme, RAG, API-Key, etc.)
- **Abhängigkeiten:** `AppSettings`, `OllamaClient`, optional `orchestrator`
- **Verwendung:** Nur in Legacy MainWindow (`app.main.MainWindow.open_settings`)

### 3.2 Externe Konsumenten

| Konsument | Import | Verwendung |
|-----------|--------|------------|
| `app/main.py` | `from app.ui.settings_dialog import SettingsDialog` | `open_settings()` – modal Dialog öffnen |

### 3.3 Klassifikation

- **settings_dialog.py:** `MIGRATE_AS_IS` – nach `app/gui/domains/settings/settings_dialog.py` verschieben

---

## 4. Importbeziehungen (settings_dialog.py)

- `app.core.config.settings` – AppSettings
- `app.providers.ollama_client` – OllamaClient
- `app.providers.cloud_ollama_provider` – get_ollama_api_key, CloudOllamaProvider
- `app.core.models.registry` – get_registry (lazy in update_models)

Alle Abhängigkeiten sind `core` oder `providers` – keine gui→ui-Verletzung bei Migration.

---

## 5. Zielstruktur

### 5.1 Gewählte Struktur

- **app/ui/settings/** → **vollständig entfernen** (nur Re-Exports, keine Konsumenten)
- **app/ui/settings_dialog.py** → **app/gui/domains/settings/settings_dialog.py** (1:1-Migration)

### 5.2 Keine Änderung an gui-Struktur

Die bestehende gui-Struktur bleibt unverändert. Es wird nur ergänzt:

```
app/gui/domains/settings/
├── __init__.py           # + SettingsDialog re-exportieren
├── settings_dialog.py    # NEU (aus ui)
├── settings_screen.py
├── settings_workspace.py
├── navigation.py
├── settings_nav.py
├── categories/
├── panels/
└── workspaces/
```

---

## 6. Zusammenfassung

| Komponente | Aktion |
|------------|--------|
| `app/ui/settings/` | Entfernen (tote Re-Exports) |
| `app/ui/settings_dialog.py` | Nach gui migrieren, dann entfernen |
| `app/main.py` | Import auf `app.gui.domains.settings.settings_dialog` umstellen |
| Übergangsbrücken | Keine nötig – direkte Umstellung möglich |
