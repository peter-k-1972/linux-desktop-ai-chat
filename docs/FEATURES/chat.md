# Feature: Chat

## Inhalt

- [Zweck](#zweck)
- [Funktionsweise](#funktionsweise)
- [Konfiguration (Auszug)](#konfiguration-auszug)
- [Typischer Ablauf](#typischer-ablauf)
- [Beispiel](#beispiel)
- [Typische Fehler](#typische-fehler)

**Siehe auch**

- [Feature: Context](context.md) · [Feature: Settings](settings.md) · [Architektur – Datenfluss (Chat)](../ARCHITECTURE.md#2-datenfluss)  
- [Benutzerhandbuch – Chat](../USER_GUIDE.md#1-chat-benutzen)

**Typische Nutzung**

- [Chat verwenden](../../docs_manual/workflows/chat_usage.md)  
- [Kontextmodus ändern](../../docs_manual/workflows/context_control.md)  
- [Agent / Delegation](../../docs_manual/workflows/agent_usage.md)  
- [Chat-Hilfe](../../help/operations/chat_overview.md)

## Zweck

Der Chat ist der zentrale Pfad, auf dem Benutzer-Nachrichten in eine geordnete Message-Liste überführt, optional mit strukturiertem Projekt-/Chat-Kontext angereichert und an Ollama (lokal oder über konfigurierte Cloud-Pfade) gesendet werden. Dabei werden Sessions verwaltet, Nachrichten gespeichert, bei Bedarf während der Generierung gestreamt und über Slash-Commands Rollen sowie Routing für einzelne Anfragen gesteuert.

## Funktionsweise

Vom UI aus ruft der Chat-Workspace Backend-Hilfen auf (`app/gui/chat_backend.py`), die wiederum `ChatService` verwenden. Vor dem Provider-Aufruf werden Slash-Commands geparst, der Konversationsverlauf aufgebaut und — sofern der Kontextmodus nicht `off` ist — ein Systemfragment aus `ChatRequestContext` eingefügt (siehe Feature **Context**). Optional greift der Chat Guard auf die letzte Nutzernachricht zu und kann die Message-Liste anpassen, bevor das Modell antwortet.

- **UI:** `app/gui/domains/operations/chat/` (Chat-Workspace, Session-Explorer, Konversation, Eingabe).  
- **Backend:** `app/services/chat_service.py` – Aufbau der Message-Liste, Kontextinjektion, Guard, Provider-Aufruf.  
- **Streaming:** `AppSettings.chat_streaming_enabled` steuert, ob Token während der Generierung angezeigt werden.  
- **Commands:** `app/core/commands/chat_commands.py` – Parsing von `/fast`, `/think`, `/delegate`, `/auto`, `/cloud`, …

## Konfiguration (Auszug)

| Schlüssel (`AppSettings`) | Bedeutung |
|---------------------------|-----------|
| `model` | Standardmodellname |
| `temperature`, `max_tokens` | Generierungsparameter |
| `chat_streaming_enabled` | Streaming an/aus |
| `chat_context_*` | siehe `FEATURES/context.md` |

## Typischer Ablauf

1. Nutzer wählt unter **Operations → Chat** eine Session oder legt eine neue an.  
2. Optional wird das Modell in der Chat-Kopfzeile bzw. am Eingabebereich gewechselt; Standard kommt aus den globalen Einstellungen.  
3. Die nächste Zeile kann mit einem Slash-Command beginnen (z. B. `/think …`); der Rest der Zeile wird als Inhalt der Nutzernachricht behandelt, nicht der Befehlstext.  
4. `ChatService` baut die Messages, löst die effektive Kontextkonfiguration auf und ruft den Provider auf; bei aktivem Streaming erscheinen Token schrittweise in der Konversation.

## Beispiel

**Beispiel** — Ablauf in der Oberfläche:

1. Operations → Chat.  
2. Neue Session.  
3. Eingabe: `/think Was ist 2+2?` → sendet die Frage mit THINK-Rolle.

## Typische Fehler

| Problem | Ursache |
|---------|---------|
| Doppelte Sends / hängender Stream | Chat-Guard-Konflikt; ggf. vorherigen Lauf warten oder App neu starten |
| Falsche Rolle | Slash-Command nicht am Zeilenanfang oder Tippfehler im Command |
| Keine Antwort | Ollama offline oder Modell nicht geladen |
