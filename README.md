# Linux Desktop Chat

Lokale Desktop-Anwendung (PySide6) für Chat mit Sprachmodellen, RAG, Agenten, Prompt-Verwaltung und QA-orientierten Werkzeugen. Anbindung an **Ollama** (lokal und optional Cloud).

## Inhalt

- [Projektüberblick](#linux-desktop-chat)
- [Architektur (Kurz)](#architektur-kurz)
- [Paket- und Repo-Landkarte](#paket--und-repo-landkarte)
- [Features](#features)
- [Quickstart](#quickstart)
- [Bedienoberfläche (textuell)](#bedienoberfläche-textuell)
- [Dokumentation im Repo](#dokumentation-im-repo)
- [Tests](#tests)

**Siehe auch**

- [Architektur](docs/ARCHITECTURE.md) — Schichten, Datenfluss, Kontext/Settings/Provider  
- [Benutzerhandbuch](docs/USER_GUIDE.md)  
- [Entwicklerhandbuch](docs/DEVELOPER_GUIDE.md)  
- [Dokumentations-Index (`docs/`)](docs/README.md)  
- [Systemkarte](docs/00_map_of_the_system.md)  
- [Kernfeatures](docs/FEATURES/)  
- [In-App-Hilfe (Artikelindex)](help/README.md)

Die folgende Tabelle fasst die wichtigsten Schichten im Code zusammen und dient der schnellen Orientierung; vertiefende Darstellung und Datenflüsse stehen in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Architektur (Kurz)

| Schicht | Rolle |
|---------|--------|
| **GUI** (`app/gui/`) | Shell, Navigation, Domains (Operations, Control Center, Settings, QA, Runtime Debug), Workspaces, Inspector |
| **Services** (`app/services/`) | Orchestrierung: Chat, Modelle, Provider, RAG, Projekte, Agenten, Prompts, QA-Adapter |
| **Context** (`app/chat/`, `app/context/`) | Kontextfragmente für Prompts, Limits, Replay/Repro, Erklärbarkeit |
| **Settings** (`app/core/config/`) | `AppSettings` + Backend (persistiert u. a. über Qt); keine Kontext-Render-Logik |
| **Provider** (`app/providers/`) | HTTP-Clients zu Ollama (lokal / Cloud) |
| **LLM** (`app/llm/`) | Completion, Ausgabe-Pipeline |
| **Agents** (`app/agents/`) | Profile, Tasks, Delegation |
| **RAG** (`app/rag/`) | Retrieval, ChromaDB-Anbindung |

Detailliert: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), Orientierung: [`docs/00_map_of_the_system.md`](docs/00_map_of_the_system.md).

## Paket- und Repo-Landkarte

Das Projekt wird als **eine Host-Distribution** (`linux-desktop-chat` in [`pyproject.toml`](pyproject.toml)) ausgeliefert; logische **Ziel-Segmente** (GUI, Services, Feature-Plattform, RAG, …) leben als Unterpakete von `app/`. Externe Erweiterungen sind **eigene Python-Pakete** und binden über die Entry-Point-Gruppe `linux_desktop_chat.features` — siehe Beispiel unter [`examples/plugins/ldc_plugin_example/`](examples/plugins/ldc_plugin_example/).

| Ressource | Inhalt |
|-----------|--------|
| [`docs/architecture/PACKAGE_MAP.md`](docs/architecture/PACKAGE_MAP.md) | Kanonische Übersicht: Segmente, CI/Release, Plugins, Legacy/Brücken |
| [`docs/developer/PACKAGE_GUIDE.md`](docs/developer/PACKAGE_GUIDE.md) | Kurzleitfaden für Platzierung von Code und Pflege der Landkarte |
| `app/packaging/landmarks.py` | Maschinenlesbare Landmarken für leichte Architektur-Guards |

## Features

Zentrale Produktbereiche im Überblick:

- **Chat:** Sessions, Streaming (einstellbar), Slash-Commands, Modell- und Rollenwahl  
- **Kontext:** Context Mode (`off` / `neutral` / `semantic`), Detail Level (`minimal` / `standard` / `full`), optionale **Profile**, **Overrides** über Policy/Hint-Kette  
- **RAG:** Indexierung, Abfrage, Spaces, Top-K  
- **Projekte:** unter **Operations → Projekte** zentral anlegen, bearbeiten (inkl. Standard-Kontextpolicy), löschen; die Settings-Kachel **Project** bleibt eine kompakte Lesensansicht zum aktiven Projekt  
- **Workflows:** DAG-Editor, Test-Runs, Historie; Register **Geplant** für zeitgesteuerte und manuelle Starts (Ausführung über `WorkflowService`)  
- **Deployment:** Ziele, Releases (Lifecycle **draft** / **ready** / **archived**), Rollout-Protokoll — keine automatischen externen Deployments  
- **Betrieb:** Audit-Aktivität, Incidents aus fehlgeschlagenen Workflow-Läufen, Plattform-Health-Checks  
- **Prompts:** Datenbank oder Verzeichnis  
- **Agenten:** Profile, Tasks, `/delegate`-Pfad  
- **Control Center:** Modelle, Provider, Agenten; **Tools** und **Data Stores** zeigen **Live-Snapshots** aus lokaler Konfiguration und Dateisystem (keine externe Tool-Registry)  
- **Settings:** acht Kategorien (Application … Workspace)  
- **QA / Runtime:** Governance-Workspaces, Debug-Monitore  
- **CLI (ohne UI):** Context Replay und Repro-Registry (`app/cli/`)

Feature-Tiefe: [`docs/FEATURES/`](docs/FEATURES/).

## Quickstart

Voraussetzungen: Python 3.x, virtuelle Umgebung empfohlen.

**Beispiel — virtuelle Umgebung und Abhängigkeiten**

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

(`requirements.txt` entspricht `pip install -e ".[rag,dev]"` gemäß `pyproject.toml`; siehe `docs/architecture/PEP621_OPTIONAL_DEPENDENCIES.md`.)

Ollama installieren, Dienst starten, mindestens ein Modell laden. **Beispiel — Ollama**

```bash
ollama serve
ollama pull qwen2.5
```

**Beispiel — Anwendung starten (empfohlen)**

```bash
python -m app
```

**Beispiel — alternative Startbefehle (Repository-Root)**

```bash
python main.py
python run_gui_shell.py
```

**Primäre GUI:** `python -m app`, `main.py` und `run_gui_shell.py` starten dieselbe Shell. **Legacy-GUI** (nur Wartung): `python archive/run_legacy_gui.py`.

Entwickler-Details: [`docs/DEVELOPER_GUIDE.md`](docs/DEVELOPER_GUIDE.md).  
Endnutzer: [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md), In-App-Hilfe aus `help/`.

## Bedienoberfläche (textuell)

1. **Linke Sidebar:** Bereiche z. B. Kommandozentrale (Dashboard), **Operations** (Projekte, Chat, Knowledge, Prompt Studio, Workflows inkl. **Geplant**, Deployment, Betrieb, Agent Tasks), **Control Center**, **QA & Governance**, **Runtime / Debug**, **Settings**.  
2. **Hauptbereich:** Der gewählte Screen zeigt einen oder mehrere **Workspaces** (z. B. Chat-Workspace mit Session-Liste, Konversation, Eingabe).  
3. **Inspector (rechts, kontextabhängig):** Zusatzinfos zu Session, Kontext, Prompt Studio usw.  
4. **Einstellungen:** Vollbild-Settings mit linker Kategorienliste (Application, Appearance, AI / Models, Data, Privacy, Advanced, Project, Workspace). **Project** und **Workspace** zeigen Übersicht bzw. Orientierung (keine leeren Platzhalterseiten).  

## Dokumentation im Repo

| Dokument | Inhalt |
|----------|--------|
| [`docs/README.md`](docs/README.md) | Index aller `docs/`-Bereiche |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Schichten, Datenfluss, Kernsysteme |
| [`docs/architecture/PACKAGE_MAP.md`](docs/architecture/PACKAGE_MAP.md) | Paket-Segmente, Repo-Spiegel, Brücken/Legacy, Segment-Dependency-Rules |
| [`docs/developer/PACKAGE_GUIDE.md`](docs/developer/PACKAGE_GUIDE.md) | Entwickler-Orientierung zu Paketgrenzen |
| [`docs/architecture/GIT_QA_GOVERNANCE.md`](docs/architecture/GIT_QA_GOVERNANCE.md) | QA-/Release-Aussagen mit Git-Provenance; Soft-Gates |
| [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) | Bedienung für Anwender |
| [`docs/DEVELOPER_GUIDE.md`](docs/DEVELOPER_GUIDE.md) | Setup, Struktur, CLI, Fallstricke |
| [`docs/FEATURES/`](docs/FEATURES/) | Kernfeatures im Detail |
| [`docs/CHANGELOG_NORMALIZATION.md`](docs/CHANGELOG_NORMALIZATION.md) | Doku-Normalisierung (dieser Stand) |
| [`help/`](help/) | Markdown für die In-App-Hilfe (Index: [`help/README.md`](help/README.md)) |
| [`docs/operations/`](docs/operations/) | Betrieb/Operator: Audit & Incidents, Plattform, Workflows/Runs |
| [`docs/user/deployment.md`](docs/user/deployment.md) · [`scheduling.md`](docs/user/scheduling.md) | Fachmodell Deployment und Scheduling |
| [`docs/glossary/terminology.md`](docs/glossary/terminology.md) | Kanonische Begriffe (Workflow, Run, Incident, …) |

## Tests

**Release Freeze (v0.9.0):** dokumentierte pytest-Referenz und Abnahme in [`docs/RELEASE_ACCEPTANCE_REPORT.md`](docs/RELEASE_ACCEPTANCE_REPORT.md); Messzahlen in [`FINAL_TEST_STATUS.md`](FINAL_TEST_STATUS.md).

Nach Aktivierung der venv und `pip install -r requirements.txt`:

**Beispiel — Testlauf**

```bash
pytest -q
```

`tests/conftest.py` setzt u. a. `LINUX_DESKTOP_CHAT_SKIP_DEFAULT_PROJECT=1`, damit kein automatisches Default-Projekt die isolierten DB-Tests verfälscht. Ohne venv fehlen typischerweise Pakete (z. B. `qasync`); zuerst die venv wie unter **Quickstart** einrichten. Weitere Marker und Suites: [`tests/README.md`](tests/README.md). Kurze manuelle Freigabe-Stichprobe: [`docs/RELEASE_MANUAL_CHECKLIST.md`](docs/RELEASE_MANUAL_CHECKLIST.md); Smoke-Suite: `pytest tests/smoke/ -q`.
