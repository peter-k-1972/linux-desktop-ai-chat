# Linux Desktop Chat – Einführung

> **User-facing help:** See [help/getting_started/introduction.md](../../help/getting_started/introduction.md) for the canonical article (used by in-app Help).

## Überblick

Der **Linux Desktop Chat** ist eine lokale Desktop-Anwendung für KI-gestützte Konversationen. Er nutzt **Ollama** als Backend für Sprachmodelle und bietet erweiterte Funktionen wie RAG, Agenten, Modell-Routing und mehr.

Für eine kompakte, in der App eingebundene Anleitung siehe [help/getting_started/introduction.md](../../help/getting_started/introduction.md). Dieses Kapitel im `docs`-Baum fokussiert die Produktbeschreibung und Verweise auf vertiefende Handbuch- und Feature-Dateien.

## Kernfunktionen

Im Überblick — ohne Anspruch auf Vollständigkeit aller Screens:

- **Chat**: Natürliche Konversation mit lokalen oder Cloud-Modellen
- **RAG**: Kontext aus indexierten Dokumenten nutzen
- **Agenten**: Spezialisierte Personas (Code, Research, Media, …)
- **Modell-Routing**: Automatische Auswahl nach Aufgabenart
- **Prompts**: Wiederverwendbare System- und User-Prompts
- **Tools**: Dateisystem-Zugriff im Workspace

## Schnellstart

1. **Ollama installieren** und mindestens ein Modell laden: `ollama pull qwen2.5`
2. **Anwendung starten** (empfohlen): `python -m app` — alternativ: `python main.py` oder `python run_gui_shell.py`
3. **Abhängigkeiten**: siehe Repository-`README.md` und `docs/DEVELOPER_GUIDE.md` (`pip install -r requirements.txt`)
4. **Neuer Chat**: unter Operations → Chat, „Neuer Chat“ bzw. Session-Liste
5. **Nachricht senden**: Text eingeben und senden

## Weitere Themen

- [Architektur](architecture.md)
- [Modelle und Provider](../02_user_manual/models.md)
- [Agenten-System](../FEATURES/agents.md) → Help: [help/operations/agents_overview.md](../../help/operations/agents_overview.md)
- [RAG-Wissenssystem](../FEATURES/rag.md) → Help: [help/operations/knowledge_overview.md](../../help/operations/knowledge_overview.md)
- [Einstellungen](../FEATURES/settings.md) → Help: [help/settings/settings_overview.md](../../help/settings/settings_overview.md)
