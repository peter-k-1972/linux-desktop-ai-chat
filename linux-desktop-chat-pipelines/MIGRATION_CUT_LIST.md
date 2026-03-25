# Cut-Liste: `linux-desktop-chat-pipelines` (Commit 1 → späterer Host-Cut)

**Stand:** Vorlage im Host-Monorepo unter `linux-desktop-chat-pipelines/`. Nach Auslagerung als eigenes Repo bleibt diese Datei im Pipelines-Repo; der Host verweist in seiner Doku auf die veröffentlichte Version.

---

## 1. 1:1 aus `app/pipelines/` ins Pipelines-Repo (`src/app/pipelines/`)

Alle Python-Module — **ohne Importpfad-Änderung** (weiter `app.pipelines.*` intern):

| Bereich | Pfade |
|---------|--------|
| Paket-Root | `__init__.py` |
| Unterpakete | `models/`, `engine/`, `services/`, `executors/`, `registry/` |

**Repo-spezifische Anpassungen am Produktcode:** keine für Commit 1 (Quelle = Spiegel des Hosts).

**Zusätzlich im Pipelines-Repo (nicht im Host-`app/pipelines/`):**

- `src/app/__init__.py` — Paketmarker für installierbares `app.pipelines`.

---

## 2. Dokumentation

| Mit ins Pipelines-Repo | Bleibt / primär im Host |
|------------------------|-------------------------|
| `README.md`, `MIGRATION_CUT_LIST.md`, `pyproject.toml` | `docs/architecture/PACKAGE_PIPELINES_*.md`, `PACKAGE_MAP.md`, `PACKAGE_SPLIT_PLAN.md` |

---

## 3. Tests

### Im Pipelines-Repo (`tests/unit/`) — minimale **isolierte** Suite

Läuft **ohne** installierten Host (`app.services`, `app.workflows`, `app.gui`, Architektur-Guards):

| Datei | Inhalt |
|-------|--------|
| `test_package_exports.py` | Smoke: zentrale Root-Imports aus `app.pipelines` |
| `test_pipelines_models.py` | Modell- und Status-Unit-Tests |
| `test_pipelines_engine.py` | `PipelineEngine` |
| `test_pipelines_service.py` | `PipelineService` (In-Memory) |
| `test_pipelines_executors.py` | Executors, Registry |

### Nur im Host — volle Integration / Governance

| Testdatei / Muster | Grund |
|--------------------|--------|
| `tests/architecture/test_pipelines_public_surface_guard.py` | Scan über Host-`app/`, `tests/`, `tools/`, … — bleibt bis Host-Cut / Guard-Umstellung im Host |
| `tests/unit/workflows/test_tool_call_node_executor.py` | importiert `app.workflows.execution.node_executors.tool_call` |
| `tests/unit/workflows/workflow_tool_stub.py` | Stubs für Workflow-Tests; von Host-Workflow-Suite genutzt |
| Weitere Workflows-/Service-Integrationstests | Kante Host → `app.pipelines` über Services oder Workflows |

### Architektur-Guards (`tests/architecture/`)

Bleiben **vollständig im Host**, bis Commit 2–4 (Umstellung auf `find_spec` / ausgelagerte Quelle) — siehe `PACKAGE_PIPELINES_PHYSICAL_SPLIT.md` §4.2.

---

## 4. Nicht mitwandern

- `app/services/pipeline_service.py`, `app/workflows/**`, Host-`pyproject.toml`, `.github/workflows/` (spätere Commits).
- Öffentliche Oberflächen- und Segment-Guards im Host.

---

## 5. Sync-Hinweis (bis zum Host-Cut)

Solange beide Bäume existieren: Änderungen an `app/pipelines/` im Host in die Vorlage `linux-desktop-chat-pipelines/src/app/pipelines/` **übernehmen** (manuell oder Skript), sonst driftet die Vorlage.
