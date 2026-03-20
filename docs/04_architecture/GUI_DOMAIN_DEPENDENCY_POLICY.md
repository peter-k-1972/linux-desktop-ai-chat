# GUI Domain Dependency Policy

**Projekt:** Linux Desktop Chat  
**Referenz:** `docs/architecture/GUI_DOMAIN_DEPENDENCY_AUDIT.md`  
**Tests:** `tests/architecture/test_gui_domain_dependency_guards.py`

---

## 1. Ziel

Die GUI soll modular bleiben. Domain-Grenzen sollen explizit sein, unerwünschte Kopplungen automatisch erkennbar.

- **Erlaubte Abhängigkeiten** explizit machen
- **Unerwünschte Abhängigkeiten** automatisch erkennen
- **Architektur-Drift** verhindern

---

## 2. Rollen und Sonderregeln

### 2.1 Orchestrierung (darf Domains importieren)

| Bereich | Pfad | Erlaubnis |
|---------|------|-----------|
| `bootstrap` | `app/gui/bootstrap.py` | Importiert alle Domain-Screens für Registrierung |
| `shell` | `app/gui/shell/` | Importiert workspace, navigation, commands; keine direkten Domain-Panels |
| `workspace` | `app/gui/workspace/` | ScreenRegistry; Domains registrieren sich |
| `navigation` | `app/gui/navigation/` | NavAreas, Sidebar, CommandPalette |

### 2.2 Shared Infrastructure (von allen Domains nutzbar)

| Bereich | Pfad | Nutzung |
|---------|------|---------|
| `shared` | `app/gui/shared/` | Base-Workspaces, Layout-Konstanten |
| `events` | `app/gui/events/` | Projekt-Events |
| `icons` | `app/gui/icons/` | IconManager, Registry |
| `themes` | `app/gui/themes/` | Theme-Infrastruktur |
| `inspector` | `app/gui/inspector/` | Domain-spezifische Inspectoren |
| `commands` | `app/gui/commands/` | Command Registry |
| `breadcrumbs` | `app/gui/breadcrumbs/` | BreadcrumbManager |

### 2.3 Domains

Domains unter `app/gui/domains/`:

- `command_center`, `control_center`, `dashboard`, `project_hub`
- `qa_governance`, `runtime_debug`, `settings`
- `operations` (Meta) mit Subdomains: `chat`, `knowledge`, `prompt_studio`, `agent_tasks`, `projects`

---

## 3. Regeln

### 3.1 FORBID – Verboten (Test schlägt fehl)

| Regel | Beschreibung |
|-------|--------------|
| **settings → chat** | `domains/settings/` darf nicht `domains/operations/chat/` importieren |
| **settings → agents** | `domains/settings/` darf nicht `domains/control_center/agents_ui/` importieren |
| **settings → runtime_debug** | `domains/settings/` darf nicht `domains/runtime_debug/` importieren |
| **project_hub → chat** | `domains/project_hub/` darf nicht `domains/operations/chat/` importieren (außer über operations_context) |
| **dashboard → chat** | `domains/dashboard/` darf nicht `domains/operations/chat/` importieren |
| **qa_governance → chat** | `domains/qa_governance/` darf nicht `domains/operations/chat/` importieren |
| **command_center → chat** | `domains/command_center/` darf nicht `domains/operations/chat/` importieren |

**Prinzip:** Settings, Dashboard, QA, Command Center sind fachlich getrennt von Chat. Keine direkten Chat-Imports.

### 3.2 ALLOW – Explizit erlaubt

| Quelle | Ziel | Begründung |
|--------|------|------------|
| `project_hub` | `operations.operations_context` | Hub→Workspace-Navigation; Kontext-Broker |
| `operations.chat` | `operations.prompt_studio` | Chat-Side-Panel zeigt Prompt-Manager; gleiche Operations-Familie |
| `operations` | `operations.*` (Subdomains) | Meta-Screen orchestriert Subdomains |
| Alle Domains | `shared`, `events`, `icons`, `themes`, `inspector`, `navigation` | Infrastruktur |

### 3.3 DISCOURAGE – Dokumentierte Ausnahmen

Diese Imports sind aktuell vorhanden und funktional notwendig. Sie sollen langfristig refaktoriert werden. **Kein Test-Fehler**, aber in `KNOWN_DOMAIN_EXCEPTIONS` dokumentiert.

| Quelle | Ziel | Datei | Follow-up |
|--------|------|-------|-----------|
| `operations.chat` | `settings` | chat_side_panel.py | Panel über Registry/Factory |
| `operations.chat` | `runtime_debug` | chat_side_panel.py | AgentDebugPanel über Inspector |

**Behoben (2026-03-16):** `settings` → `operations.prompt_studio` – `_PROMPTS_PANEL_FIXED_WIDTH` nach `app/gui/shared/panel_constants.py` verschoben.

---

## 4. Domain-Gruppen

### 4.1 Keine Cross-Domain-Imports zwischen

- `settings` ↔ `chat`, `agents`, `runtime_debug`, `dashboard`, `qa_governance`, `command_center`
- `project_hub` ↔ `chat` (außer operations_context)
- `dashboard` ↔ `chat`, `settings`
- `qa_governance` ↔ `chat`, `settings`
- `command_center` ↔ `chat`, `settings`

### 4.2 Erlaubte Cross-Domain

- `project_hub` → `operations` (nur operations_context)
- `operations.chat` → `operations.prompt_studio`
- `operations.*` untereinander (innerhalb operations)

---

## 5. Implementierung in Tests

Die Guards prüfen:

1. **FORBID-Regeln:** Domain A importiert nicht Domain B (für verbotene Paare)
2. **Ausnahmen:** `KNOWN_DOMAIN_EXCEPTIONS` für dokumentierte DISCOURAGE-Fälle
3. **Keine neuen verbotenen Paare** ohne Eintrag in Ausnahmen

Fehlermeldungen enthalten: Quelldatei, Zielimport, verletzte Regel.

---

## 6. Änderungen an der Policy

- Neue FORBID-Regeln: Architektur-Review, Test ergänzen
- Neue Ausnahmen: In `arch_guard_config.py` oder Test-Konfiguration, mit Begründung und Follow-up-Datum
- DISCOURAGE → ALLOW oder Refactor: Nach Bereinigung Ausnahme entfernen
