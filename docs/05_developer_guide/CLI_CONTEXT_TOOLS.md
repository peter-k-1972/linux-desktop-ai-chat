# CLI – Context Replay, Repro & Registry

Headless-Werkzeuge unter `app/cli/` (kein PySide6 erforderlich). Voraussetzung: virtuelle Umgebung mit `pip install -r requirements.txt`.

## Übersicht (Stichprobe)

| Modul | Zweck |
|--------|--------|
| `context_replay.py` | Replay von gespeicherten Kontext-/Chat-Szenarien |
| `context_repro_*.py` | Repro-Fälle erzeugen oder anwenden |
| `context_repro_registry_*.py` / `context_repro_registry_list.py` | Registry-Status und -Metadaten |

Vollständige Liste: `ls app/cli/` im Repository.

## Ausführung

Aus dem Projektroot:

```bash
python -m app.cli.<modul> --help
```

Ersetze `<modul>` durch den Dateinamen ohne `.py` (z. B. `context_replay`).

## Artefakte

- Replay- und Repro-Daten liegen typischerweise unter von den Skripten ausgegebenen Pfaden oder unter `app/context/replay/` (siehe jeweilige Modul-Docstrings).
- QA-JSON unter `docs/qa/` wird von der GUI-Kommandozentrale gelesen (`QADashboardAdapter`), nicht von diesen CLI-Modulen.

## Tests

- `tests/cli/` enthält CLI-Integrationstests (können optionale Abhängigkeiten benötigen).
