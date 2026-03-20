# Chat Response Completeness – Analyse

**Stand:** 2026-03-17  
**Ziel:** Robuste Erkennung und Behandlung unvollständiger bzw. abgebrochener Chatantworten.

---

## 1. Aktueller Antwortfluss

### 1.1 Architektur-Übersicht

| Komponente | Pfad | Rolle |
|------------|------|-------|
| ChatWorkspace | `app/gui/domains/operations/chat/chat_workspace.py` | Startet `_run_send`, iteriert über Stream, speichert Ergebnis |
| ChatService | `app/services/chat_service.py` | Delegiert an `ollama_client.chat()` |
| OllamaClient | `app/providers/ollama_client.py` | HTTP POST `/api/chat`, streamt JSON-Chunks |
| ChatConversationPanel | `app/gui/domains/operations/chat/panels/conversation_panel.py` | `add_assistant_placeholder`, `update_last_assistant`, `finalize_streaming` |
| ChatMessageBubbleWidget | `app/gui/domains/operations/chat/panels/chat_message_bubble.py` | Zeigt Rolle + Content |
| DatabaseManager | `app/core/db/database_manager.py` | `save_message`, `load_chat` |

### 1.2 Streaming-Pfad (ChatWorkspace._run_send)

```
User sendet → chat_svc.save_message(user) → add_user_message
           → add_assistant_placeholder(model)
           → async for chunk in chat_svc.chat(...):
                 content, _, error = _extract_content(chunk)
                 if error: full_content = "Fehler: {error}"; break
                 if content: full_content += content; update_last_assistant(full_content)
           → save_message(assistant, full_content, model=model)
           → finalize_streaming()
```

**Hinweis:** `_extract_content` liefert nun `(content, thinking, error, done)` – `done` wird für Completion-Status ausgewertet.

### 1.3 Chunk-Format (Ollama)

```json
{
  "message": { "role": "assistant", "content": "...", "thinking": "..." },
  "done": true,
  "error": null
}
```

- `done: true` = Stream regulär beendet
- `error` = Provider-Fehler
- Bei manchen Ollama-Versionen: `done_reason` (z.B. "stop", "length") – optional

### 1.4 Fehler- und Abbruchpfade

| Szenario | Aktuelles Verhalten |
|----------|---------------------|
| Chunk mit `error` | `full_content = "Fehler: {error}"`, break, wird gespeichert |
| `asyncio.CancelledError` | `update_last_assistant("(Abgebrochen)")`, **nicht** gespeichert |
| Andere Exception | `_show_error(err_msg)`, **keine** Assistant-Nachricht gespeichert |
| Stream endet ohne `done` | Keine Unterscheidung – Generator erschöpft sich |
| Timeout (aiohttp) | Exception → keine Nachricht gespeichert |

---

## 2. Bekannte Stellen für Antwortverlust / Abbruch

1. **Provider-Fehler:** Chunk mit `error` → Inhalt wird als "Fehler: …" gespeichert, aber kein Completion-Status.
2. **Exception während Stream:** `except Exception` → keine `save_message`, User sieht evtl. gar nichts oder nur Teilinhalt.
3. **CancelledError:** "(Abgebrochen)" wird angezeigt, aber **nicht** in DB gespeichert.
4. **Stream endet ohne `done=True`:** Z.B. Netzwerkabbruch – aktuell nicht erkennbar.
5. **Modell beendet zu früh:** Kein Signal vom Provider – nur heuristisch erkennbar.
6. **Offener Codeblock / Markdown:** Kein strukturelles Signal – nur heuristisch.

---

## 3. Vorhandene Metadaten

| Quelle | Verfügbar |
|--------|-----------|
| Chunk `done` | Ja, wird aber im ChatWorkspace **nicht** genutzt |
| Chunk `error` | Ja, führt zu "Fehler: …" |
| DB `messages` | `role`, `content`, `timestamp`, `model`, `agent` – **kein** completion_status |
| Exception-Typ | Ja (CancelledError, andere) |

---

## 4. Geeignete Stellen für Heuristik und Status-Markierung

| Stelle | Maßnahme |
|--------|----------|
| Nach Stream-Ende (vor `save_message`) | Completion-Status aus `done`, `error`, Exception ableiten |
| Beim Speichern | `completion_status` in DB persistieren |
| Beim Laden | `completion_status` aus DB lesen, an UI übergeben |
| ChatMessageBubbleWidget | Optionales Badge/Metazeile bei `possibly_truncated` / `interrupted` / `error` |
| Heuristik-Modul | Separates Modul `app/chat/completion_heuristics.py` – prüft Content auf strukturelle Unvollständigkeit |

---

## 5. Empfohlene minimal-invasive Lösung

### 5.1 Completion-Status-Modell

Kleines Enum/Modul mit Werten:
- `complete` – regulär beendet
- `possibly_truncated` – heuristisch oder Provider-Hinweis
- `interrupted` – Abbruch, Exception, CancelledError
- `error` – Provider-Fehler oder Exception mit Fehlermeldung

Zusätzlich optional: `completion_reason` (String) für Debug.

### 5.2 DB-Erweiterung

- Migration: `ALTER TABLE messages ADD COLUMN completion_status TEXT`
- `save_message(..., completion_status=None)` – Default `complete` für User, `complete` wenn nicht gesetzt
- `load_chat` → Tupel um `completion_status` erweitern (Index 6)

### 5.3 Heuristik (konservativ)

- Offener Codeblock (ungerade ```)
- Antwort endet mitten im Wort (kein Wortende-Zeichen)
- Antwort endet nach "1." / "2." ohne Fortsetzung (nur bei ausreichender Länge)
- Keine Überbewertung von Klammern – zu viele False Positives

### 5.4 Integration in ChatWorkspace

- In der Stream-Schleife: `done` und `error` tracken
- Nach Schleife: Status aus `done`, `error`, Exception ableiten
- Heuristik auf `full_content` anwenden, wenn Status noch `complete`
- `save_message(..., completion_status=status)`

### 5.5 UI

- `ChatMessageBubbleWidget` erhält optional `completion_status`
- Kleines Badge unter dem Content: "möglicherweise unvollständig" / "Antwort unterbrochen" / "Generierung beendet mit Fehler"

---

## 6. Nicht in dieser Phase

- Vollautomatische Retry-Orchestrierung
- "Antwort fortsetzen" – nur strukturell vorbereiten (Platzhalter-Callback)
- ComfyUI / Agent-Ausbau
