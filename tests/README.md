# Linux Desktop Chat – Testsystem

Vollständiges Testsystem für Unit-, Integration-, Live-, Smoke-, Golden-Path-, Regression- und State-Consistency-Tests.

**Aktuelle Sammlungszahl, Repro und Git-Stand:** [`FINAL_TEST_STATUS.md`](../FINAL_TEST_STATUS.md) im Projektroot (wird mit dem Repo gepflegt).

## Struktur

```
tests/
├── conftest.py              # Zentrale Fixtures (inkl. qt_event_loop)
├── TEST_AUDIT_REPORT.md     # Historisch (2025); siehe Banner — aktuell: ../FINAL_TEST_STATUS.md
├── AUDIT_MATRIX.md          # Audit-Matrix pro Kernworkflow → QA-Bauplan
├── data/                    # Testdaten
├── unit/                    # Unit Tests (isolierte Komponenten)
├── integration/             # Integration Tests (echte SQLite, ChromaDB, EventBus)
├── live/                    # Live Tests (echte Ollama, RAG, Agent)
├── ui/                      # UI Tests (pytest-qt, qasync)
│   ├── test_ui_behavior.py  # UI-Wirkung (Speichern, Löschen, Auswahl)
│   └── ...
├── smoke/                   # Smoke Tests (komplette Workflows)
├── golden_path/             # Golden-Path E2E-Tests (echte Benutzerflüsse)
│   ├── test_chat_golden_path.py
│   ├── test_prompt_golden_path.py
│   ├── test_agent_golden_path.py
│   ├── test_agent_in_chat_golden_path.py
│   ├── test_rag_golden_path.py
│   └── test_debug_panel_golden_path.py
├── regression/              # Regression-Tests (bekannte Bugs)
│   ├── README.md
│   └── test_*.py
├── state_consistency/       # State-Consistency (UI↔Service↔Repository↔Persistenz)
├── contracts/               # QA Level 2: Contract Tests (Modulverträge)
├── async_behavior/          # QA Level 2: Async/Race-Condition-Tests
├── failure_modes/           # QA Level 2: Failure-Injection-Tests
└── helpers/                 # Testdiagnostik (dump_chat_state, dump_debug_store, ...)
```

## Ausführung

```bash
# Alle Tests (ohne Live)
pytest

# Mit Verbose
pytest -v

# Nur Unit Tests
pytest tests/unit

# Nur Integration Tests (echte SQLite, ChromaDB, EventBus)
pytest tests/integration -m integration

# Nur Live Tests (Ollama, RAG, Agent – Dienste müssen laufen!)
pytest tests/live -m live

# Nur Smoke Tests
pytest tests/smoke

# Ohne langsame Tests
pytest -m "not slow"

# Alle inkl. Live (Ollama muss laufen)
pytest -m "live or integration or unit or smoke or ui"
```

## Test-Marker

| Marker         | Beschreibung |
|----------------|--------------|
| `unit`         | Unit-Tests (isolierte Komponenten) |
| `integration`  | Integration (echte SQLite, ChromaDB, EventBus) |
| `live`         | Live (echte Ollama, RAG, Agent – Dienste erforderlich) |
| `slow`         | Langsame Tests (LLM, Netzwerk) |
| `ui`           | UI-Tests (PySide6, pytest-qt) |
| `smoke`        | Smoke-Tests (komplette Workflows) |
| `golden_path`  | Golden-Path E2E (echte Benutzerflüsse) |
| `regression`   | Regression (reproduzieren bekannte Bugs) |

## Fixtures

- `test_agent` – Beispiel-Agentenprofil
- `test_prompt` – Beispiel-Prompt
- `test_document` – Beispiel-Dokument (RAG)
- `test_chunk` – Beispiel-Chunk
- `test_event` – Beispiel-AgentEvent
- `temp_db_path` – Temporäre SQLite-DB
- `agent_repository` – AgentRepository mit Temp-DB
- `temp_chroma_dir` – Temporäres ChromaDB-Verzeichnis
- **`qt_event_loop`** – Event Loop mit qasync für PySide6 (async UI-Tests)

## Integration vs. Live

- **Integration**: Echte SQLite, ChromaDB, EventBus – keine externen Dienste.
- **Live**: Echte Ollama-API, RAG-Pipeline mit Embeddings, Agent-Ausführung.  
  Live-Tests werden übersprungen, wenn Ollama nicht erreichbar ist.

## CI/CD

```bash
# Level: fast – Unit, Contract (ohne DB/Netzwerk, ~5s)
pytest -m "unit or contract" --tb=short -q

# Level: full – Alle außer Live (Standard-CI)
pytest -m "not live and not slow" --tb=short -q

# Level: live – Vollständig (Ollama muss laufen)
pytest --tb=short -q
```

### QA Level 2 – Testmarker

| Marker          | Beschreibung |
|----------------|--------------|
| `contract`     | Contract Tests (Modulverträge) |
| `async_behavior` | Async/Race-Condition-Tests |
| `failure_mode` | Failure-Injection-Tests |

## Fehleranalyse

```bash
pytest -v --tb=long
```

## Golden-Path & Regression

```bash
# Nur Golden-Path-Tests
pytest tests/golden_path -m golden_path -v

# Nur Regression-Tests
pytest tests/regression -m regression -v

# State-Consistency
pytest tests/state_consistency -v
```

## Bug-zu-Test-Workflow

1. Bug tritt auf → Test in `tests/regression/` anlegen (Test muss rot sein)
2. Fix implementieren → Test wird grün
3. Siehe `tests/regression/README.md` und `tests/TEST_AUDIT_REPORT.md`

## QA Level 2 – Berichte

- **`tests/QA_LEVEL2_REPORT.md`** – Implementierungsbericht: neue Contract-, Async- und Failure-Mode-Tests, gehärtete Tests, offene Punkte.

## Audit-Matrix & QA-Bauplan

`tests/AUDIT_MATRIX.md` enthält pro Kernworkflow (Chat, Agenten, Prompt, Debug, RAG, Startup):

- Bestehende Tests
- Echte Lücken
- Höchste Risiken
- Priorisierte neue Tests (P0/P1/P2) mit Typ (Unit/UI/Integration/Golden Path/Regression/Live)
