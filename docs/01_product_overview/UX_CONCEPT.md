# UX-Blaupause – Linux Desktop Chat

**Version:** 1.1  
**Datum:** 2026-03-15  
**Status:** Verbindliche UX-Architektur / Pflichtenheft für Produktentwicklung  
**Technische Ableitung:** docs/PYSIDE6_UI_ARCHITECTURE.md  
**GUI-Repository-Struktur:** docs/GUI_REPOSITORY_ARCHITECTURE.md  
**Screen-/Klassenarchitektur:** docs/SCREEN_CLASS_ARCHITECTURE.md  
**Migrations-Roadmap:** docs/GUI_MIGRATION_ROADMAP.md

---

## 1. Einleitung

Dieses Dokument ist die vollständige UX-Blaupause für die Linux Desktop Chat Anwendung. Es definiert Navigation, Panel-Set, Screen-Struktur, Workflows, Informationsregeln und UI-Muster. Kein Implementierungscode – ausschließlich Architektur und UX-Spezifikation.

**Leitphilosophie:** Der Nutzer betreibt ein System, nicht ein Tool.

**Produkttyp:** AI-Operations-Plattform für Desktop-Nutzung (kein einzelnes Chat-Tool).

**Arbeitsmodus-getrieben (nicht feature-getrieben):**
1. System verstehen
2. System betreiben
3. Mit dem System arbeiten
4. System analysieren / debuggen

---

## Inhaltsverzeichnis

| Abschnitt | Inhalt |
|-----------|--------|
| 2 | Konkrete Navigation Map |
| 3 | Vollständiges Panel-Set |
| 4 | Screen-Strukturen pro Hauptbereich |
| 5 | Haupt-Workflows (Chat, Agent Tasks, Knowledge, QA, Runtime/Debug) |
| 6 | Informationsplatzierungs-Regeln |
| 7 | Desktop-Layout-Architektur |
| 8 | Agenten-UX |
| 9 | UI bei Wachstum stabil halten |
| 10 | Regeln zur Kontrolle der UI-Komplexität |
| 11 | Empfehlungen für skalierbare Desktop-UX |
| 12 | Konsistente UI-Muster |
| 13 | Zusammenfassung |

---

## 2. Konkrete Navigation Map

### 2.1 Globale Hauptnavigation (6 Bereiche)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  NAVIGATION SIDEBAR (links, hierarchisch, Icon + Text)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  🏠 Kommandozentrale                                                         │
│  📋 Operations                                                               │
│      ├── Chat Workspace                                                      │
│      ├── Agent Tasks                                                         │
│      ├── Knowledge / RAG                                                     │
│      └── Prompt Studio                                                       │
│  ⚙️  Control Center                                                          │
│      ├── Models                                                              │
│      ├── Providers                                                           │
│      ├── Agents                                                              │
│      ├── Tools                                                               │
│      └── Data Stores                                                         │
│  📊 QA & Governance                                                          │
│      ├── Test Inventory                                                      │
│      ├── Coverage Map                                                        │
│      ├── Gap Analysis                                                        │
│      ├── Incidents                                                           │
│      └── Replay Lab                                                          │
│  🔍 Runtime / Debug                                                           │
│      ├── EventBus Monitor                                                    │
│      ├── Logs                                                                │
│      ├── Metrics                                                             │
│      ├── LLM Calls                                                           │
│      ├── Agent Activity                                                      │
│      └── System Graph                                                        │
│  ⚙️  Settings                                                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Navigationsregeln

| Regel | Beschreibung |
|-------|--------------|
| **Einstieg** | Kommandozentrale ist der Standard-Einstieg nach Start |
| **Tiefe** | Maximal 2 Ebenen in der Sidebar sichtbar; Drilldown erfolgt im Main Workspace |
| **Kontext** | Sidebar zeigt immer den aktuellen Hauptbereich; Unterbereiche sind kontextabhängig |
| **Kein Verstecken** | QA & Governance, Runtime/Debug sind gleichberechtigte Hauptbereiche – nicht in Dialogen versteckt |
| **Agenten-Sichtbarkeit** | Agenten erscheinen in Operations (Agent Tasks), Control Center (Agents), Runtime/Debug (Agent Activity) |

### 2.3 Abgrenzung zur aktuellen Implementierung

| Aktuell | Ziel |
|---------|------|
| Toolbar-Button „Kommandozentrale“ → QA-Dashboard | Sidebar „Kommandozentrale“ → reine Übersicht; QA → eigener Bereich „QA & Governance“ |
| Chat + Sidepanel (Modelle, Prompts, Debug) | Chat im Operations; Modelle/Prompts → Control Center bzw. Prompt Studio; Debug → Runtime/Debug |
| Agent Manager als Dialog | Agent Design → Control Center / Agents; Agent Control → Operations / Agent Tasks |
| Keine Bottom Panel | Bottom Panel für Logs, Events, Metrics, Agent Activity |

---

## 3. Exaktes Panel-Set

### 3.1 Generische Panel-Typen (5 Typen)

| Typ | Zweck | Verwendung | Beispiel |
|-----|------|------------|----------|
| **Explorer Panel** | Hierarchische Liste, Baum, Dateien, Objekte | Links oder als Tab-Inhalt | Chat-Sessions, Test Inventory, Agent Registry |
| **Editor Panel** | Bearbeitung eines einzelnen Objekts | Main Workspace | Chat Composer, Prompt Editor, Agent Editor |
| **Inspector Panel** | Metadaten, Kontext, Details zum aktuellen Objekt | Rechts | Session-Details, Modell-Info, Test-Details |
| **Monitor Panel** | Live-Daten, Streams, Status | Bottom Panel oder rechts | Logs, EventBus, Metrics, Agent Activity |
| **Dashboard Panel** | Aggregierte Übersicht, Karten, KPIs | Main Workspace | Kommandozentrale, QA Status |

### 3.2 Mapping: Bereich → Panel-Typen

| Hauptbereich | Primär | Sekundär | Tertiär |
|--------------|--------|----------|---------|
| Kommandozentrale | Dashboard | — | — |
| Operations / Chat | Editor (Chat) | Explorer (Sessions) | Inspector (Session-Kontext) |
| Operations / Agent Tasks | Explorer + Editor | Inspector | Monitor (Activity) |
| Operations / Knowledge | Explorer | Editor | Inspector |
| Operations / Prompt Studio | Explorer + Editor | Inspector | — |
| Control Center | Explorer | Editor | Inspector |
| QA & Governance | Explorer + Dashboard | Editor | Inspector |
| Runtime / Debug | Monitor | Explorer (Event-Liste) | — |
| Settings | Editor | — | — |

### 3.3 Panel-Limit-Regel

**Maximal 3 zentrale Informationsflächen gleichzeitig im Fokus.**

- Main Workspace: 1 primäre Fläche (Editor oder Dashboard)
- Inspector: 0 oder 1 (bei Bedarf)
- Bottom Panel: 0 oder 1 (bei Bedarf)

Explorer kann als Sidebar dauerhaft sichtbar sein, zählt aber nicht als „zentrale Fläche“ – er ist Navigations- und Auswahlhilfe.

### 3.4 Vollständiges Panel-Inventar (alle Panels der Anwendung)

| # | Panel-Name | Typ | Bereich | Zone | Zweck |
|---|------------|-----|---------|------|-------|
| 1 | Kommandozentrale Dashboard | Dashboard | Kommandozentrale | Main | System Status, Active Work, QA Status, Incidents, Quick Actions |
| 2 | Session Explorer | Explorer | Operations / Chat | Sidebar | Chat-Sessions, Projekte, Suche |
| 3 | Chat Editor | Editor | Operations / Chat | Main | Conversation View + Composer |
| 4 | Session Inspector | Inspector | Operations / Chat | Rechts | Session-Metadaten, RAG-Kontext, angehängte Dateien |
| 5 | Task Explorer | Explorer | Operations / Agent Tasks | Sidebar/Main | Task-Liste, Queue, Filter |
| 6 | Task Editor | Editor | Operations / Agent Tasks | Main | Beauftragung, Parameter, Ergebnis |
| 7 | Agent Inspector | Inspector | Operations / Agent Tasks | Rechts | Agent-Info, Delegationen, Status |
| 8 | Collection Explorer | Explorer | Operations / Knowledge | Sidebar | Wissensräume, Collections |
| 9 | Document Editor | Editor | Operations / Knowledge | Main | Dokumente, Indizierung, Embedding |
| 10 | Collection Inspector | Inspector | Operations / Knowledge | Rechts | Collection-Details, Embedding-Info |
| 11 | Prompt Explorer | Explorer | Operations / Prompt Studio | Sidebar | Prompt-Liste, Kategorien |
| 12 | Prompt Editor | Editor | Operations / Prompt Studio | Main | Prompt bearbeiten, Vorschau |
| 13 | Prompt Inspector | Inspector | Operations / Prompt Studio | Rechts | Variablen, Metadaten |
| 14 | Model Explorer | Explorer | Control Center / Models | Sidebar | Modell-Liste |
| 15 | Model Editor | Editor | Control Center / Models | Main | Modell-Details, Parameter |
| 16 | Provider Explorer | Explorer | Control Center / Providers | Sidebar | Provider-Liste |
| 17 | Provider Editor | Editor | Control Center / Providers | Main | Provider-Konfiguration |
| 18 | Agent Registry | Explorer | Control Center / Agents | Sidebar | Agenten-Liste |
| 19 | Agent Editor | Editor | Control Center / Agents | Main | Agent-Definition, Konfiguration |
| 20 | Tool Explorer | Explorer | Control Center / Tools | Sidebar | Tool-Liste |
| 21 | Tool Editor | Editor | Control Center / Tools | Main | Tool-Konfiguration |
| 22 | Data Store Explorer | Explorer | Control Center / Data Stores | Sidebar | Store-Liste |
| 23 | Data Store Editor | Editor | Control Center / Data Stores | Main | Store-Konfiguration |
| 24 | Test Inventory Explorer | Explorer | QA / Test Inventory | Sidebar/Main | Tests nach Subsystem/Domain/Type |
| 25 | Test Inspector | Inspector | QA / Test Inventory | Rechts | Test-Details |
| 26 | Coverage Dashboard | Dashboard | QA / Coverage Map | Main | Achsen, Failure Classes, Regression |
| 27 | Gap Dashboard | Dashboard | QA / Gap Analysis | Main | Priorisierte Gaps |
| 28 | Gap Editor | Editor | QA / Gap Analysis | Main | Gap-Detail, Aktionen |
| 29 | Incident Explorer | Explorer | QA / Incidents | Sidebar | Incident-Liste |
| 30 | Incident Editor | Editor | QA / Incidents | Main | Incident-Detail, Bindings |
| 31 | Replay Explorer | Explorer | QA / Replay Lab | Sidebar | Replay-Szenarien |
| 32 | Replay Editor | Editor | QA / Replay Lab | Main | Replay ausführen, Ergebnis |
| 33 | EventBus Monitor | Monitor | Runtime / Debug | Main/Bottom | Event-Stream |
| 34 | Log Monitor | Monitor | Runtime / Debug | Main/Bottom | Anwendungslogs |
| 35 | Metrics Monitor | Monitor | Runtime / Debug | Main/Bottom | Laufzeit-Metriken |
| 36 | LLM Trace Monitor | Monitor | Runtime / Debug | Main/Bottom | LLM-Aufrufe, Token |
| 37 | Agent Activity Monitor | Monitor | Runtime / Debug | Main/Bottom | Laufende Agenten, Schritte |
| 38 | System Graph | Monitor | Runtime / Debug | Main | System-Zustandsgraph |
| 39 | Settings Editor | Editor | Settings | Main/Modal | Theme, API-Keys, Präferenzen |
| 40 | Navigation Sidebar | — | Global | Links | Bereichswechsel (kein Panel im engeren Sinne) |
| 41 | Top Bar | — | Global | Oben | Status, Suche, Quick Actions |
| 42 | Bottom Panel (Container) | — | Global | Unten | Host für Logs, Events, Metrics, Agent Activity, LLM Trace |

**Gesamt: 39 funktionale Panels + 3 globale Zonen.** Keine weiteren Panel-Typen. Neue Features werden in bestehende Panels integriert oder nutzen einen der 5 generischen Typen.

---

## 4. Screen-zu-Screen-Struktur

### 4.1 Kommandozentrale

```
Screen: Kommandozentrale (Dashboard Panel)
├── Blöcke: System Status | Active Work | QA Status | Incidents/Warnings | Quick Actions
├── Keine tiefe Navigation
├── Quick Actions → führen zu Operations oder Control Center
└── Kein Drilldown in die Kommandozentrale selbst
```

**Transitionen:**
- Quick Action „Chat öffnen“ → Operations / Chat Workspace
- Quick Action „Agent beauftragen“ → Operations / Agent Tasks
- QA Status-Klick → QA & Governance (nicht Drilldown in Kommandozentrale)
- Incident-Warnung → QA & Governance / Incidents

### 4.2 Operations Center

```
Operations (Hauptbereich)
├── Chat Workspace
│   ├── Explorer: Sessions (links, Sidebar)
│   ├── Editor: Conversation + Composer (Main)
│   ├── Inspector: Session-Metadaten, RAG-Kontext (rechts, optional)
│   └── Keine Modelle/Prompts-Konfiguration hier – nur Kontext-Anzeige
│
├── Agent Tasks
│   ├── Explorer: Task-Liste, Queue (Main oder links)
│   ├── Editor: Task-Detail, Beauftragung (Main)
│   ├── Inspector: Agent-Info, Delegationen (rechts)
│   └── Monitor: Agent Activity (Bottom Panel, optional)
│
├── Knowledge / RAG
│   ├── Explorer: Wissensräume, Collections (links)
│   ├── Editor: Dokumente, Indizierung (Main)
│   └── Inspector: Collection-Details, Embedding-Info (rechts)
│
└── Prompt Studio
    ├── Explorer: Prompt-Liste (links)
    ├── Editor: Prompt bearbeiten, Vorschau (Main)
    └── Inspector: Prompt-Metadaten, Variablen (rechts)
```

**Transitionen:**
- Chat → Agent Tasks: z.B. „An Agent delegieren“-Aktion
- Agent Tasks → Chat: Task-Kontext öffnet Chat-Session
- Knowledge → Chat: RAG-Kontext in Chat einbinden
- Prompt Studio → Chat: Prompt in Composer übernehmen

### 4.3 Control Center

```
Control Center (Hauptbereich)
├── Models
│   ├── Explorer: Modell-Liste
│   └── Editor: Modell-Details, Konfiguration
│
├── Providers
│   ├── Explorer: Provider-Liste (Local, Cloud)
│   └── Editor: Provider-Konfiguration
│
├── Agents
│   ├── Explorer: Agent Registry (Agenten-Liste)
│   └── Editor: Agent Editor (Definition, Konfiguration)
│
├── Tools
│   ├── Explorer: Tool-Liste
│   └── Editor: Tool-Konfiguration
│
└── Data Stores
    ├── Explorer: Store-Liste (Chroma, SQLite, …)
    └── Editor: Store-Konfiguration
```

**Transitionen:**
- Agents → Operations / Agent Tasks: „Agent beauftragen“
- Models → Chat: Modell für Session auswählen (Kontext, nicht Konfiguration)

### 4.4 QA & Governance

```
QA & Governance (Hauptbereich)
├── Test Inventory
│   ├── Explorer: Tests nach Subsystem/Domain/Type
│   └── Inspector: Test-Details
│
├── Coverage Map
│   ├── Dashboard: Achsen, Failure Classes, Regression
│   └── Explorer: Backlog-Items
│
├── Gap Analysis
│   ├── Dashboard: Priorisierte Gaps
│   └── Editor: Gap-Detail
│
├── Incidents
│   ├── Explorer: Incident-Liste
│   └── Editor: Incident-Detail, Bindings
│
└── Replay Lab
    ├── Explorer: Replay-Szenarien
    └── Editor: Replay ausführen, Ergebnis
```

**Transitionen:**
- Kommandozentrale QA Status → Gap Analysis oder Test Inventory
- Incident → Replay Lab: Replay aus Incident erstellen

### 4.5 Runtime / Debug

```
Runtime / Debug (Hauptbereich)
├── EventBus Monitor
├── Logs
├── Metrics
├── LLM Calls
├── Agent Activity
└── System Graph
```

**Layout:** Diese Bereiche können als Tabs im Main Workspace erscheinen ODER als Inhalte des Bottom Panels, wenn der Nutzer im Operations-Bereich arbeitet.

**Transitionen:**
- Operations / Chat → Runtime: Debug-Panel einblenden (Bottom Panel)
- Agent Tasks → Agent Activity: Laufende Agenten beobachten

### 4.6 Settings

```
Settings (Hauptbereich oder Modal)
├── Editor: Einstellungen (Theme, API-Keys, allgemeine Präferenzen)
└── Keine Unterbereiche in der Sidebar – Settings ist flach
```

---

## 5. Kern-Workflows pro Hauptbereich

### 5.1 Kommandozentrale

| Workflow | Schritte | Ziel |
|----------|----------|------|
| **Situational Awareness** | Öffnen → Blöcke lesen → ggf. Quick Action | Nutzer weiß, was passiert |
| **Schnellzugriff Chat** | Quick Action „Chat“ → Operations / Chat | Direkt arbeiten |
| **Schnellzugriff Agent** | Quick Action „Agent beauftragen“ → Agent Tasks | Task erstellen |
| **Incident prüfen** | Incident-Warnung → QA & Governance / Incidents | Incident untersuchen |

### 5.2 Operations / Chat – Haupt-Workflows (detailliert)

| Workflow | Schritte | Exit-Punkte | Fehlerfälle |
|----------|----------|-------------|--------------|
| **Chat starten** | 1. Sidebar: Session wählen oder „Neuer Chat“ 2. Main: Composer fokussieren 3. Nachricht eingeben, senden | Chat aktiv | Keine Session → leere Conversation; Modell nicht geladen → Hinweis in Top Bar |
| **RAG einbinden** | 1. Operations → Knowledge 2. Collection wählen 3. „In Chat verwenden“ 4. Zurück zu Chat 5. RAG-Kontext erscheint im Inspector (optional) | Chat mit RAG-Kontext | Keine Collection → Hinweis; Embedding fehlt → Indizierung anbieten |
| **Agent delegieren** | 1. Im Chat: Aktion „Delegieren“ oder Slash-Command 2. Agent auswählen (aus Registry) 3. Task-Parameter eingeben 4. Task starten 5. Wechsel zu Agent Tasks oder Bottom Panel (Activity) | Agent Tasks / Bottom Panel | Agent nicht verfügbar → Control Center verweisen |
| **Prompt nutzen** | 1. Operations → Prompt Studio 2. Prompt wählen 3. „In Composer übernehmen“ 4. Zurück zu Chat 5. Prompt als System-Kontext gesetzt | Chat mit Prompt | Prompt leer → Validierung |

### 5.3 Operations / Agent Tasks – Haupt-Workflows (detailliert)

| Workflow | Schritte | Exit-Punkte | Fehlerfälle |
|----------|----------|-------------|-------------|
| **Task beauftragen** | 1. Agent Tasks öffnen 2. „Neuer Task“ 3. Agent wählen (Dropdown/Explorer) 4. Parameter eingeben (Ziel, Kontext) 5. Start 6. Task erscheint in Queue/Liste mit Status „queued“ → „running“ | Task läuft | Agent nicht definiert → Control Center; Provider offline → Warnung |
| **Task überwachen** | 1. Task-Liste → Task auswählen 2. Inspector: Agent-Info, Delegationen 3. Bottom Panel: Agent Activity (optional einblenden) 4. Status: running → waiting → finished/failed | Task abgeschlossen | Task hängt → Timeout-Anzeige; failed → Fehlerdetails im Inspector |
| **Task abschließen** | 1. Task mit Status „finished“ auswählen 2. Ergebnis im Editor anzeigen 3. Optional: „In Chat übernehmen“ 4. Task archivieren oder löschen | Chat oder Task-Liste | Ergebnis leer → Hinweis |

### 5.4 Operations / Knowledge – Haupt-Workflows (detailliert)

| Workflow | Schritte | Exit-Punkte | Fehlerfälle |
|----------|----------|-------------|-------------|
| **Collection verwalten** | 1. Knowledge öffnen 2. Collection erstellen oder wählen 3. Dokumente hinzufügen (Drag&Drop, Dateiauswahl) 4. Indizierung starten 5. Inspector: Embedding-Info prüfen | Collection bereit | Embedding-Service offline → Fehlermeldung; ChromaDB Fehler → Hinweis |
| **Kontext in Chat** | 1. Collection wählen 2. „In Chat verwenden“ 3. Zurück zu Chat 4. RAG-Retrieval aktiv für Session | Chat mit RAG | Collection leer → Warnung |

### 5.5 Operations / Prompt Studio – Haupt-Workflows

| Workflow | Schritte | Ziel |
|----------|----------|------|
| **Prompt erstellen** | Neu → Editor → Variablen definieren → Speichern | Prompt verfügbar |
| **Prompt in Chat** | Prompt wählen → „In Composer“ | System-Prompt setzen |

### 5.6 Control Center

| Workflow | Schritte | Ziel |
|----------|----------|------|
| **Modell konfigurieren** | Models → Modell wählen → Parameter setzen | Modell nutzbar |
| **Agent definieren** | Agents → Agent Editor → Speichern | Agent verfügbar |
| **Provider einrichten** | Providers → Konfiguration | Ollama Local/Cloud |

### 5.7 QA & Governance – Haupt-Workflows (detailliert)

| Workflow | Schritte | Exit-Punkte | Fehlerfälle |
|----------|----------|-------------|-------------|
| **Test-Status prüfen** | 1. QA → Test Inventory 2. Nach Subsystem/Domain filtern 3. Test auswählen 4. Inspector: Details (Failure Class, Regression) | Überblick | Keine Daten → Adapter-Fehler prüfen |
| **Gap priorisieren** | 1. QA → Gap Analysis 2. Priorisierte Gaps anzeigen 3. Gap auswählen 4. Aktion: Test erstellen, Backlog zuordnen | Gap bearbeitet | Keine Gaps → Hinweis |
| **Incident untersuchen** | 1. QA → Incidents 2. Incident auswählen 3. Detail: Bindings, Replay-Status 4. Optional: „Replay erstellen“ → Replay Lab | Replay Lab | Incident ohne Binding → Hinweis |
| **Replay ausführen** | 1. QA → Replay Lab 2. Szenario wählen oder aus Incident erstellen 3. Ausführen 4. Ergebnis anzeigen (Pass/Fail) | Verifikation | Replay fehlgeschlagen → Fehlerdetails |

### 5.8 Runtime / Debug – Haupt-Workflows (detailliert)

| Workflow | Schritte | Exit-Punkte | Fehlerfälle |
|----------|----------|-------------|-------------|
| **Live beobachten** | 1. Runtime/Debug öffnen 2. Tab wählen: EventBus, Logs, Metrics 3. Stream beobachten 4. Filter setzen (optional) | Systemzustand sichtbar | Keine Events → leerer Zustand mit Hinweis |
| **Agent debuggen** | 1. Agent Activity öffnen (Runtime oder Bottom Panel) 2. Laufenden Task auswählen 3. Timeline, Tool-Calls, Model-Usage prüfen 4. Bei Fehler: Logs/Events korrelieren | Fehler gefunden | Task nicht gefunden → Hinweis |
| **LLM-Trace** | 1. LLM Calls öffnen 2. Aufruf auswählen 3. Prompt, Response, Token anzeigen | Trace analysiert | Keine Aufrufe → leerer Zustand |

### 5.6 Control Center

| Workflow | Schritte | Ziel |
|----------|----------|------|
| **Modell konfigurieren** | Models → Modell wählen → Parameter setzen | Modell nutzbar |
| **Agent definieren** | Agents → Agent Editor → Speichern | Agent verfügbar |
| **Provider einrichten** | Providers → Konfiguration | Ollama Local/Cloud |

### 5.7 QA & Governance

| Workflow | Schritte | Ziel |
|----------|----------|------|
| **Test-Status prüfen** | Test Inventory → Subsystem → Details | Überblick Tests |
| **Gap priorisieren** | Gap Analysis → Gap auswählen → Aktion | Lücke schließen |
| **Incident untersuchen** | Incidents → Incident → Replay Lab | Reproduktion |
| **Replay ausführen** | Replay Lab → Szenario → Ausführen | Verifikation |

### 5.8 Runtime / Debug

| Workflow | Schritte | Ziel |
|----------|----------|------|
| **Live beobachten** | Runtime öffnen → EventBus/Logs/Metrics | Systemzustand |
| **Agent debuggen** | Agent Activity → Task auswählen → Timeline | Fehlersuche |
| **LLM-Trace** | LLM Calls → Aufruf auswählen → Details | Prompt/Response prüfen |

---

## 6. Informationsplatzierungs-Regeln

### 6.1 Wo erscheint was – Matrix

| Information | Kommandozentrale | Operations | Control Center | QA & Gov | Runtime/Debug |
|-------------|------------------|------------|----------------|----------|---------------|
| System Status (Ollama, Provider) | ✓ (aggregiert) | — | ✓ (Details) | — | ✓ (Live) |
| Active Work (laufende Tasks) | ✓ (Kurz) | ✓ (voll) | — | — | ✓ (voll) |
| QA Status (Tests, Gaps) | ✓ (Kurz) | — | — | ✓ (voll) | — |
| Incidents / Warnings | ✓ (Kurz) | — | — | ✓ (voll) | — |
| Quick Actions | ✓ | — | — | — | — |
| Chat Sessions | — | ✓ | — | — | — |
| Agent Tasks | — | ✓ | — | — | ✓ (Activity) |
| RAG / Knowledge | — | ✓ | — | — | — |
| Prompts | — | ✓ (Prompt Studio) | — | — | — |
| Modell-Konfiguration | — | — | ✓ | — | — |
| Provider-Konfiguration | — | — | ✓ | — | — |
| Agent-Definition | — | — | ✓ | — | — |
| Tool-Konfiguration | — | — | ✓ | — | — |
| Test Inventory | — | — | — | ✓ | — |
| Coverage Map | — | — | — | ✓ | — |
| Gap Analysis | — | — | — | ✓ | — |
| Incidents (Detail) | — | — | — | ✓ | — |
| Replay Lab | — | — | — | ✓ | — |
| EventBus, Logs, Metrics | — | — | — | — | ✓ |
| LLM Calls | — | — | — | — | ✓ |
| Agent Activity (Live) | — | ✓ (Bottom) | — | — | ✓ |

### 6.2 Verbotene Platzierungen

| Regel | Begründung |
|-------|------------|
| **Keine Konfiguration in der Kommandozentrale** | Kommandozentrale = nur Überblick |
| **Keine QA-Details in Operations** | QA hat eigenen Bereich |
| **Keine Modell-/Provider-Konfiguration im Chat** | Chat = Arbeitskontext; Konfiguration = Control Center |
| **Keine Agent-Definition in Agent Tasks** | Agent Tasks = Beauftragen; Definition = Control Center |
| **Kein EventBus/Logs in der Kommandozentrale** | Runtime/Debug oder Bottom Panel |
| **Keine tiefe Navigation in der Kommandozentrale** | Maximal 1 Ebene; Drilldown führt in andere Bereiche |

### 6.3 Progressive Disclosure

| Kontext | Standard sichtbar | Bei Bedarf einblendbar |
|---------|-------------------|------------------------|
| Chat | Sessions + Conversation + Composer | Inspector (RAG-Kontext, Metadaten), Bottom (Logs) |
| Agent Tasks | Task-Liste + Beauftragung | Agent Activity (Bottom), Inspector (Delegationen) |
| Knowledge | Collection-Liste | Dokument-Details, Embedding-Info |
| Prompt Studio | Prompt-Liste | Variablen, Vorschau mit Kontext |
| Control Center | Explorer (Liste) | Editor (Details), Inspector (Metadaten) |

---

## 7. Desktop-Layout-Architektur (Zonen)

### 7.1 Zonen-Definition

| Zone | Position | Inhalt | Sichtbarkeit |
|------|----------|--------|--------------|
| **Top Bar** | Oben | Globaler Status, Suche/Command Palette, Quick Actions | Immer |
| **Navigation Sidebar** | Links | Hauptbereiche, Unterbereiche (hierarchisch) | Immer |
| **Main Workspace** | Mitte | Editor, Dashboard, Tab-Inhalte | Immer |
| **Inspector** | Rechts | Kontext, Metadaten, Details | Optional, einblendbar |
| **Bottom Panel** | Unten | Logs, Events, Metrics, Agent Activity | Optional, einblendbar |

### 7.2 Tab-Strategie im Main Workspace

- Pro Hauptbereich können mehrere Tabs offen sein (z.B. Chat + Agent Tasks)
- Tabs sind kontextgebunden: Wechsel Sidebar → ggf. neuer Tab-Kontext
- Schließen von Tabs: nur explizit durch Nutzer; kein Auto-Close

### 7.3 Bottom Panel – Inhalt

| Tab | Inhalt | Quelle |
|-----|--------|--------|
| Logs | Anwendungslogs | Logging |
| Events | EventBus-Stream | DebugStore |
| Metrics | Laufzeit-Metriken | MetricsCollector |
| Agent Activity | Laufende Agenten, Schritte | DebugStore, AgentService |
| LLM Trace | Aufrufe, Token | LLM-Layer |

Maximal 1 Tab des Bottom Panels aktiv; Nutzer wählt.

---

## 8. Agenten-UX: Konkretisierung

### 8.1 Drei Ebenen – Ort im System

| Ebene | Ort | Panel-Typ | Inhalt |
|-------|-----|-----------|--------|
| **Agent Control** | Operations / Agent Tasks | Explorer + Editor | Beauftragen, Queue, Task-Liste |
| **Agent Activity** | Runtime/Debug, Bottom Panel | Monitor | Schritte, Status, Tool-Calls, Laufzeiten |
| **Agent Design** | Control Center / Agents | Explorer + Editor | Definition, Konfiguration, Registry |

### 8.2 Minimales Panel-Set für Agenten

| Panel | Ort | Zweck |
|-------|-----|-------|
| Agent Tasks | Operations | Beauftragen, verwalten |
| Agent Activity | Runtime/Debug, Bottom | Live-Status |
| Agent Registry | Control Center | Liste aller Agenten |
| Agent Editor | Control Center | Definition bearbeiten |
| Agent Logs | Runtime/Debug | Protokoll pro Agent/Task |

### 8.3 Agent Lifecycle – Sichtbarkeit

| Status | Bedeutung | Darstellung (später) |
|--------|-----------|----------------------|
| idle | Bereit | Grau, inaktiv |
| queued | In Warteschlange | Gelb, Warte-Icon |
| running | Läuft | Grün, Aktiv-Icon |
| waiting | Wartet auf Input | Orange |
| finished | Abgeschlossen | Blau, Check |
| failed | Fehlgeschlagen | Rot, X |

Diese Zustände müssen in Agent Tasks und Agent Activity sichtbar sein.

### 8.4 Agenten im Chat

- Optional: Im Chat sichtbar, wenn delegiert (z.B. „Delegating to Research Agent…“)
- Kein eigener Agent-Editor im Chat – nur Verweis auf Agent Tasks oder Control Center

---

## 9. Empfehlungen: UI bei Wachstum stabil halten

### 9.1 Strukturelle Regeln

| Regel | Umsetzung |
|-------|-----------|
| **Keine neuen Hauptbereiche ohne Begründung** | Maximal 6 Hauptbereiche; neue Features in bestehende Bereiche integrieren |
| **Feature → Bereich zuordnen** | Jedes neue Feature hat genau einen primären Bereich |
| **Kein Panel-Friedhof** | Neue Panels müssen einem der 5 generischen Typen zugeordnet werden |
| **Progressive Disclosure** | Neue Komplexität standardmäßig versteckt; bei Bedarf einblendbar |

### 9.2 Entscheidungsbaum für neue Features

```
Neues Feature?
├── Ist es Konfiguration/Administration? → Control Center
├── Ist es Arbeitskontext (Chat, Task, Knowledge)? → Operations
├── Ist es QA/Governance? → QA & Governance
├── Ist es Beobachtbarkeit/Debug? → Runtime / Debug
├── Ist es Einstellung? → Settings
└── Ist es Übersicht/Schnellzugriff? → Kommandozentrale (nur Kurzinfo + Link)
```

### 9.3 Wachstums-Grenzen

| Grenze | Wert | Maßnahme bei Überschreitung |
|--------|------|----------------------------|
| Hauptbereiche | 6 | Feature in bestehenden Bereich integrieren |
| Unterbereiche pro Hauptbereich | 5–7 | Gruppieren, Sub-Navigation |
| Sichtbare Panels gleichzeitig | 3 | Progressive Disclosure, Tabs |
| Quick Actions in Kommandozentrale | 5–7 | Priorisieren, Rest in Command Palette |

### 9.4 Refactoring-Prioritäten (aus aktuellem Zustand)

1. **Kommandozentrale entlasten:** QA-spezifische Inhalte nach QA & Governance verschieben; Kommandozentrale auf reine Übersicht reduzieren
2. **Sidebar einführen:** Statt Toolbar-Navigation eine persistente Navigation Sidebar mit 6 Hauptbereichen
3. **Control Center etablieren:** Models, Providers, Agents, Tools, Data Stores aus Chat-Sidepanel und Dialogen herauslösen
4. **Bottom Panel einführen:** Logs, Events, Agent Activity aus Chat-Sidepanel in Bottom Panel verschieben
5. **Agent Tasks als eigenen Bereich:** Aus „Agent Manager“-Dialog und Chat-Kontext einen Operations-Unterbereich „Agent Tasks“ formen

---

## 10. Regeln zur langfristigen Kontrolle der UI-Komplexität

### 10.1 Hard Limits

| Regel | Grenze | Konsequenz bei Überschreitung |
|-------|--------|-------------------------------|
| Hauptbereiche | 6 | Kein 7. Bereich; Feature in bestehenden integrieren |
| Unterbereiche pro Hauptbereich | 7 | Gruppieren (z.B. „Advanced“), Sub-Navigation |
| Sichtbare zentrale Panels | 3 | Progressive Disclosure; Tabs statt parallele Panels |
| Quick Actions (Kommandozentrale) | 7 | Priorisieren; Rest in Command Palette |
| Ebenen in Explorer-Bäumen | 3 | Flachere Hierarchie; Filter statt Verschachtelung |
| Tabs pro Tab-Widget | 7 | Gruppieren; „Weitere“-Tab mit Sub-Liste |

### 10.2 Entscheidungsregeln für neue Features

| Frage | Ja → | Nein → |
|-------|------|--------|
| Ist es Konfiguration/Administration? | Control Center | Weiter |
| Ist es täglicher Arbeitskontext? | Operations | Weiter |
| Ist es QA/Governance? | QA & Governance | Weiter |
| Ist es Beobachtbarkeit/Debug? | Runtime / Debug | Weiter |
| Ist es globale Einstellung? | Settings | Weiter |
| Ist es nur Übersicht/Schnellzugriff? | Kommandozentrale (Kurzinfo + Link) | Bereich klären |

### 10.3 Anti-Patterns (verboten)

| Anti-Pattern | Stattdessen |
|--------------|-------------|
| Neues Panel für jedes Feature | Bestehendes Panel erweitern oder generischen Typ nutzen |
| Konfiguration im Arbeitsbereich | Konfiguration → Control Center; Arbeitsbereich nur Kontext-Anzeige |
| Dialog für komplexe Workflows | Eigener Bereich mit Explorer + Editor |
| Versteckte Bereiche (nur über Einstellungen) | Gleichberechtigte Navigation |
| Unbegrenzte Tab-Eröffnung | Tab-Limit; Schließen alter Tabs anbieten |
| Verschiedene Layouts pro Bereich | Einheitliches Zonen-Layout (Sidebar, Main, Inspector, Bottom) |

### 10.4 Skalierungs-Trigger

Wenn eines der folgenden Ereignisse eintritt, ist eine UX-Review erforderlich:

- Neuer Agent-Typ mit abweichendem Workflow
- Neuer Provider (nicht nur Ollama)
- Neues QA-Subsystem (z.B. Performance-Tests)
- Mehr als 20 Agenten in der Registry
- Mehr als 50 Prompts im Prompt Studio
- Mehr als 10 Collections im Knowledge-Bereich

---

## 11. Empfehlungen für skalierbare Desktop-UX

### 11.1 Layout-Stabilität

- **Ein Layout für alle Bereiche:** Sidebar links, Main Mitte, Inspector rechts (optional), Bottom (optional). Keine Bereich-spezifischen Layout-Varianten.
- **Responsive innerhalb des Fensters:** Zonen können ein-/ausgeblendet werden; Proportionen bleiben erhalten.
- **Kein Layout-Modus pro Nutzer:** Ein Standard-Layout; Anpassung nur über ein-/ausblenden von Inspector/Bottom.

### 11.2 Skalierung von Listen und Bäumen

| Element | < 20 Einträge | 20–100 | > 100 |
|---------|---------------|--------|-------|
| Explorer | Einfache Liste | Filter + Suche | Virtualisierung, Pagination, Suche |
| Dropdown | Standard | Suche im Dropdown | Combobox mit Suche, kein reines Dropdown |
| Tabs | Standard | Standard | Tab-Gruppierung, „Weitere“ |

### 11.3 Skalierung bei wachsendem Agenten-Set

- **Agent Registry:** Immer als Explorer mit Suche/Filter; keine Karten-Ansicht bei > 10 Agenten.
- **Agent-Auswahl im Chat/Task:** Combobox mit Suche; Favoriten/Recent optional.
- **Agent Activity:** Nur laufende/relevante Tasks; Archiv getrennt.

### 11.4 Skalierung bei wachsendem QA-Set

- **Test Inventory:** Filter nach Subsystem, Domain, Type; keine ungefilterte Gesamtliste bei > 500 Tests.
- **Coverage Map:** Dashboard mit Aggregation; Drilldown on demand.
- **Gap Analysis:** Priorisierung beibehalten; keine unbegrenzte Gap-Liste.

### 11.5 Performance-Anforderungen (UX-relevant)

- **Wechsel Hauptbereich:** < 300 ms gefühlt
- **Explorer-Befüllung:** < 500 ms für < 100 Einträge
- **Dashboard-Aktualisierung:** < 1 s
- **Bottom Panel (Live-Stream):** Kein Blockieren des Main Thread; Throttling bei hoher Event-Rate

---

## 12. Konsistente UI-Muster im gesamten System

### 12.1 Explorer-Panel-Muster

| Aspekt | Muster | Beispiel |
|--------|--------|----------|
| **Auswahl** | Einzelauswahl; ausgewähltes Element im Editor | Session auswählen → Chat öffnet |
| **Leerer Zustand** | „Keine X. [Aktion] um zu starten.“ + Button | „Keine Sessions. Neuer Chat“ |
| **Laden** | Skeleton oder Spinner; kein leeres Panel | Session-Liste lädt |
| **Fehler** | Inline-Hinweis + Retry-Button | „Laden fehlgeschlagen. Erneut versuchen“ |
| **Kontextmenü** | Rechtsklick: Aktionen zum Objekt | Session: Umbenennen, Löschen, Duplizieren |

### 12.2 Editor-Panel-Muster

| Aspekt | Muster | Beispiel |
|--------|--------|----------|
| **Dirty State** | Ungespeichert: Indikator (Punkt, Stern); Speichern/Verwerfen anbieten | Prompt bearbeitet, nicht gespeichert |
| **Validierung** | Inline bei Feld; Submit blockieren bei Fehler | Pflichtfeld leer → roter Rahmen |
| **Speichern** | Explizit (Button) oder Auto-Save mit Debounce; konsistent pro Bereich | Chat: Auto; Prompt: Explizit |
| **Abbrechen** | „Abbrechen“ oder „Zurück“; bei Dirty: Bestätigung | „Änderungen verwerfen?“ |

### 12.3 Inspector-Panel-Muster

| Aspekt | Muster | Beispiel |
|--------|--------|----------|
| **Kein Kontext** | „Wählen Sie ein Objekt aus.“ | Keine Session ausgewählt |
| **Read-only Standard** | Metadaten primär lesend; Bearbeitung nur wo explizit vorgesehen | Session-Datum, Modell-Name |
| **Gruppierung** | Logische Gruppen (z.B. „Kontext“, „Metadaten“) | RAG-Kontext | angehängte Dateien |
| **Kompaktheit** | Platzsparend; bei Bedarf aufklappbar | „Details aufklappen“ |

### 12.4 Monitor-Panel-Muster

| Aspekt | Muster | Beispiel |
|--------|--------|----------|
| **Live-Indikator** | Visueller Hinweis: Live/Paused | Grüner Punkt „Live“ |
| **Pause/Resume** | Bei hoher Rate: Pause möglich | EventBus: Pause |
| **Filter** | Filter nach Typ, Quelle, Zeitraum | Logs: Level, Subsystem |
| **Export** | Optional: Export (Text, JSON) | Logs exportieren |
| **Leerer Zustand** | „Keine Daten. Warten auf Events.“ | EventBus leer |

### 12.5 Dashboard-Panel-Muster

| Aspekt | Muster | Beispiel |
|--------|--------|----------|
| **Karten** | Einheitliche Karten-Größe; max. 4–6 pro Reihe | Kommandozentrale: 4 Status-Karten |
| **Aktualisierung** | Zeitstempel „Stand: …“; manuell oder Auto-Refresh | QA Status: „Stand: vor 2 Min“ |
| **Drilldown** | Klick auf Karte → Wechsel in anderen Bereich, nicht tiefer im Dashboard | QA Status → QA & Governance |
| **Keine Konfiguration** | Nur Anzeige und Links | Kommandozentrale: keine Einstellungen |

### 12.6 Globale Muster

| Aspekt | Muster |
|--------|--------|
| **Breadcrumb** | Optional in Main Workspace: Bereich > Unterbereich > Objekt |
| **Command Palette** | Strg+K / Cmd+K: Suche, Quick Actions, Bereichswechsel |
| **Tastatur-Navigation** | Tab-Reihenfolge logisch; Esc schließt Modals/Panels |
| **Fehler-Toast** | Kurze Meldung, auto-dismiss; schwere Fehler: Modal mit Details |
| **Loading States** | Einheitlicher Spinner/Skeleton; kein „Nichts passiert“ |

---

## 13. Zusammenfassung

| Aspekt | Festlegung |
|--------|------------|
| **Navigation** | 6 Hauptbereiche, hierarchische Sidebar, max. 2 Ebenen |
| **Panel-Set** | 5 Typen: Explorer, Editor, Inspector, Monitor, Dashboard |
| **Layout** | Top Bar, Sidebar links, Main Workspace, Inspector rechts, Bottom Panel |
| **Kommandozentrale** | Nur Übersicht, keine Konfiguration, keine tiefe Navigation |
| **Operations** | Chat, Agent Tasks, Knowledge, Prompt Studio |
| **Control Center** | Models, Providers, Agents, Tools, Data Stores |
| **QA & Governance** | Eigener Hauptbereich, nicht versteckt |
| **Runtime / Debug** | Eigener Hauptbereich, Bottom Panel für Live-Daten |
| **Agenten** | Drei Ebenen: Control (Operations), Activity (Runtime), Design (Control Center) |
| **Wachstum** | Max. 6 Hauptbereiche, Feature→Bereich-Zuordnung, Progressive Disclosure |

---

## Dokumenten-Status

| Aspekt | Inhalt |
|--------|--------|
| **Typ** | UX-Pflichtenheft / UX-Blaupause |
| **Geltungsbereich** | Gesamte Linux Desktop Chat Anwendung |
| **Bindung** | Verbindlich für UX-/UI-Entscheidungen, Wireframes, Implementierung |
| **Review-Trigger** | Skalierungs-Trigger (Abschnitt 10.4); neue Hauptbereiche; Layout-Änderungen |

*Dieses Dokument ist die verbindliche Referenz für alle künftigen UX-/UI-Entscheidungen, Wireframes und Implementierungen.*
