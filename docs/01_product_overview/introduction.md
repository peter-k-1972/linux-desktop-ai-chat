# Linux Desktop Chat – Einführung

> **User-facing help:** See [help/getting_started/introduction.md](../help/getting_started/introduction.md) for the canonical article (used by in-app Help).

## Überblick

Der **Linux Desktop Chat** ist eine lokale Desktop-Anwendung für KI-gestützte Konversationen. Er nutzt **Ollama** als Backend für Sprachmodelle und bietet erweiterte Funktionen wie RAG, Agenten, Modell-Routing und mehr.

## Kernfunktionen

- **Chat**: Natürliche Konversation mit lokalen oder Cloud-Modellen
- **RAG**: Kontext aus indexierten Dokumenten nutzen
- **Agenten**: Spezialisierte Personas (Code, Research, Media, …)
- **Modell-Routing**: Automatische Auswahl nach Aufgabenart
- **Prompts**: Wiederverwendbare System- und User-Prompts
- **Tools**: Dateisystem-Zugriff im Workspace

## Schnellstart

1. **Ollama installieren** und mindestens ein Modell laden: `ollama pull qwen2.5`
2. **Anwendung starten**: `python main.py`
3. **Neuer Chat**: Klick auf „Neuer Chat“ in der Sidebar
4. **Nachricht senden**: Text eingeben und Senden-Button klicken

## Weitere Themen

- [Architektur](architecture.md)
- [Modelle und Provider](models.md)
- [Agenten-System](agents.md) → Help: [help/operations/agents_overview.md](../help/operations/agents_overview.md)
- [RAG-Wissenssystem](rag.md) → Help: [help/operations/knowledge_overview.md](../help/operations/knowledge_overview.md)
- [Einstellungen](settings.md) → Help: [help/settings/settings_overview.md](../help/settings/settings_overview.md)
