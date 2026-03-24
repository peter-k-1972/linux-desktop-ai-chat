# Settings-Domäne — Bestandsanalyse und Migrationsvorschlag (Schnitt 1)

Technische Arbeitsgrundlage für den ersten **vertikalen** Settings-Schnitt, analog zum Chat-Referenzmuster (`ui_contracts` → `ui_application` Port/Adapter/Presenter → GUI-Sink/Widgets).

---

## A. Bestandsanalyse Settings

### Zwei Einstiegspfade

| Pfad | Rolle | Kopplung |
|------|--------|----------|
| **`settings_dialog.py`** | Modal-Dialog (Legacy-MainWindow) | **`AppSettings`** direkt; **`get_provider_service`** (API-Key .env + async validate); **`get_unified_model_catalog_service`**; Speichern per `settings.save()`; optional **`orchestrator._cloud`** |
| **`settings_screen.py` → `settings_workspace.py`** | Vollbild-Shell mit Kategorien | Weniger monolithisch; Kategorien über Registry; **`get_theme_manager`** in Workspace (Palette für Shell) |

### Kategorien / Panels (Auszug)

- **`categories/application_category.py`** — statische Infotexte, **keine** Services (geringer Migrationsgewinn allein).
- **`categories/appearance_category.py`** → **`panels/theme_selection_panel.py`** — **ThemeManager** (Liste, `set_theme`), Persistenz über **`get_infrastructure().settings`** + `theme_id` / legacy `theme` String.
- **`panels/ai_models_settings_panel.py`**, **`data_settings_panel.py`**, **`advanced_settings_panel.py`** — **`get_infrastructure().settings`**, teils **Unified Model Catalog** (async).
- **`panels/model_settings_panel.py`** — u. a. **`get_model_usage_gui_service`**.
- **`categories/project_category.py`** — **`get_project_service`**.
- **`workspaces/appearance_workspace.py`** — **ThemeManager** + Inspector; parallele Route zur Appearance-Category.

### Starke Kopplungen

1. **`get_infrastructure().settings`** — zentral für „moderne“ Panels (Settings als globales Objekt im Widget).
2. **Theme:** Mischung **ThemeManager (Qt/QSS)** + **AppSettings-Persistenz** im selben Panel (`ThemeSelectionPanel._persist_theme`).
3. **Legacy-Dialog:** Provider + Catalog + viele Felder in einer Datei — für Schnitt 1 **nicht** anfassen.
4. **Async:** Model-Catalog und API-Key-Check — höheres Risiko als reine Theme-Zustände.

### Theme-/Infra-Touchpoints (relevant für Schnitt 1)

- **`app.gui.themes.manager.ThemeManager`** — Laufzeit-Anwendung von QSS (muss im **GUI-** bzw. Sink-Pfad bleiben, nicht im Qt-freien Contract).
- **`app.gui.themes.registry.ThemeRegistry`** — **`list_themes()`** liefert `(id, name)` **ohne** Qt; technisch aus **`app.gui.themes`** (Adapter kann das für Schnitt 1 kapseln; mittelfristig optional Verlagerung der **Metadaten** nach `ui_contracts` oder schlankes nicht-Qt-Modul, um `ui_application → gui` zu reduzieren).

---

## B. Zielschnitt 1 (kleinster sinnvoller vertikaler Schnitt)

**Empfehlung: „Appearance / Theme“ als erster vertikaler Schnitt**

**Begründung**

- **Hoher Architekturgewinn:** Trennt **Persistenz/Leselogik** von **Widget** und macht den gleichen Fluss wie Chat (Command → Presenter → Port → State/Patch → Sink → UI) sichtbar.
- **Überschaubares Risiko:** Kein Async-Catalog, kein Provider-OAuth, eine klar begrenzte Oberfläche (Theme-Liste + Auswahl + Speichern).
- **Keine halbe Symbolpolitik:** Kein „nur Port ohne Presenter“ und kein gleichzeitiges Öffnen von AI-Models + Data + Advanced.

**Explizit nicht in Schnitt 1**

- `SettingsDialog` (gesamte Datei).
- AI-Models-, Data-, Advanced-Panels (Infrastructure/Settings-Objekt bleibt vorerst wie heute).
- `project_category` / ProjectService.
- `ContextInspectionPanel`-ähnliche Debug-Pfade.

---

## C. Contract-Vorschlag (Qt-frei, `ui_contracts`)

Neues Modul z. B. **`app/ui_contracts/workspaces/settings_appearance.py`** (oder `settings.py` mit klarer Namensgebung):

### DTOs

- **`ThemeListEntry`** — `theme_id: str`, `display_name: str`
- **`AppearanceSettingsState`** — z. B. `themes: tuple[ThemeListEntry, ...]`, `selected_theme_id: str`, optional `error: SettingsErrorInfo | None`
- **`SettingsErrorInfo`** — analog Chat: `code`, `message`, `recoverable` (wiederverwendbar oder gemeinsames `ui_contracts`-Modul)

### Commands (UI → Presenter)

- **`LoadAppearanceSettingsCommand`** — Kaltstart / Refresh der Theme-Liste + aktuelle Auswahl aus Persistenz
- **`SelectThemeCommand`** — `theme_id: str` — Nutzer hat Theme gewählt

### Patch (optional, schlank)

- **`AppearanceStatePatch`** — nur geänderte Felder (`selected_theme_id`, `error`, `clear_error`)

Für Schnitt 1 reicht oft **Full-State** nach jedem Command; Patch kann in Schnitt 2 nachgezogen werden.

### Validierung / Fehler

- Ungültige `theme_id`: Presenter setzt **`SettingsErrorInfo`** (`unknown_theme`, …), kein Crash.
- Persistenz fehlgeschlagen: `persist_failed` mit Message für Inline-Label (Sink spiegelt nur).

---

## D. Port- / Adapter-Vorschlag

### `SettingsOperationsPort` (Schnitt 1: nur Appearance-Teilmenge)

Vorschlag: **ein** Port-Modul `app/ui_application/ports/settings_operations_port.py` mit **nur** den für Schnitt 1 nötigen Methoden (weitere Methoden später ergänzen, nicht alles vorfälschen).

**Operationen Schnitt 1**

- **`load_appearance_state() -> AppearanceSettingsState`**
  - Themes: über **ThemeRegistry.list_themes()** (Adapter importiert `app.gui.themes.registry` — **technische Schulden** im Adapter dokumentieren; Alternative später: statische Liste in Contract).
  - Aktuelle Auswahl: **`get_infrastructure().settings.theme_id`** bzw. Fallback über `get_theme_manager().get_current_id()` **nur im Adapter**, nicht im Widget.
- **`persist_theme_choice(theme_id: str) -> None`**
  - Setzt `settings.theme_id`, legacy `settings.theme` via **`theme_id_to_legacy_light_dark`** (Logik wie heute `ThemeSelectionPanel._persist_theme`, aber im Adapter).
  - Ruft **`settings.save()`** auf.

**Bewusst nicht im Port Schnitt 1**

- `ThemeManager.set_theme` — **bleibt GUI** (Sink ruft Manager nach erfolgreichem Persist oder Presenter triggert Sink vor Persist — siehe Fluss unten).

### Adapter

- **`ServiceSettingsAppearanceAdapter`** oder schlicht **`SettingsOperationsAdapter`** mit klarer Schnitt-1-Implementierung.
- Keine neue Fachlogik: nur Verschieben des heutigen Codes aus `ThemeSelectionPanel._persist_theme` + Liste aus Registry.

---

## E. Presenter- / State-Fluss

1. **UI** (`ThemeSelectionPanel` oder dünner Host): emit / ruft **`AppearancePresenter.handle_command(LoadAppearanceSettingsCommand())`** beim Show.
2. **Presenter** ruft **`port.load_appearance_state()`** → **`sink.apply_full_state(state)`** (oder Patch).
3. **Sink** (`SettingsAppearanceSink` o. Ä. in `gui/domains/settings/`): spiegelt State auf QListWidget / Labels; **bei `SelectThemeCommand`**:
   - optional zuerst **`ThemeManager.set_theme(theme_id)`** (sofortige UI), dann **`port.persist_theme_choice(theme_id)`**, bei Fehler Patch mit Error + ggf. Rollback-Anzeige.
   - Reihenfolge abstimmen mit heutigem Verhalten (heute: set_theme dann persist).

Abgleich mit Chat: **Sink** enthält **keine** Geschäftsregeln, nur **UI-Spiegelung** und **imperative** ThemeManager-Aufrufe als „View-Effekt“.

---

## F. Migrationsplan (konkrete Dateien)

### Zu ändern / neu

| Aktion | Datei |
|--------|--------|
| Neu | `app/ui_contracts/workspaces/settings_appearance.py` (DTOs, Commands, optional Patch) |
| Neu | `app/ui_application/ports/settings_operations_port.py` |
| Neu | `app/ui_application/adapters/service_settings_adapter.py` (nur Appearance-Methoden) |
| Neu | `app/ui_application/presenters/settings_appearance_presenter.py` |
| Neu | `app/gui/domains/settings/settings_appearance_sink.py` (oder in `ThemeSelectionPanel` integrierter dünner Sink) |
| Ändern | `app/gui/domains/settings/panels/theme_selection_panel.py` — Port/Presenter injizieren oder von Parent setzen; **Legacy:** ohne Presenter wie heute (optional `appearance_ops=None`) |
| Ändern | `appearance_category.py` / optional `appearance_workspace.py` — Presenter + Adapter instanziieren, Sink binden |
| Optional | `settings_workspace.py` — nur falls zentrale Injektion für alle Kategorien gewünscht (Schnitt 1 kann lokal bei Category bleiben) |

### Legacy-Fallback

- **`ThemeSelectionPanel`** ohne injizierten Presenter: bisheriger Codepfad (**ThemeManager** + **get_infrastructure**) bleibt erhalten (wie `chat_ops is None`).

### Tests

- **Contract:** Serialisierung / Merge (falls Patch).
- **Presenter + Fake-Port:** `Load` / `Select` → erwarteter State.
- **Adapter:** mit gemocktem `get_infrastructure().settings` und ThemeRegistry (oder kleiner Integrationstest).
- **GUI-Smoke:** Panel mit FakePresenter oder Import-Smoke der neuen Module.
- **Kein** vollständiger E2E-Shell-Test Pflicht in Schnitt 1.

### Restschulden nach Schnitt 1

- Adapter-Abhängigkeit **`gui.themes.registry`** — später entkoppeln (Metadaten nach `ui_contracts` oder neutrales Package).
- **Zwei** Appearance-Einstiege (Category + `AppearanceWorkspace`) — angleichen oder einen deprecaten.
- **SettingsDialog** Theme-Combo (`light`/`dark`) — weiter Legacy; später angleichen oder auf globales `theme_id` migrieren.

---

## G. Guardrails

### Architektur

- Erweiterung **`tests/architecture/test_ui_layer_guardrails.py`** oder Config: **`ui_contracts`** ohne Qt (bereits vorhanden); neue Settings-Contract-Datei automatisch abgedeckt.
- Optional: **AST-Regel** „`app/gui/domains/settings/panels/*` importiert nicht `get_infrastructure` wenn `SETTINGS_USE_PORT=1`“ — zu schwer für Schnitt 1; stattdessen **Review-Checkliste**.

### Import-Grenzen

- **`ui_application` Adapter** darf **Services +** (vorerst) **`app.gui.themes.registry`** — in Migrationsnotiz als **Ausnahme** festhalten; Zielbild: Registry-Metadaten ohne `gui`.

### Teststrategie

- **Presenter:** rein unit, FakePort.
- **Port/Adapter:** Mock `AppSettings` / `get_infrastructure`.
- **Sink:** Mock QWidget oder nur Callback-Liste (wie `ChatWorkspaceChatSink`-Tests).

---

## Kurzfassung

| Frage | Antwort |
|-------|---------|
| Erster Schnitt? | **Appearance / Theme** (ThemeSelectionPanel + Persistenz + Liste) |
| Referenz Chat? | Ja: Contract → Port/Adapter → Presenter → Sink → Panel |
| Größtes Risiko vermieden? | Ja (kein Catalog/Async im ersten Schnitt) |
| Legacy? | Panel ohne Injektion = alter Pfad |

Dieses Dokument ist **Planungsstand**; Umsetzung = separates Implementierungs-PR gemäß obiger Dateiliste.
