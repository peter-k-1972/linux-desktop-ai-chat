---
id: chat_overview
title: Chat Workspace
category: operations
tags: [chat, konversation, sessions]
related: [agents_overview, knowledge_overview, prompt_studio_overview]
workspace: operations_chat
screen: operations
order: 10
---

# Chat Workspace

## Überblick

Der **Chat Workspace** ermöglicht Konversationen mit lokalen oder Cloud-Sprachmodellen. Er kombiniert Session Explorer, Nachrichtenverlauf und Eingabebereich.

## Komponenten

- **Session Explorer** (links): Liste der Chats, „Neuer Chat“, Suche
- **Conversation** (Mitte): Nachrichtenverlauf mit Streaming
- **Input Panel** (unten): Modell-Auswahl, Texteingabe, Senden
- **Inspector** (rechts): Session-Details, RAG-Kontext

## Workflow

1. Chat auswählen oder „Neuer Chat“ erstellen
2. Modell und optional Agent im Header wählen
3. Nachricht eingeben und senden
4. RAG aktivieren für Kontext aus indexierten Dokumenten

## Slash-Commands

- `/think` – Denk-Modus
- `/code` – Code-Modus
- `/research` – Research-Workflow (RAG)
- `/delegate` – Agenten-Orchestrierung

## Siehe auch

- [Agenten](agents_overview)
- [RAG / Knowledge](knowledge_overview)
- [Prompts](prompt_studio_overview)
