# GUI Domain Dependency Guards – Abschlussreport

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Abschlussklassifikation:** `GUARDS_ACTIVE_WITH_EXCEPTIONS`

---

## 1. Zusammenfassung

Das Domain-Dependency-Guard-System für `app/gui/` wurde eingeführt. Architektur-Drift bei Cross-Domain-Imports wird automatisch erkannt.

---

## 2. Analysierte Bereiche

| Bereich | Pfad | Status |
|---------|------|--------|
| Domains | `app/gui/domains/` | 8 Top-Level + 5 Operations-Subdomains |
| Orchestrierung | `bootstrap.py`, `shell/`, `workspace/`, `navigation/` | Inventarisiert |
| Infrastruktur | `shared/`, `inspector/`, `icons/`, `events/` | Nutzbar von allen Domains |
| Projekt-Switcher | `project_switcher/` | Domain-Charakter |

---

## 3. Erstellte Dokumente

| Dokument | Inhalt |
|----------|--------|
| `GUI_DOMAIN_DEPENDENCY_AUDIT.md` | Domain-Inventar, Import-Matrix, verdächtige Imports, Guard-Kategorien |
| `GUI_DOMAIN_DEPENDENCY_POLICY.md` | Regeln (FORBID, ALLOW, DISCOURAGE), Sonderrollen, Domain-Gruppen |

---

## 4. Implementierte Tests

| Testdatei | Tests |
|-----------|-------|
| `tests/architecture/test_gui_domain_dependency_guards.py` | `test_no_forbidden_gui_domain_imports`, `test_known_domain_exceptions_are_valid` |

**Konfiguration:** `tests/architecture/arch_guard_config.py`

- `FORBIDDEN_GUI_DOMAIN_PAIRS` – 17 verbotene (source, target)-Paare
- `KNOWN_GUI_DOMAIN_EXCEPTIONS` – 2 dokumentierte Ausnahmen (DISCOURAGE)

---

## 5. Gefundene Verstöße

### 5.1 Direkt korrigiert

| Verstoß | Maßnahme |
|---------|----------|
| `settings` → `operations.prompt_studio` (_PROMPTS_PANEL_FIXED_WIDTH) | Konstante nach `app/gui/shared/panel_constants.py` verschoben; Import in model_settings_panel und chat_side_panel angepasst; Ausnahme entfernt |

### 5.2 Dokumentierte Ausnahmen (DISCOURAGE)

| Quelle | Ziel | Datei | Follow-up |
|--------|------|-------|-----------|
| `operations.chat` | `settings` | chat_side_panel.py | Panel über Registry/Factory |
| `operations.chat` | `runtime_debug` | chat_side_panel.py | AgentDebugPanel über Inspector |

---

## 6. Verbleibende Follow-ups

1. **ChatSidePanel-Komposition:** ModelSettingsPanel, PromptManagerPanel, AgentDebugPanel werden direkt importiert. Langfristig: Factory/Registry im Shell-Bereich.
2. **operations.chat → settings, runtime_debug:** Nach Refactor Ausnahmen aus `KNOWN_GUI_DOMAIN_EXCEPTIONS` entfernen.

---

## 7. Test-Ergebnisse

| Test-Suite | Ergebnis |
|-------------|----------|
| `tests/architecture/test_gui_domain_dependency_guards.py` | 2 passed |
| `tests/architecture/test_gui_does_not_import_ui.py` | 1 passed |
| `tests/architecture/test_app_package_guards.py` | 12 passed |
| **Architektur gesamt** | **15 passed** |
| Smoke (Bootstrap, ScreenRegistry) | OK |
| Smoke (Shell GUI) | 4 failed – pre-existing (AGENT_ACTIVITY in navigation_registry) |

---

## 8. Keine funktionalen Änderungen

- Keine fachlichen Änderungen
- Keine neuen Features
- Einzige Code-Anpassung: `_PROMPTS_PANEL_FIXED_WIDTH` nach shared (Governance-Verbesserung)

---

## 9. Konsole-Zusammenfassung

```
=== GUI DOMAIN DEPENDENCY GUARDS ===

Neue Guard-Tests:
  - test_no_forbidden_gui_domain_imports
  - test_known_domain_exceptions_are_valid

Erkannte Verstöße (vor Korrektur):
  - settings → operations.prompt_studio (_PROMPTS_PANEL_FIXED_WIDTH)
  - operations.chat → settings (chat_side_panel)
  - operations.chat → runtime_debug (chat_side_panel)

Korrigierte Verstöße:
  - settings → operations.prompt_studio: _PROMPTS_PANEL_FIXED_WIDTH nach shared

Verbleibende Ausnahmen (DISCOURAGE):
  - operations.chat → settings
  - operations.chat → runtime_debug

Dokumente:
  - docs/architecture/GUI_DOMAIN_DEPENDENCY_AUDIT.md
  - docs/architecture/GUI_DOMAIN_DEPENDENCY_POLICY.md
  - docs/architecture/GUI_DOMAIN_DEPENDENCY_GUARDS_REPORT.md
```

---

## 10. Abschlussklassifikation

**GUARDS_ACTIVE_WITH_EXCEPTIONS**

- Guards aktiv und grün
- 2 dokumentierte Ausnahmen mit Follow-up
- 1 Verstoß behoben
- Keine Funktionsänderung
