# System inventory — Linux Desktop Chat

**Scope:** Factual snapshot of the repository layout and architecture layering.  
**Generated:** 2026-03-24 (audit pass over filesystem and `docs/FEATURE_REGISTRY.md`, `pytest.ini`, `main.py`, `app/services/__init__.py`).

---

## 1. Top-level directories and notable files

Repository root entries (including hidden VCS/IDE dirs observed on disk):

| Name | Role (from name / contents) |
|------|-----------------------------|
| `alembic/` | Database migrations (with `alembic.ini`) |
| `app/` | Main Python application package |
| `archive/` | Legacy GUI entrypoint and deprecated migration docs |
| `assets/` | Static assets (icons, themes, etc.) |
| `data/` | Runtime/data directory (present) |
| `docs/` | Project documentation |
| `docs_manual/` | Additional manual docs |
| `docs_manual_latex/` | LaTeX manual sources |
| `example_output/` | Example outputs |
| `examples/` | Examples |
| `help/` | In-app help content |
| `resources/` | Bundled resources |
| `scripts/` | Scripts |
| `static/` | Static web/static files |
| `tests/` | Pytest test tree |
| `tools/` | Maintenance / codegen tools |
| `.github/` | CI / GitHub configuration |
| `.idea/` | IDE metadata |

Additional root files (non-exhaustive): `main.py`, `run_gui_shell.py`, `run_workbench_demo.py`, `pytest.ini`, `requirements.txt`, `Makefile`, `install-desktop.sh`, `start.sh`, `linux-desktop-chat.desktop`, `design_system.json`, `README.md`.

---

## 2. Logical subsystems (by `app/` package)

First-level Python packages under `app/`:

`agents`, `chat`, `chats`, `cli`, `commands`, `context`, `core`, `debug`, `devtools`, `diagnostics`, `domain`, `gui`, `gui_designer_dummy`, `help`, `llm`, `metrics`, `models`, `persistence`, `pipelines`, `projects`, `prompts`, `providers`, `qa`, `rag`, `resources`, `runtime`, `services`, `tools`, `ui_application`, `ui_contracts`, `ui_runtime`, `ui_themes`, `utils`, `workflows`.

**GUI surface areas** (from `app/gui/domains/`):

- `command_center`, `control_center`, `dashboard`, `debug`, `operations` (chat, knowledge, prompt_studio, workflows, deployment, audit_incidents, agent_tasks, projects), `project_hub`, `prompt_studio` (parallel path under domains), `qa_governance`, `runtime_debug`, `settings`.

**Supporting GUI packages** (non-domain): `shell`, `workspace`, `workbench`, `navigation`, `scheduling`, `inspector`, `monitors`, `themes`, `components`, `widgets`, `icons`, `events`, `commands`, `breadcrumbs`, `legacy`, `shared`, `project_switcher`, `devtools`, `theme`.

---

## 3. Canonical architecture layers (observed)

These layers are identifiable from package layout and the service-layer docstring in `app/services/__init__.py` (GUI ↔ services, not direct provider/DB access).

| Layer | Location | Notes |
|-------|----------|--------|
| **Entry** | `main.py` → `run_gui_shell.py`; `python -m app` referenced in `main.py` | Standard GUI start |
| **Presentation (Qt)** | `app/gui/` | PySide6 workspaces, panels, shell |
| **Application / MVP-style** | `app/ui_application/` | Presenters, ports, adapters, mappers |
| **View contracts** | `app/ui_contracts/` | Workspace-oriented protocols / DTOs |
| **Optional runtime bridge** | `app/ui_runtime/` | QML/widgets runtime helpers (`qml/`, `widgets/`) |
| **Theming** | `app/ui_themes/`, `app/gui/themes/` | Theme loading, registry, builtins |
| **Service façade** | `app/services/` | Orchestration for GUI-facing operations |
| **Domain / core** | `app/core/` | Config, DB, models, navigation, LLM helpers, audit, deployment, chat_guard, commands, context |
| **Integrations** | `app/providers/` | Ollama-oriented providers and client |
| **Persistence** | `app/persistence/` | ORM / storage (with `alembic` at repo root) |
| **Vertical features** | `app/chat`, `app/chats`, `app/agents`, `app/workflows`, `app/pipelines`, `app/rag`, `app/prompts`, `app/projects`, `app/context`, `app/qa`, `app/metrics`, `app/llm` | Feature-oriented modules |
| **CLI / tools** | `app/cli/`, `app/tools/`, repo `tools/`, `scripts/` | Non-GUI entrypoints and automation |

---

## 4. Cross-cutting documentation maps

- `docs/FEATURE_REGISTRY.md` — workspace IDs, code paths, service names, help keys, and test pointers (auto-generated; header cites `tools/generate_feature_registry.py`).
- `docs/00_map_of_the_system.md` — human-oriented workspace and navigation description.
- `app/core/navigation/feature_registry_loader.py` — loads `docs/FEATURE_REGISTRY.md` at runtime.

---

## 5. Experimental, legacy, or incomplete signals (factual only)

| Signal | Evidence |
|--------|----------|
| **Legacy GUI** | `main.py` states legacy start: `archive/run_legacy_gui.py`. `archive/` contains `run_legacy_gui.py` and `deprecated_docs/`. |
| **Designer-only assets** | `app/gui_designer_dummy/` holds `.ui` files for Qt Designer (not the runtime GUI package root). |
| **Feature registry: no tests listed** | In `docs/FEATURE_REGISTRY.md`, these rows use `Tests \| —`: **QA Incidents** (`qa_incidents`), **Runtime → Agent Activity** (`rd_agent_activity`), **Settings → Privacy** (`settings_privacy`). |
| **Pytest marker unused in tree** | `pytest.ini` defines `context_observability`; repository search under `tests/` found no `@pytest.mark.context_observability` usages. |
| **Small agent catalog package** | `app/agents/farm/` contains `loader.py`, `models.py`, `default_catalog.json`, `__init__.py`. |
| **Parallel prompt studio domain** | Both `app/gui/domains/operations/prompt_studio/` and `app/gui/domains/prompt_studio/` exist as package paths. |

No judgement is made here about production readiness; only observable structure and registry/test gaps are recorded.
