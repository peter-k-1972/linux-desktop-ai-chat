# Pipeline Engine – Abschlussreport Phase 1

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-17  
**Status:** Implementierung abgeschlossen

---

## 1. Implementierte Struktur

```
app/pipelines/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── definition.py    # PipelineDefinition, PipelineStepDefinition
│   ├── run.py           # PipelineRun, PipelineStepRun, PipelineArtifact
│   └── status.py        # PipelineStatus, StepStatus
├── engine/
│   ├── __init__.py
│   └── engine.py        # PipelineEngine
├── executors/
│   ├── __init__.py
│   ├── base.py          # StepExecutor, StepResult
│   ├── shell_executor.py
│   ├── python_executor.py
│   ├── placeholder_executors.py  # ComfyUI, Media (Placeholder)
│   └── registry.py      # ExecutorRegistry, get_executor_registry
├── services/
│   ├── __init__.py
│   └── pipeline_service.py
└── registry/
    ├── __init__.py
    └── definition_registry.py   # PipelineDefinitionRegistry

app/services/
└── pipeline_service.py   # get_pipeline_service, set_pipeline_service (delegiert an pipelines)
```

---

## 2. Architekturentscheidungen

| Entscheidung | Begründung |
|-------------|------------|
| **Sequentielle Ausführung** | Phase 1 bewusst einfach; DAG/Parallelisierung erst bei Bedarf |
| **Executor-Pattern** | Engine kennt nur StepExecutor-Interface; keine ComfyUI-Kopplung im Kern |
| **In-Memory-Runs** | Keine Persistenz-Komplexität; DB/SQLite später bei Anforderung |
| **PipelineService in app/services/** | Konsistent mit Architektur: GUI → Services → Backend |
| **pipelines ohne app.*-Imports** | Maximale Unabhängigkeit; Erweiterung nur über Executors |
| **Placeholder für ComfyUI/Media** | Vorbereitung für spätere Integration ohne Kernänderung |

---

## 3. Aktueller Funktionsumfang

### 3.1 Pipeline-Definition

- `PipelineDefinition`: pipeline_id, steps, name, metadata
- `PipelineStepDefinition`: step_id, executor_type, config, name

### 3.2 Pipeline-Ausführung

- `PipelineEngine.create_run(definition, run_id?)` → PipelineRun
- `PipelineEngine.execute(definition, run, context?)` → Run (in-place modifiziert)
- Sequentielle Ausführung, Statusaktualisierung, Log-Sammlung, Fehlerbehandlung
- `PipelineEngine.cancel()` für Abbruch-Anforderung

### 3.3 Statusmodell

- `PipelineStatus`: PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
- `StepStatus`: PENDING, RUNNING, COMPLETED, FAILED, SKIPPED, CANCELLED

### 3.4 Executors

| Typ | Status | Beschreibung |
|-----|--------|--------------|
| shell | Implementiert | Führt Shell-Befehle aus, optional capture_stdout_as |
| python_callable | Implementiert | Führt Python-Callable aus (direkt oder Modulpfad) |
| comfyui | Placeholder | Gibt Hinweis zurück |
| media | Placeholder | Gibt Hinweis zurück |

### 3.5 Service-Schicht

- `PipelineService.create_run(definition, run_id?)`
- `PipelineService.start_run(run, definition?, context?)`
- `PipelineService.get_run(run_id)`
- `PipelineService.list_runs(pipeline_id?, status?)`
- `PipelineService.cancel_run(run_id)`
- `PipelineService.register_definition(definition)`
- `get_pipeline_service()` in app.services

### 3.6 Artefakte

- `PipelineArtifact`: step_id, key, value, artifact_type
- Shell-Executor: `capture_stdout_as` für Text-Artefakte
- Kontext-Weitergabe: Artefakte vorheriger Schritte in `context["artifacts"]`

---

## 4. Bewusst nicht umgesetzt

| Thema | Begründung |
|-------|------------|
| **DAG / Parallelisierung** | Kein Overengineering; sequentiell reicht für Phase 1 |
| **Persistenz (DB/SQLite)** | In-Memory ausreichend; später bei Anforderung |
| **GUI-Integration** | Explizit aus Task ausgeschlossen |
| **Chat-/Agent-Integration** | Vorbereitet über Service; Implementierung später |
| **EventBus/Debug-Events** | Optionale Erweiterung; minimale Abhängigkeit |
| **Echte ComfyUI-Anbindung** | Placeholder; echte Integration in späterer Phase |
| **Projekt-Zuordnung** | Runs können später project_id erhalten |

---

## 5. Tests

- **tests/unit/test_pipelines_models.py**: 10 Tests (Definition, Run, Status, Artefakte)
- **tests/unit/test_pipelines_engine.py**: 7 Tests (create_run, execute, Fehler, Logs, Artefakte)
- **tests/unit/test_pipelines_executors.py**: 12 Tests (Shell, Python, Placeholder, Registry)
- **tests/unit/test_pipelines_service.py**: 7 Tests (create, start, list, filter, cancel)

**Gesamt:** 36 Unit-Tests, alle grün.

Architektur-Guards (app_package, service_governance) bestanden.

---

## 6. Governance-Integration

- `pipelines` in `TARGET_PACKAGES`
- `FORBIDDEN_IMPORT_RULES` für pipelines (keine Imports von gui, providers, services, agents, rag, prompts, core, debug, metrics, tools)
- `pipeline_service` in `CANONICAL_SERVICE_MODULES`
- `PIPELINE_ENGINE_POLICY.md` definiert Rolle, Abhängigkeiten, Executor-Regeln

---

## 7. Empfohlene nächste Schritte

1. **GUI-Workspace** (Phase 2): Screen/Workspace für Pipeline-Übersicht, Run-Details, Logs
2. **EventBus-Integration** (optional): `emit_event` bei Run-Start, Step-Complete, Run-Complete
3. **ComfyUI-Executor** (Phase 3): Echte API-Anbindung an ComfyUI
4. **Media-Executors** (Phase 3): Voice, Musik, Subtitles, Merge
5. **Chat-Integration**: Slash-Command oder Chat-Aktion „Pipeline starten“
6. **Agent-Integration**: Task-Typ „Starte Pipeline X“ in Delegation/Execution Engine
7. **Persistenz** (bei Bedarf): Runs in SQLite oder Projekt-DB

---

*Quelle: Pipeline Engine Phase 1 Abschlussreport*
