---
id: prompt_studio_overview
title: Prompt Studio
category: operations
tags: [prompts, templates, prompt-manager]
related: [chat_overview, settings_prompts, workflows_workspace]
workspace: operations_prompt_studio
screen: operations
order: 40
---

# Prompt-System

## Übersicht

Das Prompt-System verwaltet **wiederverwendbare Prompts** für System-Nachrichten, User-Templates und Entwickler-Prompts.

Unter **Operations → Prompt Studio** bearbeiten Sie diese Vorlagen; der Chat bleibt der Ort, an dem Sie sie ausprobieren und mit Modell, Kontext und RAG kombinieren. Welche Aktion genau „Anwenden“ oder „In Composer“ auslöst, hängt vom jeweiligen Button im Prompt-Manager-Panel ab — unten die üblichen Varianten.

## Prompt-Typen

Der **Typ** bestimmt primär die semantische Rolle der Vorlage (System vs. User vs. Entwickler vs. wiederverwendbare Template-Struktur). Bei der Nutzung im Chat entscheidet die gewählte Aktion, ob der Text als Systemnachricht, als Entwurf in der Eingabezeile oder anders einfließt.

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

Slash-Commands im Chat (z. B. `/think`, `/code`, `/research`, `/delegate`) sind **kein** Ersatz für gespeicherte Prompts: Sie steuern Rolle oder Delegation für die aktuelle Zeile. Gespeicherte Prompts ergänzen das — etwa lange Arbeitsanweisungen, die Sie nicht jedes Mal eintippen möchten.
