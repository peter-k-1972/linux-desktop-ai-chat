# Feature: Provider (Ollama)

## Inhalt

- [Zweck](#zweck)
- [Funktionsweise](#funktionsweise)
- [Konfiguration](#konfiguration)
- [Beispiel](#beispiel)
- [Typische Fehler](#typische-fehler)

**Siehe auch**

- [Feature: Chat](chat.md) · [Architektur – Provider](../ARCHITECTURE.md#43-provider)  
- [Hilfe: Providers](../../help/control_center/cc_providers.md) · [Models](../../help/control_center/cc_models.md)

**Typische Nutzung**

- [Einstellungen (Routing, Cloud)](../../docs_manual/workflows/settings_usage.md) — ergänzend zu Control Center

## Zweck

Ausführung von Chat-Completions gegen Ollama – lokal oder in der Cloud – über eine gemeinsame Provider-Schnittstelle.

Die Chat- und Modellpfade sprechen nicht direkt beliebige HTTP-Endpunkte an, sondern gehen über Provider-Implementierungen, die Requests formatieren und Antworten (inkl. Streaming) zurück in die App übersetzen. So bleibt die Ollama-spezifische Logik an einer Stelle; Routing-Entscheidungen (welches Modell, ob Cloud) liegen bei Orchestrator und Einstellungen.

## Funktionsweise

- **`app/providers/base_provider.py`** – abstrakte Basis.  
- **`local_ollama_provider.py`** – lokaler Endpoint (Standard localhost).  
- **`cloud_ollama_provider.py`** – Cloud-Ollama mit API-Key (`ollama_api_key` in `AppSettings`).  
- **`ollama_client.py`** – HTTP-Schicht.  
- **Orchestrierung:** erfolgt über Model-/Chat-Services und Router (`app/model_orchestrator.py`, `model_router.py`, `services/` – je nach Aufrufpfad).  
- **UI:** Control Center → **Providers** (`providers_workspace.py`, Panels in `gui/domains/control_center/panels/`).

## Konfiguration

| Schlüssel / Aspekt | Bedeutung |
|--------------------|-----------|
| `cloud_escalation` | Cloud-Modelle erlauben |
| `cloud_via_local` | Cloud über lokale Ollama-Installation |
| `ollama_api_key` | Authentifizierung Cloud |

Endpoint und Erreichbarkeit werden zur Laufzeit abgefragt (Status im Providers-Workspace).

**Datenfluss (vereinfacht):** Nach Aufbereitung der Messages im `ChatService` entscheidet die Modell-/Routing-Schicht, welcher Provider zum Zug kommt; dieser nutzt `ollama_client` für die eigentliche HTTP-Kommunikation. Schlägt die Verbindung fehl oder bleibt der Status „offline“, liegt die Ursache typischerweise vor dieser Schicht (Dienst, Netz, Schlüssel).

## Beispiel

**Beispiel** — Lokaler Betrieb:

1. Ollama lokal starten: `ollama serve`.  
2. Control Center → Providers → Status **online** prüfen.  
3. Chat starten – Anfrage läuft über den gewählten Provider-Pfad.

## Typische Fehler

| Problem | Ursache |
|---------|---------|
| Offline-Status | Dienst nicht gestartet, falscher Port, Firewall |
| Cloud ohne Modelle | API-Key fehlt oder `cloud_escalation` aus |
| Timeout | Netzwerk oder großes Modell; siehe Chaos-/Integrationstests unter `tests/` |
