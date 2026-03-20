# Implementierung: Rechte Seitenleiste (Studio Panel)

## Übersicht der Änderungen

### Neu erstellte Dateien

| Datei | Zweck |
|-------|-------|
| `app/prompts/prompt_models.py` | Datenmodell `Prompt` mit Feldern id, title, category, description, content, tags, prompt_type, created_at, updated_at |
| `app/prompts/prompt_repository.py` | SQLite-Persistenz für Prompts (nutzt `chat_history.db`, eigene Tabelle `prompts`) |
| `app/prompts/prompt_service.py` | Service-Schicht: CRUD, Validierung, Duplizieren |
| `app/prompts/__init__.py` | Modul-Export |
| `app/ui/sidepanel/chat_side_panel.py` | Hauptcontainer der rechten Seitenleiste mit Tabs (Modelle \| Prompts) |
| `app/ui/sidepanel/model_settings_panel.py` | Modell-Einstellungen als Formular (Sektionen A–E) |
| `app/ui/sidepanel/prompt_manager_panel.py` | Promptverwaltung: Liste, Editor, Vorschau, Aktionen |
| `app/ui/sidepanel/__init__.py` | Modul-Export |
| `tests/test_prompt_repository.py` | Unit-Tests für PromptRepository und PromptService |
| `tests/test_model_settings_bindings.py` | Tests für Settings-Sync (web_search, default_role) |

### Geänderte Dateien

| Datei | Änderung |
|-------|----------|
| `app/chat_widget.py` | QSplitter eingeführt: linker Bereich = Conversation + Composer, rechter Bereich = ChatSidePanel. Bindings für settings_changed, prompt_apply, prompt_as_system, prompt_to_composer. |
| `app/ui/chat/chat_composer_widget.py` | Methode `append_text()` für „In Composer einfügen“ ergänzt |
| `app/settings.py` | `web_search` und Persistenz ergänzt |
| `app/resources/styles.py` | Styles für `#chatSidePanel`, `#modelSettingsPanel`, `#promptManagerPanel` |

---

## Aufbau der rechten Seitenleiste

Die Seitenleiste ist ein **ChatSidePanel** mit zwei Tabs:

1. **Tab „Modelle“** – ModelSettingsPanel  
2. **Tab „Prompts“** – PromptManagerPanel  

### Layout

- **Breite:** 360 px (min 320, max 420)
- **Position:** rechts im Hauptbereich, per QSplitter verschiebbar
- **Design:** Karten-Sektionen (SectionCard), keine Gruppenboxen, klare Typografie

### Modell-Einstellungen (Sektion A–E)

| Sektion | Inhalt | Status |
|---------|-------|--------|
| A. Modellzuweisung | Assistant, Thinking, Vision, Code, Overkill (Combos) | UI fertig, Assistant an Settings gebunden |
| B. Routing & Verhalten | Auto-Routing, Cloud, Websuche, Overkill, Standardrolle | An Settings gebunden |
| C. Rollen → Modell | FAST, DEFAULT, CHAT, THINK, CODE, VISION, OVERKILL mit Modell-Dropdown | UI fertig, vorbereitet für Rollen-Mapping |
| D. Provider & Status | Lokal/Cloud, API-Key, Modell verfügbar, letzter Fehler | Anzeige vorbereitet, Status aus load_models |
| E. Erweitert | Temperatur, Top-p, Max Tokens, Timeout, Stream, Retry | Temperatur und Max Tokens an Settings gebunden |

### Promptverwaltung

| Funktion | Status |
|----------|--------|
| Neu, Laden, Speichern, Löschen, Duplizieren | Implementiert |
| Liste mit Suchfeld | Implementiert |
| Editor (Titel, Kategorie, Beschreibung, Inhalt, Tags, Typ) | Implementiert |
| Vorschau (read-only) | Implementiert |
| In Chat übernehmen | Implementiert (Systemnachricht) |
| Als Systemprompt setzen | Implementiert |
| In Composer einfügen | Implementiert |

---

## Datenbindung Modell-Einstellungen

- **AppSettings:** Änderungen im Panel werden in `AppSettings` geschrieben und gespeichert.
- **Header-Sync:** Bei `settings_changed` werden Header-Controls (model_combo, auto_routing, cloud, overkill, web_search) aktualisiert.
- **Modelle:** Nach `load_models()` werden die Modell-Combos im Panel befüllt.

---

## Promptverwaltung – Speicherung

- **Persistenz:** SQLite-Tabelle `prompts` in `chat_history.db`
- **Schema:** id, title, category, description, content, tags, prompt_type, created_at, updated_at
- **PromptRepository:** CRUD-Operationen
- **PromptService:** Validierung, Duplizieren

---

## Vorbereitete / noch nicht verdrahtete Teile

| Bereich | Vorbereitung |
|---------|--------------|
| Rollen-Modell-Mapping | UI vorhanden, Persistenz in Registry/Settings noch offen |
| Top-p, Timeout, Retry | UI vorhanden, Backend-Anbindung offen |
| Provider-Status „letzter Fehler“ | Platzhalter, noch nicht befüllt |
| Kontextfenster-Hinweis | Platzhalter in UI |

---

## Tests

```bash
python3 -m unittest tests.test_prompt_repository -v
```

Die Model-Settings-Tests benötigen PySide6 (z.B. in der venv).
