# Chat Response Completeness – Abschlussreport

**Stand:** 2026-03-17  
**Ziel:** Robuste Erkennung und Behandlung unvollständiger bzw. abgebrochener Chatantworten.

---

## 1. Analysierter Antwortpfad

### 1.1 Flow

```
User → ChatWorkspace._run_send
     → chat_svc.save_message(user)
     → add_assistant_placeholder(model)
     → async for chunk in chat_svc.chat(...):
           content, _, error, done = _extract_content(chunk)
           provider_done |= done
           had_error |= bool(error)
           full_content += content
     → assess_completion_heuristic(full_content, provider_done, had_error, had_exception)
     → save_message(assistant, full_content, completion_status=...)
     → set_last_assistant_completion_status(...)
     → finalize_streaming()
```

### 1.2 Änderungen am Pfad

- `_extract_content` liefert nun `(content, thinking, error, done)` – `done` wird ausgewertet
- `provider_done`, `had_error` werden während des Streams getrackt
- Bei `CancelledError` / `Exception`: Status `interrupted`, Inhalt wird gespeichert
- `assess_completion_heuristic` bewertet Content + Signale
- `completion_status` wird in DB persistiert und an UI übergeben

---

## 2. Gewähltes Statusmodell

**Modul:** `app/chat/completion_status.py`

| Status | Bedeutung |
|--------|-----------|
| `complete` | Regulär beendet |
| `possibly_truncated` | Heuristisch oder Provider-Hinweis auf Trunkierung |
| `interrupted` | Abbruch (CancelledError, Exception, Stream ohne done) |
| `error` | Provider-Fehler |

**DB:** Spalte `completion_status` (TEXT) in `messages`, Migration `_migrate_messages_completion_status`.

**Hilfsfunktionen:** `completion_status_to_db`, `completion_status_from_db`, `is_incomplete`, `status_display_label`.

---

## 3. Implementierte Heuristiken

**Modul:** `app/chat/completion_heuristics.py`

| Signal | Bedingung | Konservativ |
|--------|-----------|-------------|
| Offener Codeblock | Ungerade Anzahl ``` | Ja – nur bei vorhandenem ``` |
| Mitten im Wort | Letztes Zeichen kein Leerzeichen/Satzzeichen, Länge ≥ 50 | Ja – Mindestlänge |
| Nummerierte Liste abgebrochen | Endet mit "1." / "2." etc., Länge ≥ 80 | Ja |
| Überschrift ohne Inhalt | Endet mit Markdown-Überschrift (#...), Länge ≥ 10 | Ja |

**Priorität:** Provider-Signale (error, exception, !done) gehen vor Heuristik.

**Debug:** `get_heuristic_flags(content)` liefert rohe Flags für Tracing.

---

## 4. UI-Markierung

**ChatMessageBubbleWidget:**

- Neues `_status_badge` (QLabel) unter dem Content
- `set_completion_status(status)` aktualisiert Badge
- Labels: "möglicherweise unvollständig", "Antwort unterbrochen", "Generierung beendet mit Fehler"
- Styling: klein, grau, kursiv, unaufdringlich

**ConversationPanel:**

- `load_messages` liest `completion_status` aus Zeile (Index 5)
- `set_last_assistant_completion_status` setzt Badge nach Streaming-Ende

---

## 5. Tests

| Testdatei | Inhalt |
|-----------|--------|
| `tests/unit/test_completion_heuristics.py` | Status-Modell, Heuristik (complete, truncated, error, interrupted, Codeblock, Wortende) |
| `tests/unit/test_completion_status_integration.py` | _extract_content, DB save/load |
| `tests/ui/test_chat_hardening.py` | `test_conversation_panel_completion_status_badge` |

**Ergebnis:** Alle relevanten Tests bestanden.

---

## 6. Bekannte Grenzen / Blind Spots

1. **Provider-spezifisch:** `done_reason` (z.B. "length" bei Ollama) wird aktuell nicht ausgewertet – nur `done` als bool.
2. **Klammern/Quotes:** Nicht in Heuristik – zu viele False Positives.
3. **Legacy ChatWidget:** Nutzt eigenen Flow, keine Completion-Status-Integration.
4. **Agent-/Tool-Antworten:** Kein spezieller Pfad – würden über gleichen Flow laufen, wenn sie ChatWorkspace nutzen.
5. **Kurze Antworten:** Unter 50 Zeichen (außer Codeblock) keine Heuristik – "Ja" oder "OK" werden nie markiert.

---

## 7. Empfohlene nächste Ausbaustufen

1. **Provider done_reason:** Falls Ollama/Cloud `done_reason: "length"` liefert, als `possibly_truncated` werten.
2. **Recovery-Actions:** "Antwort fortsetzen" / "Erneut generieren" – Struktur vorbereitet (Kommentar in completion_status.py).
3. **Legacy-Integration:** ChatWidget auf Completion-Status erweitern, falls Legacy-Pfad weiter genutzt wird.
4. **Debug-Panel:** Optional `completion_status` + `get_heuristic_flags` im Runtime-Debug anzeigen.
