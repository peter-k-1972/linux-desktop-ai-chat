# Chat UX Hardening – Analyse

**Stand:** 2026-03-17  
**Ziel:** Produktionsreife Interaktion, Klarheit, Statussichtbarkeit im Chatbereich.

---

## 1. Aktueller UX-Stand

### 1.1 ChatConversationPanel

| Aspekt | Status | Details |
|--------|--------|---------|
| Nachrichtenanzeige | ✓ | ChatMessageBubbleWidget, scrollbar |
| User/Assistant-Trennung | ✓ | Visuell über Farbe (blau/weiß) |
| load_messages | ✓ | Akzeptiert (role, content, ts, model?, agent?, completion_status?) |
| Streaming | ✓ | add_assistant_placeholder, update_last_assistant, finalize_streaming |

### 1.2 ChatMessageBubbleWidget

| Aspekt | Status | Details |
|--------|--------|---------|
| Rolle/Label | ✓ | "Du" / "Assistent (model)" / "Agent (name)" |
| Modell-Anzeige | ✓ | Bei model-Parameter |
| Agent-Anzeige | ✓ | Bei agent-Parameter |
| Fallback | ✓ | "Assistent" wenn weder model noch agent |
| Completion-Status | ✓ | possibly_truncated, interrupted, error |
| Text-Selektion | ✓ | TextSelectableByMouse |
| Kontextmenü | ✓ | Copy, Select All (in _MessageContentEdit) |
| Copy-Logik | ✓ | Selektion oder komplette Nachricht |

### 1.3 ChatInputPanel (Eingabefeld)

| Aspekt | Status | Details |
|--------|--------|---------|
| Kontextmenü | ✓ | Cut, Copy, Paste, Select All |
| Cut/Copy/Paste | ✓ | Standard QTextEdit-Aktionen |
| Select All | ✓ | Vorhanden |
| Strg+Enter | ✓ | Senden |
| Status-Label | ✓ | "Wird gesendet…" während Senden |
| Modell-Auswahl | ✓ | ComboBox |

### 1.4 Metadaten im Nachrichtenpfad

| Quelle | model | agent | completion_status |
|--------|-------|-------|-------------------|
| add_assistant_placeholder | ✓ (chat_workspace) | ✗ (nicht übergeben) | – |
| add_assistant_message (load) | ✓ (aus DB) | ✓ (aus DB) | ✓ (aus DB) |
| save_message | ✓ | ✓ (DB unterstützt) | ✓ |
| chat_workspace._run_send | model=model | – | completion_status_str |

**Befund:** Agent wird bei Streaming nicht übergeben (ChatWorkspace hat keine Agent-Auswahl). Bei geladenen Chats kommen model/agent/completion_status aus der DB.

---

## 2. Was bereits sauber ist

- **Copy/Select All** in Nachrichten (ChatMessageBubbleWidget)
- **Cut/Copy/Paste/Select All** im Eingabefeld
- **Modell-/Agent-Label** in der Bubble (wenn übergeben)
- **Completion-Status-Badge** (possibly_truncated, interrupted, error)
- **Text-Selektion** funktioniert
- **Kontextmenü-Styling** einheitlich (dunkelgrau)

---

## 3. Fehlende oder inkonsistente Interaktionen

| Bereich | Problem | Priorität |
|---------|---------|-----------|
| Eingabefeld | Copy nur bei Selektion aktiv – Standard, aber Copy "ohne Selektion" könnte Alles kopieren | Niedrig |
| Nachrichten | "Komplette Nachricht kopieren" nicht explizit im Menü – aktuell: Copy ohne Selektion = alles | Niedrig |
| Status während Streaming | "Wird gesendet…" – könnte präziser "Antwort wird geladen…" sein | Mittel |
| Agent bei Streaming | Agent wird nicht an add_assistant_placeholder übergeben | Niedrig (kein Agent-UI) |

---

## 4. Metadaten – wo sie vorliegen

| Ort | model | agent | completion_status |
|-----|-------|-------|-------------------|
| DB messages | ✓ | ✓ | ✓ |
| load_chat | ✓ | ✓ | ✓ |
| load_messages | ✓ | ✓ | ✓ |
| add_assistant_placeholder | ✓ | – | – |
| set_last_assistant_completion_status | – | – | ✓ |

---

## 5. Completion-/Status-Darstellung

| Status | Label | Sichtbarkeit |
|--------|-------|--------------|
| complete | (kein Badge) | ✓ |
| possibly_truncated | "möglicherweise unvollständig" | ✓ |
| interrupted | "Antwort unterbrochen" | ✓ |
| error | "Generierung beendet mit Fehler" | ✓ |

**Befund:** Einheitlich, unaufdringlich (italic, grau).

---

## 6. Empfohlene Priorisierung

1. **Hoch:** Laufzeit-Hinweis während Streaming präzisieren ("Antwort wird geladen…")
2. **Mittel:** Kontextmenü Nachrichten – "Komplette Nachricht kopieren" explizit hinzufügen (falls Copy ohne Selektion nicht intuitiv)
3. **Niedrig:** Eingabefeld Copy – bei leerer Selektion "Alles kopieren" anbieten (optional)
4. **Dokumentation:** Klarstellen, dass Agent nur bei geladenen Chats aus DB kommt

---

## 7. Unterschiede User / Assistant / Agent

| Rolle | Label | Styling |
|-------|-------|---------|
| user | "Du" | Blau (#dbeafe) |
| assistant (model) | "Assistent (model)" | Weiß |
| assistant (agent) | "Agent (name)" | Weiß |
| assistant (fallback) | "Assistent" | Weiß |

**Konsistenz:** ✓ Gleiche Bubble-Struktur, nur Label und Farbe variieren.
