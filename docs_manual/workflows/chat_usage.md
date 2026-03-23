# chat_usage

Endnutzer-Workflow: erste Unterhaltung, Modellwahl, Streaming, Slash-Befehle. Orientierung an der GUI unter **Operations → Chat** (`operations_chat`).

## Inhalt

- [Ziel](#ziel)
- [Voraussetzungen](#voraussetzungen)
- [Schritte](#schritte)
- [Varianten](#varianten)
- [Fehlerfälle](#fehlerfälle)
- [Tipps](#tipps)

**Beteiligte Module**

- [Chat](../modules/chat/README.md) · [Kontext](../modules/context/README.md) · [Settings](../modules/settings/README.md) · [Provider / Modelle](../modules/providers/README.md)  
- [Agenten](../modules/agents/README.md) (Slash `/delegate`) · [GUI](../modules/gui/README.md)

**Siehe auch**

- [Feature: Chat](../../docs/FEATURES/chat.md) · [Benutzerhandbuch – Chat](../../docs/USER_GUIDE.md#1-chat-benutzen) · [Chat-Hilfe](../../help/operations/chat_overview.md)

Die folgenden Schritte sind bewusst **linear** beschrieben: In der Praxis wechseln Sie oft zwischen Session-Liste und Eingabe, aber die Reihenfolge „Bereich öffnen → Session → Modell → Senden“ entspricht dem minimalen erfolgreichen Pfad. Wenn etwas schiefgeht, helfen die Tabellen unter **Fehlerfälle** und die Hinweise zu Ollama/Modellliste — bevor Sie Einstellungen oder Kontext tiefer verdrehen.

## Ziel

Sie führen eine Konversation mit dem Sprachmodell: Nachrichten senden, Antwort erhalten, bei Bedarf Rolle oder Routing anpassen.

## Voraussetzungen

1. Die Anwendung ist gestartet (`python -m app` oder `python main.py`).
2. **Ollama** läuft auf dem Rechner oder dem konfigurierten Server (`ollama serve`).
3. Mindestens ein Modell ist geladen (z. B. Terminal: `ollama pull qwen2.5`).
4. Sie wissen, ob Sie mit einem **Projekt** arbeiten: Projekt im **Project Hub** oder über die Kontextleiste im Chat gewählt — oder Sie arbeiten ohne spezifisches Projekt.

## Schritte

### A) Chat-Bereich öffnen

1. Schauen Sie auf die **linke Seitenleiste**.
2. Klicken Sie auf den Bereich **Operations** (nicht Control Center, nicht Settings).
3. In der **zweiten Leiste** (neben dem Hauptfenster) wählen Sie **Chat** — nicht „Projects“, nicht „Knowledge“.
4. Es erscheint der Chat-Workspace: links die **Session-Liste**, in der Mitte die **Konversation**, unten die **Eingabe**.

### B) Chat auswählen oder anlegen

1. Links in der Session-Liste einen bestehenden Eintrag anklicken **oder** die Aktion zum **neuen Chat** nutzen (je nach Beschriftung: z. B. „Neuer Chat“ / Plus — genaue Bezeichnung in Ihrer Version).
2. Oben in der Mitte sehen Sie ggf. **Projekt**, **Chat-Titel** und optional **Topic** in der **Kontextleiste** über der Konversation. So wissen Sie, in welchem Kontext Sie schreiben.

### C) Modell prüfen

1. In der **Kopfzeile** des Chats oder neben der Eingabe: **Modell** aus der Liste wählen.
2. Wenn die Liste leer ist: abbrechen, **Control Center → Models** oder **Einstellungen → AI / Models** prüfen und Ollama-Status unter **Control Center → Providers** ansehen (siehe Workflow **settings_usage** und Fehlerfälle unten).

### D) Nachricht schreiben und senden

1. Cursor in das **Eingabefeld** unten setzen.
2. Text tippen.
3. **Senden** klicken oder die in der App vorgesehene Tastenkombination nutzen.
4. Wenn **Streaming** eingeschaltet ist (`chat_streaming_enabled` in den Einstellungen), erscheint die Antwort **während** der Erzeugung. Wenn aus, erscheint sie **am Ende** in einem Stück.

### E) Rolle nur für die nächste Frage setzen (Slash-Befehl)

1. Zeile beginnt mit **`/`** — kein Leerzeichen davor.
2. Beispiele (genau so implementiert in `app/core/commands/chat_commands.py`):
   - **`/think Ihre Frage hier`** — Denk-Rolle, der Text nach dem Befehl wird als normale Nachricht mit dieser Rolle gesendet.
   - **`/code …`**, **`/research …`**, **`/fast`**, **`/smart`**, **`/chat`**, **`/vision`**, **`/overkill`** — ebenfalls Rollen; mit Text dahinter wird mitgesendet, ohne Text nur Modus-Umschaltung mit kurzer Meldung.
3. **`/auto on`** oder **`/auto off`** — Auto-Routing.
4. **`/cloud on`** oder **`/cloud off`** — Cloud-Eskalation (nur sinnvoll, wenn Ihre Umgebung Cloud und Schlüssel erlaubt).

## Varianten

| Situation | Was Sie tun |
|-----------|-------------|
| Kurze Alltagsfrage | Direkt tippen, Standardmodell lassen. |
| Code erklären lassen | `/code` vor die Frage setzen oder Code-Rolle wählen, falls angeboten. |
| Tiefere Überlegung | `/think` plus Frage in einer Zeile. |
| Mehrstufige Aufgabe an Agenten | Workflow **agent_usage** (`/delegate`). |

## Fehlerfälle

| Was Sie sehen | Was Sie tun |
|---------------|-------------|
| Keine Antwort, endlos wartend | Ollama prüfen; **Providers** auf „online“; Netzwerk; kleineres Modell testen. |
| Modell-Dropdown leer | Modell mit `ollama pull` laden; App neu starten; **AI / Models** öffnen. |
| Slash-Befehl erscheint als normaler Chat-Text | Zeile muss mit `/` beginnen; Befehl exakt schreiben (Kleinbuchstaben nach dem Slash wie in der App). |
| Meldung „Unbekannter Befehl“ | Tippfehler; erlaubt sind u. a. `/fast`, `/smart`, `/chat`, `/think`, `/code`, `/vision`, `/overkill`, `/research`, `/delegate`, `/auto`, `/cloud`. |
| Zwei Antworten / seltsames Verhalten beim Senden | Vorherigen Lauf abwarten; ggf. App neu starten (seltener Guard-/Stream-Konflikt). |

## Tipps

- Vor längeren Arbeiten **Projekt** und **Chat-Titel** in der Kontextleiste kurz prüfen — vermeidet Nachrichten im falschen Chat.
- Für wiederkehrende Texte den **Prompt Studio** nutzen (Workflow gesondert).
- Wenn Antworten zu „allgemein“ wirken: Workflow **context_control** lesen (Kontextmodus).
