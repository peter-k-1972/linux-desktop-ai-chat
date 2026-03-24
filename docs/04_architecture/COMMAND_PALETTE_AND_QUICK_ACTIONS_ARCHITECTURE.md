# Command Palette & Quick Actions — Architektur- und UX-Konzept (QML-GUI)

**Status:** Konzept für einen späteren Implementierungs-Slice — **keine** Code- oder QML-Vorgaben.

**Bezug:** Gesamtarchitektur `QML_GUI_VISUAL_ARCHITECTURE_MAP.md`; Shell-Ist: `AppChrome`, `NavRail`, `StageHost`, `OverlayHost`, `ShellBridgeFacade`, `shell_navigation_state.py`, Domain-ViewModels (`python_bridge/*`, `app/ui_runtime/qml/*`).

**Metapher:** Die Command Palette ist das **Auskunftspult / der Indexschrank** der Bibliothek: schnell, präzise, ruhig — kein Spielplatz, keine zweite vollständige Oberfläche.

---

## 1. COMMAND PALETTE PURPOSE MODEL

### 1.1 Wofür die Palette da ist

| Zweck | Beschreibung (Linux Desktop Chat) |
|-------|-----------------------------------|
| **Raumsprung** | Jede Hauptbühne (Chat, Projects, Workflows, Prompts, Agents, Deployment, Settings) in **einem** Tastaturflow erreichbar — ergänzt die Rail, ersetzt sie nicht. |
| **Objektöffnung** | Projekte, Workflows, Chats, Prompts, Agenten **adressieren und öffnen** (Wechsel der Stage + fachliche Selektion, soweit die Bridge das kann). |
| **Standardaktionen** | Häufige Tätigkeiten: neuer Chat, neues Projekt, ausgewählten Workflow starten, zur Prompt-Bibliothek — **ohne** Menütiefe. |
| **Kontextsprünge** | Aus dem aktuellen Raum heraus logische Ziele: „aktives Projekt im War Room zeigen“, „zu Workflows wechseln“, „Provider-Einstellungen“. |
| **Einheitlicher Launcher** | Eine **semantisch kontrollierte** Befehlsschicht über alle Domänen hinweg — das fehlende Bindeglied zwischen Rail-Stages und produktivem Arbeiten. |

### 1.2 Wofür sie nicht da ist

- Keine **Admin-/Debug-Konsole** (keine Roh-JSON-Ausgabe, kein freies Skripting für Endnutzer).
- Keine **vollständige Ersatz-GUI** für komplexe Bearbeitung (Workflow-Graph, lange Formulare bleiben in den Stages).
- Keine **beliebige Volltextsuche** über alle Datenbanken als Ersatz für domäneneigene Listenfilter (die Palette **aggregiert registrierte Befehle und kuratierte Suchtreffer**, kein Wildwuchs).
- Kein **zweites Navigationsparadigma**, das die Rail obsolet macht.

### 1.3 Verhältnis zur Primärnavigation (NavRail)

| Aspekt | Rail | Command Palette |
|--------|------|-----------------|
| **Mentales Modell** | „Ich gehe in einen Raum.“ | „Ich will X — jetzt.“ |
| **Entdeckbarkeit** | Hoch (immer sichtbar) | Mittel (Shortcut + später Hinweis in UI) |
| **Tiefe** | Ein Klick = Stage | Ein Klick/Eingabe = Navigation **oder** Aktion **oder** Objekt |
| **Autorität** | `activeDomain` / `stageUrl` bleiben **Wahrheit** | Jede Navigation **muss** dieselbe Shell-Route triggern (`requestDomainChange` + ggf. Folgeaktion) |

**Regel:** Die Palette **ergänzt** die Rail; sie **ersetzt** sie nicht. Nutzer, die nur die Rail nutzen, verlieren keine Funktion.

### 1.4 Verhältnis zu Domänen-Buttons („Zum Chat“, „Zu Workflows“)

- **Domänen-Buttons** = explizite, sichtbare **Quick Actions** an der Arbeitsfläche (gut für erste Nutzung, Mausnutzer).
- **Palette** = dieselben oder äquivalente **Befehle** mit **stabiler ID** und Tastaturpfad.
- Beides speist idealerweise dieselbe **Routing-/Aktions-Schicht** (siehe §5, §8), damit keine doppelte Semantik entsteht.

### 1.5 Warum für diese App notwendig

Die Plattform verbindet **Chat**, **Projects (War Room)** und **Workflows** als gleichwertige Kernräume mit **Prompts**, **Agents** und **Deployment**. Ohne Palette entstehen **viele Wechsel** zwischen Rail und Stage-Inhalten; Power-User und Wissensarbeiter brauchen eine **souveräne, schnelle Schicht**, die Räume und Objekte **verbindet**, ohne neue „Menühölle“ zu schaffen.

---

## 2. SCOPE OF COMMANDS

### 2.1 Erlaubte Kommandotypen

| Typ | Semantik | Beispiele |
|-----|----------|-----------|
| **Navigation Commands** | Wechsel der **Hauptbühne** (Domain), optional mit Unterziel (z. B. Settings-Kategorie). | „Chat öffnen“, „Zu Workflows“, „Einstellungen: KI-Modelle“. |
| **Entity Open Commands** | Stage wechseln **und** eine Entität selektieren/laden (Projekt, Workflow, Chat, Prompt, Agent …), soweit API vorhanden. | „Projekt Alpha öffnen“, „Workflow nightly-sync öffnen“. |
| **Create Commands** | Neue Ressource anlegen **über** Service-Schicht; danach oft Navigation + Fokus. | „Neuer Chat“, „Neues Projekt“, „Neuer Prompt (Entwurf)“. |
| **Run / Execute Commands** | Einmalige Ausführung (Workflow-Run, Agent-Task …) mit klar definierten Parametern. | „Ausgewählten Workflow starten“. |
| **Context Commands** | Abhängig von **aktivem Domain / Projekt / Selektion**; keine neue Businesslogik, nur angebundene Aktionen. | „Aktives Projekt im War Room zeigen“, „Zugehörige Prompts (Studio)“. |
| **Utility Commands** | App-weit, ohne fachliches Objekt: Theme, Reload, ggf. Logs nur wenn produktionsrelevant. | „Palette schließen“, „Einstellungen: Erscheinungsbild“. |
| **Future Commands** | Platzhalter-Typen in der Taxonomie (Knowledge, Analytics …), **noch nicht** im Prioritätsset. | „Knowledge-Raum öffnen“ (wenn Domain existiert). |

### 2.2 Explizit ausgeschlossen (oder nur über gesonderte „Experten“-UI)

- Freie Shell-Befehle, SQL, beliebige Dateipfade als „Command“.
- Unstrukturierte „Macro“-Strings ohne Registry-Eintrag.
- Debug-Only-Aktionen in derselben Liste wie Produktivbefehle (höchstens separater Modus **außerhalb** der Standardpalette).

---

## 3. INFORMATION ARCHITECTURE OF THE PALETTE

### 3.1 Entscheidung: ein einheitlicher Modus (Suche + Befehle kombiniert)

**Gewählt:** **Eine** Eingabezeile, **eine** Ergebnisliste, **gruppiert nach Kategorien** — keine strikte Trennung „Suchmodus“ vs. „Aktionsmodus“.

**Begründung:** Weniger kognitive Last; die Bibliotheksmetapher („Index“) passt zu **filtern und treffen** in einem Schritt. Alternativen (Tabs „Aktionen / Suche“) würden für eine Desktop-Knowledge-App **hektischer** wirken.

### 3.2 Aufbau

| Zone | Funktion |
|------|----------|
| **Eingabefeld** | Fokus bei Öffnen; filtert und sortiert die **kombinierte** Menge aus statischen Commands + dynamischen Treffern (Projekte, Workflows, …). |
| **Ergebnisliste** | Virtualisierte Liste; Einträge mit **Primärlabel**, **Untertitel**, optional **Domain-Badge**. |
| **Gruppierung** | Fixe Reihenfolge der Gruppen (siehe §4): z. B. „Räume“ → „Zuletzt“ → „Projekte“ → … — leere Gruppen **ausblenden**. |
| **Footer (optional, minimal)** | Einzeiler: Shortcut-Hinweis (↑↓ Enter Esc) — dezent, nicht verspielt. |

### 3.3 Tastatursteuerung (Soll)

| Taste | Verhalten |
|-------|-----------|
| **Öffnen** | Globaler Shortcut (siehe §7) |
| **Escape** | Schließen, Fokus zurück an vorherigen Fokus (wo möglich) |
| **↑ / ↓** | Auswahl in der Liste |
| **Enter** | Ausführen des markierten Eintrags |
| **PgUp / PgDn** | Optional, Liste scrollen |
| **Tab** | Optional: nur wenn zweite Spalte/Filter nötig — **V1: vermeiden**, Fokus bleibt auf Eingabe + Liste |

### 3.4 Auswahlverhalten

- Erster Treffer nach Filter/Sortierung ist **vorausgewählt**.
- Leerstring zeigt **kuratierte Defaults** (häufige Navigation + Zuletzt + ggf. kontextuelle 3–5 Einträge).
- Nach Ausführung: Palette **schließt**, außer Befehl ist explizit als „Palette offen lassen“ markiert (**V1: nicht** — immer schließen für Ruhe).

### 3.5 Leer- und Fehlerzustände

| Zustand | Darstellung |
|---------|-------------|
| **Keine Treffer** | Eine ruhige Zeile: „Kein Treffer“ + Vorschlag: Tippfehler prüfen oder Rail nutzen. |
| **Backend nicht bereit** | „Befehle können gerade nicht geladen werden“; statische Navigationsbefehle dürfen **trotzdem** angeboten werden, falls ohne Service möglich. |
| **Aktion fehlgeschlagen** | Kurzer Toast oder Statuszeile (später Shell); Palette zu; Fehlertext **kurz**, Details in Logs — **kein** Stacktrace in der Palette. |

---

## 4. COMMAND TAXONOMY

### 4.1 Kategorien (Reihenfolge für Gruppierung in der Liste)

1. **Räume** — reine Navigation zu Domains.  
2. **Zuletzt verwendet** — kuratierte Wiederholungen (Objekte + Räume).  
3. **Projekte** — Entity Open + ggf. Kontext.  
4. **Workflows**  
5. **Chats**  
6. **Prompts**  
7. **Agents**  
8. **Deployment**  
9. **Einstellungen** — inkl. Provider/Modelle-Unterziele.  
10. **Aktionen** — Create / Run / Kontext, die nicht sauber unter eine Entity-Gruppe fallen.  

*(Leere Gruppen ausblenden; Reihenfolge fest für Vorhersagbarkeit.)*

### 4.2 Befehlsidentität

| Element | Regel |
|---------|--------|
| **Stabile ID** | `command_id` als string, z. B. `nav.chat`, `open.project`, `create.chat` — **nicht** vom UI-Label abgeleitet. |
| **Primärlabel** | Kurz, Title Case oder Satzcase konsistent (eine Konvention wählen und einhalten), z. B. „Chat öffnen“, „Neues Projekt“. |
| **Untertitel** | Optional: Kontext (`Projekt · zuletzt aktiv`), Objekttyp, oder Shortcut-Hinweis. |
| **Domain-Badge** | Klein: `Chat`, `Projekte`, `Workflows` … — orientiert an Rail-Labels. |

### 4.3 Aliasse und Suche

- **Aliasse** als optionale Liste pro Registry-Eintrag (`aliases: ["cc", "chat"]`) — nur **klein**, keine Explosion.  
- Filterung über **normalisierten** Text (Lowercase, Umlaute vereinheitlichen).  
- **Mehrdeutigkeit:** bei mehreren Objekten gleichen Namens Untertitel mit **ID-Snippet**, Pfad oder Projektbezug; keine automatische „rate mal“-Auswahl.

### 4.4 Dynamische vs. statische Einträge

| Quelle | Beispiel |
|--------|----------|
| **Statisch (Registry)** | Alle Navigationsbefehle, Utility, definierte Create/Run ohne Parameter. |
| **Dynamisch (Resolver)** | Projektliste, Workflowliste, Chatliste, Agentliste — aus Services/Caches, **begrenzt** (Top N nach Relevanz + Query). |

---

## 5. QUICK ACTION ARCHITECTURE

### 5.1 Drei Ebenen (Architekturmuster)

```
┌─────────────────────────────────────────────────────────────────┐
│  GLOBAL: Command Palette (Shell, Shortcut, alle registrierten   │
│          Befehle + dynamische Treffer)                          │
└───────────────────────────────┬─────────────────────────────────┘
                                │ gemeinsame Ausführungsschicht
┌───────────────────────────────▼─────────────────────────────────┐
│  DOMAIN QUICK ACTIONS (sichtbar in Stage: Buttons, Kontextmenüs) │
│  — rufen dieselben command_id / action_ids auf wie die Palette   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│  CONTEXT JUMPS (explizit benannte Sprünge, z. B. „Zu Workflows“)│
│  — Subtyp von Quick Action; oft nur Navigation + Hint an VM      │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Was global vs. nur lokal

| Global (Palette + ggf. Shortcut) | Primär lokal (Stage) |
|-----------------------------------|----------------------|
| Raumwechsel | Feinsteuerung im Canvas (Knoten hinzufügen, Zoom) |
| Objekt öffnen über Name | Auswahl im Graph/Liste ohne globale Suche |
| Neuer Chat / Projekt / … | Dialogfelder mit vielen Pflichtfeldern |
| „Aktives Projekt zeigen“ | Inspector-Details, die keine eigene Aktion sind |

### 5.3 Project → Workflow → Chat (Sprünge)

| Nutzerintention | Quick Action / Command |
|-----------------|-------------------------|
| Vom **War Room** in die **Planungstafel** | „Zu Workflows“ (Nav) + optional „Workflows dieses Projekts“ (Kontext, V1: Nav + Filter-Hint). |
| Vom **Workflow** zurück zum **Projekt** | „Aktives Projekt im War Room“ (setzt Domain + Selektion). |
| Vom **Chat** zum **Projekt** | „Aktives Projekt öffnen“ / „Projekt wechseln …“. |

**Prinzip:** Globale Befehle kennen **activeProjectId** (und activeDomain); domänenspezifische Buttons im Project/Workflow-Stage **dürfen** dieselben IDs aufrufen — **eine** Implementierung der Semantik.

### 5.4 Konkrete Rollen der Stages (Sollbild)

| Stage | Quick Actions (Beispiele) |
|-------|-------------------------|
| **Projects** | „Zu Chat“, „Zu Workflows“, „Neues Projekt“ (auch in Palette). |
| **Workflows** | „Ausführen“, „Neu laden“; Sprung zu Prompts/Agents wenn fachlich sinnvoll. |
| **Chat** | „Projekt …“, „Neuer Chat“; kein Ersatz für Composer-Features. |

Quick Actions sind **keine** beliebigen Buttons: jede wiederkehrende Aktion mit **übergreifender** Bedeutung erhält eine **command_id** und kann in der Palette erscheinen.

---

## 6. CONTEXT AWARENESS MODEL

### 6.1 Kontextdimensionen

| Dimension | Quelle (konzeptionell) |
|-----------|-------------------------|
| **activeDomain** | `ShellBridgeFacade.activeDomain` |
| **activeProject** | ProjectContextManager / ActiveProjectContext (wie heute im Produkt) |
| **Domain-Selektion** | z. B. `selectedWorkflowId` im `workflowStudio`-VM — **nur** wenn explizit an die Palette angebunden |
| **Letzte Nutzung** | Lokaler Cache / Service (Zuletzt-Gruppe) |

### 6.2 Modi (konzeptionell)

| Modus | Bedeutung |
|-------|-----------|
| **Global** | Palette zeigt immer Nav + statische Kernbefehle + dynamische Treffer unabhängig von Domain. |
| **Domain-geboostet** | Bei gleicher Query erscheinen **domänenrelevante** Befehle/Treffer **höher** (Ranking), nicht ausgeblendet. |
| **Projektgebunden** | Befehle wie „Chats dieses Projekts“ nur sinnvoll mit `activeProjectId`; ohne Projekt: deaktiviert oder ausgeblendet mit kurzem Untertitel „Kein aktives Projekt“. |
| **Selektionsgebunden** | „Workflow starten“ nur wenn Selektion gesetzt; sonst Eintrag ausgeblendet oder mit Hinweis. |

### 6.3 Version-1-Strategie (bewusst minimal)

**Enthalten in V1:**

- `activeDomain` für **Ranking** (leicht höher gewichten: passende Ziel-Domain).  
- `activeProjectId` für **Kontextbefehle**, die ohnehin im Prioritätsset sind.  
- **Zuletzt**-Gruppe mit begrenzter Historie (Räume + wenige Objekte).

**Später (nicht V1):**

- Tiefe Selektionskopplung aus jedem VM-Feld.  
- „Intelligente“ Vorschläge auf Basis von Inhalten der letzten Nachricht.  
- Mehrstufige Parameterabfrage **innerhalb** der Palette (Mikro-Wizard).

**Begründung:** Zu viel Kontext wirkt **überintelligent** und fehleranfällig; die Palette soll **souverän und vorhersagbar** bleiben.

---

## 7. QML SHELL INTEGRATION

### 7.1 Einordnung: Shell-Ebene, nicht Stage

Die Palette lebt **nicht** in `ChatStage` oder `ProjectStage`, sondern unter **AppChrome** — sinnvoll als Inhalt von **`OverlayHost`** (aktuell reservierter Layer) oder als Geschwister mit `z` über `StageHost`, **identische** visuelle Grammatik (Foundation, Theme).

```
AppChrome
├── NavRail | StageHost
└── OverlayHost
    └── CommandPaletteOverlay (modal, dimmed backdrop)
         └── Palette UI (Eingabe + Liste)
```

### 7.2 Globaler Shortcut

| Entscheidung | **Ctrl+K** (primär, wie gängige „Command Palette“-Konvention auf Desktop). |
|--------------|-----------------------------------------------------------------------------|
| **Alternative / Ergänzung** | **Ctrl+P** nur wenn nicht mit System-„Print“ kollidiert — **eine** primäre Kombination festlegen und dokumentieren. |
| **Escape** | Schließen. |

*(Exakte Keys: produktweit einheitlich; bei Konflikt mit Plattform dokumentieren.)*

### 7.3 Fokus und Modalität

- Beim Öffnen: Fokus **sofort** ins Eingabefeld; Liste per Pfeiltasten.  
- **Modal** über der Stage: keine Klicks durch die Palette hindurch auf die Stage (außer explizit „Klick außerhalb schließt“ — **Entscheidung:** Klick auf Backdrop **schließt**, konsistent mit ruhiger UX).  
- Schließen stellt den Fokus **wieder her**, wo technisch machbar (sonst Fokus auf Hauptfenster).

### 7.4 Visuelle Einbettung (Bibliotheksästhetik)

- Ruhige Fläche, **WorkSurface**-nahe Kanten, dezente **Elevation**; keine grellen Akzente.  
- Typografie aus **Foundation**; keine domänenspezifischen „Spiel-“-Farben in der Shell-Palette.

### 7.5 Verhältnis zu StageHost

- `StageHost` bleibt **unverändert** geladen; die Palette **überlagert** nur.  
- Navigation durch die Palette **entlädt** ggf. andere Stage-URL über `shell.requestDomainChange` — **kein** zweiter Loader.

---

## 8. PYTHON BRIDGE / COMMAND ROUTING MODEL

### 8.1 Datenfluss (Schichten)

```
┌──────────────────────────────────────────────────────────────────┐
│  QML: Command Palette UI (Filtereingabe, Liste, Tastatur)         │
└───────────────────────────────┬──────────────────────────────────┘
                                │ Properties / Slots
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│  CommandPaletteViewModel (QObject, context property z. B.           │
│  „commandPalette“)                                               │
│  — query, selectedIndex, QAbstractListModel der sichtbaren Zeilen   │
│  — slot: open(), refresh(), executeCurrent()                       │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│  Command Registry (statische Definitionen: id, type, labels,      │
│  category, permissions, handler key)                               │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│  Command Resolver (Query → merge static + dynamic providers)      │
│  — sort/rank; debounce für Service-Calls                          │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│  Action Dispatcher / Router                                      │
│  — unterscheidet: NAVIGATE | OPEN_ENTITY | CREATE | EXECUTE       │
│  — ruft ShellBridge (Domain), Domain-VMs (Selektion), oder        │
│    Presenter/Port/Adapter für Servicearbeit auf                   │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│  Services / DB / Streams (bestehende Schichten)                   │
└──────────────────────────────────────────────────────────────────┘
```

### 8.2 Wo Definitionen leben

| Was | Wo (konzeptionell) |
|-----|---------------------|
| **Statische Commands** | Python-Modul(e) oder Daten (JSON) **eingebunden** von der Registry — versionierbar, reviewbar. |
| **Dynamic Providers** | Eine Schnittstelle pro Quelle (Projects, Workflows, …), implementiert gegen bestehende Services **ohne** QML. |

### 8.3 Ergebniszeilen

Jede Zeile: `row_id`, `command_id` oder `entity_key`, `category`, `primary`, `secondary`, `icon_token` (optional), `enabled`, `payload` (strukturiert, nicht roher String-Befehl).

### 8.4 Navigation vs. Execute

| Typ | Router-Verhalten |
|-----|-------------------|
| **NAVIGATE** | `ShellBridgeFacade.requestDomainChange(domainId)`; optional zweite Nachricht an Ziel-VM (`hint` / `pendingSelection`). |
| **OPEN_ENTITY** | Navigation + VM-API „select/open“ (wo definiert). |
| **CREATE** | Service über Port/Adapter; dann ggf. Navigation. |
| **EXECUTE** | Ein klarer Eintrag ins bestehende Ausführungs-API (Workflow-Run, …). |

### 8.5 Fehler

- Dispatcher fängt Exceptions, setzt **kurzen** `lastError` am ViewModel für Toast/Log; Palette schließt oder bleibt mit Meldung gemäß §3.5.

### 8.6 Harte Regeln

- **Keine** Businesslogik in QML.  
- **Keine** unkontrollierten Kommando-Strings vom Nutzer direkt in Services.  
- Jede ausführbare Zeile referenziert eine **Registry- oder Provider-Identität**.

---

## 9. PRIORITY COMMAND SET (VERSION 1)

Kernmenge — **stark**, nicht vollständig. IDs sind Vorschläge für die Registry.

### A. Navigation

| ID | Label (Beispiel) |
|----|------------------|
| `nav.chat` | Chat öffnen |
| `nav.projects` | Projekte öffnen |
| `nav.prompt_studio` | Prompt Studio öffnen |
| `nav.workflows` | Workflows öffnen |
| `nav.agents` | Agenten öffnen |
| `nav.deployment` | Deployment öffnen |
| `nav.settings` | Einstellungen öffnen |
| `nav.settings.ai_models` | Einstellungen: KI-Modelle |
| `nav.settings.providers` | Einstellungen: Provider (falls als Unterziel modelliert) |

### B. Open Entity (dynamisch + ggf. statisch)

| ID / Muster | Label-Kontext |
|-------------|----------------|
| `open.project` + Ziel | Projekt „…“ öffnen |
| `open.workflow` + Ziel | Workflow „…“ öffnen |
| `open.chat` + Ziel | Chat „…“ öffnen |
| `open.prompt` + Ziel | Prompt „…“ öffnen |
| `open.agent` + Ziel | Agent „…“ öffnen |

### C. Create

| ID | Label |
|----|--------|
| `create.chat` | Neuer Chat |
| `create.project` | Neues Projekt |
| `create.prompt` | Neuer Prompt (Entwurf) |

*(Weitere Create-Befehle erst, wenn Dialog/Flow klar angebunden ist.)*

### D. Execute

| ID | Label | Voraussetzung |
|----|--------|----------------|
| `exec.workflow.run_selected` | Ausgewählten Workflow starten | Workflow ausgewählt, Domain Workflows oder Selektion bekannt |

### E. Settings / Utility

| ID | Label |
|----|--------|
| `util.palette.close` | Palette schließen (optional redundant zu Esc) |
| `nav.settings.appearance` | Einstellungen: Erscheinungsbild |

### F. Kontext (minimal, V1)

| ID | Label |
|----|--------|
| `ctx.open_active_project` | Aktives Projekt im War Room |
| `ctx.go_workflows` | Zu Workflows (Nav; ggf. mit Projekt-Hint) |

### G. Zuletzt

| ID | Label |
|----|--------|
| `recent.*` | Von Resolver befüllt: letzte Räume / Objekte (Limit 5–10) |

---

## 10. GOVERNANCE RULES

1. **Nicht jede UI-Aktion wird globaler Befehl** — nur wiederkehrende, semantisch **stabile** Handlungen.  
2. **Jeder globale Command** hat eine **stabile ID**, ein **Label** und einen **Typ** (Navigation / Open / Create / Execute / Context / Utility).  
3. **Labels** folgen **einer** Schreibkonvention; Untertitel erklären Kontext, nicht Fachjargon ohne Nutzen.  
4. **Palette ergänzt die Rail** — keine Features ausschließlich in der Palette verstecken.  
5. **Domänen-Quick-Actions**, die auch global sinnvoll sind, **müssen** dieselbe Routing-Semantik wie die Registry nutzen (keine Abweichung).  
6. **Kontextsensitive globale Einträge** nur, wenn der Kontext **eindeutig** ist (Projekt gesetzt, Selektion gesetzt); sonst ausblenden oder klar deaktivieren mit Grund.  
7. **Keine Businesslogik in QML** — nur Darstellung und Aufruf von Slots/Properties des ViewModels.  
8. **Keine Vermischung** von Produktivpalette und Debug-Konsole — Debug bleibt separat (z. B. Runtime/Debug-Workspace).  
9. **Performance:** dynamische Provider mit **Limits** und **Debouncing**; keine Vollscan-Listen bei jedem Tastendruck.  
10. **Änderungen** an Commands oder Kategorien: **dieses Dokument** §4 und §9 pflegen und Registry-Review.

---

## Referenz & Revision

| Dokument | Bezug |
|----------|--------|
| `QML_GUI_VISUAL_ARCHITECTURE_MAP.md` | Shell, Domänen, Routing-Wahrheit |

| Datum | Änderung |
|-------|----------|
| 2026-03-24 | Erstfassung Command Palette & Quick Actions |
