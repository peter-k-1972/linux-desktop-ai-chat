# agent_usage

Endnutzer-Workflow: **Agenten** wählen, **Agent Tasks** nutzen und **Delegation** über `/delegate`. Codebasis: `app/agents/`, Workspaces `operations_agent_tasks`, `cc_agents`, Slash-Parser `app/core/commands/chat_commands.py`.

## Inhalt

- [Ziel](#ziel)
- [Voraussetzungen](#voraussetzungen)
- [Schritte A: Agent im Chat verwenden](#schritte-a-agent-im-chat-verwenden)
- [Schritte B: Agent Tasks öffnen](#schritte-b-agent-tasks-öffnen)
- [Schritte C: Delegation mit `/delegate`](#schritte-c-delegation-mit-delegate)
- [Varianten](#varianten)
- [Fehlerfälle](#fehlerfälle)
- [Tipps](#tipps)

**Beteiligte Module**

- [Agenten](../modules/agents/README.md) · [Chat](../modules/chat/README.md) · [Kontext / Policies](../modules/context/README.md) · [GUI](../modules/gui/README.md)

**Siehe auch**

- [Feature: Agenten](../../docs/FEATURES/agents.md) · [Workflow: Chat](chat_usage.md) · [Hilfe: Agenten](../../help/operations/agents_overview.md)

Die Abschnitte A–C führen nacheinander durch: Agent im Chat, Agent-Tasks-Workspace und die `/delegate`-Zeile.

## Ziel

Sie nutzen ein **Agentenprofil** oder lassen eine **Delegations**-Bearbeitung mit mehreren Schritten über die Agenten-Infrastruktur laufen.

## Voraussetzungen

1. Anwendung gestartet, **Ollama** erreichbar (wie beim Chat).
2. Agenten sind in Ihrer Umgebung **angelegt** (Standard: Seed-Profile beim ersten Start — siehe `app/agents/seed_agents.py`; bei leerem Dropdown Admin informieren).
3. Sie kennen den Unterschied: **Agent im Chat** (andere Systemrolle) vs. **`/delegate`** (Orchestrierungspfad).

## Schritte A: Agent im Chat verwenden

1. **Operations → Chat** öffnen (siehe **chat_usage**).
2. In der **Kopfzeile** des Chats (oder dem dafür vorgesehenen Steuerelement): **Agent** aus der Liste wählen — falls die Oberfläche das anbietet.
3. Nachricht normal eingeben und senden.
4. Das Modell arbeitet mit dem **Systemprompt** und der **Modellzuweisung** des gewählten Profils (`AgentProfile`).

## Schritte B: Agent Tasks öffnen

1. Sidebar: **Operations**.
2. In der zweiten Leiste **Agent Tasks** wählen (Workspace **`operations_agent_tasks`**).
3. Dort die projektbezogenen Aufgaben und Status einsehen und Aktionen ausführen, die Ihre Version der Oberfläche anbietet (Listen, Buttons — ohne hier Einzelfunktionen zu erfinden).

## Schritte C: Delegation mit `/delegate`

1. **Operations → Chat** öffnen.
2. In das Eingabefeld schreiben — **eine Zeile**, beginnend mit:
   - **`/delegate `** (Slash, Wort delegate, **Leerzeichen**)
   - direkt danach **Ihre Aufgabe in eigenen Worten**, z. B.:  
     `/delegate Fasse die letzten drei Änderungen im Projekt in drei Bulletpoints zusammen`
3. Senden.
4. **Ohne Text nach `/delegate`** zeigt die App nur einen **Hinweis zur korrekten Verwendung** — es wird keine Delegationsaufgabe mit Inhalt gestartet (so implementiert in `parse_slash_command`).

## Varianten

| Situation | Vorgehen |
|-----------|----------|
| Schnelle Frage ohne Spezialagent | Keinen Agent wählen; Standard-Chat. |
| Code-fokussiert | Agent „Code“ o. Ä. wählen, falls vorhanden, oder `/code` (siehe **chat_usage**). |
| Große, mehrteilige Aufgabe | `/delegate` mit klarer Aufgabenbeschreibung in **einem** Senden. |
| Agenten verwalten | **Control Center → Agents** (`cc_agents`) — Profile ansehen/bearbeiten, soweit die UI erlaubt. |

## Fehlerfälle

| Was Sie sehen | Was Sie tun |
|---------------|-------------|
| Agent-Dropdown leer | App neu starten; **Control Center → Agents** prüfen; Admin wegen Datenbank/Seed benachrichtigen. |
| `/delegate` ohne Reaktion auf die Aufgabe | Prüfen, ob **Text nach** `/delegate` stand; nur `/delegate` allein reicht nicht. |
| Fehlermeldung „Unbekannter Befehl“ | Tippfehler: exakt **`/delegate`** schreiben. |
| Delegation läuft, Ergebnis unbefriedigend | Aufgabe **schärfer** formulieren; kürzeren Umfang pro Aufruf; anderes Modell/Agent testen. |
| Agent Tasks zeigen nichts | **Projekt** aktiv? Agent Tasks sind projektbezogen, wenn ein Projekt ausgewählt ist (siehe `docs/00_map_of_the_system.md`, global vs. projektbezogen). |

## Tipps

- **Eine klare Aufgabe pro `/delegate`**: Wer soll was liefern, in welchem Format?
- Vor **Delegation** kurz prüfen, ob **Chat-Kontext** passt (Workflow **context_control**) — sonst fehlt dem Modell der gewünschte Bezug.
- Für wiederkehrende Agenten-Einstellungen **Control Center → Agents** mit dem Team abstimmen, nicht jede Session neu erfinden.
