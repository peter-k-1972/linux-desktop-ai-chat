# Workspace-Implementierungsplan

**Version:** 1.0  
**Datum:** 2026-03-15  
**Status:** Verbindlich  
**Basis:** Analyse des aktuellen GUI-Zustands

---

## 1. Gesamtüberblick aller Workspaces

| Bereich | Workspace | Reifegrad | Kern/Folge | Blockiert Nutzbarkeit |
|---------|-----------|-----------|------------|------------------------|
| **Operations** | Chat | Teilweise | **Kern** | **Ja** |
| **Operations** | Agent Tasks | Platzhalter | Folge | Nein |
| **Operations** | Knowledge / RAG | Platzhalter | **Kern** | **Ja** |
| **Operations** | Prompt Studio | Platzhalter | Folge | Nein |
| **Control Center** | Models | Platzhalter | **Kern** | **Ja** |
| **Control Center** | Providers | Platzhalter | **Kern** | **Ja** |
| **Control Center** | Agents | Platzhalter | Folge | Nein |
| **Control Center** | Tools | Platzhalter | Folge | Nein |
| **Control Center** | Data Stores | Platzhalter | Folge | Nein |
| **QA & Governance** | Test Inventory | Platzhalter | Folge | Nein |
| **QA & Governance** | Coverage Map | Platzhalter | Folge | Nein |
| **QA & Governance** | Gap Analysis | Platzhalter | Folge | Nein |
| **QA & Governance** | Incidents | Platzhalter | Folge | Nein |
| **QA & Governance** | Replay Lab | Platzhalter | Folge | Nein |
| **Runtime / Debug** | EventBus | Platzhalter | Folge | Nein |
| **Runtime / Debug** | Logs | Platzhalter | Folge | **Teilweise** |
| **Runtime / Debug** | Metrics | Platzhalter | Folge | Nein |
| **Runtime / Debug** | LLM Calls | Platzhalter | Folge | **Teilweise** |
| **Runtime / Debug** | Agent Activity | Platzhalter | Folge | Nein |
| **Runtime / Debug** | System Graph | Platzhalter | Folge | Nein |
| **Settings** | Appearance | **Funktionsfähig** | Folge | Nein |
| **Settings** | System | Platzhalter | Folge | Nein |
| **Settings** | Models | Platzhalter | Folge | Nein |
| **Settings** | Agents | Platzhalter | Folge | Nein |
| **Settings** | Advanced | Platzhalter | Folge | Nein |
| **Kommandozentrale** | Dashboard | Teilweise | **Kern** | Nein |

---

## 2. Priorisierungsmatrix

| Priorität | Workspace | Begründung |
|-----------|-----------|------------|
| **P1** | Chat | Macht die App als erstes wirklich benutzbar. Ohne funktionierenden Chat ist die neue GUI nicht ablösungsfähig. |
| **P2** | Models | Chat braucht Modellauswahl. Ohne echte Modellliste blockiert der Chat. |
| **P3** | Providers | Models brauchen Provider-Kontext. Ollama-Status muss sichtbar sein. |
| **P4** | Knowledge / RAG | Kern-Use-Case für Wissensarbeit. RAGService existiert bereits. |
| **P5** | Logs | Wichtig für Debugging bei Chat-Integration. |
| **P6** | LLM Calls | Transparenz bei Chat-Nutzung. |
| **P7** | Agent Tasks | Folgefunktion, aber wichtig für Agenten-Workflow. |
| **P8** | Agent Activity | Ergänzt Agent Tasks. |
| **P9** | Appearance (Settings) | Bereits funktionsfähig. |
| **P10** | System (Settings) | Minimal: Ollama-Status, App-Info. |
| **P11** | Prompt Studio | Folgefunktion. |
| **P12** | Agents (CC) | Folgefunktion. |
| **P13** | Tools, Data Stores | Folgefunktion. |
| **P14** | QA & Governance (alle) | Tiefenausbau, später. |
| **P15** | Runtime: EventBus, Metrics, System Graph | Nice-to-have. |

---

## 3. Empfohlene Abarbeitungsreihenfolge

```
Phase 1: App nutzbar machen (Chat + Grundlagen)
├── 1.1 Chat Workspace (Backend-Anbindung)
├── 1.2 Models Workspace (Ollama-Anbindung)
├── 1.3 Providers Workspace (Ollama-Status)
└── 1.4 App-Bootstrap: Async + Backend in neue Shell integrieren

Phase 2: Kernfunktionen vertiefen
├── 2.1 Knowledge / RAG Workspace
├── 2.2 Logs Workspace (echte Logs)
└── 2.3 LLM Calls Workspace

Phase 3: Agenten und Steuerung
├── 3.1 Agent Tasks Workspace
├── 3.2 Agent Activity (Runtime)
├── 3.3 Control Center: Agents
└── 3.4 Settings: System, Models

Phase 4: Tiefenausbau
├── 4.1 Prompt Studio
├── 4.2 Tools, Data Stores
├── 4.3 QA & Governance (Test Inventory, Coverage, etc.)
└── 4.4 Runtime: EventBus, Metrics, System Graph
```

---

## 4. Detaillierte Workspace-Spezifikationen

### 4.1 Chat Workspace (P1)

**Zweck:** Primärer Arbeitsraum für Konversation mit dem LLM. Kern-Use-Case der App.

**Aktueller Reifegrad:** Teilweise umgesetzt.
- GUI-Struktur vorhanden: Session Explorer, Conversation Panel, Input Panel
- Session Explorer: Dummy-Sessions (hardcoded)
- Conversation: Dummy-Nachrichten + add_user_message/add_assistant_message
- Input: funktioniert, sendet Signal
- **Keine Backend-Anbindung:** Antwort immer "(Antwort wird bei Backend-Integration geladen.)"

**Warum wichtig:** Ohne funktionierenden Chat ist die neue GUI nicht ablösungsfähig. Die alte GUI (ChatWidget) hat vollständige Ollama-Integration.

**MVP (minimale nutzbare Version):**
- Session Explorer: echte Sessions aus DatabaseManager (create_chat, list_chats, load_history)
- Conversation: echte Nachrichten, Streaming-Anzeige
- Input: Senden → OllamaClient.chat() → Streaming-Response anzeigen
- Modell-Auswahl: Dropdown mit Modellen aus OllamaClient.get_models()

**Notwendige GUI-Bausteine:**
- ChatSessionExplorerPanel: Anbindung an DatabaseManager
- ChatConversationPanel: Streaming-Widget, Markdown-Rendering
- ChatInputPanel: Modell-Dropdown, Temperature/MaxTokens (optional)
- ChatContextInspector: Session-ID, Modell, RAG-Status

**Notwendige Backend-Anbindungen:**
- OllamaClient (async)
- ModelOrchestrator (für Routing)
- DatabaseManager (Chats, Messages)
- qasync / QEventLoop (async in Qt)

**Risiken:**
- Async-Integration in synchrone Shell: run_gui_shell.py nutzt kein asyncio. Entweder qasync in Shell integrieren oder Chat-Workspace mit eigenem Event-Loop.
- ChatWidget (Legacy) ist ~800 Zeilen – nicht 1:1 übernehmen, aber Logik extrahieren.

**Empfohlene Reihenfolge:** Erster Workspace. Blockiert alles Weitere.

---

### 4.2 Models Workspace (P2)

**Zweck:** Übersicht installierter Modelle, Status, Auswahl für Chat.

**Aktueller Reifegrad:** Platzhalter.
- ModelListPanel: Dummy-Daten (llama3.2, mistral, etc.)
- ModelSummaryPanel, ModelStatusPanel: statisch
- ModelActionPanel: Buttons ohne Aktion

**Warum wichtig:** Chat braucht Modellauswahl. Ohne echte Modellliste ist der Chat unvollständig.

**MVP:**
- ModelListPanel: Daten aus OllamaClient.get_models()
- Tabellen-Spalten: name, size, modified, digest (gekürzt)
- Auswahl → Inspector zeigt Details
- Optional: "Load" / "Unload" (Ollama API)

**Notwendige GUI-Bausteine:**
- ModelListPanel: refresh()-Methode, async load
- ModelInspector: dynamische Daten
- Auswahl-Signal für Chat-Workspace (Modell-Wechsel)

**Notwendige Backend-Anbindungen:**
- OllamaClient.get_models()

**Risiken:** Gering. API ist einfach.

**Empfohlene Reihenfolge:** Direkt nach Chat-Bootstrap, parallel zu Chat möglich.

---

### 4.3 Providers Workspace (P3)

**Zweck:** Provider-Übersicht, Ollama-Status, Endpoint-Konfiguration.

**Aktueller Reifegrad:** Platzhalter.
- ProviderListPanel: Dummy (Ollama, OpenAI planned, etc.)
- ProviderStatusPanel: statisch

**Warum wichtig:** Nutzer muss sehen, ob Ollama erreichbar ist. Fehlermeldungen bei Offline-Zustand.

**MVP:**
- ProviderListPanel: LocalOllamaProvider, CloudOllamaProvider (falls konfiguriert)
- ProviderStatusPanel: OllamaClient.get_debug_info() → online, version, model_count
- Endpoint anzeigen (aus Settings)

**Notwendige GUI-Bausteine:**
- ProviderListPanel: refresh(), async
- ProviderInspector: Endpoint, Health, Models Count

**Notwendige Backend-Anbindungen:**
- OllamaClient.get_debug_info()
- ModelOrchestrator (Provider-Liste)
- AppSettings (Ollama-URL)

**Risiken:** Gering.

**Empfohlene Reihenfolge:** Mit Models zusammen oder direkt danach.

---

### 4.4 Knowledge / RAG Workspace (P4)

**Zweck:** Wissensräume verwalten, Dokumente indizieren, RAG für Chat aktivieren.

**Aktueller Reifegrad:** Platzhalter.
- KnowledgeBasesPanel, IndexOverviewPanel, RetrievalStatusPanel: Struktur vorhanden
- Detailbereich: "Detailbereich – Source-Infos, Collection-Details"
- Keine RAGService-Anbindung

**Warum wichtig:** Kern-Use-Case für Wissensarbeit. RAGService, KnowledgeSpaceManager, ChromaDB existieren bereits.

**MVP:**
- KnowledgeBasesPanel: Liste aus KnowledgeSpaceManager (DEFAULT_SPACES + benutzerdefinierte)
- IndexOverviewPanel: Dokumentenanzahl pro Space, Chunk-Count
- "Dokument hinzufügen": Datei/Ordner auswählen → load_documents_from_directory → Chunker → VectorStore
- RetrievalStatusPanel: RAG aktiv/inaktiv, aktueller Space
- Toggle für Chat: RAG für aktuelle Session aktivieren

**Notwendige GUI-Bausteine:**
- KnowledgeBasesPanel: Tree/Liste, Add-Button, Refresh
- Document-Import-Dialog
- IndexOverviewPanel: Metriken aus VectorStore
- KnowledgeInspector: Collection-Details, Embedding-Info

**Notwendige Backend-Anbindungen:**
- RAGService
- KnowledgeSpaceManager
- load_document, load_documents_from_directory
- EmbeddingService (synchron oder async)

**Risiken:**
- Embedding kann langsam sein (blockierend)
- ChromaDB-Pfad: QStandardPaths.AppDataLocation

**Empfohlene Reihenfolge:** Nach Chat + Models. Chat muss RAG-Toggle haben.

---

### 4.5 Logs Workspace (P5)

**Zweck:** Anwendungslogs in Echtzeit anzeigen.

**Aktueller Reifegrad:** Platzhalter.
- LogStreamPanel: Dummy-Daten (5 Zeilen)
- Filter: Level, Module – UI vorhanden, keine Logik

**Warum wichtig:** Debugging bei Chat-Integration. Nutzer sieht Fehler.

**MVP:**
- LogStreamPanel: Python logging Handler → Queue → GUI-Update
- Echte Log-Zeilen: timestamp, level, module, message
- Filter: Level (DEBUG/INFO/WARN/ERROR), Module (optional)
- Auto-Scroll, Pause

**Notwendige GUI-Bausteine:**
- LogStreamPanel: QTableWidget oder QPlainTextEdit mit Append
- LogHandler (logging.Handler) → Signal
- Filter-ComboBoxes mit Wirkung

**Notwendige Backend-Anbindungen:**
- Python logging
- Eigenes Handler, der an GUI signalisiert

**Risiken:** Gering. Standard-Pattern.

**Empfohlene Reihenfolge:** Parallel zu Chat oder kurz danach.

---

### 4.6 LLM Calls Workspace (P6)

**Zweck:** Transparenz über LLM-Aufrufe (Modell, Token, Latenz).

**Aktueller Reifegrad:** Platzhalter.
- LLMCallHistoryPanel: Dummy-Daten

**Warum wichtig:** Nutzer sieht, was passiert. Wichtig für Debugging und Kostenbewusstsein.

**MVP:**
- Liste der letzten N LLM-Calls
- Spalten: Timestamp, Model, Prompt-Tokens, Completion-Tokens, Latenz
- Datenquelle: Metrics/Collector oder eigenes Tracking im Chat-Flow

**Notwendige GUI-Bausteine:**
- LLMCallHistoryPanel: Tabelle mit refresh
- LLMCallInspector: Detail pro Call

**Notwendige Backend-Anbindungen:**
- get_metrics_collector() oder eigenes LLM-Call-Logging
- Integration in Chat-Workspace: nach jedem Chat-Lauf Event emittieren

**Risiken:** Metrics-Collector muss LLM-Calls tracken. Prüfen ob vorhanden.

**Empfohlene Reihenfolge:** Nach Logs. Hängt von Chat-Integration ab.

---

### 4.7 Agent Tasks Workspace (P7)

**Zweck:** Agenten beauftragen, Task-Queue, Ergebnis anzeigen.

**Aktueller Reifegrad:** Platzhalter.
- AgentTasksOverviewPanel, AgentQueuePanel, AgentStatusPanel: Struktur
- Detailfläche: "Task-Details, Tool-Ausführung, Ergebnis"

**Warum wichtig:** Folgefunktion. ResearchAgent, OrchestrationService existieren.

**MVP:**
- Task-Liste: Offene Tasks, Abgeschlossene
- "Neuer Task": Eingabe, Agent-Auswahl (Research, etc.), Start
- Ergebnis-Anzeige nach Abschluss
- AgentTasksInspector: Task-Details, Status

**Notwendige GUI-Bausteine:**
- Task-Explorer (Liste)
- Task-Editor (Eingabe, Parameter)
- Agent-Auswahl-Dropdown

**Notwendige Backend-Anbindungen:**
- OrchestrationService
- ResearchAgent
- EventBus (optional) für Status-Updates

**Risiken:** Agenten-Logik ist komplex. Evtl. erst vereinfachter "Research Task" ohne volle Orchestrierung.

**Empfohlene Reihenfolge:** Phase 3. Nach Chat + RAG.

---

### 4.8 Agent Activity Workspace (P8)

**Zweck:** Laufende Agenten, Schritte, Status in Echtzeit.

**Aktueller Reifegrad:** Platzhalter.
- AgentActivityPanel: Struktur
- RuntimeAgentInspector: vorhanden

**Warum wichtig:** Ergänzt Agent Tasks. Transparenz.

**MVP:**
- Liste aktiver Agenten/Tasks
- Schritte pro Task
- Daten: EventBus oder OrchestrationService

**Notwendige Backend-Anbindungen:**
- EventBus, emit_event
- OrchestrationService (laufende Tasks)

**Empfohlene Reihenfolge:** Mit Agent Tasks zusammen.

---

### 4.9 Appearance Workspace (Settings) – Bereits funktionsfähig

**Zweck:** Theme-Auswahl.

**Aktueller Reifegrad:** Funktionsfähig.
- ThemeSelectionPanel: ThemeManager, set_theme
- AppearanceInspector: Theme-Details

**Keine Änderung nötig.**

---

### 4.10 System Workspace (Settings) (P10)

**Zweck:** App-Info, Runtime-Status, Ollama-Status.

**Aktueller Reifegrad:** Platzhalter.
- Statische Texte: "Bereit · Keine Backend-Verbindung"

**MVP:**
- Ollama-Status: Online/Offline, Version, Model Count (aus get_debug_info)
- App-Version
- Refresh-Button

**Empfohlene Reihenfolge:** Phase 3. Geringer Aufwand.

---

### 4.11 Kommandozentrale (Dashboard)

**Aktueller Reifegrad:** Teilweise.
- SystemStatusPanel, ActiveWorkPanel, QAStatusPanel, IncidentsPanel: Struktur
- Vermutlich Dummy-Daten

**MVP:**
- SystemStatusPanel: Ollama-Status, Modellanzahl
- ActiveWorkPanel: Letzte Chat-Sessions (Links)
- QAStatusPanel: Platzhalter oder Link zu QA
- IncidentsPanel: Platzhalter
- Quick Actions: "Chat öffnen", "Agent beauftragen" → Navigation

**Empfohlene Reihenfolge:** Nach Chat. Quick Actions verdrahten.

---

### 4.12 Übrige Workspaces (P11–P15)

| Workspace | MVP-Kurzbeschreibung | Priorität |
|-----------|----------------------|-----------|
| Prompt Studio | Prompt-Liste, Editor, Vorschau. Backend: prompt_backend, ModelRegistry | P11 |
| Agents (CC) | Agent-Registry aus ModelRegistry, Profil-Liste | P12 |
| Tools | Tool-Liste (FileSystemTools, etc.), Konfiguration | P13 |
| Data Stores | Platzhalter oder ChromaDB-Übersicht | P13 |
| Settings: Models, Agents, Advanced | Einstellungen aus AppSettings | P13 |
| QA: Test Inventory, Coverage, Gap, Incidents, Replay | Dummy → echte Daten, wenn QA-Backend existiert | P14 |
| Runtime: EventBus, Metrics, System Graph | EventBus-Subscription, Metrics-Dashboard | P15 |

---

## 5. Backend-Schnittstellen – Verdrahtungsreihenfolge

| Reihenfolge | Schnittstelle | Verwendet in |
|-------------|---------------|--------------|
| 1 | OllamaClient (async) | Chat, Models, Providers, Dashboard |
| 2 | DatabaseManager | Chat (Sessions, Messages) |
| 3 | ModelOrchestrator | Chat, Models, Providers |
| 4 | AppSettings | Chat, Settings, alle |
| 5 | qasync / QEventLoop | App-Bootstrap (main.py oder run_gui_shell) |
| 6 | RAGService | Knowledge, Chat (RAG-Toggle) |
| 7 | logging.Handler → GUI | Logs |
| 8 | Metrics/LLM-Call-Logging | LLM Calls |
| 9 | OrchestrationService, ResearchAgent | Agent Tasks, Agent Activity |
| 10 | EventBus | Agent Activity, EventBus Monitor |

---

## 6. Kritische Ablösungsfragen – Beantwortung

| Frage | Antwort |
|-------|---------|
| **Welcher Workspace macht die App als erstes wirklich benutzbar?** | Chat Workspace mit Ollama-Anbindung. |
| **Welche Workspaces sind noch überwiegend Platzhalter?** | Fast alle außer Appearance. Chat hat Struktur, aber kein Backend. |
| **Welche Platzhalter müssen kurzfristig ersetzt werden?** | Chat, Models, Providers. Ohne diese ist die neue GUI nicht ablösungsfähig. |
| **Welche Workspaces können vorerst mit guter Struktur, aber wenig Funktion leben?** | QA & Governance (alle), Prompt Studio, Tools, Data Stores, EventBus, Metrics, System Graph. |
| **Welche Backend-Schnittstellen müssen zuerst verdrahtet werden?** | OllamaClient, DatabaseManager, ModelOrchestrator, qasync. |
| **Welche Reihenfolge minimiert Reibungsverluste?** | 1) App-Bootstrap mit async, 2) Chat, 3) Models, 4) Providers, 5) Knowledge, 6) Logs, 7) LLM Calls. |
| **Welche Workspaces sind für die Ablösung der alten GUI kritisch?** | Chat, Models, Providers, Knowledge (RAG), Settings/Appearance (bereits OK). |
| **Was ist "nice to have" und was ist zwingend?** | Zwingend: Chat, Models, Providers. Nice-to-have: Agent Tasks, QA, Runtime-Details, Prompt Studio. |

---

## 7. Implementierungs-Roadmap (Phasen)

### Phase 1: App nutzbar machen (2–3 Sprints)

1. **App-Bootstrap anpassen**
   - run_gui_shell.py oder main.py: qasync integrieren
   - OllamaClient, ModelOrchestrator, DatabaseManager, AppSettings beim Start initialisieren
   - Singleton oder Context-Objekt für Backend-Zugriff

2. **Chat Workspace**
   - ChatSessionExplorerPanel: DatabaseManager
   - ChatConversationPanel: Streaming, Markdown
   - ChatInputPanel: Modell-Dropdown
   - ChatWorkspace: OllamaClient.chat(), ModelOrchestrator

3. **Models Workspace**
   - ModelListPanel: OllamaClient.get_models()
   - ModelInspector: dynamisch

4. **Providers Workspace**
   - ProviderListPanel, ProviderStatusPanel: get_debug_info()

### Phase 2: Kernfunktionen (1–2 Sprints)

5. **Knowledge / RAG Workspace**
   - RAGService-Anbindung
   - Document-Import
   - RAG-Toggle im Chat

6. **Logs Workspace**
   - LogHandler → GUI

7. **LLM Calls Workspace**
   - Call-Logging, Anzeige

### Phase 3: Agenten und Steuerung (1–2 Sprints)

8. **Agent Tasks Workspace**
9. **Agent Activity**
10. **Control Center: Agents**
11. **Settings: System**
12. **Dashboard: Quick Actions, Status**

### Phase 4: Tiefenausbau (backlog)

13. Prompt Studio, Tools, Data Stores
14. QA & Governance
15. Runtime: EventBus, Metrics, System Graph

---

## 8. Nächste konkrete Schritte

1. **Entscheidung:** Soll main.py (neue GUI) mit qasync + Backend starten, oder bleibt run_gui_shell backend-frei?
2. **Chat-Workspace:** ChatWidget-Logik aus app/chat_widget.py extrahieren → ChatWorkspace + Panels.
3. **Models-Workspace:** ModelListPanel mit refresh() und OllamaClient.get_models().
4. **Providers-Workspace:** ProviderStatusPanel mit get_debug_info().

---

*Dieser Plan ist verbindlich für die Workspace-Implementierung. Keine Architektur-Änderungen. Fokus: Platzhalter durch echte Funktionalität ersetzen.*
