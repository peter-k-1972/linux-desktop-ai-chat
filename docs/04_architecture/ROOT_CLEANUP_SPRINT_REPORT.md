# Root-Cleanup und Legacy-Konsolidierungs-Sprint – Abschlussbericht

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Sprint:** Root-Cleanup, Legacy-Verortung, Re-Export-Hygiene

---

## 1. Entfernte Re-Exports

| Re-Export | Status | Begründung |
|-----------|--------|------------|
| `app/context/` | **entfernt** | Keine Konsumenten; alle nutzen `app.core.context` |
| `app/settings.py` | **entfernt** | Keine Konsumenten; alle nutzen `app.core.config.settings` |
| `app/ui/events/` | **entfernt** | Keine Konsumenten; alle nutzen `app.gui.events` |
| `app/ui/widgets/` | **entfernt** | Keine Konsumenten; alle nutzen `app.gui.widgets` |

---

## 2. Verbliebene Übergangs-Re-Exports

| Re-Export | Status | Geplantes Entfernungsziel |
|-----------|--------|---------------------------|
| `app/db.py` | beibehalten | Nach Migration aller Imports auf `app.core.db` |
| `app/ollama_client.py` | beibehalten | Nach Migration auf `app.providers.ollama_client` |

---

## 3. Nach app/gui/legacy/ verschobene Dateien

| Ehemaliger Pfad | Neuer Pfad |
|-----------------|------------|
| `app/chat_widget.py` | `app/gui/legacy/chat_widget.py` |
| `app/sidebar_widget.py` | `app/gui/legacy/sidebar_widget.py` |
| `app/project_chat_list_widget.py` | `app/gui/legacy/project_chat_list_widget.py` |
| `app/message_widget.py` | `app/gui/legacy/message_widget.py` |
| `app/file_explorer_widget.py` | `app/gui/legacy/file_explorer_widget.py` |

---

## 4. Aktualisierte Importpfade

| Konsument | Alter Import | Neuer Import |
|-----------|--------------|--------------|
| `app/main.py` | `from app.chat_widget import ...` | `from app.gui.legacy import ChatWidget, SidebarWidget, ProjectChatListWidget` |
| Tests (25+ Dateien) | `from app.chat_widget import ChatWidget` | `from app.gui.legacy import ChatWidget` |
| Tests (patch) | `patch("app.chat_widget.get_agent_registry")` | `patch("app.gui.legacy.chat_widget.get_agent_registry")` |
| Tests (patch) | `patch("app.chat_widget.emit_event")` | `patch("app.gui.legacy.chat_widget.emit_event")` |

---

## 5. Root-Status nach dem Sprint

| Datei | Status | Begründung |
|-------|--------|------------|
| `__init__.py` | erlaubt | Package-Marker |
| `__main__.py` | erlaubt | Einstieg `python -m app` |
| `main.py` | erlaubt | Legacy-Einstiegspunkt |
| `resources.qrc` | erlaubt | Qt-Ressource |
| `resources_rc.py` | erlaubt | Qt-generiert |
| `db.py` | temporär erlaubt | Re-Export; kanonisch: app.core.db |
| `ollama_client.py` | temporär erlaubt | Re-Export; kanonisch: app.providers |
| `critic.py` | temporär erlaubt | Merge in app.agents.critic geplant |

---

## 6. Testergebnisse

| Test-Suite | Ergebnis | Anmerkung |
|------------|----------|-----------|
| tests/architecture/ | 11/12 passed | 1 pre-existing: core/context/active_project.py → services |
| tests/test_streaming_logic.py | 6 passed ✓ | |
| tests/smoke/test_basic_chat.py | 4 passed ✓ | |
| tests/unit/test_tools.py | 11 passed ✓ | |
| tests/async_behavior (agent_change, tool_failure) | 3 passed ✓ | |
| tests/golden_path/test_agent_in_chat_golden_path.py | 2 passed ✓ | |

**Bekannte Fehler (vor Sprint):**
- `test_no_forbidden_import_directions`: core/context/active_project.py → services
- `test_startup_partial_services`: sidebar list_projects DB-Schema (dict vs tuple)
- Prompt-Model scope/project_id
- AgentListPanel theme-Argument

---

## 7. Verbleibende manual_review-Punkte

| Punkt | Beschreibung |
|-------|--------------|
| `main.py` im Root | Bleibt; nächster Schritt: Move nach `archive/` oder `gui/legacy/` nach Legacy-Abschaltung |
| `core/context/active_project.py` → services | Architektur-Verletzung; KNOWN_IMPORT_EXCEPTIONS prüfen |
| sidebar_widget list_projects | DB liefert dicts, Widget erwartet Tuples; Schema-Anpassung nötig |

---

## 8. Arch-Guard-Anpassungen

- `settings.py` aus TEMPORARILY_ALLOWED_ROOT_FILES entfernt
- Legacy-Widgets aus TEMPORARILY_ALLOWED_ROOT_FILES entfernt
- `chat_widget.py` aus ALLOWED_UI_IMPORTER_PATTERNS entfernt (gui/ deckt gui/legacy ab)
