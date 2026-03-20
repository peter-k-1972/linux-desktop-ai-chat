# Pipeline Engine – Architektur- und Integrationsanalyse

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-17  
**Status:** Analyse für erste Implementierungsphase

---

## 1. Zielrolle des Moduls

Die **Pipeline Engine** ist ein generisches Kernmodul zur Ausführung von Medien- und Kreativpipelines. Sie dient als:

- **Orchestrierungsschicht** für sequentielle oder später erweiterbare Workflows
- **Abstraktionsschicht** zwischen Definition (was) und Ausführung (wie)
- **Vorbereitung** für die Integration externer CLI-Werkzeuge (ComfyUI, Voice, Musik, Subtitles, Merge)

**Nicht** in dieser Phase:
- ComfyUI-spezifische Logik im Kern
- GUI- oder Chat-Integration
- DAG-basierte Parallelisierung

---

## 2. Einordnung in die bestehende Architektur

### 2.1 Schichtenbezug

| Schicht | Bezug zur Pipeline Engine |
|---------|---------------------------|
| **GUI** | Später: Pipeline-Runs anzeigen, starten, abbrechen. Nutzt ausschließlich `PipelineService`. |
| **Services** | `PipelineService` in `app/services/` delegiert an `app/pipelines/`. |
| **Providers** | Keine direkte Abhängigkeit. ComfyUI/Media-Provider werden über Executors angebunden. |
| **Core** | Keine Abhängigkeit. Pipelines sind eigenständige Domäne. |
| **Agents** | Später: Agenten können Pipelines starten/überwachen. Keine Kopplung im Kern. |
| **Tools** | Executors können Tools nutzen; Tools kennen Pipelines nicht. |
| **Projects** | Später: Runs können einem Projekt zugeordnet werden. |
| **Runtime Debug** | Optional: Pipeline-Events über EventBus emitieren. |

### 2.2 Modulstruktur

```
app/pipelines/
├── __init__.py
├── models/           # PipelineDefinition, PipelineRun, PipelineStepRun, PipelineArtifact, Status
├── engine/           # PipelineEngine – sequentielle Ausführung
├── executors/        # StepExecutor-Interface, Shell, Python, Placeholder-ComfyUI/Media
├── services/         # PipelineService – create_run, start_run, get_run, list_runs
└── registry/         # ExecutorRegistry – Auflösung executor_type → Executor
```

`PipelineService` wird in `app/services/pipeline_service.py` implementiert und nutzt `app.pipelines` als Backend. Damit bleibt die Architekturregel **GUI → Services → Backend** erhalten.

---

## 3. Erlaubte Abhängigkeiten

| Quelle | Erlaubte Ziele |
|--------|----------------|
| `pipelines` | `pipelines` (intern), `typing`, `dataclasses`, `enum`, `pathlib`, `logging` |
| `pipelines` | Optional: `debug` (emit_event für Pipeline-Events) – zunächst weggelassen |
| `services` | `pipelines` (PipelineService nutzt Engine) |
| `gui` | `services` (get_pipeline_service) |

**pipelines** importiert bewusst **nicht**:
- `gui`, `providers`, `agents`, `rag`, `prompts`, `tools`, `metrics`
- `core` (außer ggf. config, wenn nötig – zunächst nicht)
- `services` (keine zirkuläre Abhängigkeit)

---

## 4. Schnittstellen zu Chat / GUI / Agents / Runtime

### 4.1 GUI

- **Zugriff:** `get_pipeline_service()` → `create_run()`, `start_run()`, `get_run()`, `list_runs()`
- **Keine** direkten Imports von `app.pipelines` in der GUI
- Später: Workspace/Screen für Pipeline-Übersicht, Run-Details, Logs

### 4.2 Chat

- Später: Slash-Command oder Chat-Aktion „Pipeline starten“
- Chat ruft `PipelineService` auf, nicht die Engine direkt

### 4.3 Agents

- Später: Agent-Task „Starte Pipeline X“ → Delegation an `PipelineService`
- Keine Kopplung im Kern; Agents kennen nur Service-API

### 4.4 Runtime Debug

- Optional: `emit_event(EventType.PIPELINE_*, ...)` bei Run-Start, Step-Complete, Run-Complete
- Erweiterung von `EventType` und `ALLOWED_EMIT_EVENT_IMPORTERS` nötig
- In Phase 1: bewusst weggelassen, um Abhängigkeit zu minimieren

---

## 5. Risiken durch zu enge ComfyUI-Kopplung

| Risiko | Mitigation |
|--------|------------|
| Kern-Engine wird ComfyUI-spezifisch | Executor-Pattern: Engine kennt nur `StepExecutor`-Interface |
| ComfyUI-Logik in Models/Engine | ComfyUI als eigener Executor-Typ; Definition bleibt generisch |
| Schwer testbar | Unit-Tests ohne ComfyUI; Placeholder-Executor für Tests |
| Schwer erweiterbar | Registry für Executor-Typen; neue Typen ohne Engine-Änderung |

**Regel:** Alle ComfyUI-spezifischen Annahmen leben ausschließlich in `executors/comfyui_executor.py` (Placeholder in Phase 1).

---

## 6. Empfohlene Integrationsform

1. **Phase 1 (dieser Task):**
   - Pipeline-Kernmodell, Engine, Executors (inkl. Placeholder), Service-Schicht
   - Keine GUI, keine Chat-Integration
   - In-Memory-Run-Speicherung

2. **Phase 2 (später):**
   - GUI-Workspace für Pipelines
   - Optional: EventBus-Integration für Debug
   - Optional: Projekt-Zuordnung für Runs

3. **Phase 3 (später):**
   - ComfyUI-Executor (echte Implementierung)
   - Media-/Voice-/Musik-Executors
   - Chat-/Agent-Integration

4. **Governance:**
   - Policy-Dokument (`PIPELINE_ENGINE_POLICY.md`)
   - Architektur-Guards für `pipelines`-Package
   - `pipelines` in `TARGET_PACKAGES`

---

## 7. Abhängigkeitsgraph (vereinfacht)

```
gui
  └── services (get_pipeline_service)
        └── pipelines (engine, models, executors)

pipelines
  └── (keine app.*-Abhängigkeiten außer ggf. debug)
```

---

*Quelle: Architekturanalyse für Pipeline Engine Phase 1*
