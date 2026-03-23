# Command Center & Dashboard Unification

**Date:** 2026-03-16  
**Scope:** `app/ui/command_center/*` vs `app/gui/domains/dashboard/*`  
**Role:** Software Architect

---

## 1. Overlapping Panels

| Concept | UI (`command_center`) | GUI (`dashboard`) | Overlap |
|--------|------------------------|-------------------|---------|
| **QA Status** | Executive Status cards (Tests, Gaps, Orphan, QA Health) + QA Health group + QA Drilldown | `QAStatusPanel` – "Tests, Coverage, Gaps, Governance." | ✓ Same domain |
| **System Status** | Runtime/Debug group – link to Chat Debug-Panel | `SystemStatusPanel` – "Bereit", "Ollama, RAG, Agents" | ✓ Same domain |
| **Active Work** | Next Actions group (from `QADashboardAdapter`) | `ActiveWorkPanel` – "Laufende Chats, Agent Tasks, Verifikationen." | ✓ Same domain |
| **Incidents** | Incident Operations view (drilldown) | `IncidentsPanel` – "Offene Incidents, Bindings, Replay-Status." | ✓ Same domain |

**Conclusion:** All four dashboard panels overlap conceptually with UI command_center sections. The UI has real data and drilldowns; the GUI has static placeholders.

---

## 2. Unique Functionality

### 2.1 UI (`command_center`) – Unique

| Feature | Module | Description |
|---------|--------|--------------|
| **QADashboardAdapter** | `app/qa/dashboard_adapter.py` | Real data: Executive Status, Coverage, Subsystems, Gaps, Next Actions |
| **Executive Status Cards** | `command_center_view` | Tests, Gaps, Orphan, QA Health – live from adapter |
| **Geführte Operations-Schritte** | `command_center_view` | Orphan Review, QA Verification, Incident-Status, Audit Follow-up (nicht Operations → Workflows) |
| **Operations Center** | `command_center_view` | QA Ops, Incident Ops, Review Ops, Audit Ops – 4 drilldown buttons |
| **QA Health / Coverage** | `command_center_view` | Coverage axes, gap count per axis |
| **Gap-Report Hinweise** | `command_center_view` | Gap warnings from adapter |
| **Subsystem-Übersicht** | `command_center_view` | Clickable subsystem cards → SubsystemDetailView |
| **Next Actions** | `command_center_view` | From adapter |
| **Quick Links** | `command_center_view` | Gap Report, Coverage Map, Test Inventory – open files |
| **QA Drilldown** | `qa_drilldown_view` | Gaps table, Coverage axes, Orphan Backlog |
| **Subsystem Detail** | `subsystem_detail_view` | Tests, Domains, Hints per subsystem |
| **Runtime Debug** | `runtime_debug_view` | Link to Chat Debug-Panel |
| **Governance** | `governance_view` | Freeze-Zonen: QA-Kern, Produkt, Experimentell |
| **QA Operations** | `qa_operations_view` | Verifikationsstatus, Artefakte |
| **Incident Operations** | `incident_operations_view` | Incidents, Bindings, Replay |
| **Review Operations** | `review_operations_view` | Orphan Backlog, Review-Batches |
| **Audit Operations** | `audit_operations_view` | Audit-Follow-ups, Technical Debt |

### 2.2 GUI (`dashboard`) – Unique

| Feature | Module | Description |
|---------|--------|-------------|
| **BaseScreen integration** | `dashboard_screen` | `NavArea.COMMAND_CENTER`, shell navigation |
| **BasePanel styling** | `panels/*` | Consistent card styling via `BasePanel` |
| **Grid layout** | `dashboard_screen` | 2×2 grid of panels |
| **Placeholder content** | All 4 panels | Static labels, no backend |

**Conclusion:** The UI has the full implementation; the GUI provides shell integration and placeholder structure.

---

## 3. Entry Points

| Entry | Path | Screen/View |
|-------|------|-------------|
| **Standard (run_gui_shell)** | Nav → Kommandozentrale | `DashboardScreen` (4 placeholder panels) |
| **Legacy (run_legacy_gui)** | Toolbar "Kommandozentrale" | `CommandCenterView` (full QA dashboard) |

**Problem:** Users of the standard shell see placeholders; legacy users see the full dashboard.

---

## 4. Unified Dashboard Architecture

### 4.1 Target Structure

```
app/gui/domains/dashboard/
├── dashboard_screen.py          # Host – keeps BaseScreen, NavArea
├── command_center_content.py    # NEW: Wraps or embeds CommandCenterView content
├── panels/
│   ├── executive_status_panel.py # NEW: Executive cards (from UI)
│   ├── qa_health_panel.py        # NEW: QA Health + Drilldown button
│   ├── active_work_panel.py      # UPDATED: Next Actions (from adapter)
│   ├── incidents_panel.py        # UPDATED: Incidents summary + link to Incident Ops
│   └── system_status_panel.py    # UPDATED: Runtime/Debug link
└── views/                       # NEW: Drilldown views (moved from ui)
    ├── qa_drilldown_view.py
    ├── subsystem_detail_view.py
    ├── runtime_debug_view.py
    ├── governance_view.py
    ├── qa_operations_view.py
    ├── incident_operations_view.py
    ├── review_operations_view.py
    └── audit_operations_view.py
```

### 4.2 Unification Strategy

**Phase 1 – Fast unification (embed):**

1. Replace `DashboardScreen` content with `CommandCenterView` (or a shell-adapted variant).
2. Remove "← Zurück zum Chat" or adapt to shell navigation (e.g. back to Operations).
3. Wire theme from shell.
4. Remove the 4 placeholder panels.

**Phase 2 – Clean migration (refactor):**

1. Move drilldown views from `ui/command_center/` to `gui/domains/dashboard/views/`.
2. Create dashboard panels that use `QADashboardAdapter` directly.
3. Use `BasePanel` for consistent styling.
4. Deprecate `CommandCenterView` and `ui/command_center/`.

---

## 5. Modules to Move

| Source | Target | Notes |
|--------|--------|-------|
| `ui/command_center/qa_drilldown_view.py` | `gui/domains/dashboard/views/qa_drilldown_view.py` | Adapt back navigation for shell |
| `ui/command_center/subsystem_detail_view.py` | `gui/domains/dashboard/views/subsystem_detail_view.py` | Same |
| `ui/command_center/runtime_debug_view.py` | `gui/domains/dashboard/views/runtime_debug_view.py` | Same |
| `ui/command_center/governance_view.py` | `gui/domains/dashboard/views/governance_view.py` | Same |
| `ui/command_center/qa_operations_view.py` | `gui/domains/dashboard/views/qa_operations_view.py` | Same |
| `ui/command_center/incident_operations_view.py` | `gui/domains/dashboard/views/incident_operations_view.py` | Same |
| `ui/command_center/review_operations_view.py` | `gui/domains/dashboard/views/review_operations_view.py` | Same |
| `ui/command_center/audit_operations_view.py` | `gui/domains/dashboard/views/audit_operations_view.py` | Same |

**Shared (keep in place):**

- `app/qa/dashboard_adapter.py` – used by both; no move
- `app/qa/operations_adapter.py` – used by operations views
- `app/qa/drilldown_models.py` – DTOs

---

## 6. Modules to Remove

| Module | When | Reason |
|--------|------|--------|
| `ui/command_center/command_center_view.py` | After Phase 2 | Replaced by `dashboard_screen` + content |
| `ui/command_center/qa_drilldown_view.py` | After move | Moved to gui |
| `ui/command_center/subsystem_detail_view.py` | After move | Moved to gui |
| `ui/command_center/runtime_debug_view.py` | After move | Moved to gui |
| `ui/command_center/governance_view.py` | After move | Moved to gui |
| `ui/command_center/qa_operations_view.py` | After move | Moved to gui |
| `ui/command_center/incident_operations_view.py` | After move | Moved to gui |
| `ui/command_center/review_operations_view.py` | After move | Moved to gui |
| `ui/command_center/audit_operations_view.py` | After move | Moved to gui |
| `ui/command_center/` (package) | After all moves | Empty |
| `gui/domains/dashboard/panels/qa_status_panel.py` | Phase 1 | Replaced by real QA content |
| `gui/domains/dashboard/panels/active_work_panel.py` | Phase 1 | Replaced by real content |
| `gui/domains/dashboard/panels/incidents_panel.py` | Phase 1 | Replaced by real content |
| `gui/domains/dashboard/panels/system_status_panel.py` | Phase 1 | Replaced by real content |

**Note:** Placeholder panels can be removed in Phase 1 when embedding `CommandCenterView`. In Phase 2, new `BasePanel`-based panels replace the embedded view.

---

## 7. Summary

| Output | Result |
|--------|--------|
| **Unified dashboard structure** | `DashboardScreen` hosts full Kommandozentrale content. Overview + 8 drilldown views. Uses `QADashboardAdapter`. |
| **Modules to move** | 8 drilldown views: `qa_drilldown`, `subsystem_detail`, `runtime_debug`, `governance`, `qa_operations`, `incident_operations`, `review_operations`, `audit_operations` → `gui/domains/dashboard/views/`. |
| **Modules to remove** | Entire `ui/command_center/` after migration. Four placeholder panels (`qa_status`, `active_work`, `incidents`, `system_status`) when replaced. |

### Migration Order

1. **Phase 1:** Embed `CommandCenterView` in `DashboardScreen`; remove placeholder panels; adapt back navigation.
2. **Phase 2:** Move views to `gui/domains/dashboard/views/`; refactor overview into `BasePanel`-based panels; remove `ui/command_center/`.
