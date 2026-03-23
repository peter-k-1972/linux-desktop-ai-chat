# Providers

## Verwandte Themen

- [Chat](../chat/README.md) · [Settings](../settings/README.md) · [GUI](../gui/README.md)  
- [Feature: Provider](../../../docs/FEATURES/providers.md) · [Architektur – Provider](../../../docs/ARCHITECTURE.md#43-provider)

## 1. Fachsicht

**Provider** kapseln die **HTTP-Anbindung an Ollama** für Chat-Completions: lokal (Standardhost) und optional **Cloud** mit API-Key. Die GUI zeigt Status und Endpunkt im **Control Center → Providers**; die Auswahl des konkreten Provider-Pfads erfolgt über Modell-/Chat-Services und Orchestrator, nicht durch direkte UI→Provider-Kopplung.

**Code-Paket:** `app/providers/`

## 2. Rollenmatrix

| Rolle | Nutzung |
|-------|---------|
| **Fachanwender** | Sieht Online/Offline und Provider-Infos im Workspace `cc_providers`. |
| **Admin** | Ollama-Dienst, Firewall, `ollama_api_key`, Flags `cloud_escalation`, `cloud_via_local` in `AppSettings`. |
| **Entwickler** | `base_provider.py`, `local_ollama_provider.py`, `cloud_ollama_provider.py`, `ollama_client.py`. |
| **Business** | „Anbindung ans Modell-Backend“. |

## 3. Prozesssicht

```
ChatService / Orchestrator
        │
        ▼
BaseProvider-Implementierung
  ├── LocalOllamaProvider  (app/providers/local_ollama_provider.py)
  └── CloudOllamaProvider (app/providers/cloud_ollama_provider.py)
        │
        ▼
Ollama HTTP (ollama_client.py)
        │
        ▼
Modellantwort (Stream oder komplett) → ChatService → GUI
```

## 4. Interaktionssicht

**UI**

- `app/gui/domains/control_center/workspaces/providers_workspace.py`
- Panels unter `app/gui/domains/control_center/panels/providers_panels.py`
- Workspace-ID: **`cc_providers`** (`control_center_screen.py`)

**Services**

- `app/services/provider_service.py` (in `docs/SYSTEM_MAP.md` als Service aufgeführt)
- Nutzung aus Chat-/Model-Pfad (`app/services/chat_service.py`, Model-Orchestrierung)

**Konfiguration (`AppSettings`)**

- `cloud_escalation`, `cloud_via_local`, `ollama_api_key` u. a.

## 5. Fehler- / Eskalationssicht

| Problem | Ursache |
|---------|---------|
| Offline-Status | `ollama serve` nicht aktiv oder falscher Port. |
| Cloud ohne Antwort | `ollama_api_key` leer/ungültig oder `cloud_escalation` aus. |
| Timeout | Netzwerk, großes Modell; siehe Tests unter `tests/chaos/`, `tests/integration/`. |

## 6. Wissenssicht

| Begriff | Datei |
|---------|--------|
| `BaseProvider` | `app/providers/base_provider.py` |
| `LocalOllamaProvider` | `app/providers/local_ollama_provider.py` |
| `CloudOllamaProvider` | `app/providers/cloud_ollama_provider.py` |
| `Ollama`-Client | `app/providers/ollama_client.py` |
| `cc_providers` | Workspace-ID in `control_center_screen.py` |

## 7. Perspektivwechsel

| Perspektive | Fokus |
|-------------|--------|
| **User** | Providers-Workspace: Refresh, Status. |
| **Admin** | Endpoint, Keys, Erreichbarkeit. |
| **Dev** | Fehlerbehandlung im Client, Aggregation im Orchestrator. |
