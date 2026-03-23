# context_control

Endnutzer-Workflow: **Chat-Kontext** steuern — wie viel Hintergrund (Projekt, Chat, ggf. Topic) dem Modell als Strukturinformation mitgegeben wird. Technische Details (Policies, Profil-Overrides) sind in `docs_manual/modules/context/README.md`; hier nur das, was Sie in der App direkt sehen und einstellen können.

## Inhalt

- [Ziel](#ziel)
- [Voraussetzungen](#voraussetzungen)
- [Begriffe in drei Stufen (für Endnutzer)](#begriffe-in-drei-stufen-für-endnutzer)
- [Schritte: Kontextmodus ändern](#schritte-kontextmodus-ändern)
- [Wann **off**?](#wann-off)
- [Wann **semantic**?](#wann-semantic)
- [Wann **neutral**?](#wann-neutral)
- [Kontextleiste im Chat (ohne Einstellungen zu ändern)](#kontextleiste-im-chat-ohne-einstellungen-zu-ändern)
- [Varianten](#varianten)
- [Fehlerfälle](#fehlerfälle)
- [Tipps](#tipps)

**Beteiligte Module**

- [Context / Chat-Kontext](../modules/context/README.md) · [Settings](../modules/settings/README.md) · [Chat](../modules/chat/README.md)

**Siehe auch**

- [Feature: Context](../../docs/FEATURES/context.md) · [Benutzerhandbuch – Kontext](../../docs/USER_GUIDE.md#3-kontextmodi-verstehen) · [Hilfe: Chat-Kontext](../../help/settings/settings_chat_context.md)

Zuerst die Begriffe in verständlicher Form, danach die konkreten Klicks in den Einstellungen und Hinweise zu **off** vs. eingeschaltetem Kontext.

## Ziel

Sie entscheiden, ob das Modell **Projekt- und Chat-Bezug** als zusätzlichen Systemtext bekommt und in welcher **Darstellungsform** — oder ob dieser Teil **abgeschaltet** ist.

## Voraussetzungen

1. Anwendung gestartet.
2. Sie können **Einstellungen** öffnen (Sidebar **Settings**).
3. Optional: Sie nutzen **Operations → Chat**, um die **Kontextleiste** über der Konversation zu sehen (Projekt, Chat, Topic).

## Begriffe in drei Stufen (für Endnutzer)

Die App speichert einen **Chat-Kontext-Modus** (`chat_context_mode`). In der Oberfläche stellen Sie ihn unter **Einstellungen → Advanced** im Feld **„Chat-Kontext-Modus“** ein (`AdvancedSettingsPanel` — Auswahlliste mit **neutral**, **semantic**, **off**).

| Einstellung | Was es für Sie bedeutet |
|-------------|-------------------------|
| **off** | Es wird **kein** strukturierter Hintergrund aus Projekt/Chat/Topic in den Prompt eingefügt. Das Modell arbeitet nur mit dem, was in den Nachrichten (und ggf. RAG, Prompts, Agenten-Systemtext) steht. |
| **neutral** | Strukturierter Hintergrund wird **knapp/sachlich** formuliert mitgegeben. |
| **semantic** | Strukturierter Hintergrund wird **ausführlicher** formuliert mitgegeben. |

**Hinweis:** Weitere Schalter wie **Detailstufe** (minimal / standard / full) und **welche Felder** (Projekt/Chat/Topic) einfließen, existieren in der Konfiguration (`AppSettings`), sind in den **Einstellungs-Panels** aber **nicht** jedes Mal als eigene Felder sichtbar — nur dieser **Modus** ist dort direkt gebunden. Wenn sich etwas „nicht wie erwartet“ verhält, kann eine **andere Regel** in der App Vorrang haben (z. B. Profil oder Policy); das klärt der Support mit den Debug-Ansichten.

## Schritte: Kontextmodus ändern

1. Sidebar: **Settings** (Einstellungen) anklicken.
2. Links die Kategorie **Advanced** wählen (nicht Appearance, nicht AI / Models).
3. Im Formular **„Chat-Kontext-Modus:“** die Liste öffnen.
4. **off**, **neutral** oder **semantic** wählen.
5. Die App speichert typischerweise **automatisch** beim Wechsel (an `AppSettings` gebunden).

## Wann **off**?

Wählen Sie **off**, wenn:

- Sie **allgemeine** Fragen stellen, die **nicht** vom aktuellen Projekt oder Chat-Titel abhängen sollen.
- Sie vermeiden wollen, dass **interne Namen** (Projekt, Titel) das Modell in eine Richtung lenken.
- Sie testen wollen, ob Antworten ohne diesen Zusatztext **neutraler** werden.

**Konsequenz:** Die **Kontextleiste** im Chat kann weiter Projekt/Chat anzeigen — das ist nur **Anzeige**. Der Modus **off** bedeutet: dieser Block wird **nicht** als strukturierter Systemkontext injiziert.

## Wann **semantic**?

Wählen Sie **semantic**, wenn:

- Das Modell **Projekt- und Chatbezug** nutzen soll, um Antworten **passender** zu formulieren (z. B. „in diesem Repo“, „zu diesem Chat“).
- Sie die **ausführlichere** Darstellungsvariante wollen (gegenüber **neutral**).

**Standard** in der Konfiguration ist **semantic**, falls nichts anderes gesetzt war (`AppSettings.load`).

## Wann **neutral**?

Wählen Sie **neutral**, wenn:

- Sie Hintergrund **mitgeben** wollen, aber die **kürzere/sachlichere** Formulierung bevorzugen (z. B. weniger erklärender Text im Systemblock).

## Kontextleiste im Chat (ohne Einstellungen zu ändern)

1. **Operations → Chat** öffnen.
2. Über der Konversation: Anzeige **Projekt**, **Chat**, ggf. **Topic**.
3. **Klicks** auf diese Einträge: dienen der **Navigation/Umbenennung** je nach Implementierung — **nicht** dem Umschalten von **off/neutral/semantic** (das bleibt unter **Advanced**).

## Varianten

| Situation | Empfehlung (fachlich) |
|-----------|------------------------|
| Support-Mail formulieren, ohne Projektbezug | **off** |
| Feature in genau diesem Projekt besprechen | **semantic** (oder **neutral**) |
| Datenschutz: keine Projektnamen ins Modell | **off** |
| Vergleich: gleiche Frage mit/ohne Kontext | Erst **off**, dann **semantic** testen |

## Fehlerfälle

| Symptom | Ursache (aus Nutzersicht) | Was Sie tun |
|---------|---------------------------|-------------|
| Modell „ignoriert“ das Projekt | Modus **off** aktiv | Unter **Advanced** auf **semantic** oder **neutral** stellen. |
| Modell halluziniert Projektbezug | Trotz **off** kommen noch **RAG** oder **lange Chat-Historie** — das ist ein anderer Mechanismus | RAG in Einstellungen prüfen; kürzeren Chat wählen. |
| Änderung wirkt nicht | Eine **höherpriore** Regel in der App überschreibt die manuelle Einstellung | Support/Admin mit **Kontext-Inspection** (`context_debug_enabled` unter Advanced) klären lassen. |
| Nur **eine** Stelle zum Umstellen gefunden | **Richtig** — nur **Chat-Kontext-Modus** ist dort an die GUI angebunden | Detailstufe/Includes ggf. nur über Admin/Support änderbar. |

## Tipps

- Nach dem Umstellen des Modus **eine neue kurze Frage** stellen, um den Effekt zu prüfen — alte Antworten ändern sich nicht rückwirkend.
- **Kontext-Inspection aktivieren** (Checkbox unter **Advanced**) nur, wenn Ihre Organisation das erlaubt — für Diagnose, nicht für den Alltag nötig.
