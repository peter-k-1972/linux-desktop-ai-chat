---
id: chat_overview
title: Chat Workspace
category: operations
tags: [chat, konversation, sessions]
related: [agents_overview, knowledge_overview, prompt_studio_overview, settings_chat_context]
workspace: operations_chat
screen: operations
order: 10
---

# Chat Workspace

## Inhalt

- [Überblick](#überblick)
- [Komponenten](#komponenten)
- [Workflow](#workflow)
- [Slash-Commands](#slash-commands)
- [Siehe auch](#siehe-auch)

**Siehe auch (Repository)**

- [Feature: Chat](../../docs/FEATURES/chat.md) · [Benutzerhandbuch – Chat](../../docs/USER_GUIDE.md#1-chat-benutzen) · [Workflow: Chat](../../docs_manual/workflows/chat_usage.md)

## Überblick

Der **Chat Workspace** ermöglicht Konversationen mit lokalen oder Cloud-Sprachmodellen. Er kombiniert Session Explorer, Nachrichtenverlauf und Eingabebereich.

Sie arbeiten hier durchgehend in **einer** aktiven Session: alles, was Sie senden, hängt an dieser Session und erscheint im mittleren Verlauf. Wechseln Sie die Session links, wechseln Sie den Gesprächsstrang — vergleichbar mit mehreren Tabs in einem Messenger, jedoch mit Modellwahl und optional RAG- und Kontextanreicherung pro Anfrage.

## Komponenten

Die Fläche ist in feste Bereiche aufgeteilt, damit Navigation (welcher Chat?), Inhalt (was wurde gesagt?) und Eingabe (was kommt als Nächstes?) getrennt bleiben.

- **Session Explorer** (links): Liste der Chats, „Neuer Chat“, Suche
- **Conversation** (Mitte): Nachrichtenverlauf mit Streaming
- **Input Panel** (unten): Modell-Auswahl, Texteingabe, Senden
- **Inspector** (rechts): Session-Details, RAG-Kontext

## Workflow

1. Chat auswählen oder „Neuer Chat“ erstellen
2. Modell und optional Agent im Header wählen
3. Nachricht eingeben und senden
4. RAG aktivieren für Kontext aus indexierten Dokumenten (Knowledge-Workspace, Einstellungen `rag_enabled`)
5. **Chat-Kontext** (Projekt/Chat/Topic im Systemprompt): siehe [Chat-Kontext & Einstellungen](settings_chat_context)

**Typischer Fehler:** Nachricht in der falschen Session — vor dem Senden kurz Titel und ggf. Projektzeile in der Kontextleiste prüfen.

## Slash-Commands

Slash-Commands gelten für die **aktuelle Zeile** der Eingabe: Sie müssen am **Anfang** der Zeile stehen (kein Leerzeichen vor dem `/`). Alles nach dem Befehl wird als eigentlicher Nachrichtentext bzw. als Parameter interpretiert, nicht der Befehlsname selbst.

Definiert in `app/core/commands/chat_commands.py`:

- **Rollen:** `/fast`, `/smart`, `/chat`, `/think`, `/code`, `/vision`, `/overkill`, `/research` — mit nachfolgendem Text wird die Nachricht mit dieser Rolle gesendet (Beispiel: `/think Erkläre …`).
- **Routing:** `/auto on` | `/auto off`, `/cloud on` | `/cloud off`
- **Delegation:** `/delegate <Anfrage>` — die Zeile nach dem Befehl ist die Aufgabe an die Agenten-Orchestrierung

## Siehe auch

- [Agenten](agents_overview)
- [RAG / Knowledge](knowledge_overview)
- [Prompts](prompt_studio_overview)
- [Chat-Kontext](settings_chat_context)
