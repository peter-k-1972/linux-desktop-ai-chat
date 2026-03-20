# Pipeline Engine – Governance Policy

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-17  
**Referenz:** PIPELINE_ENGINE_ANALYSIS.md

---

## 1. Rolle des Pipeline-Moduls

Das **Pipeline-Modul** (`app/pipelines/`) ist ein generisches Kernmodul zur Ausführung von Medien- und Kreativpipelines. Es:

- Definiert und führt Pipelines sequentiell aus
- Bietet eine Executor-Abstraktion (Shell, Python, ComfyUI, Media)
- Führt Status, Logs und Artefakte
- Bereitet die Integration externer CLI-Werkzeuge vor

**Nicht:** ComfyUI-spezifische Architektur, GUI, Chat oder Agent-Logik im Kern.

---

## 2. Erlaubte Abhängigkeiten

| Quelle | Erlaubte Ziele |
|--------|----------------|
| `pipelines` | Nur `pipelines` (intern), stdlib, typing, dataclasses, enum, pathlib, logging, subprocess, importlib, uuid |
| `services` | `pipelines` (PipelineService delegiert an Engine) |
| `gui` | `services` (get_pipeline_service) |

**pipelines** importiert **keine** anderen `app.*`-Pakete.

---

## 3. Verbotene Kopplungen

| Verboten | Begründung |
|----------|------------|
| `pipelines` → `gui` | Keine UI-Abhängigkeit im Kern |
| `pipelines` → `providers` | ComfyUI/Media über Executors, nicht direkt |
| `pipelines` → `services` | Keine zirkuläre Abhängigkeit |
| `pipelines` → `agents`, `rag`, `prompts`, `core`, `debug`, `metrics`, `tools` | Minimale Kopplung; Erweiterung nur über Executors |
| ComfyUI-Logik in `models/` oder `engine/` | ComfyUI nur in `executors/` |

---

## 4. Executor-Anbindung

### 4.1 Interface

- Alle Executors implementieren `StepExecutor` (execute(step_id, config, context) → StepResult)
- Die Engine kennt nur das Interface, nicht die konkreten Typen
- Executor-Typen werden über `ExecutorRegistry` aufgelöst

### 4.2 Registrierung

- Neue Executor-Typen: `ExecutorRegistry.register(executor_type, executor)`
- Keine Änderung der Engine bei neuen Typen
- Erlaubte Typen (Phase 1): `shell`, `python_callable`, `comfyui`, `media`

### 4.3 ComfyUI-Integration (später)

- ComfyUI-Executor lebt in `executors/comfyui_executor.py`
- Keine ComfyUI-Imports in `models/`, `engine/`, `services/`
- ComfyUI-spezifische Config nur in Step-Definition (config-Dict)

---

## 5. Tool-/ComfyUI-Integration (später)

- **Tools:** Executors dürfen `app.tools` nutzen, wenn nötig – aber nicht umgekehrt
- **ComfyUI:** Als Executor; API-Anbindung ausschließlich im ComfyUI-Executor
- **Externe CLI:** Über Shell-Executor oder eigene Executor-Implementierung

---

## 6. Regeln gegen Wildwuchs

| Regel | Beschreibung |
|-------|--------------|
| Keine GUI im Kern | Keine Qt-, Widget- oder UI-Imports in `app/pipelines/` |
| Keine Provider-Direktimporte | Ollama, ComfyUI etc. nur über Executors |
| Keine DAG-Overengineering | Phase 1: sequentiell; DAG erst bei nachgewiesenem Bedarf |
| Keine unnötige Persistenz | Phase 1: In-Memory; DB/SQLite erst bei Anforderung |
| Executor-Erweiterung | Nur über Registry; keine Engine-Änderung für neue Typen |

---

## 7. Architektur-Guards

- `pipelines` in `TARGET_PACKAGES`
- `FORBIDDEN_IMPORT_RULES` für `pipelines` (siehe arch_guard_config.py)
- `pipeline_service` in `CANONICAL_SERVICE_MODULES`
- Tests: `tests/unit/test_pipelines_*.py`

---

*Quelle: Pipeline Engine Governance Policy*
