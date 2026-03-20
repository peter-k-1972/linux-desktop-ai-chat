---
id: prompt_studio_overview
title: Prompt Studio
category: operations
tags: [prompts, templates, prompt-manager]
related: [chat_overview, settings_prompts]
workspace: operations_prompt_studio
screen: operations
order: 40
---

# Prompt-System

## Übersicht

Das Prompt-System verwaltet **wiederverwendbare Prompts** für System-Nachrichten, User-Templates und Entwickler-Prompts.

## Prompt-Typen

| Typ | Verwendung |
|-----|------------|
| user | User-Nachrichten, Templates |
| system | System-Prompts für LLM |
| developer | Entwickler-spezifisch |
| template | Vorlagen mit Platzhaltern |

## Kategorien

- general, code, analysis, creative, instruction, other

## Speicherung

- **Database**: SQLite (Standard)
- **Directory**: Markdown-Dateien in einem Verzeichnis

Einstellbar unter: Einstellungen → Prompts → Speichertyp

## Prompts im Side-Panel

Das **Prompt-Manager-Panel** (rechte Seite) bietet:

- **Liste** aller Prompts
- **Anwenden**: Prompt als System-Nachricht in den Chat
- **Als System**: Wie Anwenden
- **In Composer**: Prompt-Text in die Eingabezeile übernehmen

## Prompt erstellen

1. Side-Panel → Prompt-Manager
2. Neuer Prompt
3. Titel, Kategorie, Typ, Inhalt eingeben
4. Speichern

## Slash-Commands

Rollen-Commands: `/think`, `/code`, `/research`, `/delegate`
