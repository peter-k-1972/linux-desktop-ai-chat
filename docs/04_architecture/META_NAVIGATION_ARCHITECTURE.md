# Meta Navigation Architecture

## Overview

Unified navigation under a shared metadata layer. Single source of truth for all navigable entities.

---

## 1. Navigation Registry

**`app/core/navigation/navigation_registry.py`**

Defines all navigable entities with:
- `id` – unique key (workspace_id or area_id)
- `title` – display name
- `area` – area_id
- `workspace` – workspace_id or None for area-only
- `description` – short description
- `help_topic_id` – optional
- `feature_ref` – optional feature name
- `icon` – icon registry key

**Functions:**
- `get_all_entries()` – all entries by id
- `get_entry(id)` – single entry
- `get_sidebar_sections()` – sections with entry ids for sidebar grouping

---

## 2. Resolver Layers

| Module | Reads | Purpose |
|--------|-------|---------|
| `app/core/navigation/feature_registry_loader.py` | docs/FEATURE_REGISTRY.md | workspace → code, services, help, tests |
| `app/core/navigation/help_topic_resolver.py` | HelpIndex, TRACE_MAP | workspace → help topic id/title |
| `app/core/navigation/trace_map_loader.py` | docs/TRACE_MAP.md | workspace → help, workspace → code, services |

---

## 3. Refactored Integrations

| System | Change |
|--------|--------|
| **Sidebar** | `sidebar_config.get_sidebar_sections()` builds from registry |
| **Breadcrumbs** | `WORKSPACE_INFO` built from registry |
| **Command Palette** | `palette_loader` (gui/commands) uses registry for WORKSPACE_TO_NAV, area commands |
| **Workspace Graph** | Uses `sidebar_config` (registry-backed) |
| **Help Context** | Uses `help_topic_resolver` for context help |

---

## 4. Files Changed

| File | Change |
|------|--------|
| `app/core/navigation/` | **New** – registry, nav_areas, loaders, resolvers |
| `app/core/navigation/navigation_registry.py` | Central registry |
| `app/core/navigation/feature_registry_loader.py` | Parse FEATURE_REGISTRY.md |
| `app/core/navigation/help_topic_resolver.py` | Resolve workspace → help |
| `app/core/navigation/trace_map_loader.py` | Parse TRACE_MAP.md |
| `app/core/navigation/nav_areas.py` | NavArea constants (moved from gui) |
| `app/gui/navigation/nav_areas.py` | Re-exports from core |
| `app/gui/navigation/sidebar_config.py` | Builds from registry |
| `app/gui/breadcrumbs/manager.py` | WORKSPACE_INFO from registry |
| `app/gui/commands/palette_loader.py` | Uses registry, help_topic_resolver (verschoben aus core) |
| `app/gui/navigation/workspace_graph_resolver.py` | Uses core loaders |

---

## 5. Metadata Resolution

- **Registry** – canonical id, title, area, workspace, description, help_topic_id, feature_ref
- **Feature registry** – code paths, services, tests (from docs)
- **Help resolver** – HelpIndex primary, TRACE_MAP fallback
- **Trace map** – workspace → help, workspace → code

---

## 6. Validation Steps

1. `python -c "from app.core.navigation import get_all_entries; print(len(get_all_entries()))"` → 34
2. `python run_gui_shell.py` – app starts
3. Sidebar shows sections from registry
4. Command Palette (Ctrl+K) – search works, navigation works
5. Workspace Graph – opens, nodes navigate
6. `pytest tests/behavior/ux_behavior_simulation.py tests/behavior/ux_regression_tests.py` – all pass
