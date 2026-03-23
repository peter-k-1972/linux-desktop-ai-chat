# Fachanwender

Handbuch für die tägliche Nutzung der Desktop-App ohne technische Implementierungsdetails. Begriffe und Schritte sind an der realen Oberfläche und den Modulen unter `docs_manual/modules/` ausgerichtet.

## Relevante Module

- [Chat](../../modules/chat/README.md) · [Kontext](../../modules/context/README.md) · [RAG](../../modules/rag/README.md) · [Prompts](../../modules/prompts/README.md)  
- [Agenten](../../modules/agents/README.md) · [Settings](../../modules/settings/README.md) · [Provider](../../modules/providers/README.md) · [GUI](../../modules/gui/README.md)

**Workflows:** [Chat](../../workflows/chat_usage.md) · [Kontext](../../workflows/context_control.md) · [Einstellungen](../../workflows/settings_usage.md) · [Agenten](../../workflows/agent_usage.md) · [Hilfe-Index](../../../help/README.md)

## Aufgaben

- Im Bereich **Operations** Chats führen, Inhalte mit dem Modell erarbeiten.
- Unter **Knowledge** Dokumente verwalten und für RAG-basierte Antworten nutzen (wenn aktiviert).
- Im **Prompt Studio** Vorlagen pflegen und im Arbeitsfluss verwenden.
- **Agent Tasks** und **Agentenwahl im Chat** nutzen, wenn Ihre Umgebung das vorsieht.
- **Einstellungen** öffnen: Erscheinungsbild, KI/Modelle, ggf. erweiterte Optionen inkl. **Chat-Kontext-Modus**.
- Über **Control Center** prüfen, ob Modelle und Provider erreichbar sind, bevor Sie chatten.

## Typische Workflows

### Neuen Chat starten und schreiben

1. Sidebar: **Operations** wählen.
2. In der linken Leiste **Chat** aktivieren (Workspace **Chat**).
3. Session wählen oder neue Session anlegen.
4. Unten Text eingeben und senden.
5. Modell oder Agent über die Kopfzeile des Chats wählen, soweit angeboten.

### Rolle oder Routing per Eingabezeile

Am Anfang der Nachricht, direkt nach den Regeln der App:

- `/think …`, `/code …`, `/research …` usw. setzen die **Rolle** für diese Nachricht (Rest der Zeile wird mitgesendet).
- `/auto on` oder `/auto off` schalten **Auto-Routing**.
- `/cloud on` oder `/cloud off` steuern **Cloud-Eskalation** (nur wirksam, wenn Ihre Organisation Ollama-Cloud und Schlüssel freigibt).
- `/delegate Aufgabe` startet die **Delegations**-Bearbeitung mit dem Text nach dem Befehl — ohne Text erscheint nur ein Hinweis.

(Implementierung: `app/core/commands/chat_commands.py`.)

### RAG nutzen

1. **Operations → Knowledge:** Quellen anlegen oder aktualisieren, Indexierung ausführen (wie in Ihrer Umgebung vorgesehen, z. B. über Skripte aus dem Projekt).
2. In den **Einstellungen** RAG aktivieren und **Space** sowie **Top-K** prüfen (`rag_enabled`, `rag_space`, `rag_top_k`).
3. Im **Chat** Frage stellen, die zu den indexierten Inhalten passt.

### Kontext verstehen (ohne Technik)

Der **Chat-Kontext** ist zusätzlicher Hintergrund, den die App dem Modell mitgeben kann: z. B. zu welchem **Projekt** und welchem **Chat** die Nachricht gehört. Darüber gibt die Leiste **über** der Konversation Auskunft (Projektname, Chat-Titel, ggf. Topic).

**Drei Stufen „wie viel Hintergrund“ (vereinfacht):**

- **Aus:** Es wird kein solcher Struktur-Hintergrund mitgeschickt. Das Modell sieht nur das, was Sie in den Nachrichten schreiben (plus ggf. RAG, Prompts, Agenten-Systemprompt).
- **Neutral:** Hintergrund wird sachlich/knapp formuliert mitgegeben.
- **Semantisch:** Hintergrund wird ausführlicher mitgegeben.

Wo Sie das umstellen: **Einstellungen → Advanced → Chat-Kontext-Modus** (`AdvancedSettingsPanel`).

**Wichtig:** Wenn Antworten „ohne Bezug zum Projekt“ wirken, kann der Modus **Aus** aktiv sein — oder eine andere Regel in der App hat Vorrang vor Ihrer manuellen Einstellung (das klären ggf. Admins oder Support über die QA-/Debug-Ansichten).

### Typische Fehler und was Sie tun können

| Symptom | Was prüfen |
|---------|------------|
| Keine Antwort / dauert sehr lange | **Control Center → Providers:** Online? Ollama auf dem Rechner/Server gestartet? |
| Modellliste leer | Modell mit `ollama pull …` laden; App neu starten; **Einstellungen → AI / Models** oder **Control Center → Models**. |
| RAG liefert nichts | Unter **Knowledge** indexiert? RAG in den Einstellungen eingeschaltet? Richtiger **Space**? |
| Slash-Befehl wird als normaler Text gesendet | Zeile muss mit `/` beginnen; Tippfehler im Befehlsnamen → App meldet „Unbekannter Befehl“. |
| `/delegate` passiert nichts Sichtbares | Kein Text nach `/delegate` eingegeben — es erscheint nur die Verwendungsmeldung. |
| Chat wirkt „ohne Projektbezug“ | Kontextmodus **Aus**; oder Projekt/Chat in der Kontextleiste prüfen. |

## Genutzte Module

| Modul | Nutzen für Sie |
|-------|----------------|
| [gui](../../modules/gui/README.md) | Navigation, Operations, Chat-, Knowledge-, Prompt-Studio-Workspaces. |
| [chat](../../modules/chat/README.md) | Senden, Streaming, Slash-Commands. |
| [context](../../modules/context/README.md) | Bedeutung von Kontextmodus (fachlich vereinfacht oben). |
| [prompts](../../modules/prompts/README.md) | Prompt Studio. |
| [rag](../../modules/rag/README.md) | Knowledge-Workspace und RAG-Schalter. |
| [agents](../../modules/agents/README.md) | Agent Tasks, Agentenwahl, `/delegate`. |
| [settings](../../modules/settings/README.md) | Alle Einstellungskategorien inkl. Advanced. |
| [providers](../../modules/providers/README.md) | Providers-Workspace (Status). |

## Risiken

- **Falsche Annahmen zum Kontext:** Bei Modus **Aus** oder eingeschränkten Includes „weiß“ das Modell nicht automatisch alles über Projekt/Chat.
- **Cloud und Daten:** Wenn **Cloud** eingeschaltet ist und Ihre Organisation Cloud-Modelle nutzt, verlassen Anfragen das lokale Ollama-Szenario — Klärung mit Admin/Richtlinien.
- **RAG-Qualität:** Antworten hängen von Index, gewähltem Space und Dokumentqualität ab.

## Best Practices

- Vor längeren Sessions **Provider-Status** und **Standardmodell** prüfen.
- Für wiederkehrende Texte **Prompt Studio** nutzen statt jedes Mal neu zu formulieren.
- Bei Themen mit internen Dokumenten **Knowledge** pflegen und RAG gezielt aktivieren.
- Wenn Antworten zu allgemein sind: Kontextmodus nicht auf **Aus**, sofern Ihre Richtlinien Projektbezug erlauben.
