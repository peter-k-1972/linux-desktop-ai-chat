# Version strategy — product recommendation

**Role:** Product Strategist.  
**Inputs:** `docs/release_audit/release_readiness.md` (overall **71/100**), `architecture_status.md`, `feature_maturity_matrix.md`, `dead_systems.md`, `system_inventory.md`.  
**External signal:** `docs/RELEASE_ACCEPTANCE_REPORT.md` cites **v0.9.0** / tag `v0.9.0`.

---

## Strategy options (decision frame)

| Option | Label | Fit to current audit |
|--------|--------|----------------------|
| **A** | Stay on **0.9.x** | **Strong** — matches existing **v0.9.0** story; use **patch/minor** for stabilization without resetting narrative. |
| **B** | Release **1.0** | **Poor** — readiness **71**, **5** failing architecture guards, **0** features at maturity LEVEL 5; would over-promise stability. |
| **C** | **0.10** stabilization branch / line | **Optional** — valid if the org wants a **visible phase change** after 0.9.x; not required technically. |
| **D** | **Major refactor** before any release | **Poor as gate** — drift is **concentrated**; audit points to **surgical** fixes, not a big-bang rewrite that freezes value delivery. |

---

## Recommended strategy

### Primary: **A — stay on 0.9.x**

### Recommended next version: **`0.9.1`** (first *stabilization-first* release)

**Optional variant:** If product marketing wants a clear “new chapter” without calling it 1.0, ship the same work as **`0.10.0`** (strategy **C**) *after* `0.9.1`–`0.9.2`, or use a **`stabilization/0.9.x`** branch name while still tagging **0.9.1**.

---

## Rationale

1. **Do not regress the version story** — You already positioned **v0.9.0**. Dropping to **0.8.x** (as pure engineering severity might suggest) would confuse users and partners; instead, treat **0.9.x** as *feature-rich beta* and use **patches** to improve truthfulness (stability, gates, docs).

2. **1.0 is a promise** — `release_readiness.md` ties **1.0** to sustained green gates, help parity, and explicit acceptance of expert-only areas. At **71/100** with **non-green** `tests/architecture`, **B** would damage trust.

3. **0.10 / stabilization branch (C)** is a **communications tool**, not a technical necessity — Use **C** if you need a roadmap headline (“0.10 = hardening line”). Otherwise **0.9.1, 0.9.2, …** keeps semver simple.

4. **Major refactor (D)** — Risk of **months** without shippable increments. The audit’s **dead_systems** and **architecture_status** items are **bounded** (P0 arch fixes, empty packages, provider imports, theme decoupling). Package that as **milestones**, not a single “refactor release.”

---

## Milestone roadmap

Roadmap is **ordered**; dates are **not** fixed—use your cadence.

### M1 — **Gate integrity** (target: `0.9.1`)

**Goal:** Release engineering truth matches marketing (“beta, improving”).

| Deliverable | Source |
|-------------|--------|
| **100% pass** on `tests/architecture` (fix 5 failures) | `architecture_status.md` |
| Root entrypoint policy: **`run_workbench_demo.py`** allowlisted or moved | `architecture_status`, `dead_systems` |
| Remove **ghost packages** (`app/models`, `app/diagnostics`, empty `project_hub`) or document intent | `dead_systems` |

**Exit criteria:** CI can block merge on architecture suite without exception.

---

### M2 — **Hygiene & debt burn-down** (target: `0.9.2`)

**Goal:** Fewer sharp edges for contributors and power users.

| Deliverable | Source |
|-------------|--------|
| Resolve or formally waive **core↔gui** theme validation and **core→services** orchestrator path (policy + code) | `architecture_status` |
| **Provider-class** imports removed from named services or exceptions documented in guard config | `architecture_status` |
| **`ui_application` → `gui`** theme dependency reduced (adapter / port) | `architecture_status` |
| Deprecate **`app/llm`** shim; collapse **Prompt Studio** duplicate re-export | `dead_systems` |

**Exit criteria:** Second architecture audit pass with **0** new unlisted violations.

---

### M3 — **Feature truthfulness** (target: `0.9.3` or fold into `0.9.2`)

**Goal:** What ships in the sidebar matches quality users infer.

| Deliverable | Source |
|-------------|--------|
| **LEVEL 3** features: add **tests** and/or **Help** for Incidents, Agent Activity, Replay Lab, Providers, Logs, Gap Analysis, **or** hide until ready | `feature_maturity_matrix` |
| **Privacy** settings: real controls **or** “informational only” copy + nav visibility decision | `dead_systems`, maturity matrix |
| Regenerate **`FEATURE_REGISTRY`**; add missing runtime workspaces to inventory | `feature_maturity_matrix` |

**Exit criteria:** No registry row with **Tests | —** for **default-visible** nav items (or explicit “preview” badge in product).

---

### M4 — **1.0 candidate** (only after M1–M3)

**Goal:** Earn **strategy B** (`1.0`).

| Deliverable | Source |
|-------------|--------|
| Readiness **≥ ~85** on the same weighted model (or updated rubric) | `release_readiness.md` |
| At least **core user journeys** at **LEVEL 5** *or* documented exclusions | `feature_maturity_matrix` |
| **Documentation** score uplift: Help for all default workspaces | `release_readiness` |
| Decision on **`agents/farm`**: ship integrated **or** archive out of `app/` | `dead_systems` |

**Release classification:** **`1.0.0`** only when `release_readiness` and leadership sign-off align.

---

## If you must pick exactly one letter

| Letter | Verdict |
|--------|---------|
| **A** | **Recommended** — **`0.9.1`** next. |
| **B** | **Defer** — use after M4. |
| **C** | **Optional** — use **`0.10.0`** *or* a named stabilization branch if you need a phase narrative; not mutually exclusive with **A**. |
| **D** | **Do not** block releases on a monolithic refactor; use **M1–M3** incremental work instead. |

---

## Summary one-liner

**Ship `0.9.1` as a stabilization-first patch on the existing 0.9 line; keep `1.0` for after architecture gates are green and visible features match documented quality—use `0.10` only if you need a marketing-visible “hardening generation” label.**

---

*Revisit this document after each tagged release; link `CHANGELOG` entries to M1–M4 milestones.*
