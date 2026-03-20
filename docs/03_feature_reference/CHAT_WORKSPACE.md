# Chat-Workspace – Implementierung

**Status:** Produktiv nutzbar  
**Datum:** 2026-03-15

## Startanweisung

```bash
python main.py
# oder
.venv/bin/python main.py
```

Voraussetzung: Ollama muss laufen (`ollama serve`).

## Architektur

### Klassen

| Klasse | Zweck |
|--------|-------|
| **ChatBackend** | Service-Schicht: OllamaClient, DatabaseManager, AppSettings. Singleton. |
| **ChatWorkspace** | Orchestriert Session Explorer, Conversation, Input. Async Send-Logik. |
| **ChatSessionExplorerPanel** | Liste der Chats aus DB, "Neuer Chat"-Button. |
| **ChatConversationPanel** | Nachrichtenverlauf, Streaming-Updates. |
| **ChatInputPanel** | Modell-ComboBox, Texteingabe, Senden. |
| **ChatContextInspector** | Session-ID, Modell, Status, Nachrichtenanzahl. |

### Datenfluss

```
Session Explorer (chat_id) ──► ChatWorkspace._on_session_selected
                                    │
                                    ▼
                              load_messages(chat_id)
                                    │
                                    ▼
                              ConversationPanel.load_messages()

InputPanel.send_requested(text) ──► ChatWorkspace._on_send_requested
                                    │
                                    ▼
                              asyncio.create_task(_run_send)
                                    │
                                    ▼
                              Backend.chat() ──► Stream ──► ConversationPanel.update_last_assistant()
```

### Signalfluss

- `session_selected(int)` – Chat gewechselt
- `send_requested(str)` – Nachricht senden
- Backend: sync (DB) und async (Ollama)

### Backend-Initialisierung

In `run_gui_shell.main()`:
1. qasync QEventLoop
2. `ChatBackend()` + `set_chat_backend()`
3. ShellMainWindow

## Fehlerbehandlung

- Kein Modell: "Bitte ein Modell auswählen."
- Ollama offline: "Ollama nicht erreichbar" im Status
- API-Fehler: "Fehler: …" im Verlauf
- Leere Eingabe: ignoriert

## Persistenz

- SQLite: `chat_history.db`
- Chats: `create_chat`, `list_chats`, `save_message`, `load_chat`
