# Feature: Prompts

## Inhalt

- [Zweck](#zweck)
- [Funktionsweise](#funktionsweise)
- [Konfiguration](#konfiguration)
- [Beispiel](#beispiel)
- [Typische Fehler](#typische-fehler)

**Siehe auch**

- [Feature: Chat](chat.md) · [Feature: Settings](settings.md) · [Feature: Workflows](workflows.md)  
- [Benutzerhandbuch – Prompts](../USER_GUIDE.md#2-prompts-nutzen)

**Typische Nutzung**

- [Prompt Studio (Hilfe)](../../help/operations/prompt_studio_overview.md) · [Prompt-Einstellungen](../../help/settings/settings_prompts.md)

## Zweck

Wiederverwendbare Prompt-Vorlagen verwalten und im **Chat** oder im **Workflow-Editor** nutzen (Knoten `prompt_build` mit `prompt_id`; siehe [Feature: Workflows](workflows.md)).

Prompts sind Kurztexte oder strukturierte Vorlagen, die Sie nicht bei jeder Anfrage neu tippen möchten — etwa feste Systemanweisungen, wiederkehrende Arbeitsaufträge oder Bausteine mit Platzhaltern. Sie werden je nach `prompt_storage_type` in der Datenbank oder als Dateien im konfigurierten Verzeichnis gehalten und über Prompt Studio sowie Chat-Anbindungen wiederverwendet.

## Funktionsweise

- **Paket:** `app/prompts/` – Speicherung, Zugriff aus Services.  
- **Service:** über `prompts` / Topic-Service in der Infrastruktur (`app/services/`).  
- **UI:** Operations → **Prompt Studio** (`prompt_studio_workspace.py`).  
- **Integration Chat:** Prompts können auf den Composer angewendet werden (Workspace-spezifische Aktionen).

**Typischer Ablauf:** Vorlage in Prompt Studio pflegen → im laufenden Chat über das Prompt-Panel in die Eingabe übernehmen oder als Systemnachricht anwenden → Nachricht wie gewohnt senden. Der Unterschied zur Slash-Rolle (`/think` usw.) ist: Prompts sind **Ihre** gespeicherten Texte; Slash-Commands schalten vordefinierte Rollen oder Routing für die nächste Zeile.

## Konfiguration

| Schlüssel (`AppSettings`) | Bedeutung |
|---------------------------|-----------|
| `prompt_storage_type` | `database` oder Verzeichnis |
| `prompt_directory` | Pfad bei Directory-Modus |
| `prompt_confirm_delete` | Löschdialog an/aus |

## Beispiel

**Beispiel** — Vorlage anlegen und nutzen:

1. Prompt Studio → neuen Prompt anlegen, speichern.  
2. Im Chat oder Studio: Prompt auswählen und in die Eingabe übernehmen (je nach UI-Button).

## Typische Fehler

| Problem | Ursache |
|---------|---------|
| Speichern fehlgeschlagen | SQLite-Datei gesperrt oder Directory nicht beschreibbar |
| Prompts fehlen nach Wechsel | `prompt_storage_type` oder `prompt_directory` geändert ohne Migration |
| Alter Inhalt sichtbar | Cache/Liste nicht aktualisiert – Workspace neu laden |
