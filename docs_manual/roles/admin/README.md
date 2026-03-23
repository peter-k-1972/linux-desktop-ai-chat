# Admin

Handbuch für Betrieb, Konfiguration und Kontrolle der Linux-Desktop-Chat-Instanz. Schritte beziehen sich auf die implementierte GUI (`app/gui/`), Einstellungen (`AppSettings` in `app/core/config/settings.py`) und Provider unter `app/providers/`.

## Relevante Module

- [Settings](../../modules/settings/README.md) · [Provider](../../modules/providers/README.md) · [RAG](../../modules/rag/README.md) · [GUI](../../modules/gui/README.md)  
- [Agenten](../../modules/agents/README.md) (Persistenz) · [Chat](../../modules/chat/README.md) (Nutzung)

**Siehe auch:** [Entwickler-Rollenhandbuch](../entwickler/README.md) (Repository, Tests, Erweiterungspunkte).

## Aufgaben

- **Ollama** bereitstellen: Dienst laufen lassen, Modelle vorab laden (`ollama pull …`), Erreichbarkeit prüfen.
- **Einstellungen** der App überwachen: Organisation `OllamaChat` / `LinuxDesktopChat` in **QSettings** (Endnutzerdoku: `help/settings/settings_overview.md`).
- **Provider- und Modellzugriff** prüfen: **Control Center → Providers** und **Models** entsprechen `cc_providers` / `cc_models`.
- **RAG-Betrieb:** `chromadb` installiert (`requirements.txt`), Datenverzeichnis typisch `./chroma_db`; Embedding-Modell in Ollama (z. B. `nomic-embed-text`) bereitstellen; Indexierung z. B. über `scripts/index_rag.py` (siehe `help/troubleshooting/troubleshooting.md`).
- **Cloud:** `ollama_api_key`, `cloud_escalation`, `cloud_via_local` in den App-Einstellungen abstimmen.
- **Backups:** SQLite-Datei für Chat-Historie (`chat_history.db`), ChromaDB-Ordner, ggf. Prompt-Verzeichnis bei `prompt_storage_type=directory`.

## Typische Workflows

### Erreichbarkeit Ollama prüfen

1. Auf dem Zielrechner: `ollama serve` (oder Dienst-Unit).
2. Prüfen: `curl http://localhost:11434/api/tags` (oder Ihr Endpoint).
3. In der App: **Control Center → Providers** — Status **online** erwarten.
4. Wenn offline: Firewall, Port **11434**, falsche URL in der Provider-Konfiguration prüfen.

### Standardmodell und Modellliste

1. **Control Center → Models:** Liste aktualisieren; Standardmodell setzen (speichert über Backend in `AppSettings.model`, siehe Modul **providers** / **settings**).
2. Fehlende Modelle: auf dem Ollama-Host `ollama pull <name>`.

### Einstellungskategorien durchgehen (8 Stück)

Unter **Settings** die linke Navigation nutzen — IDs und Titel aus `app/gui/domains/settings/navigation.py`:

| Kategorie (UI) | ID |
|----------------|-----|
| Application | `settings_application` |
| Appearance | `settings_appearance` |
| AI / Models | `settings_ai_models` |
| Data | `settings_data` |
| Privacy | `settings_privacy` |
| Advanced | `settings_advanced` |
| Project | `settings_project` |
| Workspace | `settings_workspace` |

Im **Advanced**-Bereich: **Chat-Kontext-Modus** (`chat_context_mode`), **Kontext-Inspection** (`context_debug_enabled`), **Agent Debug Tab** (`debug_panel_enabled`) — nur für vertrauenswürdige Nutzer aktivieren.

### RAG-Space und Top-K

1. **Settings:** `rag_enabled`, `rag_space`, `rag_top_k` prüfen (`AppSettings`).
2. Index für den gewählten Space erzeugen/aktualisieren (Skript-Pfad im Troubleshooting-Artikel).
3. Bei leeren Treffern: falschen Space, leeren Index oder fehlendes Embedding-Modell ausschließen.

### Kontrolle bei Supportfällen

1. **Runtime / Debug** in der App: Logs, Metriken, **LLM Calls**, **Agent Activity** (Workspace-IDs z. B. `rd_logs`, `rd_llm_calls`, `rd_agent_activity` in `runtime_debug_screen.py`).
2. **QA & Governance** bei internem Qualitätsprozess: **Incidents**, **Replay Lab** (`qa_incidents`, `qa_replay_lab`).

## Genutzte Module

| Modul | Admin-Fokus |
|-------|-------------|
| [settings](../../modules/settings/README.md) | Acht Kategorien, alle persistierten Keys. |
| [providers](../../modules/providers/README.md) | Lokaler/Cloud-Ollama, Status-Anzeige. |
| [rag](../../modules/rag/README.md) | ChromaDB, Spaces, Index-Pipeline. |
| [gui](../../modules/gui/README.md) | Welche Screens/Workspaces für Kontrolle genutzt werden. |
| [context](../../modules/context/README.md) | Kontextmodus, Overrides — bei „falschem“ Verhalten. |
| [chains](../../modules/chains/README.md) | Prioritätskette bei Kontext-Konflikten. |

## Risiken

- **Cloud-Keys** in Klartext in QSettings: Zugriff auf Nutzerkonten / Arbeitsplatz absichern.
- **ChromaDB-Verzeichnis beschädigt:** Neuindexierung nötig; Datenverlust des Vektorstores.
- **Kontext-Inspection / Debug** für alle aktiviert: erhöhte Sichtbarkeit interner Abläufe — nur für berechtigte Personen.
- **Profile/Policy-Overrides:** Endnutzer-Änderungen an `chat_context_mode` können durch höherpriore Quellen überstimmt werden — Support muss `ChatService._resolve_context_configuration` logisch kennen (siehe Modul **context**).

## Best Practices

- Modelle und Ollama-Version dokumentieren; nach Updates Rauchtest: Chat senden, Provider grün.
- RAG: feste Spaces pro Umgebung (Entwicklung/Test/Produktion) und klare Index-Jobs.
- Backups vor Migrationen (DB + `chroma_db` + relevante Verzeichnisse).
- Für produktive Nutzer **Cloud** und **RAG**-Policies schriftlich festlegen.
