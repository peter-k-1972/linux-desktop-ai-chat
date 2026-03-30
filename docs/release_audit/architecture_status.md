# Architecture status — Linux Desktop Chat

**Role:** Principal architect assessment against **enforced** rules in `tests/architecture/` and `tests/architecture/arch_guard_config.py`, plus `docs/04_architecture/ARCHITECTURE_GUARD_RULES.md` and `docs/04_architecture/SERVICE_GOVERNANCE_POLICY.md`.  
**Evidence date:** 2026-03-24  
**Tooling:** `python -m pytest tests/architecture` (`.venv-ci`), repository search.

**Update 2026-03-30 (targeted refactor, no full-suite re-baseline):** The earlier services-to-provider-class finding in `app/services/model_orchestrator_service.py` / `app/services/unified_model_catalog_service.py` was reduced via a focused service-layer refactor. `pytest -q tests/architecture/test_provider_orchestrator_governance_guards.py` passed after the change. The suite-wide metrics below remain the 2026-03-24 audit snapshot until a fresh full `tests/architecture` run is recorded for this document.

---

## Executive summary

| Metric | Value |
|--------|--------|
| **Architecture test suite** | 224 tests collected (`pytest tests/architecture --collect-only`) |
| **Failing tests (current)** | **5** |
| **Compliance score** | **97.8%** — defined as `(224 − 5) / 224 × 100` (pass rate of the architecture test module) |

The tree is **mostly aligned** with the guard model (GUI ↔ service boundaries, no `app.gui` → `app.ui`, `ui_contracts` Qt-free, many governance sentinels green). **Recorded drift** is concentrated in: **core layer purity**, **provider-orchestrator boundaries in services**, and **root entrypoint allowlist**.

---

## 1. Layer violations (vs guards + policy)

### 1.1 `gui` importing `core`

**Intended rule:** Allowed. `SERVICE_GOVERNANCE_POLICY.md` §2.1 lists `gui` → `core` as permitted.

**Guard failure:** None for this direction.

### 1.2 `core` importing `gui` (forbidden)

**Rule:** `FORBIDDEN_IMPORT_RULES` includes `("core", "gui")`; `test_core_no_gui_imports` / `test_no_forbidden_import_directions` enforce it.

**Violation (failing tests):**

| File | What |
|------|------|
| `app/core/config/settings.py` | Imports `app.gui.themes.theme_id_utils.is_registered_theme_id` inside `_normalize_theme_id` (module-level dependency on `app.gui`). Docstring claims “Qt-frei”; the **package** import still ties core config to the GUI theme registry. |

**Risk:** Tight coupling and **potential import-cycle pressure** (core ↔ gui) if future gui modules pull `AppSettings` at import time. Today `theme_id_utils` avoids importing `AppSettings`; the edge remains **core → gui**, which the guards flag.

### 1.3 `core` importing `services` (forbidden)

**Rule:** `("core", "services")` in `FORBIDDEN_IMPORT_RULES`. Policy §2.1 states `core` should use only `core` (with exceptions documented in guards).

**Violation (failing tests):**

| File | What |
|------|------|
| `app/core/models/orchestrator.py` | Lazy/local imports of `app.services.infrastructure` and `app.services.model_chat_runtime` (instrumented chat path). |

**Note:** `orchestrator.py` already has a **documented** exception for `app.providers` in `KNOWN_IMPORT_EXCEPTIONS`. The **services** imports are **not** in that exception list → guards fail.

### 1.4 `services` importing `gui`

**Rule:** Forbidden except documented exceptions (`KNOWN_SERVICE_GUI_EXCEPTIONS` currently empty).

**Status:** **No failing test** for `test_services_do_not_import_gui` in the latest run. Service layer does not regress this guard.

### 1.5 `services` importing provider **classes** (orchestrator governance)

**Rule:** `tests/architecture/test_provider_orchestrator_governance_guards.py::test_services_do_not_import_provider_classes`

**Violations at audit time (2026-03-24):**

| File | Import |
|------|--------|
| `app/services/model_orchestrator_service.py` | `LocalOllamaProvider`, `CloudOllamaProvider` |
| `app/services/unified_model_catalog_service.py` | `CloudOllamaProvider` |

**Intent (per test message):** Services should use infrastructure / client facades, not concrete provider types directly.

**Update 2026-03-30:** This targeted finding is improved. The service-layer imports above were removed; provider-adjacent helper access is now bundled behind the existing service-side facade in `app/services/model_orchestrator_service.py`, and `app/services/unified_model_catalog_service.py` no longer imports provider helpers directly. This narrows the remaining architecture work but does **not** by itself close the other open items in this audit.

### 1.6 `gui` importing `providers`

**Rule:** `test_gui_does_not_import_providers_directly`; exceptions: `main.py` (and config documents `settings_dialog` — verify against current `KNOWN_GUI_PROVIDER_EXCEPTIONS`: only `main.py` listed).

**Status:** **Passing** in the latest architecture run (no failure reported for this test).

### 1.7 `ui` importing `gui`

**Rule:** `test_gui_layer_does_not_import_ui_layer` — inverse: **`app/gui` must not import `app.ui.*`**. `KNOWN_GUI_UI_VIOLATIONS` is empty.

**Status:** **Passing.**

### 1.8 `ui_application` importing `gui`

**Rule:** Not encoded in `FORBIDDEN_IMPORT_RULES`. `test_ui_layer_guardrails.py` states a **future tightening** (“ui_application ohne direkte gui-imports”).

**Observed code:**

| File | Import |
|------|--------|
| `app/ui_application/adapters/service_settings_adapter.py` | `app.gui.themes.get_theme_manager`, `app.gui.themes.theme_id_utils.theme_id_to_legacy_light_dark` |

**Assessment:** **Policy gap vs target architecture** for the MVP slice: adapters should ideally depend on theme ports or `ui_themes`/`core` only; today **one adapter** reaches into `app.gui`.

### 1.9 `ui_contracts` / `ui_themes` / `ui_runtime`

**Rules:** `test_ui_contracts_has_no_qt_imports`, `test_ui_themes_python_has_no_app_services`, `test_ui_runtime_core_theme_modules_avoid_services`.

**Status:** **Passing** in the architecture run (no failures in `test_ui_layer_guardrails.py`).

### 1.10 Circular dependencies

**No dedicated “cycle detector” test** was executed. **Static fact:** `core/config/settings.py` → `app.gui.themes.theme_id_utils` is a **forbidden upward** edge; whether a full import cycle occurs at runtime depends on load order. **Guard outcome:** layer violation is already **fail-closed**.

---

## 2. Migration progress: `app/ui` vs `app/gui`

| Finding | Evidence |
|---------|----------|
| **No top-level `app/ui` package** | `glob app/ui/**/*.py` returns **no** matches under `app/ui/`. |
| **Canonical GUI** | `app/gui/` with domains, shell, navigation, legacy under `app/gui/legacy/`. |
| **Residual `app.ui` imports** | Ripgrep for `from app.ui.` / `import app.ui` in `*.py`: **no** production imports; only a **comment** in `app/gui/domains/control_center/agents_ui/__init__.py` and test docstring text. |
| **Guard** | `FORBIDDEN_PARALLEL_PACKAGES` includes `"ui"`; parallel tree not present. `test_ui_only_imported_by_allowed_transition_modules` **passes**. |
| **Docs lag** | `ARCHITECTURE_GUARD_RULES.md` still describes `app.ui.*` re-exports in several bullets; filesystem shows **migration of the `app/ui` package largely complete**, documentation partially historical. |

**Conclusion:** **Canonical = `app/gui`.** Legacy package **`app/ui` is not present** as an active code tree; **`app/gui/workbench/ui/`** is a **nested helper package** (not `app.ui`).

---

## 3. Presenter → Port → Adapter adoption

### 3.1 Infrastructure present

- **Ports:** `app/ui_application/ports/*.py` (chat, prompt studio, deployment, agent tasks, settings, model usage, Ollama settings, AI catalog).  
- **Adapters:** `app/ui_application/adapters/service_*_adapter.py` bridging ports to services.  
- **Presenters:** `app/ui_application/presenters/*_presenter.py` (excluding `base_presenter.py`).

### 3.2 Guard on `presenter_base`

- `test_presenter_base_usage`: **`BasePresenter.run` exists**; **existing `*_presenter.py` files must not import** `app.ui_application.presenter_base` (migration discipline). **Passes.**

### 3.3 Pattern usage in workspaces (examples)

| Area | Evidence |
|------|----------|
| **Chat** | `app/gui/domains/operations/chat/chat_workspace.py` instantiates `ChatPresenter` with a port (`ChatPresenter(..., port=self._chat_port)`). |
| **Prompt Studio** | `prompt_studio_workspace.py` wires `ServicePromptStudioAdapter`, multiple presenters, sinks; mixed with **direct** `get_prompt_service()` in some branches (`uses_port_driven_detail()` gating). |
| **Agent tasks / deployment / settings slices** | Dedicated presenters + ports in `ui_application` (covered by unit tests under `tests/unit/ui_application/`). |

### 3.4 Partial / hybrid presenters

These presenter modules **do not** subclass `BasePresenter` (class name scan):

- `SettingsLegacyModalPresenter` (`settings_legacy_modal_presenter.py`)
- `SettingsModelRoutingPresenter` (`settings_model_routing_presenter.py`)
- `PromptStudioWorkspacePresenter` (`prompt_studio_workspace_presenter.py`)

**Interpretation:** **Adoption is intentional but uneven**: new slices use **Presenter + Port + Adapter**; some modules remain **thin facades** or **legacy-shaped** APIs.

---

## 4. Direct service access inside widgets

**Guard stance:** `SERVICE_GOVERNANCE_POLICY.md` allows **`gui` → `services`**. There is **no** architecture test forbidding `get_chat_service()` inside panels.

**Observed pattern (non-exhaustive):** widespread **`from app.services.* import get_*_service()`** inside `app/gui/domains/operations/chat/panels/` (e.g. `chat_item_context_menu.py`, `chat_navigation_panel.py`, `topic_actions.py`) and elsewhere (see grep hits for `get_chat_service` / `get_project_service` under `app/gui`).

**Architectural intent (target):** For **new** work, MVP-style **sink + presenter + port** reduces scattered service calls; **legacy and chat navigation** still use **direct service singletons**.

---

## 5. Dependency graph stability

| Signal | Status |
|--------|--------|
| **Architecture pytest suite** | 5 failures in the **2026-03-24 audit snapshot** → **not stable** under full `tests/architecture` until re-run and fixed or exceptions updated with review. |
| **GUI domain dependency guards** | `test_no_forbidden_gui_domain_imports` — **passing** (no failure in latest run). |
| **Drift radar artifact** | `docs/04_architecture/ARCHITECTURE_DRIFT_RADAR_STATUS.md` (timestamp 2026-03-24) reports **OK** for scripted categories — **orthogonal** to the 5 pytest failures above; both should be read together. |
| **Root entrypoint guard** | **Failure:** `test_root_entrypoint_scripts_are_allowed` — `run_workbench_demo.py` exists in repo root but is **not** in `ALLOWED_PROJECT_ROOT_ENTRYPOINT_SCRIPTS` in `arch_guard_config.py`. |

---

## 6. Violations list (actionable; audit snapshot plus update)

1. **`test_no_forbidden_import_directions` / `test_core_no_gui_imports` / `test_feature_packages_no_gui_imports`:** `app/core/config/settings.py` imports `app.gui.themes.theme_id_utils`.  
2. **`test_no_forbidden_import_directions`:** `app/core/models/orchestrator.py` imports `app.services.*` (instrumentation path).  
3. **`test_services_do_not_import_provider_classes` (2026-03-24 snapshot):** Earlier hits in `app/services/model_orchestrator_service.py` and `app/services/unified_model_catalog_service.py` were reduced on 2026-03-30 by removing the direct service-side provider-class coupling; re-run the full architecture suite before clearing the wider audit state.  
4. **`test_root_entrypoint_scripts_are_allowed`:** `run_workbench_demo.py` missing from allowlist (or script should move / be removed per policy).

---

## 7. Subsystems still using legacy or non-canonical patterns

| Subsystem / concern | Pattern |
|---------------------|---------|
| **Core config** | `AppSettings` validation reaches into **`app.gui.themes`** (layer violation). |
| **Core orchestrator** | Reaches into **`app.services`** for infrastructure / instrumented runtime (layer violation vs strict `core`-only). |
| **Model / catalog services** | Service-side provider-class imports were reduced on 2026-03-30; remaining provider/orchestrator governance work is now narrower than in the original audit snapshot. |
| **Settings adapter (MVP)** | **`ui_application` → `gui`** for theme manager / theme id utils. |
| **Chat / topic / project panels** | **Direct `get_*_service()`** in widgets (allowed by policy, **not** full presenter-led style). |
| **Prompt Studio** | **Mixed** port-driven paths and **direct `get_prompt_service()`** depending on feature flags / code paths. |
| **Documentation** | `ARCHITECTURE_GUARD_RULES.md` still references **`app.ui`** migration details that no longer match an `app/ui` tree. |
| **Repo root** | Extra demo entrypoint **`run_workbench_demo.py`** vs **allowlist**. |

---

## 8. Subsystems already clean (relative to current guards)

| Area | Why |
|------|-----|
| **`app/gui` → `app.ui` imports** | Guard passes; `KNOWN_GUI_UI_VIOLATIONS` empty. |
| **`app/services` → `app.gui`** | No failure on `test_services_do_not_import_gui`. |
| **`app/gui` → `app.providers` (direct)** | No failure on provider-direct-import guard in latest run. |
| **`ui_contracts` Qt-free** | Passes. |
| **`ui_themes` / theme-runtime service isolation** | Passes configured Python modules check. |
| **GUI domain cross-import bans** | Domain dependency guard passes. |
| **Navigation / screen registry / help index** | Covered by `test_gui_governance_guards.py` — **passing** in suite (no listed failures). |
| **Presenter base discipline** | `presenter_base` not imported by individual presenter modules — passes. |

---

## 9. Scoring notes (transparency)

- The **97.8%** score is **only** the architecture test pass rate; it does **not** include unit/integration tests or coverage.  
- **Failing tests are binary:** any merge gate treating `tests/architecture` as mandatory should treat current state as **non-compliant** until the five issues are resolved or **explicitly** reclassified via `arch_guard_config.py` / policy update after review.

---

## 10. References

- `tests/architecture/arch_guard_config.py` — `FORBIDDEN_IMPORT_RULES`, `KNOWN_IMPORT_EXCEPTIONS`, allowlists.  
- `docs/04_architecture/ARCHITECTURE_GUARD_RULES.md`  
- `docs/04_architecture/SERVICE_GOVERNANCE_POLICY.md`  
- `docs/04_architecture/ARCHITECTURE_DRIFT_RADAR_STATUS.md`  
