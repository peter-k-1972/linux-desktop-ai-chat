# Chat

## Verwandte Themen

- [Kontext / Chat-Kontext](../context/README.md) · [Settings](../settings/README.md) · [Provider / Modelle](../providers/README.md)  
- [Agenten](../agents/README.md) · [Prompts](../prompts/README.md) · [GUI](../gui/README.md)  
- [Workflow: Chat verwenden](../../workflows/chat_usage.md) · [Feature: Chat](../../../docs/FEATURES/chat.md)

## 1. Fachsicht

Das **Chat-Modul** umfasst die geführte Konversation mit einem Sprachmodell über Ollama: Sitzungen (Chats), Nachrichtenverlauf, Eingabe, optionales Streaming und Slash-Commands zur Rollen- und Routing-Steuerung. Es verbindet die Oberfläche mit `ChatService`, Kontextinjektion (siehe Modul **context**), Modell-/Provider-Pfad und optional RAG-Anreicherung über den Knowledge-Pfad.

**Nutzen:** zentraler Arbeitsbereich für alle textbasierten Modellanfragen innerhalb eines Projekts oder global.

In einem Satz: Alles, was der Nutzer tippt, passiert **nach** der Session-Auswahl und **vor** der Provider-Antwort in einer klar definierten Pipeline (Slash-Parsing → Nachrichtenliste → Kontext/Gewährleistung → Modell). Wer die Fehleranalyse betreibt, sollte diese Reihenfolge im Kopf behalten — häufige Symptome (kein Kontext, falsche Rolle) hängen an frühen Schritten, nicht am Ollama-Endpunkt.

## 2. Rollenmatrix

| Rolle | Nutzung |
|-------|---------|
| **Fachanwender** | Chat-Workspace unter Operations; Sessions, senden, Slash-Commands. |
| **Admin** | Erreichbarkeit Ollama/Modelle, ggf. Cloud-Keys (über Settings/Control Center, nicht im Chat-Modul selbst). |
| **Entwickler** | `app/services/chat_service.py`, `app/gui/domains/operations/chat/`, `app/core/commands/chat_commands.py`, Chat Guard (`app/core/chat_guard/`). |
| **Business** | Nutzung als Produktfunktion „Chat mit KI“; keine zusätzliche technische Oberfläche. |

## 3. Prozesssicht

```
┌─────────────────────────────────────────────────────────────┐
│ GUI: ChatWorkspace → Senden (Text)                           │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ parse_slash_command (app/core/commands/chat_commands.py)     │
│ → Rolle, /auto, /cloud, /delegate (use_delegation)           │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ ChatService: Message-Liste, Kontextauflösung & Injektion    │
│ (Mode off → kein Kontextfragment)                            │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Chat Guard (optional): assess_async → apply_to_messages      │
│ (app/services/chat_service.py → _apply_chat_guard)            │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Modell-Routing / Orchestrator → Provider (Ollama)            │
│ Streaming gesteuert über AppSettings.chat_streaming_enabled    │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Antwort-Stream oder komplette Antwort → GUI Conversation      │
└─────────────────────────────────────────────────────────────┘
```

**Workspace-IDs (Operations):** `operations_chat` in `app/gui/domains/operations/operations_screen.py` (Eintrag `ChatWorkspace`).

## 4. Interaktionssicht

**UI**

- `app/gui/domains/operations/chat/chat_workspace.py` – Orchestrierung Session-Explorer, Konversation, Eingabe.
- `app/gui/domains/operations/chat/panels/chat_context_bar.py` – Anzeige Projekt / Chat / Topic; Klicks und Kontextmenü (Navigation, keine Kontext-Modus-Logik).
- `app/gui/chat_backend.py` – Zugriff der GUI auf Backend-Funktionen (Modelle, Senden, Status).

**Services / Commands**

- `app/services/chat_service.py` – Sendepfad, Kontext, Guard, Streaming.
- `app/core/commands/chat_commands.py` – `ROLE_COMMANDS`, `parse_slash_command`, `SLASH_COMMANDS`.

**Relevante Settings-Keys (Auszug)**

- `chat_streaming_enabled` – Streaming ein/aus (`AppSettings` in `app/core/config/settings.py`).

## 5. Fehler- / Eskalationssicht

| Problem | technische Ursache (Code) |
|---------|---------------------------|
| Keine Antwort / hängt | Ollama nicht erreichbar; Provider-Timeout (siehe Provider-Modul). |
| Doppeltes Senden / Konflikt bei Stream | Chat Guard und Sendelogik in `ChatService`; parallele Sends. |
| Slash-Command wirkt nicht | Zeile beginnt nicht mit `/` oder unbekannter Befehl → Rückgabe mit Fehlermeldung in `SlashCommandResult.message`. |
| `/delegate` ohne Text | `parse_slash_command`: `consumed=True`, nur Verwendungshinweis, kein Delegationslauf. |
| Kontext fehlt | `ChatContextMode.OFF` oder höherpriore Kontext-Override-Kette (siehe Modul **context**). |
| Unerwartete Prompt-Härtung | Chat Guard bewertet letzte User-Nachricht und modifiziert Messages (`_apply_chat_guard`). |

## 6. Wissenssicht

| Begriff | Quelle |
|---------|--------|
| `ChatWorkspace` | `app/gui/domains/operations/chat/chat_workspace.py` |
| `ChatService` | `app/services/chat_service.py` |
| `SlashCommandResult`, `use_delegation` | `app/core/commands/chat_commands.py` |
| `chat_streaming_enabled` | `app/core/config/settings.py` |
| `operations_chat` | Workspace-ID in `operations_screen.py` |

## 7. Perspektivwechsel

| Perspektive | Fokus |
|-------------|--------|
| **User** | Operations → Chat; Slash-Commands; Modellwahl in der Chat-Oberfläche. |
| **Admin** | Ollama-Dienst, Modelle, Netz; keine Chat-spezifische Admin-Konsole. |
| **Dev** | `ChatService`, Guard-Hooks, Workspace-IDs, Signal/Async-Pfade in `chat_workspace.py`. |

## 8. Typischer Nutzungsablauf (Kurz)

Ein Fachanwender öffnet **Operations → Chat**, wählt oder erstellt eine Session, prüft Modell und ggf. Projektzeile, sendet eine Nachricht — optional mit Slash-Command am Zeilenanfang. Technisch läuft dieselbe Sequenz wie im Abschnitt **Prozesssicht**; für Support reicht oft die Frage, ob Kontextmodus, RAG und Guard in der betroffenen Konstellation aktiv sind.
