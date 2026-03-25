# Entwicklerhandbuch – Linux Desktop Chat

Dieses Handbuch richtet sich an Entwicklerinnen und Entwickler: Setup, relevante Verzeichnisse, Erweiterungspunkte und CLI-Werkzeuge. Endnutzer-Dokumentation liegt in [`USER_GUIDE.md`](USER_GUIDE.md); Architekturüberblick in [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Inhalt

- [1. Setup](#1-setup)
- [2. Projektstruktur (relevant)](#2-projektstruktur-relevant)
- [3. Module (Kurzreferenz)](#3-module-kurzreferenz)
- [4. Erweiterungspunkte](#4-erweiterungspunkte)
- [5. CLI – Context Replay und Repro](#5-cli--context-replay-und-repro)
- [6. Typische Fehlerquellen](#6-typische-fehlerquellen)
- [7. Dokumentations-Index](#7-dokumentations-index)

**Siehe auch**

- [Architektur](ARCHITECTURE.md) · [Paket-Landkarte](architecture/PACKAGE_MAP.md) · [Paket-Leitfaden](developer/PACKAGE_GUIDE.md) · [Dokumentations-Index](README.md) · [Systemkarte](00_map_of_the_system.md)  
- [Handbuch-Module](../docs_manual/modules/) · [Workflows](../docs_manual/workflows/)  
- [In-App-Hilfe](../help/README.md)

---

## 1. Setup

### 1.1 Voraussetzungen

- Python 3 (Version wie in eurer CI oder lokal üblich; Abhängigkeiten siehe `pyproject.toml` / `pip install -r requirements.txt`).  
- Git-Arbeitskopie des Repositories.

### 1.2 Virtuelle Umgebung und Abhängigkeiten

**Beispiel**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**PEP 621:** Es gibt ein `pyproject.toml` (`[project.dependencies]` = Basis, optional-dependencies für u. a. `rag`, `dev`). Die Datei `requirements.txt` installiert das übliche Entwickler-Äquivalent (`-e .[rag,dev]`). Details: `docs/architecture/PEP621_OPTIONAL_DEPENDENCIES.md`.

### 1.3 Ollama und RAG (optional)

- Für Live-Chat: Ollama installieren, `ollama serve`, Modell z. B. `ollama pull qwen2.5`.  
- Für RAG-Tests: `chromadb` liegt im Extra `rag` (bei Standard-Setup über `requirements.txt` mitinstalliert); Embeddings-Modell z. B. `ollama pull nomic-embed-text`.

### 1.4 Startbefehle

| Befehl | Quelle |
|--------|--------|
| `python -m app` | `app/__main__.py` → `run_gui_shell.main` |
| `python main.py` | Root-Delegator |
| `python run_gui_shell.py` | Direkter GUI-Einstieg |

Legacy-GUI liegt unter `archive/` (siehe `main.py`-Kommentar im Root).

### 1.5 Tests

Siehe [`tests/README.md`](../tests/README.md): `pytest`, Marker `unit`, `integration`, `live`, `ui`, usw.

---

## 2. Projektstruktur (relevant)

```
app/
  gui/           # PySide6 Shell, Domains, Workspaces, Settings-UI
  services/      # ChatService, KnowledgeService, ProviderService, …
  chat/          # Kontext-Rendering, Profile, Limits
  context/       # Explainability, Replay, Repro, Registry
  core/config/   # AppSettings, Enums, SettingsBackend
  core/commands/ # Slash-Commands
  providers/     # Ollama local/cloud
  llm/           # Completion-Pipeline
  agents/        # Agenten, Delegation, Planner, …
  rag/           # Retrieval, Index
  prompts/       # Prompt-Daten
  cli/           # Kopflose Tools (Replay/Repro)
  pipelines/     # Pipeline-Engine (Medien/Kreativ, generisch)
docs/            # Architektur, QA, dieses Handbuch
help/            # In-App-Hilfe (Markdown)
tests/           # pytest-Suites
tools/           # generate_system_map.py, generate_feature_registry.py, …
```

Die **kanonische GUI** liegt unter `app/gui/`. Das Verzeichnis `app/ui/` existiert im aktuellen Stand nicht; ältere Reports können noch `app/ui/` erwähnen.

**Paket-Segmente, CI/Release und Plugin-Grenzen:** [`architecture/PACKAGE_MAP.md`](architecture/PACKAGE_MAP.md); Kurzleitfaden für neue Module: [`developer/PACKAGE_GUIDE.md`](developer/PACKAGE_GUIDE.md).

---

## 3. Module (Kurzreferenz)

| Modul / Pfad | Rolle |
|--------------|--------|
| `app/gui/shell/` | Hauptfenster, Docking |
| `app/gui/workspace/` | Screen-Registry |
| `app/gui/domains/operations/chat/` | Chat-Workspace |
| `app/gui/chat_backend.py` | Brücke GUI ↔ Services (Modelle, Senden, …) |
| `app/services/chat_service.py` | Sendelogik, Kontextauflösung, Guard |
| `app/chat/context.py` | `ChatRequestContext`, Fragment-Rendering |
| `app/chat/context_profiles.py` | Profile, Hint-Mapping, Resolution-Trace-Daten |
| `app/core/config/settings.py` | `AppSettings`, alle QSettings-Keys |
| `app/providers/*.py` | Ollama-Provider |
| `app/context/replay/` | ReplayInput, Repro-Fälle, Registry |
| `app/help/help_index.py` | Lädt `help/`, Fallback `docs/*.md`, generierte Topics |

---

## 4. Erweiterungspunkte

- **Settings-Kategorie:** `register_settings_category_widget()` in `app/gui/domains/settings/settings_workspace.py`; Navigation: `register_settings_category()` in `navigation.py`.  
- **Help-Themen:** Markdown unter `help/` mit YAML-Frontmatter (`id`, `title`, `category`, optional `workspace`).  
- **Slash-Commands:** Erweiterung in `app/core/commands/chat_commands.py` (Konstanten `ROLE_COMMANDS`, Parser `parse_slash_command`).  
- **Pipelines:** Distribution `linux-desktop-chat-pipelines` (Import `app.pipelines`) — Quelle `linux-desktop-chat-pipelines/src/app/pipelines/`; siehe [`docs/architecture/PACKAGE_PIPELINES_COMMIT2_LOCAL.md`](architecture/PACKAGE_PIPELINES_COMMIT2_LOCAL.md).

---

## 5. CLI – Context Replay und Repro

Die CLI-Module laufen ohne GUI und eignen sich für Replay, Repro-Fälle und Registry-Pflege. Aufrufschema: `python -m app.cli.<modul>` vom Repository-Root mit aktivierter venv.

| Modul | Aufruf |
|-------|--------|
| `context_replay` | `python -m app.cli.context_replay <replay_input.json>` |
| `context_repro_run` | `python -m app.cli.context_repro_run <repro_case.json>` |
| `context_repro_batch` | `python -m app.cli.context_repro_batch <verzeichnis>` |
| `context_repro_registry_list` | `python -m app.cli.context_repro_registry_list <registry.json>` |
| `context_repro_registry_rebuild` | `python -m app.cli.context_repro_registry_rebuild <repro_root> <registry.json>` |
| `context_repro_registry_set_status` | `python -m app.cli.context_repro_registry_set_status <repro_root> <failure_id> <status> [<registry.json>]` |

Ausgaben sind als deterministisches JSON dokumentiert (sortierte Keys, siehe Docstrings in den CLI-Dateien).

---

## 6. Typische Fehlerquellen

| Symptom | Ursache | Prüfen |
|---------|---------|--------|
| Leeres Modell-Liste | Ollama nicht erreichbar | `ollama serve`, Endpoint, Firewall |
| Kontext „fehlt“ | Context Mode `off` oder Override-Kette | Settings, `ChatService._resolve_context_configuration` |
| Falsche Pfade in alten Docs | Migration `app/ui` → `app/gui` | Immer `app/gui/` als GUI-Quelle nutzen |
| Drift in `SYSTEM_MAP.md` | Generator nicht gelaufen | `python3 tools/generate_system_map.py` |
| Tests schlagen fehl ohne DB | SQLite-Pfade, Fixtures | `tests/conftest.py`, Kategorie `integration` |

---

## 7. Dokumentations-Index

- [`ARCHITECTURE.md`](ARCHITECTURE.md) – Schichten und Datenfluss  
- [`USER_GUIDE.md`](USER_GUIDE.md) – Endnutzer  
- [`FEATURES/`](FEATURES/) – Feature-Tiefenbeschreibung  
- [`00_map_of_the_system.md`](00_map_of_the_system.md) – Systemkarte  
- [`architecture/PACKAGE_MAP.md`](architecture/PACKAGE_MAP.md) – Paket- und Repo-Landkarte  
- [`developer/PACKAGE_GUIDE.md`](developer/PACKAGE_GUIDE.md) – Paketgrenzen und Pflege  
- [`architecture/GIT_QA_GOVERNANCE.md`](architecture/GIT_QA_GOVERNANCE.md) – Git-Provenance für QA/Release-Berichte, Soft-Gates (`app/qa/git_*.py`, `scripts/dev/print_git_qa_provenance.py`)  
- [`CHANGELOG_NORMALIZATION.md`](CHANGELOG_NORMALIZATION.md) – letzte Doku-Runde  
