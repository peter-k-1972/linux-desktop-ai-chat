---
id: cc_models
title: Models
category: control_center
tags: [models, ollama, cloud]
workspace: cc_models
order: 15
related: [settings_overview]
---

# Models

Im Workspace **Models** listen Sie verfügbare Sprachmodelle (lokal und über Ollama Cloud) und steuern Zuordnungen, die der Chat und andere Bereiche nutzen. Ergänzend zu **Settings → AI / Models** bietet dieses Panel die Control-Center-Sicht inkl. Status; Navigation zu weiteren Einstellungen: [Einstellungen](settings_overview).

## Verbrauch und Quotas

- Jeder produktive Modellaufruf kann in der Datenbank als **Usage-Eintrag** (Ledger) landen, sofern das Tracking in den Einstellungen nicht deaktiviert ist (`model_usage_tracking_enabled`).
- **Aggregationen** (Stunde, Tag, Woche, Monat, gesamt) werden aus dem Ledger fortgeschrieben und im Control Center u. a. bei Modell-Details und Provider-Summen angezeigt.
- **Quota-Richtlinien** (Tab „Quota-Richtlinien“ im gleichen Workspace) begrenzen oder warnen vor Überschreitung. **Offline** (lokaler Ollama-Pfad) gilt standardmäßig **kein** Limit über die eingebaute Standard-Policy; zusätzliche Policies können Limits setzen – analog zu Online, sofern sie auf den Kontext passen (z. B. global, modellbezogen, API-Key-Fingerprint für Cloud).
- **Online-Limits** in der App sind **konfigurierte** Obergrenzen; sie ersetzen keine automatische Synchronisation mit externen Provider-Kontingenten.

## Blockierung, Warnung und technischer Fehler (Chat)

Die Laufzeit unterscheidet fachlich:

| Situation | Typische Anzeige / Semantik |
|-----------|----------------------------|
| **Quota / Limit** | Anfrage wird **nicht** an den Provider geschickt; Hinweis auf Limit (**Block**). |
| **Warnschwelle** | Anfrage läuft; Hinweis (**Warnung**), z. B. nahe an einem Limit. |
| **Providerfehler** | Anfrage schlägt fehl; **kein** erfolgreicher Verbrauch – von einem Limit-Block zu trennen (**Fehler**). |
| **Konfiguration** (z. B. fehlender Cloud-API-Key) | **Fehler** mit Konfigurationsbezug, nicht als erfolgreiche Nutzung gezählt. |
| **Abbruch** (Cancel) | kann einen abgebrochenen Usage-Eintrag erzeugen; unterscheidet sich von „erfolgreich abgeschlossen“. |

Exakte Tokenzahlen stammen aus der Provider-Antwort, wenn vorhanden; sonst kann das System **schätzen** (`estimated` vs. exakt) – die UI weist auf geschätzte Anteile hin, wo Daten vorliegen.

## Lokale Speicherorte und `~/ai/`

- Unter **Lokale Speicherorte & Assets** können registrierte **Storage Roots** und gefundene **ModelAsset**-Einträge angezeigt werden.
- **Speicherorte scannen** führt die Synchronisation mit dem Dateisystem aus (kein Dateimanager): fehlende Dateien werden als **nicht verfügbar** markiert, ohne Dateien zu löschen oder zu verschieben.
- Standardmäßig kann ein Root für **`~/ai`** angelegt werden, sofern noch keiner existiert (Home-Pfad wird aufgelöst). Zuordnungen Modell ↔ Datei erfolgen **heuristisch**; unklare Treffer bleiben **ohne Modell-Zuordnung** sichtbar.
- Dateien werden **registriert** (Inventar in der Datenbank), nicht zwingend physisch importiert oder kopiert.
- Fehlen Tabellen wie `model_storage_roots` (Migration noch nicht ausgeführt), erscheinen **Registry- und Ollama-Modelle trotzdem** in der Liste; nur die **lokalen Asset-Zeilen aus `~/ai`** entfallen bis die Datenbank migriert ist.

## Modellliste im Control Center und in der Chat-Auswahl

Die App führt **Registry-Einträge**, **Ollama-installierte Modelle**, optional **Cloud-Modelle** (wenn API-Key und Eskalation passen) und **lokale Gewichts-Assets** (z. B. GGUF/SafeTensors aus registrierten Roots wie `~/ai`) in **einer gemeinsamen Katalogquelle** zusammen.

- **Auswählbar im Chat** sind nur Einträge, für die eine **Runtime** existiert (typisch: Modell in Ollama geladen bzw. Cloud erreichbar). Registry- oder Cloud-Einträge ohne erreichbare Runtime erscheinen mit Hinweis, sind aber nicht für den Chat wählbar.
- **Nur registrierte Datei, kein zugeordnetes Chat-Modell**: erscheint als Zeile mit Präfix **`local-asset:`** und interner Asset-ID. Status **„Chat: nein (nur Anzeige)“** – sichtbar in der Modellliste und im Inspector, **kein** „Als Standard“ und keine Chat-Nutzung, bis ein Modell zugeordnet und in Ollama verfügbar ist.
- **Zugeordnetes Asset ohne Ollama**: sichtbar mit Hinweis **„lokale Datei, nicht in Ollama“**; ebenfalls nicht chat-auswählbar, bis die Runtime passt.
- **Fehlende Datei** (`is_available` false): weiter in der Liste, mit **„Datei fehlt“**; nicht als lauffähig behandeln.

Kurzinfos (Provider, Routing, Chat ja/nein) stehen in der Tabelle; **Verbrauch, Quotas und Policy** erscheinen im Inspector und in den **Tooltips** der Modell-Combos (Chat, Einstellungen), sofern die Datenbank die Aggregationen liefert. Im Chat zeigt die **Statuszeile** neben der Modellwahl eine kompakte Usage-/Quota-Zeile zum aktuell gewählten Modell. Bei reinen `local-asset:`-Zeilen entfallen Chat-Bundles bewusst; stattdessen Hinweise zu Registrierung, Pfad und Asset-Typ.

Technische QA und Grenzen: [`docs/MODEL_USAGE_PHASE_E_QA_REPORT.md`](../../docs/MODEL_USAGE_PHASE_E_QA_REPORT.md).
