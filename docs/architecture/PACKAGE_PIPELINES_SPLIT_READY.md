# `app.pipelines` — Split-Readiness (Welle 3)

**Projekt:** Linux Desktop Chat  
**Status:** Split-Readiness inkl. **verbindlicher Public Surface** und **pytest-Guard** — **Monorepo-Abschluss Welle 3:** [`PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md`](PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md); DoR [`PACKAGE_PIPELINES_CUT_READY.md`](PACKAGE_PIPELINES_CUT_READY.md).  
**Bezug:** [`PACKAGE_PIPELINES_CUT_READY.md`](PACKAGE_PIPELINES_CUT_READY.md) (**Definition of Ready for Cut**), [**`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`**](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md) (Packaging **Variante B**), [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §6.2, §3.5, [`arch_guard_config.py`](../../tests/architecture/arch_guard_config.py), [`PIPELINE_ENGINE_ANALYSIS.md`](../04_architecture/PIPELINE_ENGINE_ANALYSIS.md)

---

## 1. Modulbaum und Verantwortung

| Pfad | Rolle |
|------|--------|
| [`app/pipelines/models/`](../../linux-desktop-chat-pipelines/src/app/pipelines/models/) | DTOs: Definition, Run, Step-Run, Artefakte, Status-Enums |
| [`app/pipelines/engine/`](../../linux-desktop-chat-pipelines/src/app/pipelines/engine/) | [`PipelineEngine`](../../linux-desktop-chat-pipelines/src/app/pipelines/engine/engine.py) — sequentielle Ausführung, Cancel-Flag |
| [`app/pipelines/services/`](../../linux-desktop-chat-pipelines/src/app/pipelines/services/) | [`PipelineService`](../../linux-desktop-chat-pipelines/src/app/pipelines/services/pipeline_service.py) — In-Memory-Runs/Definitionen, delegiert an Engine |
| [`app/pipelines/executors/`](../../linux-desktop-chat-pipelines/src/app/pipelines/executors/) | `StepExecutor` / `StepResult`, Registry, Shell-, Python-Callable-, Placeholder-Executors |
| [`app/pipelines/registry/`](../../linux-desktop-chat-pipelines/src/app/pipelines/registry/) | [`PipelineDefinitionRegistry`](../../linux-desktop-chat-pipelines/src/app/pipelines/registry/definition_registry.py) + Singleton-Helfer |

Paket-Root-Docstring: generische Medien-/Kreativ-Pipelines, nicht ComfyUI-spezifisch; Placeholder-Executors für ComfyUI/Media.

---

## 2. Architektur-Insel (Ist-Prüfung)

### 2.1 Statische `app.*`-Importe innerhalb `app/pipelines/**`

Alle produktiven Module importieren **ausschließlich** `app.pipelines.*` (plus **stdlib**). **Keine** Kanten nach `app.core`, `app.services`, `app.gui`, `app.utils`, `app.providers`, `app.debug`, …

Das entspricht den Package-Guards: `pipelines` darf u. a. **nicht** `core`, `services`, `gui`, `providers`, `agents`, `rag`, `prompts` importieren (`FORBIDDEN_IMPORT_RULES` in `arch_guard_config.py`).

### 2.2 GUI / Hybrid

- **Kein** `from app.gui …` / `import app.gui …` unter `app/pipelines/`.
- Die GUI importiert **nicht** direkt `app.pipelines` (siehe auch [`PIPELINE_ENGINE_ANALYSIS.md`](../04_architecture/PIPELINE_ENGINE_ANALYSIS.md)); Zugriff läuft über **`app.services.pipeline_service`** (`get_pipeline_service`).
- In [`app/gui/registration/feature_builtins.py`](../../app/gui/registration/feature_builtins.py) erscheint der Name `"pipelines"` nur in einer **Metadaten-Tupel** (`packages=(…)`), ohne Modulimport — **kein** Hybrid-Risiko.

### 2.3 Versteckte Laufzeit-Kopplungen

| Mechanismus | Bewertung |
|-------------|-----------|
| [`PythonCallableExecutor`](../../linux-desktop-chat-pipelines/src/app/pipelines/executors/python_executor.py) | Nutzt **`importlib.import_module`** für `config["callable"]` als `"modul.attr"` — **dynamisch**, nicht im statischen Import-Graphen. Kann beliebige installierte Module laden (Sandbox-/Sicherheits- und SemVer-Thema für Aufrufer, nicht für die Insel-Grenze des Pakets). |
| `subprocess` in `ShellExecutor` | Stdlib; kein Produkt-Querschnitt. |

**Fazit:** Statisch ist `app.pipelines` eine **saubere Insel**; die Callable-Executor-Konfiguration ist der einzige nennenswerte **Laufzeit-„Ausbruch“**.

---

## 3. Direkte Produkt-Consumer (außerhalb `app/pipelines`)

| Ort | Import(e) | Zweck |
|-----|-----------|--------|
| [`app/services/pipeline_service.py`](../../app/services/pipeline_service.py) | `from app.pipelines import PipelineDefinition, PipelineRun, PipelineService as _PipelineService` | Öffentliche Host-Fassade `get_pipeline_service()` / `set_pipeline_service()` |
| [`app/workflows/execution/node_executors/tool_call.py`](../../app/workflows/execution/node_executors/tool_call.py) | `get_executor_registry` (kanonisch: `from app.pipelines import get_executor_registry`) | Workflow-Knoten `tool_call` → StepExecutor |

**Tests (Auszug):** `tests/unit/test_pipelines_*.py`, `tests/unit/workflows/workflow_tool_stub.py`; Architektur: [`test_service_governance_guards.py`](../../tests/architecture/test_service_governance_guards.py) (relevant: `get_pipeline_service`); Public Surface: [`test_pipelines_public_surface_guard.py`](../../tests/architecture/test_pipelines_public_surface_guard.py).

**Doku:** u. a. [`PIPELINE_ENGINE_ANALYSIS.md`](../04_architecture/PIPELINE_ENGINE_ANALYSIS.md), [`FULL_SYSTEM_CHECKUP_ANALYSIS.md`](../04_architecture/FULL_SYSTEM_CHECKUP_ANALYSIS.md).

---

## 4. Verbindliche öffentliche API (ab API-Härtung)

### 4.1 Regel (verbindlich)

Außerhalb von `app/pipelines/**` gelten **zwei gleichwertige** erlaubte Import-Stile:

1. **Paket-Root:** `from app.pipelines import …` — alle in [`__all__`](../../linux-desktop-chat-pipelines/src/app/pipelines/__init__.py) aufgeführten Namen.  
2. **Submodule genau eine Ebene unter `app.pipelines`:**  
   `app.pipelines.models`, `app.pipelines.engine`, `app.pipelines.services`, `app.pipelines.executors`, `app.pipelines.registry` — **keine** tieferen Pfade (z. B. **verboten:** `app.pipelines.engine.engine`, `app.pipelines.executors.base`, `app.pipelines.services.pipeline_service`).

Durchsetzung: [`test_pipelines_public_surface_guard.py`](../../tests/architecture/test_pipelines_public_surface_guard.py) (AST über `app/`, `tests/`, `tools/`, `examples/`, `scripts/`). Zusätzlich: **keine** Imports von Symbolen mit führendem Unterstrich aus `app.pipelines` außerhalb des Pakets.

**Innerhalb** `app/pipelines/**` bleiben Implementierungsimporte zwischen Untermodulen erlaubt (Guard schließt diesen Baum aus).

### 4.2 Paket-Root [`app.pipelines`](../../linux-desktop-chat-pipelines/src/app/pipelines/__init__.py) — `__all__`

| Kategorie | Symbole |
|-----------|---------|
| Modelle | `PipelineDefinition`, `PipelineStepDefinition`, `PipelineRun`, `PipelineStepRun`, `PipelineArtifact`, `PipelineStatus`, `StepStatus` |
| Engine | `PipelineEngine` |
| Service | `PipelineService` |
| Executors | `StepExecutor`, `StepResult`, `ExecutorRegistry`, `get_executor_registry`, `ShellExecutor`, `PythonCallableExecutor`, `PlaceholderComfyUIExecutor`, `PlaceholderMediaExecutor` |
| Definitions-Registry | `PipelineDefinitionRegistry`, `get_definition_registry` |

Host-Orchestrierung bleibt **`get_pipeline_service()`** in `app.services` (bleibt im Host nach Split); die Fassade importiert die Klassen **über das Paket-Root** (`from app.pipelines import …`).

### 4.3 Submodule — gleiche Semantik wie Root

| Modul | Re-Export / `__all__` |
|--------|----------------------|
| [`app.pipelines.models`](../../linux-desktop-chat-pipelines/src/app/pipelines/models/__init__.py) | wie bisher |
| [`app.pipelines.engine`](../../linux-desktop-chat-pipelines/src/app/pipelines/engine/__init__.py) | `PipelineEngine` |
| [`app.pipelines.services`](../../linux-desktop-chat-pipelines/src/app/pipelines/services/__init__.py) | `PipelineService` |
| [`app.pipelines.executors`](../../linux-desktop-chat-pipelines/src/app/pipelines/executors/__init__.py) | inkl. konkreter Executor-Klassen (siehe Root-Tabelle) |
| [`app.pipelines.registry`](../../linux-desktop-chat-pipelines/src/app/pipelines/registry/__init__.py) | unverändert |

### 4.4 Intern / ohne semver-Garantie (oder höheres Review-Level)

| Bereich | Inhalt |
|---------|--------|
| Modul-Singletons | `_default_registry` / globale Defaults in `executors/registry.py` und `registry/definition_registry.py` |
| Placeholder | `PlaceholderComfyUIExecutor`, `PlaceholderMediaExecutor` — bewusst Fehlerpfad bis echte Integration |
| Engine-Detail | `PipelineEngine._cancelled` — kooperativer Abbruch; `cancel_run` auf `PipelineService` setzt nur Engine-Flag (ein Engine pro Service — bei parallelen Runs limitierend, dokumentiertes Verhalten) |

---

## 5. Bekannte API-/Design-Punkte

### 5.1 `PipelineDefinitionRegistry` vs. `PipelineService`

[`PipelineDefinitionRegistry`](../../linux-desktop-chat-pipelines/src/app/pipelines/registry/definition_registry.py) und `get_definition_registry()` haben **keine** Produkt-Consumer außerhalb von `app/pipelines` (Ist-Stand: keine Treffer in `app/` oder `tests/` außer dem Paket selbst). `PipelineService` hält eigene `_definitions`. Das ist **kein** Bruch der Insel, aber **API-/Aufräum-Kandidat** vor „hartem“ 1.0 des Wheels (optional später).

### 5.2 Public-Surface-Guard

Vorhanden: [`test_pipelines_public_surface_guard.py`](../../tests/architecture/test_pipelines_public_surface_guard.py) — kanonische Module + keine `_*`-Imports von außen (siehe §4.1).

---

## 6. Abhängigkeiten des Ziel-Wheels

| Von `app.pipelines` | Erlaubt (Ziel) |
|---------------------|----------------|
| Python | **stdlib** (u. a. `dataclasses`, `enum`, `logging`, `subprocess`, `importlib`, `typing`, `abc`, `datetime`) |
| Produkt | **Nur** `app.pipelines.*` |

**Transitive Host-Abhängigkeit:** Nach physischem Cut hängt der Host weiterhin über `app.services.pipeline_service` und `app.workflows` vom Pipelines-Wheel ab; `pipelines` selbst **nicht** umgekehrt vom Host.

---

## 7. Split-Reifegrad und Blocker

| Kriterium | Einschätzung |
|-----------|----------------|
| **Technische Isolation** | **Hoch** — statische Imports nur intern; Guards passend. |
| **API-Klarheit** | **Hoch** — Root-`__all__` deckt Konsumenten-Oberfläche ab; Guard für Import-Tiefe; Registry-Duplikat-Idee bleibt optionaler Aufräum-Punkt (§5.1). |
| **GUI-/Hybrid-Risiko** | **Gering** — keine direkte GUI-Kante. |
| **CI-/Test-Risiko** | **Mittel** — Unit-Tests + Workflow-Executor + Service-Governance; kein separates Produkt-Extra nötig (anders als `rag`). |

**Blocker vor Cut:** tabellarisch und mit DoR-Checklisten in [**`PACKAGE_PIPELINES_CUT_READY.md`**](PACKAGE_PIPELINES_CUT_READY.md) §5–§6. Kurz: API/Guard + **Packaging-Entscheidung** ([`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md)) **erledigt**; **offen:** Vorlage Commit 1, Wheel/Host-Dep, CI/Guard-Pfade auf installiertes Paket, Changelog.

**Nicht** blockierend für die **logische** Insel: `PipelineDefinitionRegistry`-Nutzungslücke (§5.1).

---

## 8. Definition of Ready (kanonische Quelle)

Die vollständige **Definition of Ready for Cut**, die **Cut-Blocker-Matrix** und **Post-Cut-Verifikation** stehen ausschließlich in [**`PACKAGE_PIPELINES_CUT_READY.md`**](PACKAGE_PIPELINES_CUT_READY.md) (§5–§7). Dieses Dokument bleibt die **Ist-Analyse** und Public-Surface-Referenz (§4).

---

## 9. Pytest-Kurzset (Regression im Monorepo)

```bash
cd Linux-Desktop-Chat
pytest tests/architecture/test_pipelines_public_surface_guard.py \
       tests/unit/test_pipelines_models.py \
       tests/unit/test_pipelines_engine.py \
       tests/unit/test_pipelines_service.py \
       tests/unit/test_pipelines_executors.py -q
```

---

## 10. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: Insel-Nachweis, Consumer, API-Vorschlag, DoR-Checkliste (Welle 3, ohne physischen Split) |
| 2026-03-25 | API-Härtung: Root-`__all__` + `executors`-Re-Exports; verbindliche Public-Surface-Regel §4; Guard `test_pipelines_public_surface_guard.py` |
| 2026-03-25 | [`PACKAGE_PIPELINES_CUT_READY.md`](PACKAGE_PIPELINES_CUT_READY.md): DoR / Blocker; §8 verweist dorthin als kanonische Cut-Quelle |
| 2026-03-25 | [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md): verbindliche Variante B; Bezug §7 / Kopf |
