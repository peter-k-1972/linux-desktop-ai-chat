# Feature Governance Audit

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Kontext:** Feature-Governance-System

---

## 1. Übersicht

Audit der Feature-Registry-Logik: Quellen, Datenmodell, Beziehungen zu Navigation, Commands und GUI.

---

## 2. Was ist ein "Feature"?

Im Projekt: Ein **GUI-Feature** ist ein erreichbarer Arbeitsbereich (Workspace) mit:
- **Workspace-ID** (z.B. `operations_chat`, `cc_models`)
- **Display-Name** (z.B. "Chat", "Models")
- **Area** (Operations, Control Center, QA & Governance, Runtime / Debug, Settings)
- Zuordnung zu Code, Services, Help, Tests, QA-Docs

---

## 3. Quellen und Datenfluss

### 3.1 Source of Truth

| Quelle | Pfad | Rolle |
|--------|------|-------|
| **FEATURES** (Generator) | `tools/generate_feature_registry.py` | Kanonische Feature-Liste: (area_title, [(display_name, workspace_id), ...]) |
| **FEATURE_REGISTRY.md** | `docs/FEATURE_REGISTRY.md` | Generierte Dokumentation; wird von palette_loader geparst |

### 3.2 Datenfluss

```
FEATURES (Generator)
    → generate() → FEATURE_REGISTRY.md
    → palette_loader._parse_feature_registry() → [(display_name, workspace_id, help_id)]
    → load_feature_commands() → workspace_to_nav.get(workspace_id)
    → CommandRegistry.register(PaletteCommand(id="feature.open.{workspace_id}", ...))
```

### 3.3 Zusätzliche Generator-Daten

| Konstante | Rolle |
|-----------|-------|
| WORKSPACE_SERVICES | workspace_id → [services] |
| WORKSPACE_TEST_KEYWORDS | workspace_id → [keywords] für Test-Discovery |
| domain_to_ws | Dateipfad-Scan → workspace_id |
| cat_to_ws | Settings-Kategorien → workspace_id |

---

## 4. Kennungen

| Kennung | Format | Beispiel |
|---------|--------|----------|
| workspace_id | snake_case | operations_chat, cc_models |
| feature_id (implizit) | = workspace_id | operations_chat |
| command_id | feature.open.{workspace_id} | feature.open.operations_chat |
| display_name | Human-readable | Chat, Models |
| area_title | Sektions-Name | Operations, Control Center |

---

## 5. Beziehungen

### 5.1 Feature ↔ Navigation

- **Navigation Registry** (`app/core/navigation/navigation_registry.py`): NavEntry mit id, area, workspace
- Für Workspace-Features: entry.id = workspace_id (z.B. operations_chat)
- **Linkage:** palette_loader nutzt get_all_entries(); workspace_id muss als entry.id existieren

### 5.2 Feature ↔ Commands

- **Command:** `feature.open.{workspace_id}` (core CommandRegistry)
- **Callback:** workspace_host.show_area(area_id, workspace_id)
- **Linkage:** Nur wenn workspace_id in navigation registry → Command wird registriert

### 5.3 Feature ↔ Screen/Workspace

- **GUI_SCREEN_WORKSPACE_MAP** (arch_guard_config): area_id → set(workspace_ids)
- **Linkage:** workspace_id muss in passendem area sein und von Screen unterstützt werden

### 5.4 Feature ↔ FEATURE_REGISTRY.md

- **Generator** schreibt FEATURE_REGISTRY.md aus FEATURES + Scans
- **palette_loader** parst FEATURE_REGISTRY.md (### Display, | Workspace | `id` |)
- **Linkage:** Parsed workspace_ids müssen in navigation registry sein

---

## 6. Kanonische Feature-Liste (aus Generator FEATURES)

| Area | workspace_ids |
|------|---------------|
| Operations | operations_chat, operations_knowledge, operations_prompt_studio, operations_agent_tasks, operations_projects |
| Control Center | cc_models, cc_providers, cc_agents, cc_tools, cc_data_stores |
| QA & Governance | qa_test_inventory, qa_coverage_map, qa_gap_analysis, qa_incidents, qa_replay_lab |
| Runtime / Debug | rd_eventbus, rd_logs, rd_metrics, rd_llm_calls, rd_agent_activity, rd_system_graph |
| Settings | settings_application, settings_appearance, settings_ai_models, settings_data, settings_privacy, settings_advanced, settings_project, settings_workspace |

**Gesamt:** 27 workspace_ids

---

## 7. Gefundene Inkonsistenzen

### 7.1 OK

| Thema | Status |
|-------|--------|
| workspace_ids in FEATURES eindeutig | OK |
| Alle workspace_ids in GUI_SCREEN_WORKSPACE_MAP | OK |
| Alle workspace_ids in Navigation Registry | OK (als entry.id oder über area+workspace) |
| Generator reproduzierbar | OK |
| palette_loader parst FEATURE_REGISTRY.md | OK |

### 7.2 GUARD_NEEDED

| Thema | Details |
|-------|---------|
| Drift Generator ↔ FEATURE_REGISTRY.md | Generiertes MD kann manuell editiert worden sein |
| Drift FEATURES ↔ Navigation | Neue Features in FEATURES ohne Nav-Eintrag = stille Skip |
| Drift FEATURES ↔ GUI_SCREEN_WORKSPACE_MAP | Config muss manuell gepflegt werden |

### 7.3 INVESTIGATE

| Thema | Details |
|-------|---------|
| domain_to_ws.settings.agents_workspace | "settings_agents" in domain_to_ws, nicht in FEATURES – totes Mapping |
| FEATURE_REGISTRY.md als Parser-Quelle | palette_loader liest generiertes MD; Generator ist Source of Truth |

### 7.4 FOLLOW_UP

| Thema | Details |
|-------|---------|
| Feature-ID explizit machen | Aktuell workspace_id = feature_id; evtl. separates Feld |
| Generator als einzige Quelle | palette_loader könnte direkt FEATURES aus Generator importieren statt MD zu parsen |

---

## 8. Generierungslogik – kritische Stellen

1. **FEATURES** – einzige autoritative Feature-Liste
2. **_scan_workspace_to_code()** – domain_to_ws, cat_to_ws müssen zu FEATURES passen
3. **WORKSPACE_SERVICES**, **WORKSPACE_TEST_KEYWORDS** – müssen alle FEATURES workspace_ids abdecken
4. **FEATURE_REGISTRY.md** – Output; Änderungen nur über Regenerierung

---

## 9. Empfohlene Guards

1. **Feature Identity:** Keine doppelten workspace_ids in FEATURES
2. **Feature Reachability:** Jeder workspace_id in Navigation Registry und GUI_SCREEN_WORKSPACE_MAP
3. **Registry Integrity:** FEATURE_REGISTRY.md parsebar; enthält alle FEATURES workspace_ids
4. **Generator Consistency:** Generator-Output enthält alle FEATURES; keine fehlenden Einträge
5. **Linkage:** palette_loader kann für alle geparsten Features einen Nav-Eintrag finden
