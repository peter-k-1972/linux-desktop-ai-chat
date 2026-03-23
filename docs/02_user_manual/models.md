# Modelle und Provider

## Übersicht

Das System unterstützt **lokale** (Ollama) und **Cloud**-Modelle. Der **ModelOrchestrator** aggregiert beide Provider und wählt je nach Konfiguration das passende Modell.

## Modell-Rollen

| Rolle | Beschreibung | Standard-Modell |
|-------|--------------|-----------------|
| FAST | Schnelle Antworten, Brainstorming | mistral:latest |
| DEFAULT | Allround, Standard | qwen2.5:latest |
| CHAT | Natürliches Gespräch | llama3:latest |
| THINK | Analyse, komplexe Aufgaben | gpt-oss:latest |
| CODE | Code, Debugging | qwen2.5-coder:7b |
| VISION | Multimodal, Bildanalyse | qwen3-vl |
| OVERKILL | Cloud-Eskalation | gpt-oss:120b |
| RESEARCH | Research Agent | gpt-oss:latest |

## Modell-Router

Der `model_router.route_prompt()` analysiert den Prompt-Text und wählt eine Rolle:

- Keywords wie „debug“, „code“ → CODE
- „analysiere“, „strukturiere“ → THINK
- „schnell“, „kurz“ → FAST
- etc.

## Auto-Routing

Wenn **Auto-Routing** aktiv ist, wird die Rolle automatisch aus dem Prompt abgeleitet. Sonst gilt die manuell gewählte Rolle im Header.

## Cloud-Eskalation

- **Cloud-Checkbox**: Erlaubt Cloud-Modelle (OLLAMA_API_KEY erforderlich)
- **Eskalieren-Button**: Erneuter Versuch mit stärkerem Modell (OVERKILL)
- **cloud_via_local**: Cloud-Anfragen über lokale Ollama-Instanz routen

## Provider

- **LocalOllamaProvider**: Direkte Ollama-API (localhost)
- **CloudOllamaProvider**: Ollama Cloud API mit API-Key

## Verbrauch, Quotas und lokale Artefakte

- **Usage-Tracking:** Produktive Aufrufe können in der SQLite-Datenbank protokolliert werden (Ledger + Aggregationen nach Stunde/Tag/Woche/Monat/gesamt). Schalter in den Einstellungen: `model_usage_tracking_enabled`.
- **Quotas:** Im Control Center → Workspace **Models** lassen sich Richtlinien pflegen (Warnung oder harte Blockade, Grenzen pro Zeitfenster). Offline ist standardmäßig keine Limit-Policy aktiv; zusätzliche Regeln gelten auch für lokale Nutzung, wenn sie den Kontext treffen.
- **Unterscheidung Fehlerarten:** Ein **Limit-Block** verhindert den Provider-Aufruf; ein **Providerfehler** entsteht nach dem Aufruf – beides wird in der UI unterschiedlich zum erfolgreichen Lauf dargestellt.
- **Lokale Modelldateien:** Registrierte Verzeichnisse (z. B. **`~/ai`**) können gescannt werden; Ergebnisse erscheinen als **Assets** in der Datenbank. Der Scan verschiebt oder löscht keine Dateien. Zuordnungen zu Registry-Modellen sind heuristisch und können fehlen (**unassigned**).

Ausführliche QA- und Risikoübersicht: [`MODEL_USAGE_PHASE_E_QA_REPORT.md`](../MODEL_USAGE_PHASE_E_QA_REPORT.md).
