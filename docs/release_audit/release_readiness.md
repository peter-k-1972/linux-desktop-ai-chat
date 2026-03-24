# Release readiness — Linux Desktop Chat

**Role:** Release Engineering Lead.  
**Inputs:** `docs/release_audit/system_inventory.md`, `architecture_status.md`, `feature_maturity_matrix.md`, `dead_systems.md`.  
**Evidence dates:** Primarily 2026-03-22–24 as stamped in those reports.

---

## 1. Scoring method (transparent)

Each dimension is scored **0–100**. Scores are **judgement calls** anchored to the audit artefacts, not a full CI run of the entire `tests/` tree in this pass.

| Dimension | Anchors used |
|-----------|----------------|
| **Stability** | Architecture suite pass rate; optional runtime deps (Ollama, Chroma); legacy entrypoints (`app.main`, `gui/legacy` in tests); dead-systems noise (empty packages do not crash runtime). |
| **Architecture cleanliness** | Count and severity of **failing** architecture guards; `ui_application`→`gui` adapter leak; root shims and temporary allowlists (`dead_systems.md`). |
| **Feature completeness** | `feature_maturity_matrix.md` LEVEL 4 vs 3 counts; absence of LEVEL 5; registry gaps (`Tests | —`, missing Help). |
| **Documentation** | Help/QA doc coverage implied by registry rows; `FEATURE_REGISTRY` automation; known doc drift (`system_inventory`, `dead_systems`). |
| **QA reliability** | Breadth of test tree (`system_inventory` / `pytest.ini` markers); architecture gate status; uneven per-feature tests. |

**Overall readiness (0–100)** is a **weighted** blend:

| Dimension | Weight |
|-----------|--------|
| Stability | **22%** |
| Architecture cleanliness | **22%** |
| Feature completeness | **22%** |
| Documentation | **18%** |
| QA reliability | **16%** |

Weights reflect release engineering priority: **stability + architecture + feature shape** together dominate; docs and QA breadth follow.

---

## 2. Dimension scores

### 2.1 Stability — **73 / 100**

**Supporting evidence**

- `architecture_status.md`: **5 failing** tests in `tests/architecture` out of **224** collected (~**97.8%** pass rate for that module only). A branch that treats architecture tests as **release gates** is **not** currently “stable green.”
- Core product flows depend on **optional/local** services (Ollama, Chroma/RAG) — expected for this product class, but increases **environment variance** (`feature_maturity_matrix`: Chat, Knowledge, Providers).
- `dead_systems.md`: **empty packages** (`app/models`, `app/diagnostics`, empty `project_hub`) are hygiene issues, not runtime failures; **legacy** `MainWindow` / `ChatWidget` still anchor many tests — migration risk on change.

**Deductions**

- −15 to −20 for **non-green** architecture gate (if enforced).
- −5 to −10 for **env-dependent** primary features without a single “offline demo” guarantee in this audit.

---

### 2.2 Architecture cleanliness — **69 / 100**

**Supporting evidence**

- Documented **layer violations**: `core`→`gui` (`settings.py`), `core`→`services` (`orchestrator.py`), **service**→**provider class** imports, **root entrypoint** allowlist miss (`run_workbench_demo.py`) — all in `architecture_status.md`.
- **Soft debt**: `service_settings_adapter.py` imports `app.gui.themes` (`ui_application`→`gui`).
- `dead_systems.md`: **multiple C-class** items (root shims, `app/llm` shim, Prompt Studio split, QML skeleton, legacy GUI path).

**Strengths**

- Most **forbidden** directions **hold** (e.g. `gui`↮`ui`, `services`↮`gui`, `ui_contracts` Qt-free per guards).
- **97.8%** of architecture tests still pass — drift is **concentrated**, not chaotic.

---

### 2.3 Feature completeness — **76 / 100**

**Supporting evidence**

- `feature_maturity_matrix.md`: **26 / 33** features at **LEVEL 4** (stable with known gaps), **7 / 33** at **LEVEL 3** (functional but incomplete), **0** at **LEVEL 5**.
- Rough “completeness index” from maturity levels (treat 5=100, 4=82, 3=58, 2=35, 1=10):  
  `(26×82 + 7×58) / 33 ≈ 76.9` → aligns with score **76**.
- **LEVEL 3** clusters: Control Center Providers, QA Gap/Incidents/Replay, Runtime Logs & Agent Activity, Settings Privacy — user-visible or operator-visible, not absent.

**Deductions**

- No feature at **production-ready (LEVEL 5)** per matrix criteria.
- Registry/index gaps: e.g. runtime workspaces **not** in `FEATURE_REGISTRY` (`rd_introspection`, `rd_qa_cockpit`, `rd_qa_observability`).

---

### 2.4 Documentation — **64 / 100**

**Supporting evidence**

- Many registry rows lack **Help** or **QA docs** (`feature_maturity_matrix` / `FEATURE_REGISTRY`): Runtime/Debug sub-features, several Settings categories, some QA surfaces.
- **Strength:** QA & Governance features carry a **large `docs/qa/`** bundle in the registry.
- `system_inventory.md` / `dead_systems.md`: **documentation drift** (e.g. historical `app.ui` mentions vs current tree; designer dummy excluded from narrative docs).

---

### 2.5 QA reliability — **74 / 100**

**Supporting evidence**

- **Strength:** Broad pytest layout (`system_inventory`: **532** test Python files; markers for unit, integration, contract, chaos, architecture, golden_path, etc.).
- **Weakness:** **Five** failing **architecture** tests undermine a **single automated “arch gate”** story.
- **Uneven coverage:** Registry **`Tests | —`** for some workspaces (Incidents, Agent Activity, Privacy); `pytest.ini` defines `context_observability` with **no** matching `@pytest.mark` usages noted in prior audit — marker hygiene gap.

---

## 3. Overall readiness score

| Dimension | Score | Weight | Weighted contribution |
|-----------|-------|--------|------------------------|
| Stability | 73 | 0.22 | **16.06** |
| Architecture cleanliness | 69 | 0.22 | **15.18** |
| Feature completeness | 76 | 0.22 | **16.72** |
| Documentation | 64 | 0.18 | **11.52** |
| QA reliability | 74 | 0.16 | **11.84** |
| **Total** | — | **1.00** | **71.32** |

### **Overall readiness: 71 / 100** (rounded)

**Interpretation:** Solid **internal engineering depth** (breadth of tests, most features at LEVEL 4), but **not** release-station quality for a **1.0** if architecture gates are mandatory and documentation/help parity is expected for all shipped shells.

---

## 4. Release classification recommendation

| Version line | Meaning (per your taxonomy) |
|--------------|-----------------------------|
| **0.8.x** | Unstable beta |
| **0.9.x** | Feature-complete beta |
| **1.0** | Stable release |

### Recommended label: **0.8.x — unstable beta** (current evidence)

**Rationale**

1. **Architecture suite not fully green** — conflicts with “stable” or “feature-frozen beta” if CI blocks on `tests/architecture`.
2. **Overall readiness 71** — squarely in **beta** territory, not GA.
3. **Dead-system / shim debt** — empty packages and compat layers (`dead_systems.md`) are acceptable in beta but **not** polished for 1.0.

### Path toward **0.9.x — feature-complete beta**

- Restore **100%** pass on `tests/architecture` (or explicitly waive with signed architecture exceptions — not recommended without review).
- Close or **document** the seven **LEVEL 3** features: either ship minimal help + tests, or **hide** nav entries until ready (product decision).
- Resolve **provider-orchestrator** and **core↔theme** coupling so model/settings stories are guard-clean.

### Path toward **1.0 — stable**

- Sustained **green** gates (architecture + agreed smoke/integration tier).
- At least **selected** features at **LEVEL 5** (or formal acceptance that some areas are “community/expert only”).
- **Documentation** parity: Help topics for all **default-visible** workspaces; `FEATURE_REGISTRY` regenerated with no orphan nav workspaces.
- **Legacy** test dependency on `ChatWidget` reduced or isolated to a **compat** test module with explicit sunset date.

---

## 5. One-page checklist (next actions)

| Priority | Action | Ties to |
|----------|--------|---------|
| P0 | Fix the **5** failing `tests/architecture` issues | Stability, Architecture, QA |
| P1 | Remove or populate **empty** `app/` packages (`models`, `diagnostics`, `project_hub`) | Dead systems, Architecture hygiene |
| P1 | Decide **Privacy** settings: implement, hide, or document “informational only” | Feature completeness, Documentation |
| P2 | Add **Help** stubs for Runtime/Debug and Settings rows missing `Help` in registry | Documentation |
| P2 | **`run_workbench_demo.py`**: allowlist or move under `scripts/` | Architecture cleanliness |
| P3 | **`agents/farm`**: integrate or archive | Dead systems, Feature completeness |

---

## 6. Source index

| Report | Path |
|--------|------|
| System inventory | `docs/release_audit/system_inventory.md` |
| Architecture status | `docs/release_audit/architecture_status.md` |
| Feature maturity matrix | `docs/release_audit/feature_maturity_matrix.md` |
| Dead systems | `docs/release_audit/dead_systems.md` |

---

*Recompute the numeric score after each significant merge: rerun `pytest tests/architecture`, refresh `FEATURE_REGISTRY`, and update the maturity matrix if workspace scope changes.*
