# `app.pipelines` — Definition of Ready for Cut

**Projekt:** Linux Desktop Chat  
**Status:** Verbindliche **API- und Reife-Definition**; Packaging **Variante B** — im Monorepo **Commits 1–4** umgesetzt (Vorlage, Host-Cut, CI, Guard-/QA-Abschluss: [`PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md`](PACKAGE_PIPELINES_COMMIT4_WAVE3_CLOSEOUT.md)). **Offen:** eigenständiges Release-Repo / PyPI-Pin / Changelog — nicht Teil dieses Dokuments.  
**Bezug:** [`PACKAGE_PIPELINES_SPLIT_READY.md`](PACKAGE_PIPELINES_SPLIT_READY.md) (Insel-Analyse, Public-Surface-Regeln §4), [**`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`**](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md) (verbindliche Packaging-/Importpfad-Entscheidung), [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §3.5 / §6.2, [`arch_guard_config.py`](../../tests/architecture/arch_guard_config.py), [`test_pipelines_public_surface_guard.py`](../../tests/architecture/test_pipelines_public_surface_guard.py), [`PIPELINE_ENGINE_ANALYSIS.md`](../04_architecture/PIPELINE_ENGINE_ANALYSIS.md)

**Importpfad nach physischem Cut:** **Variante B** — verbindlich in [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md) §2 (Distribution **`linux-desktop-chat-pipelines`**, installiertes Paket **`app.pipelines`**).

---

## 1. Verbindliche öffentliche API

### 1.1 Paket-Root `app.pipelines`

Alles in [`app.pipelines.__all__`](../../linux-desktop-chat-pipelines/src/app/pipelines/__init__.py) ist **semver-relevant** für Konsumenten außerhalb des Pakets.

```text
from app.pipelines import …
```

| Kategorie | Symbole |
|-----------|---------|
| Modelle | `PipelineDefinition`, `PipelineStepDefinition`, `PipelineRun`, `PipelineStepRun`, `PipelineArtifact`, `PipelineStatus`, `StepStatus` |
| Engine | `PipelineEngine` |
| In-Process-Service | `PipelineService` |
| Executors | `StepExecutor`, `StepResult`, `ExecutorRegistry`, `get_executor_registry`, `ShellExecutor`, `PythonCallableExecutor`, `PlaceholderComfyUIExecutor`, `PlaceholderMediaExecutor` |
| Definitions-Registry | `PipelineDefinitionRegistry`, `get_definition_registry` |

### 1.2 Kanonische Submodule (eine Ebene)

Gleichwertig zum Root, sofern **kein** tieferer Pfad:

| Modul | Inhalt (`__all__`) |
|--------|-------------------|
| `app.pipelines.models` | wie Root-Modelle |
| `app.pipelines.engine` | `PipelineEngine` |
| `app.pipelines.services` | `PipelineService` |
| `app.pipelines.executors` | Executor-API inkl. konkreter Klassen |
| `app.pipelines.registry` | `PipelineDefinitionRegistry`, `get_definition_registry` |

**Verboten** außerhalb `app/pipelines/**`: z. B. `app.pipelines.engine.engine`, `app.pipelines.executors.base`, `app.pipelines.services.pipeline_service`.

### 1.3 Durchsetzung

- [`test_pipelines_public_surface_guard.py`](../../tests/architecture/test_pipelines_public_surface_guard.py): erlaubte Modulpfade + kein Import von `_*`-Symbolen aus `app.pipelines` außerhalb des Pakets.

---

## 2. Intern / nicht exportieren (keine semver-Garantie nach außen)

| Bereich | Beispiele / Hinweis |
|---------|---------------------|
| Tiefe Modulpfade | `app.pipelines.models.definition`, `…/engine/engine`, `…/executors/registry` (nur **innerhalb** `app/pipelines/**` für Implementierung) |
| Modul-Singletons | `_default_registry` in `executors/registry.py`, `registry/definition_registry.py` — nicht von außen referenzieren |
| Engine-Implementierungsdetail | `PipelineEngine._cancelled` — kooperativer Abbruch |
| Platzhalter-Executors | öffentliche **Klassen**, aber bewusster Fehlerpfad bis Produktintegration — Breaking-Änderungen mit Review |

**Hinweis:** `PipelineDefinitionRegistry` / `get_definition_registry` sind **öffentlich** exportiert, haben aber aktuell **keine** Host-Consumer außerhalb `app/pipelines` — optionaler Konsolidierungs-Punkt mit `PipelineService._definitions` (nicht Cut-blockierend).

---

## 3. Direkte Consumer (Produkt)

| Ort | Import / Nutzung | Rolle nach Split |
|-----|------------------|------------------|
| [`app/services/pipeline_service.py`](../../app/services/pipeline_service.py) | `from app.pipelines import PipelineDefinition, PipelineRun, PipelineService as _PipelineService` | Host-Fassade `get_pipeline_service()` — **bleibt im Host** |
| [`app/workflows/execution/node_executors/tool_call.py`](../../app/workflows/execution/node_executors/tool_call.py) | `from app.pipelines import get_executor_registry` | Host-Workflow — **hängt vom Pipelines-Wheel ab** |

**Tests:** `tests/unit/test_pipelines_*.py`, `tests/unit/workflows/workflow_tool_stub.py`; Governance: `test_service_governance_guards.py` (Indirektion über `get_pipeline_service`).

**Kein** direkter `app.gui` → `app.pipelines`-Import.

---

## 4. Erlaubte direkte Abhängigkeiten (Zielpaket)

| Von | Erlaubt |
|-----|---------|
| `app/pipelines/**/*.py` | **stdlib** und ausschließlich **`app.pipelines.*`** |
| Verboten (Package-Guards) | `app.gui`, `app.services`, `app.core`, `app.providers`, `app.agents`, `app.rag`, `app.prompts`, `app.debug`, `app.metrics`, `app.tools`, … siehe `FORBIDDEN_IMPORT_RULES` für `pipelines` |

---

## 5. Cut-Blocker

| Blocker | Stand |
|---------|--------|
| Öffentliche API / Root-`__all__` | **Erledigt** — siehe §1; Code [`app/pipelines/__init__.py`](../../linux-desktop-chat-pipelines/src/app/pipelines/__init__.py). |
| Tiefe Außenimporte / private Symbole | **Erledigt** — `test_pipelines_public_surface_guard.py`. |
| Architektur-Insel (statisch) | **Erledigt** — siehe SPLIT_READY §2. |
| **`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`** (Variante B, Wheel-Name, Skizze, Guard-/CI-Folgen) | **Erledigt** (Doku); **Ausführung** Commit 1 ff. offen. |
| **Commit-1-Vorlage** (`linux-desktop-chat-pipelines/`) | **Erledigt** — siehe [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md) §0. |
| **Host:** Abhängigkeit `file:` / Version-Pin im `pyproject.toml` | **Erledigt (Commit 2)** — [`PACKAGE_PIPELINES_COMMIT2_LOCAL.md`](PACKAGE_PIPELINES_COMMIT2_LOCAL.md). |
| **Guards/CI/QA:** installierte Quelle / `find_spec` statt Host-`app/pipelines/` | **Erledigt (Commit 2/3)** — Guards/Tests: Commit 2; CI: [`PACKAGE_PIPELINES_COMMIT3_CI.md`](PACKAGE_PIPELINES_COMMIT3_CI.md). |
| **Segment-AST** (`test_segment_dependency_rules.py`) | **Erledigt (Commit 2)** — `app_pipelines_source_root()`. |
| **Release-Notes / API-Changelog** für das Wheel | **Offen**. |
| **`PythonCallableExecutor`** / dynamisches `importlib` | **Kein** harter Cut-Blocker für Packaging; **empfohlen:** Betriebs-/Security-Policy dokumentieren (SPLIT_READY §2.3). |

Unabhängig von `pipelines`: allgemeine Host-Sauberkeit (`test_app_package_guards`, App-Root-Dateien) — **kein** logischer Blocker für die Pipelines-API selbst.

---

## 6. Definition of Ready for Cut

### 6.1 Bereits erfüllt (Monorepo, logisch Cut-Ready)

- [x] Nur `app.pipelines.*` + stdlib innerhalb des Segments; keine verbotenen Kanten zu anderen Top-Segmenten (Import-Guards).  
- [x] Verbindliche Public Surface: Root-`__all__` + kanonische Submodule (§1).  
- [x] `test_pipelines_public_surface_guard.py` grün.  
- [x] Produkt-Consumer auf Root- bzw. erster Submodulebene; schmale Fan-in-Fläche.  
- [x] Submodule `models`, `engine`, `services`, `executors`, `registry` mit `__all__` abgestimmt — **keine** zusätzliche Code-Änderung in diesem Lauf nötig.

### 6.2 Zwingend vor physischem Split (Ausführung)

- [x] `PACKAGE_PIPELINES_PHYSICAL_SPLIT.md` — verbindliche Entscheidung **Variante B**, Wheel-Name, Skizze — [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md).  
- [x] Commit-1: Vorlage `linux-desktop-chat-pipelines/` mit `pyproject.toml`, Tests, README — [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md) §0.  
- [x] Host: Abhängigkeit deklarieren (`file:` im Monorepo, später Index-Pin) — Commit 2.  
- [x] Architektur-/Segment-Tests und ggf. QA-Pfad-Heuristiken auf **installiertes** Paket umstellen — Commit 2.  
- [x] CI-Workflows (Install + Verify) nach Muster Welle 1–2 — Commit 3 [`PACKAGE_PIPELINES_COMMIT3_CI.md`](PACKAGE_PIPELINES_COMMIT3_CI.md).  
- [ ] Release-Notes / Changelog für öffentliche Symbole §1.1.

### 6.3 Nach dem Cut zu verifieren (Auszug)

- [ ] `pytest tests/architecture/test_pipelines_public_surface_guard.py tests/unit/test_pipelines_*.py -q`  
- [ ] `pytest tests/unit/workflows/test_tool_call_node_executor.py -q` (Kante Workflows → Executors)  
- [ ] Keine Regression in `test_segment_dependency_rules.py` / Service-Governance nach Anpassung der Scan-Pfade  
- [ ] Kein Verlust der in §1.1 dokumentierten Root-Symbole

---

## 7. Pytest-Kommandos (Kurzset)

```bash
cd Linux-Desktop-Chat
pytest tests/architecture/test_pipelines_public_surface_guard.py \
       tests/unit/test_pipelines_models.py \
       tests/unit/test_pipelines_engine.py \
       tests/unit/test_pipelines_service.py \
       tests/unit/test_pipelines_executors.py \
       tests/unit/workflows/test_tool_call_node_executor.py -q
```

---

## 8. Änderungshistorie

| Datum | Änderung |
|--------|----------|
| 2026-03-25 | Erste Fassung: DoR, Blocker-Matrix, Consumer, Abhängigkeiten; empfohlene Variante B ohne PHYSICAL_SPLIT-Dokument |
| 2026-03-25 | Verweis [`PACKAGE_PIPELINES_PHYSICAL_SPLIT.md`](PACKAGE_PIPELINES_PHYSICAL_SPLIT.md); §5/§6.2 Blocker/DoR angepasst |
| 2026-03-25 | Commit-1-Vorlage `linux-desktop-chat-pipelines/` — §5 Commit-1-Zeile, §6.2 Checkbox |
