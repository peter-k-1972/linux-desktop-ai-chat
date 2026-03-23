# settings_usage

Endnutzer-Workflow: **Einstellungen** finden, die **acht Kategorien** durchlaufen und die wichtigsten Schalter setzen. Codebasis: `app/gui/domains/settings/navigation.py`, `settings_workspace.py`, `app/core/config/settings.py`.

## Inhalt

- [Ziel](#ziel)
- [Voraussetzungen](#voraussetzungen)
- [Schritte: Einstellungen öffnen](#schritte-einstellungen-öffnen)
- [Schritte: Kategorien der Reihe nach (8 Stück)](#schritte-kategorien-der-reihe-nach-8-stück)
- [Schritte: Änderung speichern](#schritte-änderung-speichern)
- [Varianten](#varianten)
- [Fehlerfälle](#fehlerfälle)
- [Tipps](#tipps)

**Beteiligte Module**

- [Settings](../modules/settings/README.md) · [GUI](../modules/gui/README.md) · [Kontext](../modules/context/README.md) (Advanced / Kontextmodus) · [Provider](../modules/providers/README.md) (AI/Models, indirekt)

**Siehe auch**

- [Feature: Settings](../../docs/FEATURES/settings.md) · [Workflow: Kontext](context_control.md) · [Hilfe: Einstellungen](../../help/settings/settings_overview.md)

Der Ablauf ist: Einstellungen öffnen → Kategorien der Reihe nach → typische Anpassungen (Theme, Modell, Advanced/Kontext) wie in den Tabellen beschrieben.

## Ziel

Sie passen Darstellung, Modell, Daten, Datenschutz, erweiterte Optionen sowie projekt- und workspacebezogene Seiten an — ohne die technischen Schlüsselnamen kennen zu müssen.

## Voraussetzungen

1. Anwendung gestartet.
2. Sie haben die Berechtigung, Einstellungen auf diesem Rechner zu ändern (kein schreibgeschütztes Nutzerprofil auf OS-Ebene, das QSettings blockiert).

## Schritte: Einstellungen öffnen

1. In der **linken Sidebar** ganz nach unten bzw. zum Eintrag **Settings** (Einstellungen) gehen.
2. Klicken Sie **Settings** — der **volle Bildschirm** wechselt in den Einstellungsmodus (nicht nur ein kleines Pop-up).
3. Layout: **links** die **Kategorienliste**, **Mitte** der Inhalt, **rechts** optional ein kurzer Hilfetext (`SettingsHelpPanel`).

## Schritte: Kategorien der Reihe nach (8 Stück)

Die **Reihenfolge** entspricht der Navigation in der App:

| Nr. | Kategorie (Anzeigename) | Typische Inhalte (was Sie dort erwarten) |
|-----|-------------------------|-------------------------------------------|
| 1 | **Application** | Globale Anwendungsoptionen. |
| 2 | **Appearance** | **Theme**, Darstellung — hier wechseln Sie z. B. hell/dunkel bzw. registrierte Themes (`ThemeManager`). |
| 3 | **AI / Models** | **Standardmodell**, Temperatur, Token-Grenzen, Denkmodus — alles, was die Generierung direkt betrifft. |
| 4 | **Data** | Datenbezogene Optionen (Speicherorte, Pfade — je nach Panel-Inhalt Ihrer Version). |
| 5 | **Privacy** | Datenschutzbezogene Schalter. |
| 6 | **Advanced** | **Debug-Panel**, **Kontext-Inspection**, **Chat-Kontext-Modus** (`off` / `neutral` / `semantic`) — siehe Workflow **context_control**. |
| 7 | **Project** | Einstellungen mit **Projektbezug**. |
| 8 | **Workspace** | Einstellungen mit **Arbeitsbereichsbezug**. |

**IDs im Code** (falls Support danach fragt): `settings_application`, `settings_appearance`, `settings_ai_models`, `settings_data`, `settings_privacy`, `settings_advanced`, `settings_project`, `settings_workspace`.

## Schritte: Änderung speichern

1. In den meisten Panels werden Änderungen beim Umstellen **sofort** an `AppSettings` übergeben und mit **`save()`** persistiert (z. B. Checkboxen und Combos in `AdvancedSettingsPanel`).
2. Schließen Sie die Einstellungen über die **Navigation zurück** zum Arbeitsbereich (Sidebar: wieder **Operations** oder **Chat** wählen).

## Varianten

| Bedarf | Wo hin |
|--------|--------|
| Nur Theme ändern | **Appearance** — fertig. |
| Ollama langsam / falsches Modell | **AI / Models** + **Control Center → Models** zur Kontrolle. |
| RAG an/aus, Space, Top-K | In den Panels, die **RAG**-Schalter anzeigen — oft in Zusammenhang mit Daten/KI; exakte Platzierung hängt vom Panel Ihrer Version ab; Schlüssel in der App: `rag_enabled`, `rag_space`, `rag_top_k` (`AppSettings`). |
| Chat ohne Projekt-Kontext | **Advanced** → Chat-Kontext-Modus **off** (Workflow **context_control**). |
| Prompts nur im Dateiordner | Schlüssel `prompt_storage_type` / `prompt_directory` — über das Prompt-Panel in den Einstellungen, falls vorhanden; sonst Hilfe-Artikel `help/settings/settings_prompts.md`. |

## Fehlerfälle

| Symptom | Was Sie tun |
|---------|-------------|
| Einstellung springt nach Neustart zurück | Support: prüfen, ob `save()` für dieses Feld aufgerufen wird; QSettings-Pfad `OllamaChat` / `LinuxDesktopChat`. |
| Kategorie leer oder nur Platzhalter | **Project** / **Workspace** können in frühen Versionen weniger Felder haben — kein Bedienfehler. |
| RAG-Schalter nicht auffindbar | Unter **Data** oder **AI / Models** suchen; ggf. Dokumentation `help/settings/settings_rag.md` öffnen. |
| Nach Theme-Wechsel wirkt etwas „kaputt“ | App einmal neu starten; Theme-Registry in `AppearanceWorkspace` / `ThemeSelectionPanel`. |
| Sie kommen nicht zurück zum Chat | Sidebar: **Operations** → **Chat** — Settings sind ein eigener Hauptbereich, kein „OK“-Dialog. |

## Tipps

- **Vor Modellwechsel** unter **AI / Models** kurz **Control Center → Providers** prüfen — sonst wirkt ein neues Modell „tot“, obwohl die Einstellung gespeichert ist.
- **Advanced** nicht für alle Nutzer freigeben: Debug und Kontext-Inspection sind für **Entwicklung und QA** gedacht.
- Für **RAG** und **Prompts** die speziellen Hilfeseiten im Ordner `help/settings/` nutzen (`settings_rag.md`, `settings_prompts.md`).
