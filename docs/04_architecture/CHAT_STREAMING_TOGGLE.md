# Chat Streaming Toggle – Architektur

**Stand:** 2026-03-17  
**Geltungsbereich:** Umschaltung zwischen Streaming- und Non-Streaming-Modus für Chat-Antworten.

---

## 1. Zweck

Der Streaming-Toggle ermöglicht dem Benutzer:

- **Streaming EIN (Standard):** Antworten werden während der Generierung inkrementell angezeigt.
- **Streaming AUS:** Die komplette Antwort erscheint erst am Ende.

**Nutzen:**

- **UX:** Bei Darstellungsproblemen (Layout, Scroll, Rendering) kann Streaming deaktiviert werden.
- **Debug:** Vergleich von Verhalten mit/ohne Streaming zur Fehlersuche.
- **Stabilität:** Non-Streaming reduziert die Anzahl der UI-Updates und kann bei schwacher Hardware helfen.

---

## 2. Verhalten ON vs. OFF

| Aspekt | Streaming ON | Streaming OFF |
|--------|--------------|---------------|
| Provider-Aufruf | `stream=True` | `stream=False` |
| Chunks | Viele kleine Chunks | Ein Chunk am Ende |
| UI-Updates | Inkrementell bei jedem Chunk | Einmalig am Ende |
| Message-Komponente | Gleiche (`ChatMessageBubbleWidget`) | Gleiche |
| Speicherung | Nach Abschluss | Nach Abschluss |

---

## 3. Architektur

### 3.1 Schichtverteilung

```
GUI (ChatWorkspace, Legacy ChatWidget)
    → liest settings.chat_streaming_enabled
    → ruft ChatService.chat(stream=...)
         ↓
ChatService
    → leitet stream an OllamaClient weiter
         ↓
OllamaClient (Provider)
    → stream=True:  HTTP-Stream, Chunks einzeln
    → stream=False: HTTP-Response komplett, ein Chunk
```

- **GUI** kennt nur das Setting, nicht Provider-Details.
- **Services** steuern das Verhalten über den `stream`-Parameter.
- **Provider** bleibt austauschbar; beide Modi werden unterstützt.

### 3.2 Setting

- **Key:** `chat_streaming_enabled` (Backend), logisch: `chat.streaming_enabled`
- **Typ:** `bool`
- **Default:** `True`
- **Speicherort:** AppSettings über SettingsBackend (QSettings oder InMemory)

### 3.3 UI-Integration

- **Neue UI:** Einstellungen → AI Models → „Streaming aktiv“
- **Legacy UI:** Chat Side-Panel → Modell-Einstellungen → „Streaming aktiv“

Beide nutzen dieselbe Einstellung. Umschaltung wirkt zur Laufzeit für den nächsten Chat-Lauf.

---

## 4. Debug-Unterstützung

Optionales Logging (bei `logging.DEBUG`):

- `Streaming: ON` / `Streaming: OFF` beim Start des Chat-Laufs
- `Chunks received: X` nach Abschluss

Aktivierung z.B. über:

```python
import logging
logging.getLogger("app.services.chat_service").setLevel(logging.DEBUG)
```

---

## 5. Bekannte Einschränkungen

- **Prompt Test Lab:** Nutzt weiterhin `stream=True` für Tests; der Toggle gilt primär für den Haupt-Chat.
- **Agent-Tasks:** Verwenden intern `stream=True` zum Sammeln der Antwort; kein UI-Streaming.
- **Cloud-Provider:** Verhalten analog zum lokalen Ollama; `stream=False` liefert eine vollständige Response.

---

## 6. Tests

- `tests/test_chat_streaming_toggle.py`: ChatService mit stream=True/False, Settings-Persistenz
- `tests/test_chat_streaming.py`: Legacy-Widget respektiert `chat_streaming_enabled` (ON/OFF)

---

## 7. Änderungshistorie

| Datum | Änderung |
|-------|----------|
| 2026-03-17 | Erste Version: Toggle, Service-Anpassung, UI, Tests, Doku |
