---
id: settings_chat_context
title: Chat-Kontext & Einstellungen
category: settings
tags: [kontext, context mode, detail level, profil, chat]
related: [chat_overview, settings_overview]
workspace: settings_application
order: 5
---

# Chat-Kontext & Einstellungen

Der **Chat-Kontext** ist zusätzlicher Systemtext mit Projekt-, Chat- und ggf. Topic-Informationen. Er wird nur mitgeschickt, wenn der **Context Mode** nicht `off` ist. Die genauen Schlüssel und Defaults stehen in `app/core/config/settings.py` (`AppSettings`).

Damit unterscheidet sich dieser Block vom reinen Gesprächsverlauf: Er beschreibt *wo* und *unter welchem Titel* Sie gerade arbeiten, nicht den Wortlaut früherer Nachrichten. Das Modell kann so Antworten stärker an Projekt- oder Chat-Bezug anbinden, ohne dass Sie jedes Mal Titel und Zuordnung wiederholen müssen.

## Inhalt

- [Context Mode](#context-mode)
- [Detail Level](#detail-level)
- [Einblendung: Projekt, Chat, Topic](#einblendung-projekt-chat-topic)
- [Profile (Presets)](#profile-presets)
- [Override-Reihenfolge](#override-reihenfolge)
- [Wo einstellen (GUI)](#wo-einstellen-gui)
- [Siehe auch](#siehe-auch)

**Siehe auch (Repository)**

- [Feature: Context](../../docs/FEATURES/context.md) · [Benutzerhandbuch – Kontext](../../docs/USER_GUIDE.md#3-kontextmodi-verstehen) · [Workflow: Kontext](../../docs_manual/workflows/context_control.md) · [Architektur – Zentrale Systeme](../../docs/ARCHITECTURE.md#4-zentrale-systeme)

## Context Mode

Der Kontextmodus bestimmt, **ob** und **in welcher sprachlichen Form** diese Metadaten in den Prompt einfließen. Bei `off` entfällt die strukturierte Kontextinjektion vollständig — der Chat läuft dann nur mit dem normalen Nachrichtenverlauf und allen anderen Systemanteilen (z. B. RAG), nicht mit dem zusätzlichen Projekt-/Chat-/Topic-Block aus `ChatRequestContext`.

Die Modi `neutral` und `semantic` liefern beide einen Text aus `ChatRequestContext.to_system_prompt_fragment` in `app/chat/context.py`; sie unterscheiden sich in der **Formatierung** (neutral vs. semantisch ausgerichteter Block), nicht in der Datenquelle. Ungültige gespeicherte Werte werden wie **semantic** behandelt.

| Wert | Wirkung |
|------|---------|
| **off** | Kein strukturierter Chat-Kontext wird injiziert. |
| **neutral** | Kontext wird in neutraler Form ausgegeben. |
| **semantic** | Kontext wird in semantischer Form ausgegeben. |

**Typischer Einsatz:** `off`, wenn Sie strikt nur den sichtbaren Verlauf sehen wollen; `semantic`, wenn das Modell die Einordnung in Projekt und Session ausdrücklich nutzen soll.

## Detail Level

Das Detail-Level begrenzt, **wie viel** von Projekt-, Chat- und Topic-Feldern in den Kontextblock kommt (Länge und Ausprägung der Darstellung). Bei `minimal` bleibt der Block knapper; bei `full` können mehr Hilfsinformationen erscheinen — immer noch begrenzt durch die Budget-Logik in `app/chat/context_limits.py`, damit der Prompt nicht unkontrolliert wächst.

| Wert | Wirkung |
|------|---------|
| **minimal** | geringerer Umfang der Kontextdarstellung |
| **standard** | mittlerer Umfang |
| **full** | voller Umfang |

Ungültige Werte werden wie **standard** behandelt.

## Einblendung: Projekt, Chat, Topic

Unabhängig von Mode und Detail können Sie steuern, **welche** der drei Informationsgruppen überhaupt gerendert werden. So können Sie etwa den Projektbezug beibehalten, aber Chat-Titel oder Topic gezielt ausblenden, wenn sie für die aktuelle Aufgabe irrelevant sind oder Rauschen erzeugen.

Drei Schalter (Persistenz-Keys):

- `chat_context_include_project` — Projektanteil ein/aus  
- `chat_context_include_chat` — Chat-/Session-Anteil ein/aus  
- `chat_context_include_topic` — Topic-Anteil ein/aus  

Standard beim Laden: Projekt und Chat **an**, Topic **aus** (siehe `AppSettings.load()`).

**Häufiges Missverständnis:** Diese Schalter ändern nicht, *welcher* Chat oder *welches* Projekt aktiv ist — das wählen Sie in der Oberfläche (Projekt-Hub, Session-Liste, Kontextleiste). Sie steuern nur, ob die zugehörigen Bezeichnungen in den System-Kontextblock geschrieben werden.

## Profile (Presets)

Profile fassen Mode, Detail und Include-Flags zu vordefinierten Kombinationen zusammen. Sobald der **Profil-Modus** aktiv ist, setzen diese Presets die effektive Konfiguration — unabhängig von den manuellen Schaltern, bis Sie den Profil-Modus wieder deaktivieren oder die Prioritätskette eine andere Quelle erzwingt (siehe unten).

Wenn **Profil-Modus** aktiv ist (`chat_context_profile_enabled`), bestimmt `chat_context_profile` ein festes Preset:

| Profil | Kurzbeschreibung (aus `app/chat/context_profiles.py`) |
|--------|--------------------------------------------------------|
| **strict_minimal** | Mode semantic, Detail minimal, nur Projekt |
| **balanced** | Mode semantic, Detail standard, Projekt + Chat |
| **full_guidance** | Mode semantic, Detail full, Projekt + Chat + Topic |

Ist der Profil-Modus **aus**, gelten die manuellen Einstellungen zu Mode, Detail und Include-Flags — sofern keine höherpriore Quelle greift (siehe nächster Abschnitt).

## Override-Reihenfolge

Mehrere Mechanismen können gleichzeitig „Meinungen“ zu Kontext haben (Profil, projekt- oder chat-spezifische Defaults, Laufzeit-Hinweise). Die Anwendung reduziert das zu **genau einer** wirksamen Kombination aus Modus, Detailstufe und Include-Flags. Wenn Sie in den Einstellungen etwas ändern und im Chat nichts passiert, liegt das oft daran, dass eine **höherpriore** Quelle aus der folgenden Liste noch aktiv ist.

Die App wählt **eine** siegreiche Konfiguration. Reihenfolge von höchster zu niedrigster Priorität (`ChatService._resolve_context_configuration` in `app/services/chat_service.py`):

1. Profil-Modus eingeschaltet  
2. Explizite Context-Policy (Laufzeit)  
3. Chat-Default-Context-Policy  
4. Projekt-Default-Context-Policy  
5. Request-Context-Hint  
6. **Individual Settings** — die Werte aus den Einstellungen für Mode, Detail und Include-Flags  

Wenn die effektive Quelle nicht die manuellen Schalter sind, wirken Änderungen an Mode/Detail/Include erst, nachdem die höherpriore Quelle entfällt oder angepasst wird.

## Wo einstellen (GUI)

In `app/gui/domains/settings/` ist **nur** der **Chat-Kontext-Modus** (`chat_context_mode`) an ein Steuerelement gebunden: **Settings → Advanced** → Kombinationsfeld „Chat-Kontext-Modus“ (`AdvancedSettingsPanel`).

Weitere gespeicherte Schlüssel — **Detail Level**, **Include-Flags**, **Profil-Modus** und **Profilname** — werden in `AppSettings` geladen und gespeichert, haben aber **keine** weiteren gebundenen Formularfelder in den Settings-Panels (Stand: Suche unter `app/gui/domains/settings/`).

Zusätzlich im Chat-Workspace: **ChatContextBar** oberhalb der Konversation zeigt Projekt-, Chat- und ggf. Topic-Bezeichnung; Klicks und Kontextmenü dienen der Navigation/Bearbeitung, nicht dem Setzen von Mode/Detail.

**Kontext-Inspection:** Checkbox „Kontext-Inspection aktiv“ ebenfalls unter **Settings → Advanced** (`context_debug_enabled`).

## Siehe auch

- [Chat Workspace](chat_overview)  
- [Einstellungen – Übersicht](settings_overview)  
- [Hilfe-Index](../README.md)
