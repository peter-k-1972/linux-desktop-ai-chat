# Linux Desktop Chat – Test-Audit und Gap-Analyse

> **⚠️ VERALTET (historisches Dokument)**  
> **Stand:** 2025-03-15 — beschreibt **nicht** die aktuelle Testbaum-Größe, Shell-GUI oder heutigen pytest-Umfang.  
> **Maßgeblich stattdessen:** `tests/README.md` (Struktur und Marker), `FINAL_TEST_STATUS.md` (Sammlungszahl und Repro am Repo-Commit), `docs/RELEASE_ACCEPTANCE_REPORT.md` (Release).  
> **Kontext:** Als Basis für neue QA-Entscheidungen **nicht** verwenden; höchstens als historische Lesehilfe. Aktualisierung wäre ein separates Improvement (Backlog IMP-002 Folge).

---

**Datum:** 2025-03-15  
**Rolle:** Senior QA-Architekt, Test-Auditor

---

## TEIL 1 – TEST-AUDIT

### 1.1 Übersicht vorhandener Tests

| Kategorie | Dateien | Tests | Abdeckung |
|-----------|---------|-------|-----------|
| Unit | unit/*.py | ~80 | Agent, Prompt, RAG, Router, Tools, Metrics |
| Integration | integration/*.py | ~15 | SQLite, ChromaDB, EventBus |
| Live | live/*.py | ~6 | Ollama, RAG-Pipeline, Agent-Execution |
| UI | ui/*.py | ~20 | Chat, Agent HR, Debug Panel |
| Smoke | smoke/*.py | ~12 | App-Startup, Basic Chat, Agent Workflow |
| Root-Level | tests/*.py | ~50 | Streaming, History, Metrics, Debug, Orchestration |

### 1.2 Komponenten-Analyse

#### Getestet (gut)
- **AgentProfile, AgentService, AgentRegistry, AgentFactory** – CRUD, Validierung, Slug-Lookup
- **PromptService, PromptStorage** – DB/Directory CRUD
- **RAG** – DocumentLoader, Chunker, VectorStore, Retriever (teils gemockt)
- **Chat Streaming** – `test_chat_streaming.py` prüft Content/Thinking/Persist/Retry
- **Chat History Filtering** – Platzhalter werden aus Historie gefiltert
- **EventBus, DebugStore** – emit/subscribe, Event-Historie

#### Nur oberflächlich getestet
- **ChatWidget** – Smoke prüft nur `hasattr(run_chat)`; kein echter UI→Backend→UI-Flow
- **ChatHeaderWidget** – Nur `agent_combo is not None`; keine Agent-Auswahl-Wirkung
- **AgentManagerPanel** – Löschen prüft `isinstance(agents, list)` statt „Agent wirklich weg“
- **PromptManagerPanel** – **Keine UI-Tests vorhanden**
- **Debug Panel** – Nur `refresh()` und `isVisible()`; kein Event-Inhalt sichtbar geprüft

#### Nicht getestet
- **PromptManagerPanel** – Anlegen, Speichern, Laden, Bearbeiten, Löschen im UI
- **RAG-UI** – Aktivieren, Dokument indexieren, Retrieval in Chat
- **Agent-Auswahl im Chat** – System-Prompt landet in Messages
- **Chat Side Panel** – Prompt-Übernahme, Modell-Einstellungen
- **State-Konsistenz** – UI ↔ Service ↔ Repository ↔ Persistenz

### 1.3 Tests prüfen nur Existenz statt Verhalten

| Test | Problem |
|------|---------|
| `test_chat_composer_send_signal` | Prüft `send_requested is not None` (immer True) statt ob Signal ausgelöst wurde |
| `test_agent_manager_delete_button` | Prüft `isinstance(agents, list)` – Liste kann noch den gelöschten Agenten enthalten |
| `test_agent_profile_panel_loads_profile` | Prüft nur `hasattr(panel, "load_profile")` – kein Inhalt geprüft |
| `test_event_timeline_refresh` | Prüft nur `view.isVisible()` – kein Event-Inhalt |
| `test_main_window_creation` | Starke Mocks – fast keine echte Logik |

### 1.4 Mocks vs. echte Integration

| Bereich | Aktuell | Bewertung |
|---------|---------|-----------|
| Chat run_chat | FakeOllamaClient, FakeDB | **Angemessen** – Streaming-Logik isoliert getestet |
| Smoke Basic Chat | Alles gemockt | **Zu stark** – kein echter Flow |
| Agent Workflow | Mock run_fn | **Angemessen** für Smoke |
| RAG Retriever | Mock VectorStore | **Risiko** – echte Similarity-Suche nicht geprüft |
| Ollama | Live-Tests mit echtem Ollama | **Korrekt** – optional, skip wenn nicht da |

### 1.5 UI-Tests prüfen nur Widget-Erzeugung

- `test_conversation_view_add_message` – Nachricht wird hinzugefügt, aber **nicht** ob sie sichtbar/richtig dargestellt wird
- `test_chat_header_opens` – Combos existieren, aber **keine** Agent-/Modell-Befüllung
- `test_agent_manager_new_button_clickable` – Klick erfolgt, aber **kein** neuer Agent in Liste
- `test_debug_panel_clear_button` – Button klickbar, aber **nicht** ob Events gelöscht werden

---

## TEIL 2 – GAP-ANALYSE (priorisiert)

### Schweregrad: KRITISCH

| # | Fehlerart | Beschreibung | Aktuell erkannt? |
|---|-----------|--------------|------------------|
| 1 | Agent-Auswahl ohne Effekt | Agent im Header gewählt, aber System-Prompt nicht in API-Messages | Nein |
| 2 | Prompt speichern → Liste leer | Prompt gespeichert, erscheint nicht in Liste / falscher Inhalt | Nein |
| 3 | Chat-Antwort nicht sichtbar | Antwort kommt, aber UI zeigt Platzhalter/leer | Teilweise (Streaming-Tests) |
| 4 | RAG aktiviert, kein Kontext | RAG an, Dokument indexiert, aber Kontext nicht in Antwort | Nein |

### Schweregrad: HOCH

| # | Fehlerart | Beschreibung | Aktuell erkannt? |
|---|-----------|--------------|------------------|
| 5 | Agent löschen → noch in Liste | Löschen-Button geklickt, Agent bleibt sichtbar | Nein |
| 6 | Prompt laden → falscher Inhalt | Aus Liste geladen, Editor zeigt anderen Prompt | Nein |
| 7 | Debug Panel zeigt falsche Events | Event gesendet, Timeline zeigt anderen/keinen Inhalt | Nein |
| 8 | Toggle/Settings ändern → kein Effekt | RAG an/aus, Modell-Wechsel ohne Wirkung | Nein |

### Schweregrad: MITTEL

| # | Fehlerart | Beschreibung | Aktuell erkannt? |
|---|-----------|--------------|------------------|
| 9 | CRUD logisch unvollständig | Duplikat erstellt, aber nicht nutzbar (z.B. fehlende Referenzen) | Teilweise |
| 10 | Signal/Slot falscher Zielzustand | Speichern-Signal ausgelöst, aber DB nicht aktualisiert | Nein |
| 11 | Gespeicherte Daten in Filtern falsch | Prompt/Agent gefiltert, aber falsche Treffer | Nein |
| 12 | Agent-Profil bearbeiten → Registry veraltet | Profil geändert, Registry liefert alte Werte | Nein |

### Schweregrad: NIEDRIG

| # | Fehlerart | Beschreibung | Aktuell erkannt? |
|---|-----------|--------------|------------------|
| 13 | Button klickbar, aber ohne Effekt | Speichern klickbar, aber keine Aktion | Teilweise |
| 14 | Eingabe landet im falschen Feld | Text in Titel, erscheint in Content | Nein |
| 15 | Sichtbare Texte ≠ interner Zustand | UI zeigt "Agent A", Backend hat "Agent B" | Nein |

---

## TEIL 7 – MOCK VS LIVE STRATEGIE

| Testtyp | Mocking | Begründung |
|---------|---------|------------|
| **unit** | Ja, wo sinnvoll | Isolierte Komponenten, schnelle Ausführung |
| **integration** | Nein (SQLite, ChromaDB, EventBus) | Echte Persistenz/Events prüfen |
| **ui** | Minimale Mocks (DB, Client) | UI-Logik mit echtem Service |
| **smoke** | Reduzieren | Mindestens ein echter Flow pro Hauptpfad |
| **live** | Nein | Ollama, RAG, Agent – echte Dienste |
| **regression** | Nur wo Bug reproduzierbar | Bug-spezifisch |

**Regel:** Mocks dürfen nicht reale Fehler verdecken. Wo UI↔Backend↔Persistenz zusammenspielt, Integration testen.

---

## TEIL 8 – SCHWACHE/IRREFÜHRENDE TESTS

| Test | Problem | Empfehlung |
|------|---------|------------|
| `test_chat_composer_send_signal` | Assertion `send_requested is not None` ist trivial | Prüfen, ob `received` nach Klick gefüllt |
| `test_agent_manager_delete_button` | Prüft nur `isinstance(agents, list)` | Prüfen: `agent_id not in [a.id for a in agents]` |
| `test_agent_profile_panel_loads_profile` | Prüft nur `hasattr` | Prüfen: Editor-Felder enthalten Profil-Daten |
| `test_event_timeline_refresh` | Kein Event-Inhalt | Prüfen: Event-Message in View sichtbar |
| `test_main_window_creation` | Fast alles gemockt | Wenigstens echte DB, reduzierte Mocks |

---

## TEIL 9 – EMPFEHLUNGEN BUG-zu-TEST-WORKFLOW

1. **Jeder gemeldete Bug** → Reproduzierbarer Test in `tests/regression/`
2. **Vor Fix** → Test muss rot sein (reproduziert Bug)
3. **Nach Fix** → Test muss grün sein
4. **Regression-Test** → Sollte möglichst wenig mocken, um ähnliche Bugs zu fangen
5. **Neue Features** → Mindestens ein Golden-Path-Test + relevante Unit-Tests

---

## Nächste Schritte (Implementierung)

- [x] Golden-Path-Tests (Chat, Prompt, Agent, RAG, Debug, Agent-Auswahl)
- [x] Regression-Test-Struktur + erste Tests
- [x] UI-Behavior-Tests erweitern
- [x] State-Consistency-Tests
- [x] Schwache Tests verbessern (test_chat_composer_send_signal, test_agent_manager_delete_button)

---

## Zusammenfassung der Implementierung

### Neu erstellte Tests

| Kategorie | Dateien | Tests |
|-----------|---------|-------|
| Golden Path | 6 Dateien | 6 Tests |
| Regression | 2 Dateien | 3 Tests |
| State Consistency | 3 Dateien | 3 Tests |
| UI Behavior | 1 Datei | 3 Tests |

### Verbesserte Tests

- `test_chat_composer_send_signal`: Prüft jetzt tatsächliche Signal-Emission
- `test_agent_manager_delete_button`: Prüft jetzt, dass gelöschter Agent nicht mehr in Liste ist
