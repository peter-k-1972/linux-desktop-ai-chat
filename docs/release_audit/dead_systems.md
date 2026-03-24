# Dead systems & architectural dead ends — audit

**Role:** Technical debt auditor.  
**Method:** Static search (imports, directory contents, registry/docs cross-check). **Not** a full call-graph or coverage tool run—findings are **likely** dead ends where evidence is stated.  
**Classifications:** **A** = remove immediately · **B** = archive · **C** = refactor · **D** = keep (still valuable or intentionally retained).

---

## Summary table

| # | Subsystem / artifact | Classification | Primary evidence |
|---|----------------------|----------------|-------------------|
| 1 | `app/models/` (empty package) | **A** | Directory exists under `app/` with **no** `.py` sources; no `app.models` imports found. |
| 2 | `app/diagnostics/` (empty package) | **A** | Only `__pycache__/`; **no** `app.diagnostics` imports in the repo. |
| 3 | `app/gui/domains/project_hub/` (empty tree) | **A** | No `.py` files (only `__pycache__`); **no** `project_hub` references in `app/`. |
| 4 | `app/agents/farm/` (agent catalog) | **B** / **C** | Implemented + unit-tested; **no** imports from other `app/` packages (only `app/agents/farm/*` and `tests/unit/agents/test_agent_farm_catalog.py`). Dead as a **product integration** until wired into agent registry/UI. |
| 5 | `app/llm/` (compat re-exports) | **C** | `__init__.py` documents move to `app.core.llm`; **no** `from app.llm` / `import app.llm` consumers found—canonical usage is `app.core.llm`. |
| 6 | `prompt_studio_detail_sink.py` (re-export) | **C** | `app/gui/domains/operations/prompt_studio/prompt_studio_detail_sink.py` re-exports `PromptDetailSink` from `app.gui.domains.prompt_studio` (“bitte … bevorzugen”)—duplicate surface. |
| 7 | Split Prompt Studio paths | **C** | Full workspace under `app/gui/domains/operations/prompt_studio/`; parallel mini-package `app/gui/domains/prompt_studio/` holds only `prompt_detail_sink.py`—structural duplication. |
| 8 | `app/gui_designer_dummy/` | **D** | **Not** imported by runtime Python; `.ui` stubs for Qt Designer (`README_DESIGNER_DUMMY.md`). Listed in `tools/doc_drift_check.py` as non-doc path. Keep as **design asset**; do not treat as executable subsystem. |
| 9 | `app/main.py` (`MainWindow` legacy) | **B** / **C** | Module header: **LEGACY**, not standard start; `archive/run_legacy_gui.py` delegates here. Still imported by **many** tests + `app.main.main`. **Not** safe to delete without test migration. |
| 10 | `app/gui/legacy/` | **C** | Heavy use: `ChatWidget` etc. in tests, `app.main`, contracts—**not** unused. Architectural dead-end **as primary UI**, not as artifact. |
| 11 | Root shims `app/db.py`, `app/ollama_client.py`, `app/critic.py` | **C** | `TEMPORARILY_ALLOWED_ROOT_FILES` in `arch_guard_config.py`; `app.db` still imported from **tests** (not necessarily from production `app/gui`). Migrate consumers to `app.core.db` / canonical modules. |
| 12 | `app/ui_runtime/qml/qml_runtime.py` | **C** | Docstring: “architektonisches Skelett”; tests only assert `activate` raises—**no** production QML shell integration observed. Either integrate or mark explicitly experimental in docs. |
| 13 | `run_workbench_demo.py` (repo root) | **C** | **Valid** launcher for `MainWorkbench`; fails **root entrypoint guard** (`architecture_status.md`). Move under `scripts/` or add allowlist—**not** dead code. |
| 14 | Settings **Privacy** category UI | **C** | `privacy_category.py`: static `QLabel` copy only—no settings keys, no tests in `FEATURE_REGISTRY` for `settings_privacy`. Placeholder, not abandoned (nav entry exists). |
| 15 | `archive/` (legacy GUI + docs) | **D** | Explicit archive; `main.py` points here for legacy start. Keep; do not merge back without review. |

---

## Detailed findings

### A — Remove immediately

**1. `app/models/`**  
- **Evidence:** `find` shows no Python modules; grep shows no `app.models` usage.  
- **Risk:** Low if nothing registers this namespace (verify one-off dynamic imports before delete).  
- **Action:** Delete empty package directory or add a one-line `README` if the name is reserved—otherwise removal reduces confusion.

**2. `app/diagnostics/`**  
- **Evidence:** No source files; no importers.  
- **Action:** Remove directory or implement the intended module; current state is a **ghost package**.

**3. `app/gui/domains/project_hub/`**  
- **Evidence:** Empty except `__pycache__`; no code references.  
- **Action:** Remove folder; if a feature is planned, recreate from a tracked spec.

---

### B — Archive

**4. `app/agents/farm/`**  
- **Evidence:** Self-contained catalog loader + `default_catalog.json`; **only** `tests/unit/agents/test_agent_farm_catalog.py` references it outside the package. No wiring to `agent_service`, registry, or GUI.  
- **Interpretation:** **Experimental data layer** without integration points—classic dead-end until adopted.  
- **Action:** Either **archive** under `archive/` or `experimental/` with a short README, or **promote** (classification **C**) by connecting to agent discovery.

**9. `app/main.py` (legacy `MainWindow`)**  
- **Evidence:** Marked legacy; canonical shell is `run_gui_shell.py` / `main.py` at repo root.  
- **Action:** Keep until tests stop importing `MainWindow`; then **archive** module or shrink to a thin compatibility shim. **Do not “remove immediately”**—high coupling to test suite.

---

### C — Refactor

**5. `app/llm/`**  
- **Evidence:** Re-exports `app.core.llm` only; **zero** `from app.llm` usages found.  
- **Action:** Deprecation period + delete package, or grep CI gate to prevent new imports; update any external docs still citing `app.llm`.

**6–7. Prompt Studio duplicate / re-export**  
- **Evidence:** `prompt_studio_detail_sink.py` is a pass-through; real sink lives under `app/gui/domains/prompt_studio/prompt_detail_sink.py`.  
- **Action:** Collapse imports to a single canonical module; delete re-export file after updating call sites.

**10. `app/gui/legacy/`**  
- **Evidence:** Dozens of test + `app.main` imports; `ChatWidget` still central to many automated scenarios.  
- **Action:** **Gradually** route product UI through `operations/chat` + shell; migrate tests to workspace-level fixtures; then shrink legacy surface. Class **A** is inappropriate until replacement coverage exists.

**11. Root `app/db.py`, `app/ollama_client.py`, `app/critic.py`**  
- **Evidence:** Governance explicitly flags temporary root files; `app.critic` still used by `tests/unit/test_critic_review_response.py`; `app.db` by multiple tests.  
- **Action:** Move implementations under `app/core/` or `app/services/` and update imports; remove from `TEMPORARILY_ALLOWED_ROOT_FILES` when clean.

**12. `QmlRuntime` skeleton**  
- **Evidence:** `app/ui_runtime/qml/qml_runtime.py` describes skeleton behaviour; tests treat it as non-production.  
- **Action:** If QML is not on the roadmap, move to `experimental/` or document “not shipped”; if on roadmap, define a single integration owner (shell vs workbench).

**13. `run_workbench_demo.py`**  
- **Evidence:** Functional demo; excluded from `ALLOWED_PROJECT_ROOT_ENTRYPOINT_SCRIPTS`.  
- **Action:** Relocate to `scripts/workbench_demo.py` (or add allowlist + policy entry)—**refactor packaging**, not deletion.

**14. Settings Privacy panel**  
- **Evidence:** Informational labels only; registry lists no tests/help for `settings_privacy`.  
- **Action:** Implement real controls + persistence + tests, or hide entry until scope is defined (product decision).

---

### D — Keep

**8. `app/gui_designer_dummy/`**  
- **Evidence:** Designer-only `.ui` files; no runtime import dependency.  
- **Action:** Retain for UI design workflow; optionally symlink or document path in contributor guide.

**15. `archive/`**  
- **Evidence:** Explicit legacy entrypoint and deprecated docs.  
- **Action:** Keep; periodic review to avoid duplicate living code outside `archive/`.

---

## Explicitly *not* classified as dead

| Area | Why |
|------|-----|
| **`run_gui_shell` / shell MainWindow** | Canonical product entry. |
| **`app/gui/domains/debug/`** | `ContextInspectionPanel` imported from `chat_workspace.py` and `introspection_workspace.py`. |
| **`app/ui_application` / ports / adapters** | Active MVP wiring for multiple workspaces. |
| **`app/core/context`, replay, QA services** | Integrated with CLI/tests per feature registry. |

---

## Suggested order of operations (release hygiene)

1. **A** items (empty packages / empty domain folder)—quick win, low risk after grep.  
2. **C** root shims and **`run_workbench_demo.py`** location—satisfy architecture guards.  
3. **C** Prompt Studio re-export collapse—localised refactor.  
4. **B/C** **`agents/farm`**—product call: wire or archive.  
5. **C** **`app/llm`** removal after deprecation check.  
6. **C** legacy **`MainWindow`** / **`gui/legacy`**—long-running; track as its own epic.

---

*Re-run this audit after large refactors; consider `vulture` or import-graph tooling for a stricter unused-module pass.*
