# Benutzerhandbuch – Linux Desktop Chat

Zielgruppe: Endnutzer der Desktop-Anwendung. Begriffe **Context Mode**, **Detail Level**, **Profile** und **Override** entsprechen den Einstellungen und der Auflösungslogik in `AppSettings` bzw. `ChatService`.

Die Abschnitte sind nach Arbeitsauftrag gegliedert: zuerst Chat und Prompts, danach Kontextlogik, Einstellungen und RAG. So finden Sie typische Bedienfolgen am Anfang und Hintergrund zu Prioritäten und Schaltern weiter hinten.

## Inhalt

- [1. Chat benutzen](#1-chat-benutzen)
- [2. Prompts nutzen](#2-prompts-nutzen)
- [3. Kontextmodi verstehen](#3-kontextmodi-verstehen)
- [4. Settings bedienen](#4-settings-bedienen)
- [5. Typische Workflows](#5-typische-workflows)
- [6. Hilfe im Programm](#6-hilfe-im-programm)

Unter [5. Typische Workflows](#5-typische-workflows) finden Sie auch Knowledge (5.7), Agent Tasks (5.8) und den Workflow-Editor (5.6).

**Siehe auch**

- [Architektur – Schichten und Datenfluss](ARCHITECTURE.md) · [Zentrale Systeme (inkl. Kontext)](ARCHITECTURE.md#4-zentrale-systeme)  
- [Feature: Chat](FEATURES/chat.md) · [Feature: Context](FEATURES/context.md) · [Feature: Settings](FEATURES/settings.md)  
- [Workflows: Chat](../docs_manual/workflows/chat_usage.md) · [Kontext](../docs_manual/workflows/context_control.md) · [Einstellungen](../docs_manual/workflows/settings_usage.md) · [Agenten](../docs_manual/workflows/agent_usage.md)  
- [In-App-Hilfe (Index)](../help/README.md) · [Chat-Hilfe](../help/operations/chat_overview.md) · [Kontext-Hilfe](../help/settings/settings_chat_context.md)

---

## 1. Chat benutzen

1. Sidebar: unter **Operations** den Eintrag **Chat** wählen.  
2. Links: Session-Liste – bestehenden Chat wählen oder neuen Chat anlegen.  
3. Mitte: Konversation; bei aktivem Streaming erscheint die Antwort während der Generierung (sofern in den Einstellungen nicht deaktiviert).  
4. Unten: Eingabefeld – Nachricht senden; Modell und Rolle über die Chat-Kopfzeile bzw. Modus-Schalter, soweit die Oberfläche sie anbietet.  
5. **Slash-Commands** (Anfang der Zeile mit `/`), implementiert in `app/core/commands/chat_commands.py`:  
   - Rollen: `/fast`, `/smart`, `/chat`, `/think`, `/code`, `/vision`, `/overkill`, `/research`  
   - Mit Text dahinter (Beispiel `/think Erkläre X`): Rolle wird gesetzt, der Rest wird als normale Nachricht gesendet.  
   - `/auto on` | `/auto off` – Auto-Routing  
   - `/cloud on` | `/cloud off` – Cloud-Eskalation  
   - `/delegate <Text>` – Delegation mit folgendem Prompt-Text (ohne Text: Hinweis in der Konsole/UI)  

Wiederkehrende Textbausteine und Vorlagen pflegen Sie gesondert im Prompt Studio; der nächste Abschnitt verweist dorthin und auf die zugehörigen Speicher-Einstellungen.

---

## 2. Prompts nutzen

1. **Operations → Prompt Studio:** Prompts anlegen, bearbeiten, auf den Chat anwenden (je nach UI-Elementen des Workspaces).  
2. Speicherort der Prompts: **Settings →** passende Kategorie bzw. Einträge zu Prompts (Schlüssel `prompt_storage_type`: Datenbank oder Verzeichnis, `prompt_directory` bei Verzeichnis).  
3. Im Chat können Prompt-Vorlagen aus dem Studio über die dafür vorgesehenen Aktionen übernommen werden (konkrete Klicks: Prompt-Studio-Workspace).

Wie viel Hintergrund das Modell zur **aktuellen Sitzung** (Projekt, Chat-Titel, Topic) mitbekommt, steuern die Kontexteinstellungen und deren Prioritätskette im folgenden Kapitel.

---

## 3. Kontextmodi verstehen

Der **Chat-Kontext** ist zusätzlicher Text (Projektname, Chat-Titel, Topic, …), der dem Modell als Systemkontext mitgegeben wird – abhängig von **Context Mode**, **Detail Level** und den Einblendungs-Schaltern.

### 3.1 Context Mode

| Wert | Wirkung |
|------|---------|
| **off** | Es wird kein strukturierter Chat-Kontext injiziert. |
| **neutral** | Kontext wird in einer sachlichen Form ausgegeben (`ChatContextMode.NEUTRAL`). |
| **semantic** | Kontext wird in der semantischen Form ausgegeben (`ChatContextMode.SEMANTIC`). |

Ungültige Werte in der Konfiguration werden wie **semantic** behandelt (`get_chat_context_mode()`).

### 3.2 Detail Level

| Wert | Bedeutung |
|------|-----------|
| **minimal** | geringerer Umfang der Kontextdarstellung |
| **standard** | mittlerer Umfang |
| **full** | voller Umfang |

Ungültige Werte werden wie **standard** behandelt.

### 3.3 Felder (Project / Chat / Topic)

Über die Schlüssel `chat_context_include_project`, `chat_context_include_chat`, `chat_context_include_topic` steuert die App, welche Bereiche überhaupt einfließen. Default in `AppSettings.load()`: Projekt und Chat an, Topic aus.

### 3.4 Profile

Wenn **Profil-Modus** aktiv ist (`chat_context_profile_enabled`), bestimmt `chat_context_profile` ein festes Preset:

| Profil | Auflösung (aus Code) |
|--------|----------------------|
| **strict_minimal** | Mode semantic, Detail minimal, nur Projekt |
| **balanced** | Mode semantic, Detail standard, Projekt + Chat |
| **full_guidance** | Mode semantic, Detail full, Projekt + Chat + Topic |

Ist der Profil-Modus **aus**, gelten die manuellen Context-Mode-/Detail-/Include-Einstellungen – sofern keine **Override**-Quelle mit höherer Priorität greift.

### 3.5 Override (Priorität)

Die effektive Konfiguration wird in `ChatService._resolve_context_configuration()` gewählt. Reihenfolge von höchster zu niedrigster Priorität:

1. Profil-Modus an (`profile_enabled`)  
2. Explizite Context-Policy (Laufzeit)  
3. Chat-Default-Context-Policy  
4. Projekt-Default-Context-Policy  
5. Request-Context-Hint  
6. **Individual Settings** – die Werte aus den Einstellungen für Mode, Detail und Include-Flags  

Für Feinanalyse stehen in QA-/Debug-Workspaces Erklärungen und Traces bereit (`Context`-Inspector, Runtime-Debug).

Die übrigen Einstellungen der App (Darstellung, Modell, Datenschutz usw.) erreichen Sie über den Vollbild-Dialog **Settings**; die Kategorien entsprechen der linken Navigationsliste in der Oberfläche.

---

## 4. Settings bedienen

**Navigation:** Sidebar **Settings** → Vollbild-Dialog mit linker Liste.

Kategorien (Reihenfolge wie in `app/gui/domains/settings/navigation.py`):

1. **Application** – globale App-Einstellungen  
2. **Appearance** – Darstellung, Theme  
3. **AI / Models** – Modellparameter, Standardmodell  
4. **Data** – datenbezogene Optionen  
5. **Privacy** – datenschutzbezogene Optionen  
6. **Advanced** – u. a. Debug-Panel, **Kontext-Inspection**, **Chat-Kontext-Modus** (`chat_context_mode`: neutral / semantic / off)  
7. **Project** – **Lesen:** Kurzübersicht zum aktuell aktiven Projekt. **Anlegen, Bearbeiten, Status und Standard-Kontextpolicy, Löschen** erfolgen zentral unter **Operations → Projekte** (nicht in dieser Settings-Kachel).  
8. **Workspace** – **Orientierung:** wo Operations- und Control-Center-Schalter liegen (keine eigenen Speicherkeys)  

**Projekt löschen** (u. a. **Operations → Projekte**, Schaltfläche „Projekt löschen“; weiterhin möglich über die Legacy-Sidebar): entfernt die Projektzeile und Themen sowie Chat-Zuordnungen; Chats, Prompts, Agenten und Workflows werden nicht verworfen, sondern wo nötig **globalisiert**. Der RAG-Unterordner des Projekts unter dem App-Datenpfad wird entfernt (ohne referenzierte Dateien auf der Platte zu löschen). Datenbank-Verknüpfungen (z. B. `project_files`) werden aufgehoben. War das Projekt aktiv, ist danach kein Projekt mehr aktiv.

Änderungen werden über das Settings-Backend persistiert (in der Regel beim Speichern durch die UI).

**Hinweis Kontext:** Neben dem Modus existieren in `AppSettings` auch **Detail Level**, **Include-Flags** und **Profil**-Schlüssel; gebundene Steuerelemente dafür liegen in den Settings-Panels aktuell **nicht** vor (nur der Modus unter **Advanced**). Overrides aus Policy/Hint greifen trotzdem zur Laufzeit.

RAG- und Prompt-relevante Schlüssel sind zusätzlich in den Hilfe-Artikeln `help/settings/settings_rag.md` und `help/settings/settings_prompts.md` beschrieben.

Die folgenden Kurzabläufe verbinden die zuvor genannten Bausteine zu häufigen Aufgaben (erster Chat, RAG, Slash-Commands, Kontext, Delegation).

---

## 5. Typische Workflows

### 5.1 Erste Unterhaltung

Ollama starten → Modell ziehen (`ollama pull …`) → App starten (`python -m app`) → Chat öffnen → Modell wählen → Nachricht senden.

### 5.2 Chat mit RAG

Knowledge-Workspace: Quellen anlegen/indexieren → in den Chat-Einstellungen oder im Chat RAG aktivieren (`rag_enabled`) → Space und `rag_top_k` prüfen → Frage stellen.

### 5.3 Fokus „Code“

Im Eingabefeld `/code` senden oder Code-Rolle wählen, dann die eigentliche Frage (ggf. in derselben Zeile nach dem Command).

### 5.4 Kontext reduzieren

In der GUI: **Settings → Advanced** → Chat-Kontext-Modus **off** (keine Injektion) oder **neutral** / **semantic** nach Bedarf. **Detail Level** und **Profil** sind in `AppSettings` definiert, aber ohne eigene Settings-Formularfelder — Anpassung erfolgt über Persistenz/andere Werkzeuge, nicht über die beschriebenen Panels.

### 5.5 Delegation

`/delegate Aufgabenbeschreibung` eingeben und senden; der Chat-Service verarbeitet den Delegation-Pfad über die Agenten-Infrastruktur.

### 5.6 Workflow-Editor (gespeicherte DAGs)

**Operations → Workflows:** eigene gespeicherte Knoten-/Kanten-Workflows (nicht identisch mit Chat-Slash-Commands). Anlegen, validieren, Test-Run, Run-Historie und Canvas mit Status-Overlay. Kurzdokumentation: [`docs/02_user_manual/workflows.md`](02_user_manual/workflows.md) · Feature-Überblick [`docs/FEATURES/workflows.md`](FEATURES/workflows.md) · Hilfe `help/operations/workflows_workspace.md`.

### 5.7 Knowledge (RAG) im Überblick

**Operations → Knowledge** (gleicher Bereich wie in der Sidebar): Quellen und Collections verwalten, Indexstatus prüfen, Retrieval testen. Für die Nutzung im Chat gelten weiterhin RAG-Schalter und Space-Einstellungen (siehe 5.2 und `help/settings/settings_rag.md`). Ohne gebauten Chroma-Index zeigen die Flächen entsprechende Hinweise — das ist erwartetes Verhalten, keine „fehlende“ Funktion.

### 5.8 Agent Tasks

**Operations → Agent Tasks:** Agentenprofil wählen, Aufgabe mit Prompt starten; Ergebnis, aktive Läufe und Kurzinfos erscheinen in den Karten des Workspaces. Das ist ein eigener Pfad neben dem Chat (kein Ersatz für `/delegate` im Chat). Details: [`help/operations/agents_overview.md`](../help/operations/agents_overview.md).

In der laufenden Anwendung steht dieselbe inhaltliche Basis auch als strukturierte Hilfe bereit; der letzte Abschnitt zeigt, wo diese herkommt.

---

## 6. Hilfe im Programm

Menü/Command-Palette: Hilfe öffnen. Inhalt kommt aus `help/` (Markdown mit Frontmatter). Im Hilfefenster gibt es unter **Ansicht** zusätzlich **Semantische Doku-Suche** (Vektorindex über Repo-Dokumentation; Aufbau siehe Hinweis im Panel und `tools/build_doc_embeddings.py`). Ergänzend: [`docs/FEATURES/context.md`](FEATURES/context.md).
