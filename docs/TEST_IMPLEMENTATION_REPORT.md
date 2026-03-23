# Test-Implementierungsbericht (Nach Umsetzung)

Stand: nach Abgleich der Testlandschaft mit Prompt-Modell (`scope` / `project_id`), Infrastruktur-Snapshots, Control-Center-Remediation und Legacy-GUI/DB-Shape.

## Neu hinzugefügte Tests

| Datei | Zweck |
|-------|--------|
| `tests/unit/test_critic_review_response.py` | `review_response`: bei `enabled=False` unverändert; bei `enabled=True` Warnlog + Rückgabe des Primärtexts (async, `caplog`). |
| `tests/architecture/test_remediation_cc_agents.py` | Regression: `AgentsWorkspace` nutzt `AgentManagerPanel`; `agents_panels.py` existiert nicht; `__all__` der Control-Center-Panels ohne entfernte Agent-Panels. |
| `tests/ui/test_remediation_panels.py` | Verdrahtung: ToolRegistry-, DataStoreOverview-, SystemStatus-, QAStatus- (mit gemocktem `QADashboardAdapter`), PromptEditor/Preview-Signale. Läuft mit `qapplication` + `QApplication.processEvents()`. |
| `tests/qt_ui.py` | Hilfsfunktion `process_events_and_wait` (QTest), **ohne** Import über `tests.helpers` (vermeidet schwere Abhängigkeiten beim Modulimport). |

## Erweiterte Tests

| Datei | Ergänzungen |
|-------|-------------|
| `tests/unit/test_infrastructure_snapshot.py` | SQLite-Fehlerpfad (ungültiger URI statt beliebiger Textdatei), Chroma-Status (fehlende Basis, Index-Datei, leere Basis), Health-Summary-Farben, `probe_ollama_localhost` (Erfolg/Fehler), Tool-Snapshot mit gemockter Infrastruktur (`rag_enabled`). |

## Angepasste Tests (Modell- / Laufzeit-Kompatibilität)

| Bereich | Änderung |
|---------|-----------|
| `tests/conftest.py` | Fixture `test_prompt` mit `scope` / `project_id`. |
| `tests/unit/test_prompt_system.py` | `Prompt.empty()`-Assertions, `to_dict`, Directory-Storage: vollständiges Modell. |
| `tests/unit/test_rag.py` | VectorStore-Tests: `pytest.importorskip("chromadb")` (optionale Abhängigkeit). |
| `tests/test_prompt_repository.py`, `tests/golden_path/test_prompt_golden_path.py`, `tests/state_consistency/test_prompt_consistency.py`, `tests/cross_layer/test_prompt_apply_affects_real_request.py`, `tests/integration/test_chat_prompt_integration.py`, `tests/ui/test_chat_ui.py`, `tests/ui/test_prompt_manager_ui.py` | `Prompt`-Konstruktoren und/oder Ersetzung von `qtbot` durch `qapplication` + `tests.qt_ui.process_events_and_wait`; Composer-Sendetest nutzt `setPlainText` + `click()` statt Key/Mouse-Simulation. |

## Produktionscode-Fixes, die durch Tests sichtbar wurden

Diese Änderungen sind **keine** Test-Attrappen, sondern Korrekturen realer Laufzeitfehler:

1. **`PromptEditorWidget` in `prompt_manager_panel.py`**  
   `get_prompt()` / `load_prompt()` / `clear()` berücksichtigen jetzt `scope` und `project_id` (übernommen aus geladenem Prompt, Neu = global).

2. **Legacy-Sidebar / Explorer / Projekt-Chat-Liste**  
   `DatabaseManager.list_projects` und `list_chats_of_project` liefern **Dicts**; Widgets erwarteten Tupel. Anpassung in `sidebar_widget.py`, `file_explorer_widget.py`, `project_chat_list_widget.py` mit Rückwärtskompatibilität für Tupel.

## Abgedeckte Risiken

- **Falsche SQLite-/Ollama-/Chroma-Meldungen** in Dashboard/Control-Center-Snapshots (Infrastruktur-Layer).
- **Critic-Pfad** bei aktiviertem Review (Logging, kein stilles Verschlucken).
- **Doku-vs-Code Control-Center Agents** (kein Rückfall auf entfernte Module).
- **Prompt-CRUD und Chat-Integration** (Modellfelder, Speichern/Laden/Apply, ohne `pytest-qt`-Pflicht).
- **Legacy MainWindow** startet Sidebar ohne Crash bei Dict-Projektzeilen.

## Schwer testbar (kurz)

| Bereich | Grund |
|---------|--------|
| Voller Fenster-Workflow in neuer GUI-Shell | Hoher Aufwand, oft manuell oder mit spezieller Qt-Async-Umgebung. |
| Echte Ollama/Chroma-Prozesse | Live-Marker, Umgebung, Timing. |
| Pixel-/Layout-Regression | Kein etabliertes Screenshot-Gate im Repo. |
| Architektur-Guard-Suite | Teilweise **bewusste** Policy-Verletzungen oder lokale Artefakte (z. B. `app/gui.zip`); siehe Lückenbericht. |

## Empfohlene Ausführung

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest tests/unit tests/ui tests/architecture tests/integration tests/state_consistency tests/golden_path tests/cross_layer -q
```

Ohne venv schlagen Imports fehl, wenn System-Python `qasync` / `deepdiff` nicht bereitstellt (PEP 668).
