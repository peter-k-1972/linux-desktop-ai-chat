# Prompts

## Verwandte Themen

- [Chat](../chat/README.md) · [Settings](../settings/README.md) · [GUI](../gui/README.md)  
- [Feature: Prompts](../../../docs/FEATURES/prompts.md) · [Hilfe: Prompt Studio](../../../help/operations/prompt_studio_overview.md)

## 1. Fachsicht

**Prompts** sind **wiederverwendbare Textbausteine** (Vorlagen), verwaltet über das Paket **`app/prompts/`** mit Repository und Speicher-Backends. Die Hauptoberfläche ist **Operations → Prompt Studio** (`PromptStudioWorkspace`). Speicherort und Löschverhalten steuern **`AppSettings`**: `prompt_storage_type` (`database` oder Verzeichnis), `prompt_directory`, `prompt_confirm_delete`.

## 2. Rollenmatrix

| Rolle | Nutzung |
|-------|---------|
| **Fachanwender** | Prompt Studio: anlegen, bearbeiten, auf Chat anwenden. |
| **Admin** | Schreibrechte auf `prompt_directory`; SQLite-Datei `chat_history.db` bei DB-Modus. |
| **Entwickler** | `prompt_service.py`, `prompt_repository.py`, `storage_backend.py`, `prompt_models.py`. |
| **Business** | Standardantworten und Arbeitsvorlagen. |

## 3. Prozesssicht

```
GUI: PromptStudioWorkspace
        │
        ▼
PromptService (app/prompts/prompt_service.py)
        │
        ▼
PromptRepository + StorageBackend
  (database vs. directory laut AppSettings)
        │
        ▼
Persistenz (SQLite oder Dateisystem)
```

**Service-Registrierung:** Name `prompts` in der Infrastruktur (`docs/SYSTEM_MAP.md`).

## 4. Interaktionssicht

**UI**

- Workspace-ID: **`operations_prompt_studio`** (`operations_screen.py`)
- Datei: `app/gui/domains/operations/prompt_studio/prompt_studio_workspace.py`
- Inspector: `app/gui/inspector/` (kontextbezogen für Prompt Studio, siehe `docs/00_map_of_the_system.md`)

**Settings**

- `prompt_storage_type`, `prompt_directory`, `prompt_confirm_delete` — `app/core/config/settings.py`

**Integration Chat**

- Beide Workspaces liegen unter `app/gui/domains/operations/` (`ChatWorkspace`, `PromptStudioWorkspace`); die konkrete Kopplung (Signale/Methoden) steht in diesen Modulen und zugehörigen Panels.

## 5. Fehler- / Eskalationssicht

| Problem | Ursache |
|---------|---------|
| Speichern fehlgeschlagen | Backend-Fehler, Pfad nicht beschreibbar, DB gesperrt. |
| Prompts „weg“ nach Umstellung | Wechsel `prompt_storage_type`/`prompt_directory` ohne Migration. |
| Leere Liste | Falsches Verzeichnis oder leere Datenbank. |

## 6. Wissenssicht

| Begriff | Ort |
|---------|-----|
| `PromptStudioWorkspace` | `app/gui/domains/operations/prompt_studio/` |
| `operations_prompt_studio` | Workspace-ID |
| `PromptRepository` | `app/prompts/prompt_repository.py` |
| `StorageBackend` | `app/prompts/storage_backend.py` |

## 7. Perspektivwechsel

| Perspektive | Fokus |
|-------------|--------|
| **User** | Prompt Studio, Anwendung im Chat. |
| **Admin** | Speicherort, Backups. |
| **Dev** | Kontrakttests Prompts unter `tests/contracts/`, Integration `tests/integration/test_chat_prompt_integration.py`. |
