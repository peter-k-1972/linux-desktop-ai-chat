# ModelsWorkspace & ProvidersWorkspace – Implementierung

## Übersicht

ModelsWorkspace und ProvidersWorkspace im Control Center sind produktiv nutzbar und an Ollama angebunden.

## Geänderte / neue Dateien

| Datei | Änderung |
|-------|----------|
| `app/gui/chat_backend.py` | `get_models_full()`, `get_default_model()`, `set_default_model()` ergänzt |
| `app/gui/domains/control_center/panels/models_panels.py` | Echte Daten, Signale, Refresh |
| `app/gui/domains/control_center/panels/providers_panels.py` | Echte Ollama-Daten, ProviderSummaryPanel |
| `app/gui/domains/control_center/workspaces/models_workspace.py` | Async-Load, Set Default, Inspector |
| `app/gui/domains/control_center/workspaces/providers_workspace.py` | Async-Load, Inspector |

## Wichtige Klassen

### ModelsWorkspace
- Lädt Modelle asynchron über `ChatBackend.get_models_full()`
- Zeigt Modellliste, Status, Details, Aktionen
- „Als Standard setzen“ speichert in `AppSettings.model`
- Inspector zeigt Modellname, Status, Größe, Typ

### ProvidersWorkspace
- Lädt Ollama-Status über `ChatBackend.get_ollama_status()`
- Zeigt Provider (Ollama), Endpoint, Online/Offline
- Inspector zeigt Provider, Endpoint, Verfügbarkeit

### ModelListPanel
- `set_models(models)` – Modellliste mit Name, Provider, Größe, Status
- `model_selected` – Signal bei Auswahl
- `refresh_requested` – Signal bei Aktualisieren

### ProviderListPanel
- `set_providers(providers)` – Provider-Liste
- `provider_selected` – Signal bei Auswahl
- `refresh_requested` – Signal bei Aktualisieren

## Daten- und Signalflüsse

### Models
1. `QTimer.singleShot(0, _defer_load)` → `asyncio.create_task(_load_models())`
2. `get_chat_backend().get_models_full()` → Modellliste
3. `get_chat_backend().get_default_model()` → aktuelles Standardmodell
4. `model_selected` → Summary, Action, Inspector
5. `set_default_requested` → `get_chat_backend().set_default_model()` → `AppSettings.save()`

### Providers
1. `QTimer.singleShot(0, _defer_load)` → `asyncio.create_task(_load_providers())`
2. `get_chat_backend().get_ollama_status()` → online, version, model_count, base_url
3. `provider_selected` → Summary, Inspector

## Fehlerbehandlung

- Keine Modelle: „Keine Modelle – ist Ollama gestartet?“
- Ollama offline: Status „Offline“, Inspector mit „Ollama nicht erreichbar“
- Fehler beim Laden: rote Fehlermeldung im Status-Label
- Keine stillen Fehler, keine Tracebacks in der GUI

## Startanweisung

```bash
# Mit aktivem venv
python run_gui_shell.py

# Oder
python main.py
```

1. Control Center in der Sidebar öffnen
2. **Models** – Modellliste laden, Modell auswählen, „Als Standard setzen“
3. **Providers** – Ollama-Status prüfen, Provider auswählen

Das Standardmodell wird in den App-Settings gespeichert und vom Chat-Workspace beim nächsten Modell-Load verwendet.
