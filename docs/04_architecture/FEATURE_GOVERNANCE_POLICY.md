# Feature Governance Policy

**Projekt:** Linux Desktop Chat  
**Referenz:** `docs/architecture/FEATURE_GOVERNANCE_AUDIT.md`  
**Tests:** `tests/architecture/test_feature_governance_guards.py`

---

## 1. Ziel

Feature-Registry, Navigation, Commands und GUI-Struktur konsistent halten. Drift früh erkennen.

---

## 2. Feature Identity

### 2.1 Regeln

| Regel | Beschreibung |
|-------|--------------|
| **Eindeutige workspace_ids** | Keine doppelten workspace_ids in FEATURES (tools/generate_feature_registry.py) |
| **Benennung** | workspace_id = snake_case (z.B. operations_chat, cc_models) |
| **Keine stillen Duplikate** | Jeder workspace_id erscheint nur einmal in der kanonischen Liste |

### 2.2 Source of Truth

- **FEATURES** in `tools/generate_feature_registry.py` ist die kanonische Feature-Liste
- Format: `(area_title, [(display_name, workspace_id), ...])`

---

## 3. Feature Reachability

### 3.1 Regeln

| Regel | Beschreibung |
|-------|--------------|
| **Navigation** | Jeder workspace_id muss in der Navigation Registry existieren (als entry.id) |
| **Screen/Workspace** | Jeder workspace_id muss in GUI_SCREEN_WORKSPACE_MAP vorkommen |
| **Keine toten Ziele** | Kein Feature ohne erreichbaren Einstiegspunkt |

### 3.2 Einstiegspunkte

- **Sidebar:** Navigation Registry → get_sidebar_sections
- **Command Palette:** feature.open.{workspace_id} (via palette_loader)
- **WorkspaceHost:** show_area(area_id, workspace_id)

---

## 4. Feature Registry Consistency

### 4.1 Regeln

| Regel | Beschreibung |
|-------|--------------|
| **Generator reproduzierbar** | `python3 tools/generate_feature_registry.py` erzeugt konsistentes FEATURE_REGISTRY.md |
| **Keine verwaisten Einträge** | FEATURE_REGISTRY.md enthält nur workspace_ids aus FEATURES |
| **Parsebar** | palette_loader kann FEATURE_REGISTRY.md parsen |

### 4.2 Generator vs. Dokumentation

- **Generator** ist Source of Truth
- **FEATURE_REGISTRY.md** ist abgeleitet; Änderungen nur über Regenerierung
- Guards prüfen: Generiertes MD enthält alle FEATURES workspace_ids

---

## 5. Navigation / Command Linkage

### 5.1 Regeln

| Regel | Beschreibung |
|-------|--------------|
| **Feature ↔ Navigation** | workspace_id muss in get_all_entries() als entry.id existieren |
| **Feature ↔ Command** | palette_loader registriert feature.open.{workspace_id} nur wenn Nav-Eintrag existiert |
| **Keine Nav-/Feature-Drift** | Neue Features in FEATURES erfordern Nav-Eintrag |

### 5.2 NavEntry-Struktur

- Für Workspace-Features: entry.id = workspace_id, entry.workspace = workspace_id
- palette_loader: workspace_to_nav[workspace_id] = (area, workspace)

---

## 6. Dokumentationskonsistenz

### 6.1 Regeln

| Regel | Beschreibung |
|-------|--------------|
| **FEATURE_REGISTRY.md** | Wird von Generator erzeugt; keine manuellen Abweichungen |
| **Generator-Lauf** | `tools/generate_feature_registry.py` muss erfolgreich laufen |
| **Strukturkritische Inhalte** | Workspace-Spalte muss workspace_ids aus FEATURES enthalten |

---

## 7. Ausnahmen

| Ausnahme | Begründung |
|----------|------------|
| rd_introspection, rd_qa_cockpit, rd_qa_observability | In Navigation, nicht in FEATURES – bewusst (Observability-Bereich ohne eigenes Feature) |
| project_hub, command_center | Area-only, keine Workspace-Features |

---

## 8. Implementierung in Tests

Die Guards prüfen:

1. **Feature Identity:** Keine doppelten workspace_ids in FEATURES
2. **Feature Reachability:** workspace_ids in Navigation Registry und GUI_SCREEN_WORKSPACE_MAP
3. **Registry Integrity:** FEATURE_REGISTRY.md parsebar; enthält erwartete workspace_ids
4. **Generator Consistency:** Generator läuft; Output-Struktur konsistent

Fehlermeldungen: workspace_id, betroffene Datei, verletzte Regel.
