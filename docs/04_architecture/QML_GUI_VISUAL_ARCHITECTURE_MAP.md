# Visuelle Gesamtarchitektur der QML-GUI (Linux Desktop Chat)

**Status:** Referenzkarte für Umsetzung und Konsistenz — beschreibt den **Ist-Zustand der Shell** (Repo-Stand) und die **intendierte Raumlogik**, ohne Implementierungsvorgaben oder QML-Code.

**Technische Anker im Repo:** `qml/AppRoot.qml`, `qml/shell/AppChrome.qml`, `qml/shell/NavRail.qml`, `qml/shell/StageHost.qml`, `qml/shell/OverlayHost.qml`, `app/ui_runtime/qml/shell_bridge_facade.py`, `app/ui_runtime/qml/shell_navigation_state.py`, `app/ui_runtime/qml/qml_runtime.py`, Domänen unter `qml/domains/*/`, Foundation unter `qml/foundation/`, Themes unter `qml/themes/`.

---

## 1. SYSTEM-WEITE RAUMKARTE

### 1.1 Bibliotheksmetapher (Leitbild)

Die GUI ist als **räumlich geordnete Wissensmaschine** gedacht: Räume haben Rollen wie in einer Bibliothek/Druckerei (Lesetisch, Archiv, Planungstafel, Regal, Arbeitsstation, Verlag, Hausordnung). Das ist **kein** Tab-Zoo und kein monolithisches Dashboard, sondern **wechselnde Hauptbühnen** mit gemeinsamer Shell-Grammatik.

### 1.2 Gewichtung: drei tragende Säulen + Spezialräume

| Gewicht | Räume | Rolle |
|--------|--------|--------|
| **Strukturell zentral** | **Chat**, **Projects**, **Workflows** | Chat = primärer Denk- und Dialograum; Projects = organisatorischer Rahmen (Projekt → Chats, Kontext, Artefakte); Workflows = Prozess- und Automationsraum. Alle drei sind **gleichwertig in der Navigation** hintereinander sichtbar (Reihenfolge siehe §2), nicht „Unterseiten“ von Chat. |
| **Stark unterstützend** | **Prompts** (Prompt Studio), **Agents** | Spezialisierte Ressourcen und Ausführungseinheiten; viele fachlichen Pfade laufen über sie, ohne dass sie die alleinige Startinstanz sein müssen. |
| **Betrieb / Auslieferung** | **Deployment** | Verlag/Druckerei — Artefakte, Ziele, Rollouts; stützt sich auf Ergebnisse und Definitionen aus anderen Räumen. |
| **Querschnitt** | **Settings** | Regeln, Provider, Erscheinungsbild, Datenpfade — wirkt **auf alle** Stages, bleibt eigenständiger Raum. |

### 1.3 Gesamtdiagramm (logische Anordnung)

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                    SETTINGS (Querschnitt)                 │
                    │         Policies · Provider · Appearance · Daten        │
                    └───────────────────────────┬─────────────────────────────┘
                                                │ wirkt auf
                                                ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                           APPLICATION SHELL (global)                          │
│  NavRail  │  StageHost (aktive Domänen-Stage)  │  OverlayHost (reserviert)   │
└───────────────────────────────────────────────────────────────────────────────┘
          │
          ├──────────────┬──────────────┬──────────────┬──────────────┬─────────┐
          ▼              ▼              ▼              ▼              ▼         ▼
      CHAT          PROJECTS      PROMPT STUDIO    WORKFLOWS      AGENTS   DEPLOYMENT
   Denkraum       War Room /        Regal /      Planungstafel   Dienst-   Verlag /
                  Archiv           Katalog        Prozess        liste     Rollout
```

### 1.4 Zusammenarbeit (stark gekoppelt)

```
  PROJECTS ──────► Chats, Workflows, Agents, Dateien, Kontext (organisatorisch)
       │
       └──────────► aktiver Projektkontext (global, außerhalb QML sichtbar)

  WORKFLOWS ─────► Prompts, Agents (Knoten / Rollen / Aufrufe)
       │
       └──────────► Deployment (Artefakte, Freigaben, Ziele)

  CHAT ──────────► Projekt + Kontextpolicies + Modellrouting (Settings)
```

**Entscheidung zur Anordnung:** Chat bleibt **Einstieg und emotionaler Mittelpunkt** (Default-Domain im Shell-State: `chat`), Projects und Workflows werden **nicht** hierarchisch unter Chat versteckt, sondern als **eigenständige Hauptbühnen** geführt — passend zu einer AI-Operations-Plattform, in der Organisation (Projects) und Prozess (Workflows) genauso oft geöffnet werden wie der Dialograum.

---

## 2. NAVIGATIONSKARTE

### 2.1 Primärnavigation (Ist: NavRail + ShellBridge)

Die **einzige durchgängige globale Liste** der Hauptbühnen ist die **Navigation Rail**; sie spricht mit `ShellBridgeFacade.requestDomainChange(domainId)` und lädt die zugehörige Stage-QML-Datei in den `StageHost`-`Loader`.

**Reihenfolge (Ist, `shell_navigation_state.py`):**

| # | Domain-ID        | Label (UI)     | Stage (rel. zu `qml/`)        |
|---|------------------|----------------|-------------------------------|
| 1 | `chat`           | Chat           | `domains/chat/ChatStage.qml`  |
| 2 | `projects`       | Projekte       | `domains/projects/ProjectStage.qml` |
| 3 | `prompt_studio`  | Prompt Studio  | `domains/prompts/PromptStage.qml` |
| 4 | `workflows`      | Workflows      | `domains/workflows/WorkflowStage.qml` |
| 5 | `agent_tasks`    | Agenten        | `domains/agents/AgentStage.qml` |
| 6 | `deployment`     | Deployment     | `domains/deployment/DeploymentStage.qml` |
| 7 | `settings`       | Settings       | `domains/settings/SettingsStage.qml` |

### 2.2 Begründung der Reihenfolge

1. **Chat zuerst** — häufigster Einstieg, Default-Domain.
2. **Projects direkt danach** — organisatorischer Rahmen für alles Weitere; Kurzweg vom Denkraum zum „War Room“.
3. **Prompt Studio vor Workflows** — Katalog/Bearbeitung vor graphischer Orchestrierung (Ressource vor Prozess).
4. **Workflows** — zentrale Planungstafel, oft nach Kontext aus Projects/Prompts.
5. **Agents** — Ausführung und Profile, ergänzt Workflows und Chat.
6. **Deployment** — Betrieb/Release; seltener im Tagesrhythmus, aber eigener Raum.
7. **Settings zuletzt** — Querschnitt; bewusst nicht in der Mitte, um keine „Menü-Mitte“ zu suggerieren.

### 2.3 Erreichbarkeit

| Typ | Was |
|-----|-----|
| **Direkt erreichbar** | Alle sieben Einträge — ein Klick, voller Stage-Wechsel. |
| **Häufige Wechsel** | Chat ↔ Projects; Projects ↔ Workflows; Workflows ↔ Prompts; Workflows ↔ Agents; Chat ↔ Settings (Modell/Kontext). |
| **Seltenere Wechsel** | Deployment ↔ Settings; Deployment ↔ Workflows (ohne tägliche Pflege). |

### 2.4 Navigationsmodell (über die Rail hinaus)

```
┌─────────────────────────────────────────────────────────────────┐
│  PRIMÄR: NavRail  →  shell.requestDomainChange(domainId)        │
│           ein aktiver globaler „Screen“-Zustand (activeDomain)    │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
   Kontextsprung         Quick Action          Command Palette
   (in Stage: z. B.       (in Stage: Buttons   (noch nicht als
    „Zu Workflows“)        zu anderer Domain)     globale Shell —
    über dieselbe          explizit erlaubt,      später; darf
    Bridge-API             solange Rail-State     dieselbe domain-
    synchron halten)       konsistent bleibt)     Logik nutzen)
```

**Regel:** Jeder Wechsel der **sichtbaren Hauptbühne** soll langfristig dieselbe **Routing-Wahrheit** wie die Rail haben (kein „geheimer“ paralleler Stack ohne Shell-State).

---

## 3. STAGE-/SUBSTAGE-MODELL

### 3.1 Globale Schichten

| Schicht | Komponente (Ist) | Funktion |
|---------|------------------|----------|
| Fenster | `ApplicationWindow` (`AppRoot.qml`) | Root; Theme-Hintergrund, Titel. |
| Chrome | `AppChrome` | Horizontal: **NavRail \| Trenner \| StageHost**; **OverlayHost** full-rect obenauf (z aktuell minimal). |
| Arbeitsfläche | `StageHost` → `WorkSurface` → `Loader` | Lädt **genau eine** aktive Domain-Stage aus `shell.stageUrl`. |
| Überlagerung | `OverlayHost` | Reserviert für modale/overlay UI (Ist: Platzhalter-Layer mit hohem `z`). |
| Domäne | `*Stage.qml` je Domain | Trägt **domänenspezifisches** Layout (Spalten, Regale, Canvas, Inspector). |

### 3.2 Begriffe SideSurface / DrawerSurface

| Begriff | Ist im Repo | Bedeutung für die Karte |
|---------|-------------|-------------------------|
| **SideSurface** | Nicht als eigenes Modul benannt; **in den Stages** als linke/rechte Spalten (z. B. Listen, Inspector, Kontext). | **Konzeptionell:** seitliche Flächen mit **Lesen/Auswahl**; visuell über Foundation-Tokens (Surfaces, Divider). |
| **DrawerSurface** | Kein globaler Drawer in der Shell beschrieben. | **Konzeptionell:** optional ausklappbare Tiefe (z. B. tiefe Einstellungen, mobile-first — wenn eingeführt, nicht die Rail ersetzen). |
| **OverlaySurface** | `OverlayHost` + in Stages `Dialog`/`Popup` mit `Overlay.overlay` (z. B. Projects Löschdialog). | Modal über der Bühne; globale Toasts könnten hier anbinden. |

### 3.3 Substages pro Domäne (Mindeststruktur — aus Ist-Stages abgeleitet)

| Domain | Typische Substages / Zonen (konzeptionell) |
|--------|---------------------------------------------|
| **Chat** | Session-Bereich, Lesetisch/Manuskript, Composer, Kontext-/Kontextfläche. |
| **Projects** | Projektliste, War-Room-Übersicht (Chats/Workflows/Agents/Dateien), Inspector. |
| **Prompts** | Katalog/Regal, zentrale Bearbeitung, ggf. Lesepult/Inspector. |
| **Workflows** | Listen/Übersicht, Graph/Canvas, Inspector, Run-Historie (je nach Stage-Ausbau). |
| **Agents** | Roster, Arbeitsstation/Task-Fläche, Inspector. |
| **Deployment** | Boards/Lines je nach Stage-Design (Releases, Targets, Rollouts). |
| **Settings** | Kategorienavigation + Inhaltsstack + ggf. Hilfe/Inspector. |

**Gemeinsame Grammatik:** Abstände, Flächenfarben, Typo, Radien aus **Foundation + LibraryTheme**; jede Stage bleibt **eine** geladene Datei mit **interner** Spaltenlogik — keine zweite globale Navigationsleiste pro Domain.

---

## 4. DOMÄNEN-BEZIEHUNGEN

### 4.1 Abhängigkeitsgraph (fachlich)

```
                    ┌─────────────┐
                    │  SETTINGS   │
                    └──────┬──────┘
                           │ Policies, Models, Theme, Datenpfade
     ┌─────────────────────┼─────────────────────┐
     ▼                     ▼                     ▼
┌─────────┐         ┌───────────┐         ┌──────────┐
│  CHAT   │◄───────►│ PROJECTS  │◄───────►│ WORKFLOW │
└────┬────┘         └─────┬─────┘         └────┬─────┘
     │                    │                    │
     │                    │    ┌───────────────┤
     │                    │    │               │
     ▼                    ▼    ▼               ▼
     │              ┌─────────┴────┐    ┌──────────┐
     │              │ PROMPTS      │    │ AGENTS   │
     │              └──────┬───────┘    └────┬─────┘
     │                     │                 │
     └─────────────────────┴────────┬──────────┘
                                  ▼
                           ┌────────────┐
                           │ DEPLOYMENT │
                           └────────────┘
```

### 4.2 Kurzmatrix

| Von | Nach | Beziehung |
|-----|------|-----------|
| Projects | Chat | Projekt umfasst/zuordnet Chats; aktiver Projektkontext speist Chat-Kontext. |
| Projects | Workflows | Projekt als Scope für projektgebundene Workflows (fachlich/DB-seitig verankert). |
| Projects | Agents | Agentenprofile projektgebunden oder global; War Room zeigt Überblick. |
| Workflows | Prompts | Knoten/Typen referenzieren Prompt-Builds und Vorlagen. |
| Workflows | Agents | Agent-Knoten, Delegation. |
| Chat | Settings | Modellrouting, Kontextmodi, Provider. |
| Deployment | Workflows / Agents | Artefakte und Freigaben aus dem Betriebsprozess. |
| Settings | alle | Querschnitt — keine Inhalte, aber Regeln für alle Stages. |

---

## 5. SHELL-ARCHITEKTURKARTE

### 5.1 Baum (Ist)

```
ApplicationWindow (AppRoot)
├── color / title / Theme-Hintergrund
└── AppChrome (RowLayout + OverlayHost)
    ├── NavRail                    ← GLOBAL: Domain-IDs, Labels, activeDomain
    ├── Trennlinie
    ├── StageHost                  ← GLOBAL: WorkSurface + Loader(stageUrl)
    │   └── [aktive *Stage.qml]    ← DOMÄNENSPEZIFISCH
    └── OverlayHost (z full rect)  ← GLOBALER Slot (Ist: leer/transparenter Reserve-Layer)
```

### 5.2 Global vs. domänenspezifisch

| Element | Global | Domänenspezifisch |
|---------|--------|-------------------|
| `shell` (Bridge) | ✓ activeDomain, stageUrl, requestDomainChange | — |
| NavRail | ✓ | — |
| StageHost / WorkSurface | ✓ Rahmen, Margins | — |
| Loader-Inhalt | — | ✓ je `*Stage.qml` |
| Context properties (`chat`, `projectStudio`, …) | Registrierung in `QmlRuntime` | ✓ je Domain-VM |
| Modals (`Dialog`) | — | ✓ in Domain-QML (nutzen `Overlay.overlay`) |
| Foundation / Theme | ✓ Tokens | ✓ Anwendung in Komponenten |

### 5.3 Noch nicht als Shell-Baustein im Repo ausgebaut (Platz halten)

| Zone | Zweck |
|------|--------|
| **Toast / Notification** | Querschnitts-Feedback ohne Stage-Wechsel. |
| **Command Palette** | Schnellwechsel Domain + Aktionen; muss `activeDomain`/`stageUrl` konsistent halten. |
| **Statusleiste / Kontextzeile** | Aktives Projekt, Verbindung, Modus — optional unterhalb der Stage oder in Chrome. |

---

## 6. DATENFLUSS-KARTE

### 6.1 Schichten (QML-Pfad, Ist + nahe Widget-Pipeline)

Die QML-Shell hält **keine** Service-Objekte im Root-Kontext; Anbindung erfolgt über **pro-Domain-ViewModels** (u. a. `python_bridge/*`, `app/ui_runtime/qml/chat/*`).

```
┌─────────────────────────────────────────────────────────────────────────┐
│  QML STAGE (*Stage.qml)                                                 │
│    └── View-Komponenten (Listen, Canvas, Forms) — nur Darstellung/Input   │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │ Properties, Signals, Slots
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  QML VIEWMODEL / BRIDGE (QObject, context property z. B. chat,          │
│                          projectStudio, workflowStudio, …)              │
│    — setzt QAbstractListModel / Properties für Binding                   │
│    — ruft synchron oder orchestriert async (z. B. Chat + schedule_coro)  │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
          ┌─────────────────────────┴─────────────────────────┐
          │ Widget-/Alt-Pfad (weiterhin im Produkt vorhanden):   │
          ▼                                                     │
┌──────────────────────┐                                        │
│ Presenter / Facade   │  (app/ui_application/presenters, …)   │
└──────────┬───────────┘                                        │
           ▼                                                    │
┌──────────────────────┐                                        │
│ Port (Interface)     │                                        │
└──────────┬───────────┘                                        │
           ▼                                                    │
┌──────────────────────┐                                        │
│ Adapter              │                                        │
└──────────┬───────────┘                                        │
           ▼                                                    │
┌──────────────────────┐◄───────────────────────────────────────┘
│ Service / Infra      │  (app/services/*, DB, Provider, …)
└──────────────────────┘
```

**Kernregel:** QML-Bridge darf **Orchestrierung und Mapping** machen, aber **keine** fachliche Kernlogik duplizieren (Validierung, Stream-Parsing, Persistenz-Regeln bleiben in Services bzw. bestehenden Schichten).

### 6.2 Zustände: wo was leben darf

| Zustand | Ort | Anmerkung |
|---------|-----|-----------|
| **Routing** (`activeDomain`, `stageUrl`) | `ShellBridgeFacade` / Presenter dahinter | Single Source of Truth für sichtbare Hauptbühne. |
| **Domain-Selektion** (z. B. gewählter Workflow, Projekt) | Domain-ViewModel + ggf. globaler Projektkontext (außerhalb QML) | Cross-Domain: aktiv gesetztes Projekt soll Rail-Wechsel überleben. |
| **Streaming / async tokens** | Service + VM (Chat), nicht in QML-JS | QML nur binden/anzeigen. |
| **Theme / Density** | Theme-Manifest / Registry + Foundation | Global konsistent. |

### 6.3 Explizit nicht in QML

- Direkte DB-Zugriffe, Roh-SQL, Dateisystem-Geschäftslogik.
- Parser für LLM-Streams, komplexe Policy-Entscheidungen.
- „Ersatz“ für Ports/Adapter — keine zweite Service-Schicht in `.qml`-Dateien.

---

## 7. INTERAKTIONS-KARTE

### 7.1 Routen (exemplarisch)

| Route | Warum wichtig | Ideale Unterstützung | Primär vs. Sprung |
|-------|---------------|----------------------|-------------------|
| **A. Chat ↔ Projects** | Denken im Kontext des richtigen Projekts; Übersicht über Sessions. | Rail + in Projects „Zum Chat“ (Bridge-Call wie heute); langfristig Kontextzeile „aktives Projekt“. | Rail primär; **Kontextsprung** aus Stage sinnvoll. |
| **B. Projects ↔ Workflows** | Prozessplantafel im Projektscope. | Rail; optional Deep-Link mit vorausgewähltem Projekt/Filter (wenn VM/State es erlaubt). | Rail + **Kontextsprung** von Projects. |
| **C. Workflows ↔ Agents** | Knoten und Ausführung. | Rail; im Workflow-Stage Auswahl/Inspector zu Agenten. | Mix aus **Substages** und Rail. |
| **D. Prompts ↔ Workflows** | Vorlagen in Graphen. | Rail; Nebeneinander in Arbeitsablauf: erst Katalog, dann Graph. | Rail; **selten** Palette nötig. |
| **E. Deployment ↔ Workflows** | Was wird wohin ausgeliefert. | Rail; fachliche Verknüpfung in Deployment-UI. | Rail; tiefe Details **Substages**. |
| **F. Settings ↔ global** | Alles hängt an Provider/Modellen. | Rail; nach Änderung ggf. Toast + VM-Reload in aktiver Stage. | Rail; **kein** versteckter Settings-Dialog als Ersatz für Rail. |

### 7.2 Nutzungsweg (vereinfacht)

```
  Nutzer startet in CHAT
        │
        ├─► wechselt zu PROJECTS (Rail) — organisiert Kontext
        │
        ├─► springt zu WORKFLOWS (Rail oder In-Stage-Button) — plant Automatisierung
        │
        ├─► öffnet PROMPTS (Rail) — pflegt Vorlagen
        │
        ├─► prüft AGENTS (Rail) — Profile/Ausführung
        │
        ├─► DEPLOYMENT (Rail) — wenn Release ansteht
        │
        └─► SETTINGS (Rail) — wenn Regeln/Modelle/Theme angepasst werden
```

---

## 8. ERWEITERUNGS-KARTE

### 8.1 Anbindung neuer Räume

```
  shell_navigation_state: neue domainId + Label + Stage-Pfad
           │
           ▼
  NavRail (DomainNavModel) — automatisch eine Zeile mehr
           │
           ▼
  Neues qml/domains/<name>/<Name>Stage.qml — folgt WorkSurface-Grammatik
           │
           ▼
  QmlRuntime: optionales context property für ViewModel
           │
           ▼
  python_bridge oder app/ui_runtime ViewModel — nur Mapping/Orchestrierung
```

### 8.2 Mögliche spätere Domänen (nur Einordnung)

| Raum | Rolle in der Bibliothek | Nähe zu |
|------|-------------------------|---------|
| **Knowledge / RAG** | Lesesaal / Quellenarchiv | Chat, Projects, Settings |
| **Analytics** | Ausleihstatistik / Nutzungsdiagnose | Deployment, Workflows |
| **Automation** (über Workflows hinaus) | Erweiterte Orchestrierung | Workflows, Agents |
| **Media** | Bild/Ton-Arbeitsraum | Agents, Workflows |
| **Global Timeline** | Chronik über Domänen | Querschnitt, eher Overlay als Rail-Monster |
| **Command Center** | Betriebslage | Deployment, Agents — eher Dashboard-ähnlich, **nur** wenn klar von „Operations Rail“ getrennt |

**Regel:** Neue Rail-Einträge nur mit **klarer Metapher und Prozessrolle**; sonst lieber **Substages** oder **Overlay**.

---

## 9. GOVERNANCE-REGELN FÜR DIE GESAMTKARTE

1. **Jeder neue Raum** braucht eine **einzige Satz-Rolle** im Wissens-/Operationsprozess (kein „Noch ein Screen“).
2. **Bibliotheksgrammatik:** neue UI nutzt **Foundation + Theme**; keine privaten Farb-/Spacing-Inseln ohne Absprache.
3. **Navigation:** maximal **eine** primäre globale Liste (Rail); alles Weitere = Substages, Overlay oder später Palette — **keine** tiefe Menühierarchie als Ersatz.
4. **Stages** sprechen dieselbe **Shell-Sprache**: Außenrahmen über `StageHost`/`WorkSurface`, innen domänenspezifische Spalten.
5. **Globale Shell-Elemente** (Rail, Bridge, OverlayHost) **nicht** mit domänenreinen Business-Widgets füllen.
6. **QML absorbiert keine Businesslogik** — nur Bindings, Aufrufe, Darstellung; Fachlogik in Services/Ports.
7. **Projects und Workflows** bleiben **Hauptbühnen**, nicht Unterdialoge von Chat.
8. **Chat zentral, nicht exklusiv:** Default-Einstieg ja, aber **kein** Monopol auf Navigation oder Kontext — Projects/Workflows sind gleichwertige Strukturanker.
9. **Routing-Wahrheit:** Jeder sichtbare Hauptbühnenwechsel soll mit **`activeDomain` / `stageUrl`** übereinstimmen (kein unsynchroner zweiter Stack).
10. **Dokumentationspflicht:** Änderungen an Rail oder Shell → **diese Karte** in §2, §3, §5 aktualisieren.

---

## Revision

| Datum | Änderung |
|-------|----------|
| 2026-03-24 | Erste Fassung an Repo-Ist (Shell, Domains, Bridge) und intendierte Raumlogik angeglichen. |
