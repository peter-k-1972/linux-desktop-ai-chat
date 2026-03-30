# GUI Governance Policy

**Projekt:** Linux Desktop Chat  
**Referenz:** `docs/architecture/GUI_GOVERNANCE_AUDIT.md`  
**Tests:** `tests/architecture/test_gui_governance_guards.py`

---

## 1. Ziel

Strukturelle GUI-Konsistenz automatisch prüfen: Screen Registry, Navigation, Commands, Bootstrap. Drift früh erkennen, keine stillen Broken-Wiring-Konstellationen.

---

## 2. Screen Registry

### 2.1 Regeln

| Regel | Beschreibung |
|-------|--------------|
| **Eindeutige area_ids** | Keine doppelten area_ids in der ScreenRegistry |
| **Auflösbare Screens** | Alle registrierten Screen-Klassen müssen importierbar und instanziierbar sein |
| **Bootstrap-Konsistenz** | Bootstrap registriert nur area_ids, die zu NavArea-Konstanten gehören |
| **Keine toten Registrierungen** | Jede Bootstrap-Registrierung referenziert eine gültige Screen-Klasse |

### 2.2 Erwartete area_ids

- command_center, operations, control_center, qa_governance, runtime_debug, settings

### 2.3 Ausnahmen

- Keine stillen Ausnahmen. Neue area_ids nur nach Architektur-Review.

---

## 3. Navigation

### 3.1 Regeln

| Regel | Beschreibung |
|-------|--------------|
| **Gültige area-Referenzen** | Jeder NavEntry.area muss eine gültige NavArea-Konstante sein |
| **Auflösbare workspace_ids** | workspace_id eines NavEntry muss vom zugehörigen Screen unterstützt werden (show_workspace) |
| **Keine toten Targets** | Kein NavEntry verweist auf nicht existierende area/workspace-Kombination |
| **Sektionen konsistent** | Alle entry_ids in NavSectionDef müssen in _ENTRIES existieren |

### 3.2 Gültige NavAreas

- command_center, operations, control_center, qa_governance, runtime_debug, settings

### 3.3 Screen-Workspace-Mapping (Referenz)

- Operations: operations_projects, operations_chat, operations_knowledge, operations_prompt_studio, operations_workflows, operations_agent_tasks, operations_deployment, operations_audit_incidents
- ControlCenter: cc_models, cc_providers, cc_agents, cc_tools, cc_data_stores
- RuntimeDebug: rd_introspection, rd_qa_cockpit, rd_qa_observability, rd_markdown_demo, rd_theme_visualizer, rd_eventbus, rd_logs, rd_llm_calls, rd_agent_activity, rd_metrics, rd_system_graph
- QAGovernance: qa_test_inventory, qa_coverage_map, qa_gap_analysis, qa_incidents, qa_replay_lab
- Settings: settings_application, settings_appearance, settings_ai_models, settings_data, settings_privacy, settings_advanced, settings_project, settings_workspace

### 3.4 Ausnahmen

- Area-only Einträge (workspace=None): Kein show_workspace nötig, Screen zeigt Default-View.

---

## 4. Commands

### 4.1 Regeln (gui CommandRegistry – Standard-Navigation)

| Regel | Beschreibung |
|-------|--------------|
| **Eindeutige Command-IDs** | Keine doppelten Command-IDs nach vollständigem Load |
| **Auflösbare Handler** | Jeder Command hat einen gültigen callback (oder dokumentierte Ausnahme) |
| **Keine stillen Überschreibungen** | Spätere Registrierung mit gleicher ID soll erkennbar sein (palette_loader skippt explizit) |

### 4.2 Command-Kategorien

- Workspace, Feature, Help, Setting, Command

### 4.3 Ausnahmen

- Für diesen Guard-Bereich gilt die GUI-CommandRegistry aus `app/gui/commands/registry.py`; die Core-/Palette-Registry ist separat governiert.

---

## 5. Bootstrap / Wiring

### 5.1 Regeln

| Regel | Beschreibung |
|-------|--------------|
| **Bootstrap-Screens** | Alle in bootstrap.py registrierten Screens müssen importierbar sein |
| **NavArea-Abdeckung** | Jede NavArea-Konstante (außer evtl. dokumentierte) hat einen Bootstrap-Eintrag |
| **Keine toten Imports** | Keine Screen-Klasse, die nicht importierbar ist; Bootstrap liefert eine Factory pro area_id |

### 5.2 Ausnahmen

- NavArea.all_areas() kann von Bootstrap abweichen (z.B. PROJECT_HUB) – dokumentiert in Audit.

---

## 6. Implementierung in Tests

Die Guards prüfen:

1. **Screen Guards:** Doppelte area_ids; Importierbarkeit der Screen-Klassen
2. **Navigation Guards:** NavEntry.area in NavArea; workspace_ids in Screen-Mapping
3. **Command Guards:** Doppelte IDs in core CommandRegistry (nach Load)
4. **Bootstrap Guards:** Bootstrap area_ids ⊆ NavArea; alle Screens instanziierbar

Fehlermeldungen: Quelle, Registry/Key/Target, verletzte Regel.

---

## 7. Änderungen an der Policy

- Neue Regeln: Architektur-Review, Test ergänzen
- Ausnahmen: Explizit dokumentieren, mit Begründung
