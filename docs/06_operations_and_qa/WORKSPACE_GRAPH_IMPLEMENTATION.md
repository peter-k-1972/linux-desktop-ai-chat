# Workspace Graph Navigator – Implementation Summary

## Overview

The Workspace Graph provides a visual, clickable map of the system’s workspaces and their relationships. It improves orientation, navigation, and discoverability. The second-stage version adds architecture-aware metadata: help topics, feature registry, trace map, and related workspaces.

---

## 1. Components

| File | Purpose |
|------|---------|
| `app/gui/navigation/workspace_graph.py` | `WorkspaceGraphDialog`, `WorkspaceGraphNode`, `WorkspaceGraphDetailsPanel` |
| `app/gui/navigation/workspace_graph_resolver.py` | Metadata resolution from FEATURE_REGISTRY, TRACE_MAP, HelpIndex |

---

## 2. Integration Points

| Entry Point | How |
|-------------|-----|
| **Command Palette** | Ctrl+K → search "Workspace Graph" or "map" → "Open Workspace Graph" |
| **TopBar** | "Workspace Map" button (system graph icon) next to Status |

---

## 3. Metadata Resolution

**`workspace_graph_resolver.py`** – `resolve_metadata(workspace_id, area_id, title, description)` returns `WorkspaceNodeMetadata`:

| Field | Source |
|-------|--------|
| `short_description` | NavItem.tooltip, WORKSPACE_INFO |
| `help_topic_id`, `help_topic_title` | HelpIndex.get_topic_by_workspace, FEATURE_REGISTRY, TRACE_MAP |
| `help_article_path` | Scan of help/ for topic id |
| `feature_names`, `code_module_paths`, `service_paths`, `test_paths` | docs/FEATURE_REGISTRY.md |
| `related_workspace_ids` | Static RELATED_WORKSPACES mapping |

Graceful fallback when sources are missing.

---

## 4. Details Panel

When hovering a node, the right-side panel shows:

- Workspace name, area
- Short description
- **Open Workspace** – navigates and closes dialog
- **Open Help** – opens HelpWindow with mapped topic (or hidden if none)
- Feature references
- Code module paths (up to 3, "+N more" if more)
- See also: related workspaces

---

## 5. Help Integration

- If workspace has mapped help topic (HelpIndex or FEATURE_REGISTRY): show title, "Open Help" button
- "Open Help" opens HelpWindow with `initial_topic_id`
- If no help: show "No help article mapped", hide "Open Help" button

---

## 6. Feature Registry Integration

- Parses `docs/FEATURE_REGISTRY.md` (table format)
- Extracts: Workspace, Code, Services, Help, Tests per feature
- Details panel shows feature name(s) and code paths

---

## 7. Trace Map Integration

- Parses `docs/TRACE_MAP.md` section 3 (Workspace → Help)
- Fallback for help topic when HelpIndex has no mapping

---

## 8. Related Workspaces

Static mapping in `RELATED_WORKSPACES` (e.g. Chat → Knowledge, Prompt Studio, Agents). Shown as "See also" in details panel.

---

## 9. Navigation

- Click node → `workspace_host.show_area()` → dialog closes
- "Open Workspace" in details panel → same
- Breadcrumb and sidebar update via existing signals

---

## 10. Validation Steps

1. Start app: `python run_gui_shell.py`
2. Open Workspace Graph (TopBar or Ctrl+K)
3. Hover over Chat → details panel shows help, features, code paths, related
4. Click "Open Help" → HelpWindow opens with chat_overview
5. Click "Open Workspace" or node → navigates, dialog closes
6. Hover over workspace without help → "No help article mapped"
