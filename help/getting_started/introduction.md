---
id: introduction
title: Linux Desktop Chat – Einführung
category: getting_started
tags: [einführung, schnellstart, überblick]
related: [chat_overview, agents_overview, knowledge_overview, prompt_studio_overview, settings_chat_context]
order: 10
---

# Linux Desktop Chat – Einführung

## Inhalt

- [Überblick](#überblick)
- [Kernfunktionen](#kernfunktionen)
- [Schnellstart](#schnellstart)
- [Weitere Themen](#weitere-themen)

**Siehe auch (Repository)**

- [Benutzerhandbuch](../../docs/USER_GUIDE.md) · [Architektur](../../docs/ARCHITECTURE.md) · [Feature: Chat](../../docs/FEATURES/chat.md)  
- [Workflows im Handbuch](../../docs_manual/workflows/chat_usage.md) · [Hilfe-Index](../README.md)

## Überblick

Der **Linux Desktop Chat** ist eine lokale Desktop-Anwendung für KI-gestützte Konversationen. Er nutzt **Ollama** als Backend für Sprachmodelle und bietet erweiterte Funktionen wie RAG, Agenten, Modell-Routing und mehr.

Die Oberfläche ist in **Bereiche** gegliedert (u. a. Operations für den laufenden Chat und zugehörige Werkzeuge, Control Center für Modelle und Anbindungen, Settings für dauerhafte Konfiguration). Sie müssen nicht alles vor dem ersten Chat verstehen: Für den Einstieg reichen laufender Ollama-Dienst, ein geladenes Modell und der Pfad **Operations → Chat**.

## Kernfunktionen

- **Chat**: Natürliche Konversation mit lokalen oder Cloud-Modellen
- **RAG**: Kontext aus indexierten Dokumenten nutzen
- **Agenten**: Spezialisierte Personas (Code, Research, Media, …)
- **Modell-Routing**: Automatische Auswahl nach Aufgabenart
- **Prompts**: Wiederverwendbare System- und User-Prompts
- **Tools**: Dateisystem-Zugriff im Workspace

## Schnellstart

1. **Python-Umgebung**: Abhängigkeiten installieren (`pip install -r requirements.txt` im Projektroot)
2. **Ollama installieren** und mindestens ein Modell laden: `ollama pull qwen2.5`
3. **Ollama-Dienst starten**: `ollama serve`
4. **Anwendung starten** (empfohlen): `python -m app` — alternativ: `python main.py` (kanonische Shell; Legacy nur `archive/run_legacy_gui.py`)
5. **Neuer Chat**: Operations → Chat, Session wählen oder neu anlegen
6. **Nachricht senden**: Text eingeben und senden

## Weitere Themen

- **Hilfe öffnen** (Menü/Palette): unter **Ansicht → Semantische Doku-Suche** kann das Repository per Vektorindex durchsucht werden, sofern der Index gebaut wurde (Hinweis im Hilfefenster).
- [Chat Workspace](chat_overview)
- [Agenten-System](agents_overview)
- [RAG-Wissenssystem](knowledge_overview)
- [Prompt Studio](prompt_studio_overview)
- [Einstellungen](settings_overview)
