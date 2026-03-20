# Architecture Proposal: Repository Structure, Documentation & Help System

**Project:** Linux Desktop Chat  
**Version:** 1.0  
**Date:** 2026-03-16  
**Status:** Strategy Document — No Implementation Yet

---

## Executive Summary

This proposal defines a unified architecture for three interconnected areas:

1. **Repository structure** — Clear separation of concerns, elimination of duplication, and logical layering
2. **Documentation system** — Multi-audience documentation with a single source of truth
3. **In-app help system** — Browsable and context-sensitive help, integrated with chat, without content duplication

**Core principle:** Documentation and help content share a single source of truth. Markdown files in `help/` serve both external readers and the in-app Help Center; the same content can be indexed for RAG and chat-assistant context.

**Current state (audit findings):**
- Root-level entry points (`main.py`, `run_gui_shell.py`, `run_legacy_gui.py`) with unclear hierarchy
- Overlapping `app/ui` (legacy) and `app/gui` (primary) — gui still depends on ui components
- 139+ docs in flat `docs/` plus deep `docs/qa/` — mixed audiences, no clear taxonomy
- Help system loads from `docs/*.md` with hardcoded `DOC_TO_CATEGORY` mapping; no workspace→help mapping; no chat integration
- Assets scattered across `app/gui/icons/`, `app/resources/`, `app/gui/themes/`

---

## Part 1 — Repository Target Structure

### 1.1 Current Issues Identified

| Issue | Location | Impact |
|-------|----------|--------|
| Duplicated directories | `app/ui` vs `app/gui/domains` | Unclear ownership; gui imports from ui |
| Unclear module boundaries | `app/` root has `main.py`, `db.py`, `chat_widget.py` alongside `app/main.py` | Legacy vs new entry points mixed |
| Legacy/abandoned code | `run_legacy_gui.py`, `app/main.py` | Confusion about canonical entry |
| Overlapping UI layers | Chat, Knowledge, Prompt Studio, Settings in both ui and gui | Two KnowledgeWorkspace implementations |
| Scattered documentation | 100+ files in `docs/`, `docs/qa/`, root-level `*.md` | No taxonomy, mixed audiences |
| Misplaced assets | Icons in `app/gui/icons/svg/` and `app/resources/icons/` | Inconsistent paths |
| Inconsistent naming | `RAG_ARCHITEKTUR.md` vs `rag.md`; `ai_studio.md` vs `AI_STUDIO` | Mixed languages and conventions |

### 1.2 Target High-Level Layout

```
Linux-Desktop-Chat/
├── src/                    # All application source code
├── docs/                   # Structured documentation (see Part 2)
├── tests/                  # All tests
├── scripts/                # Build, dev, and ops scripts
├── assets/                 # Icons, themes, media (single location)
├── help/                   # Single source of truth for help content
├── tools/                  # Dev tooling (lint, format, generators)
├── archive/                # Deprecated code, legacy docs
├── main.py                 # Single entry point (delegates to src)
├── requirements.txt
└── README.md
```

### 1.3 Source Code Structure (`src/`)

```
src/
├── shell/                  # Application shell, main window, docking
├── ui/                     # UI components (consolidated from app/ui + app/gui)
│   ├── shared/             # Layout constants, base workspaces, widgets
│   ├── navigation/         # Sidebar, breadcrumbs, command palette
│   ├── themes/             # QSS, theme manager
│   ├── icons/              # Icon registry, SVG assets (symlink or copy from assets/)
│   └── monitors/           # Bottom panel, logs, metrics, events
├── domains/                # Domain-specific screens and workspaces
│   ├── command_center/     # Dashboard
│   ├── project_hub/        # Project Hub
│   ├── operations/         # Chat, Knowledge, Prompt Studio, Agents, Projects
│   ├── control_center/     # Models, Providers, Agents, Tools, Data Stores
│   ├── qa_governance/      # Test Inventory, Coverage Map, Incidents, Replay Lab
│   ├── runtime_debug/     # EventBus, Logs, Metrics, LLM Calls, Agent Activity
│   └── settings/           # All settings workspaces
├── services/               # Business logic services
│   ├── chat/
│   ├── agents/
│   ├── knowledge/
│   ├── prompts/
│   └── ...
├── data/                   # Data access, persistence
│   ├── db/
│   ├── rag/
│   └── ...
├── integrations/          # External integrations (Ollama, ChromaDB)
├── settings/               # App settings, QSettings
├── observability/          # Debug, metrics, event bus
└── help/                   # Help system (index, UI, context resolver)
```

### 1.4 Other Top-Level Directories

| Directory | Purpose |
|-----------|---------|
| `docs/` | Structured documentation (see Part 2) |
| `tests/` | Unit, integration, regression, behavior, qa — keep existing structure, add `tests/help/` |
| `scripts/` | `index_rag.py`, `build_help_index.py`, `qa/` scripts |
| `assets/` | `icons/`, `themes/`, `media/` — single source for all UI assets |
| `help/` | Markdown help articles (single source of truth) — see Part 3 |
| `tools/` | `ruff`, `mypy`, `pytest` configs, code generators |
| `archive/` | `legacy_gui/`, `deprecated_docs/` — read-only, for reference |

### 1.5 Why This Improves Maintainability

- **Single entry point:** `main.py` → `src`; no confusion between `app/main.py` and root `main.py`
- **Clear layering:** shell → ui → domains → services → data; dependencies flow inward
- **No duplication:** One `ui/` tree; `app/ui` and `app/gui` merged into `src/ui` + `src/domains`
- **Asset consolidation:** All icons/themes in `assets/`; `src/ui/icons` references them
- **Help content isolated:** `help/` is the only source for in-app help; docs reference it, not vice versa
- **Archive for legacy:** Deprecated code moved to `archive/` with clear deprecation notices

---

## Part 2 — Documentation Architecture

### 2.1 Documentation Structure

```
docs/
├── 01_product_overview/       # Product vision, positioning, roadmap
├── 02_user_manual/            # End-user handbook
├── 03_feature_reference/      # Feature-by-feature reference
├── 04_architecture/            # Technical architecture
├── 05_developer_guide/         # Developer onboarding, contribution
├── 06_operations_and_qa/       # QA, operations, incidents
├── 07_troubleshooting/         # Common issues, diagnostics
├── 08_glossary/               # Terms, abbreviations
└── README.md                  # Documentation index
```

### 2.2 Section Purposes and Contents

| Section | Audience | Purpose | Example Contents |
|---------|----------|---------|------------------|
| **01_product_overview** | All | High-level product understanding | Vision, use cases, roadmap, release notes |
| **02_user_manual** | End users | How to accomplish tasks | Getting started, Chat, Knowledge, Prompts, Agents, Settings workflows |
| **03_feature_reference** | End users, support | Detailed feature descriptions | Slash commands, RAG options, model roles, tools |
| **04_architecture** | Architects, senior devs | System design | Module structure, data flow, GUI architecture, RAG, QA |
| **05_developer_guide** | Developers | Contribution, setup | Setup, testing, coding standards, PR process |
| **06_operations_and_qa** | QA, ops | Quality and operations | Test strategy, incidents, coverage map, CI |
| **07_troubleshooting** | Support, users | Problem resolution | Error messages, diagnostics, FAQ |
| **08_glossary** | All | Terminology | RAG, Agent, Workspace, Model Role, etc. |

### 2.3 What Belongs Where

| Content Type | Location | Notes |
|--------------|----------|-------|
| User-facing help articles | `help/` (see Part 3) | Single source; linked from docs |
| Architecture decisions | `docs/04_architecture/` | ADRs, module diagrams |
| UX specifications | `docs/04_architecture/` or `docs/02_user_manual/` | UX_CONCEPT → user_manual |
| QA schemas, incidents | `docs/06_operations_and_qa/` | Move from `docs/qa/` |
| Implementation logs | `docs/05_developer_guide/` or archive | Phase logs, migration notes |
| Troubleshooting | `docs/07_troubleshooting/` | Consolidate from `troubleshooting.md` |

### 2.4 Relationship to Help Content

- **help/** contains **user-facing** articles (browsable, searchable, context-sensitive)
- **docs/** contains **project documentation** (architecture, dev guide, QA)
- **Overlap:** Some docs (e.g. `introduction.md`, `settings.md`) are suitable as help articles → live in `help/` and are **linked** from docs, not duplicated
- **Rule:** If content is shown in the in-app Help Center, it lives in `help/`. Docs reference it with relative links

---

## Part 3 — Single Source of Truth for Help Content

### 3.1 Content Model

**Format:** Markdown with YAML frontmatter (recommended) or JSON metadata sidecar.

**Rationale:** Markdown is human-editable, versionable, and already used. YAML frontmatter keeps metadata close to content without a separate index file.

### 3.2 Help Article Structure

```yaml
---
id: chat_overview
title: Chat Workspace
category: operations
tags: [chat, conversation, sessions]
related: [chat_sessions, chat_rag, slash_commands]
workspace: operations_chat
screen: operations
order: 10
---
```

```markdown
# Chat Workspace

The Chat workspace lets you ...
```

### 3.3 Metadata Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier; used in URLs and links |
| `title` | string | Yes | Display title |
| `category` | string | Yes | Top-level category (e.g. `operations`, `control_center`) |
| `tags` | list[string] | No | Search keywords |
| `related` | list[string] | No | IDs of related articles |
| `workspace` | string | No | NavArea/workspace ID for context-sensitive help |
| `screen` | string | No | Screen ID (operations, settings, etc.) |
| `order` | int | No | Sort order within category |
| `audience` | string | No | `user` \| `advanced` \| `developer` |

### 3.4 Categorization

Categories align with navigation:

| Category ID | Display Name | Workspaces |
|-------------|--------------|------------|
| `getting_started` | Erste Schritte | — |
| `operations` | Operations | Chat, Knowledge, Prompt Studio, Agents, Projects |
| `control_center` | Control Center | Models, Providers, Agents, Tools, Data Stores |
| `qa_governance` | QA & Governance | Test Inventory, Coverage Map, Incidents, Replay Lab |
| `runtime_debug` | Runtime / Debug | EventBus, Logs, Metrics, LLM Calls, Agent Activity |
| `settings` | Einstellungen | All settings workspaces |
| `troubleshooting` | Fehlerbehebung | — |

### 3.5 Linking Between Articles

- **Internal links:** `[Chat Sessions](chat_sessions)` or `[Chat Sessions](#chat_sessions)` — resolved to `#chat_sessions` in-app
- **Related topics:** Rendered as "See also" section from `related` frontmatter
- **Cross-references:** Docs can link to help: `[Chat Help](../../help/chat_overview.md)`

### 3.6 Directory Layout for Help Content

```
help/
├── index.yaml               # Optional: explicit ordering, category config
├── getting_started/
│   ├── introduction.md
│   └── quick_start.md
├── operations/
│   ├── chat_overview.md
│   ├── chat_sessions.md
│   ├── knowledge_overview.md
│   ├── prompt_studio_overview.md
│   └── agents_overview.md
├── control_center/
│   ├── models.md
│   ├── providers.md
│   └── ...
├── qa_governance/
├── runtime_debug/
├── settings/
└── troubleshooting/
```

---

## Part 4 — In-App Help Architecture

### 4.1 Two Help Modes

#### Mode 1: Browsable Help Center

| Feature | Description |
|---------|-------------|
| **Table of contents** | Hierarchical TOC from `help/` structure and `order` metadata |
| **Categories** | Filter by category (Operations, Control Center, etc.) |
| **Search** | Full-text search over title, content, tags |
| **Article viewer** | Markdown rendered to HTML; internal links work |
| **Related topics** | "See also" section from `related` frontmatter |

**UI:** Dedicated Help window (evolved from current `HelpWindow`), or dockable Help panel.

#### Mode 2: Contextual Help

| Feature | Description |
|---------|-------------|
| **Workspace help** | Each workspace can declare a default help article |
| **Quick explanation** | Tooltip or info icon for UI elements (from `tooltip_helper` or metadata) |
| **Link to detailed help** | "Learn more" → opens Help Center with article |

### 4.2 Workspace → Help Mapping

| Workspace | Help Article ID | Notes |
|-----------|-----------------|-------|
| Operations → Chat | `chat_overview` | Default when Chat workspace is active |
| Operations → Knowledge | `knowledge_overview` | |
| Operations → Prompt Studio | `prompt_studio_overview` | |
| Operations → Agent Tasks | `agents_overview` | |
| Operations → Projects | `projects_overview` | |
| Control Center → Models | `control_center_models` | |
| Control Center → Providers | `control_center_providers` | |
| Control Center → Agents | `control_center_agents` | |
| Control Center → Tools | `control_center_tools` | |
| Control Center → Data Stores | `control_center_data_stores` | |
| QA Governance → Test Inventory | `qa_test_inventory` | |
| QA Governance → Coverage Map | `qa_coverage_map` | |
| QA Governance → Incidents | `qa_incidents` | |
| QA Governance → Replay Lab | `qa_replay_lab` | |
| Runtime/Debug → (each) | `runtime_*` | |
| Settings → (each category) | `settings_application`, etc. | |

### 4.3 Context Resolution

1. **Screen/Workspace registers help ID:** e.g. `ChatWorkspace.help_topic_id = "chat_overview"`
2. **Help panel/sidebar** subscribes to workspace changes; when workspace activates, loads and displays the registered article
3. **Fallback:** If no article for workspace, show Help Center home or last viewed article

### 4.4 Integration Points

- **Top bar:** "Help" button → opens Help Center (current behavior)
- **Workspace header:** Optional "?" icon → opens context help for current workspace
- **Command palette:** "Help: Open Help Center", "Help: Show context help"
- **Settings:** Right-hand help panel (existing pattern) can pull from `help/settings_*.md`

---

## Part 5 — Help Data Flow

### 5.1 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SINGLE SOURCE OF TRUTH                           │
│                              help/*.md                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
            │ Help Index   │ │ RAG Index   │ │ Docs Links   │
            │ (in-memory   │ │ (ChromaDB   │ │ (relative    │
            │  or JSON)    │ │  optional)  │ │  paths)      │
            └──────────────┘ └──────────────┘ └──────────────┘
                    │               │               │
                    ▼               ▼               ▼
            ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
            │ In-App Help  │ │ Chat         │ │ docs/        │
            │ Center       │ │ Assistant    │ │ README       │
            │ (browse,     │ │ (RAG context │ │ (links to    │
            │  search)     │ │  for "how    │ │  help/)      │
            │              │ │  do I...")   │ │              │
            └──────────────┘ └──────────────┘ └──────────────┘
```

### 5.2 Loading Help Content

1. **Startup:** `HelpIndex` scans `help/` directory, parses frontmatter, builds in-memory index
2. **Optional:** `scripts/build_help_index.py` pre-builds `help/index.json` for faster startup
3. **Search:** In-memory full-text search (title, content, tags) — no external search engine required initially
4. **RAG (optional):** `scripts/index_rag.py` can include `help/` in a dedicated `help` space for chat augmentation

### 5.3 docs → in-app help

- **No duplication:** Help articles live only in `help/`
- **Docs reference help:** `docs/02_user_manual/README.md` links to `../../help/operations/chat_overview.md` for "Chat" section
- **Generated content:** `doc_generator` (agents, models, tools, settings) continues to generate `HelpTopic` objects; these can be merged with `help/` index or kept as dynamic topics

### 5.4 docs → chat assistant context

- **Option A:** Add `help` as a ChromaDB collection; when user asks "How do I...", RAG retrieves from help
- **Option B:** On help-related queries, inject top-k help articles into system/context
- **Option C:** Hybrid — RAG for knowledge docs, explicit help injection for "help" intent

---

## Part 6 — Migration Strategy

### 6.1 Principles

- **Incremental:** No big-bang rewrite; each phase leaves the app runnable
- **Reversible:** Use feature flags or path configs to switch between old and new
- **Audit first:** Document current state before moving

### 6.2 Migration Steps

| Step | Action | Risk | Rollback |
|------|--------|------|----------|
| 1 | Repository audit (done) | None | — |
| 2 | Create `archive/` and move `run_legacy_gui.py`, deprecated docs | Low | Restore from archive |
| 3 | Create target dirs: `help/`, `assets/`, `tools/` | None | Delete empty dirs |
| 4 | Migrate `docs/` to numbered structure; move files, update links | Medium | Git revert |
| 5 | Extract help-worthy content from docs → `help/`; add frontmatter | Medium | Keep docs copy until verified |
| 6 | Update `HelpIndex` to load from `help/` instead of `docs/` | Low | Revert HelpIndex |
| 7 | Add workspace→help mapping; implement context help | Medium | Feature flag |
| 8 | Consolidate `app/ui` + `app/gui` into `src/` (large refactor) | High | Branch-based |
| 9 | Move assets to `assets/`; update references | Low | Path config |
| 10 | Legacy cleanup: remove `app/` after `src/` migration | High | Keep app/ until full cutover |

### 6.3 Non-Breaking Approach

- **Path abstraction:** Use `HELP_CONTENT_DIR = Path("help")` or env var; fallback to `docs/` during transition
- **Dual load:** HelpIndex loads from both `help/` and `docs/` during migration; `help/` overrides `docs/` when same id
- **Tests:** Add `tests/help/` for HelpIndex, workspace mapping; run full test suite after each step

---

## Part 7 — Implementation Phases

### Phase 1 — Repository Cleanup

| Item | Scope | Risk | Modules Affected |
|------|-------|------|------------------|
| Create `archive/`, move legacy | 1–2 files | Low | None |
| Create `help/`, `assets/`, `tools/` | New dirs | None | None |
| Consolidate assets (icons, themes) | Path updates | Low | `app/gui/icons`, `app/resources` |
| Document current structure | Docs only | None | — |

**Deliverable:** Clean top-level layout; archive in place; no app behavior change.

---

### Phase 2 — Documentation Structure

| Item | Scope | Risk | Modules Affected |
|------|-------|------|------------------|
| Create `docs/01_product_overview` … `08_glossary` | New structure | Low | None |
| Move existing docs into sections | 100+ files | Medium | Links in docs, possibly README |
| Update `docs/README.md` as index | 1 file | Low | — |
| Move `docs/qa/` → `docs/06_operations_and_qa/` | Subdir move | Low | Scripts referencing `docs/qa/` |

**Deliverable:** Structured docs; all content accessible; links updated.

---

### Phase 3 — Help Content Model

| Item | Scope | Risk | Modules Affected |
|------|-------|------|------------------|
| Define frontmatter schema | Spec + examples | None | — |
| Create `help/` with initial articles | 10–20 articles | Low | — |
| Migrate `introduction`, `agents`, `rag`, `prompts`, `settings`, `troubleshooting` from docs | Content move | Low | HelpIndex |
| Add `scripts/build_help_index.py` | New script | Low | — |
| Update HelpIndex to read from `help/` with frontmatter | `app/help/help_index.py` | Medium | HelpWindow |

**Deliverable:** Help content in `help/`; HelpIndex loads it; HelpWindow works with new structure.

---

### Phase 4 — In-App Help UI

| Item | Scope | Risk | Modules Affected |
|------|-------|------|------------------|
| Enhance HelpWindow: TOC from categories, related topics | UI | Low | `app/help/help_window.py` |
| Add "Context help" panel or sidebar | New component | Medium | `app/gui/shell`, workspace host |
| Implement workspace→help mapping registry | New module | Low | `app/help/` |
| Wire workspace activation → context help | Integration | Medium | `app/gui/domains/*` |

**Deliverable:** Browsable Help Center + context-sensitive help for workspaces.

---

### Phase 5 — Context Help Integration

| Item | Scope | Risk | Modules Affected |
|------|-------|------|------------------|
| Register `help_topic_id` per workspace | All domains | Low | `app/gui/domains/*` |
| Settings right panel: load from help | Settings | Low | `app/ui/settings` or `app/gui/domains/settings` |
| "?" button in workspace headers | UI | Low | Base workspace, domain screens |
| Command palette: "Help: Show context help" | Commands | Low | `app/gui/commands` |

**Deliverable:** Every workspace has contextual help; users can quickly access relevant articles.

---

### Phase 6 — Help Search

| Item | Scope | Risk | Modules Affected |
|------|-------|------|------------------|
| Improve search: tags, fuzzy matching | HelpIndex | Low | `app/help/help_index.py` |
| Search result snippets | HelpWindow | Low | `app/help/help_window.py` |
| Optional: Whoosh or SQLite FTS for large help sets | Optional | Low | — |

**Deliverable:** Reliable, fast help search.

---

### Phase 7 — Chat-Help Integration

| Item | Scope | Risk | Modules Affected |
|------|-------|------|------------------|
| Add `help` RAG space or collection | RAG | Medium | `app/rag`, `scripts/index_rag.py` |
| Index `help/` into ChromaDB | Script | Low | — |
| Chat: detect help intent, augment with help context | Chat flow | Medium | `app/services`, `app/chat_widget` or chat workspace |
| Fallback: "See Help" suggestion when RAG has no knowledge hits | UX | Low | — |

**Deliverable:** Chat assistant can answer "How do I…" using help content.

---

## Summary Table

| Area | Current State | Target State |
|------|---------------|--------------|
| **Repository** | Flat `app/`, mixed ui/gui, scattered assets | `src/` with layers, `assets/`, `help/`, `archive/` |
| **Documentation** | 100+ flat docs, mixed audiences | `docs/01_` … `08_` with clear taxonomy |
| **Help content** | docs/*.md, hardcoded mapping | `help/*.md` with frontmatter, single source |
| **In-app help** | HelpWindow, search, no context | Browsable + context-sensitive, workspace mapping |
| **Chat integration** | RAG for knowledge only | Optional RAG over help for "how-to" queries |

---

## Next Steps

1. **Review and approve** this proposal
2. **Prioritize phases** (e.g. Phase 1–3 first for quick wins)
3. **Create tracking issues** or tasks per phase
4. **Begin Phase 1** — repository cleanup and directory creation
5. **Iterate** — adjust structure based on feedback from first phases

---

*End of Architecture Proposal*
