# Startup Governance – Abschlussreport

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Status:** Startup-Governance aktiv

---

## 1. Analysierter Ist-Zustand

### 1.1 Einstiegspunkte

| Einstiegspunkt | Pfad | Delegation | Bootstrap |
|----------------|------|------------|-----------|
| Standard-GUI | `run_gui_shell.py` | — | init_infrastructure(create_qsettings_backend()) ✓ |
| Standard-GUI | `app/__main__.py` | → run_gui_shell.main | ✓ |
| Standard-GUI | `main.py` (Root) | → run_gui_shell.main | ✓ |
| Legacy-GUI | `archive/run_legacy_gui.py` | → app.main.main | init_infrastructure(create_qsettings_backend()) ✓ |

### 1.2 Bootstrap-Reihenfolge (run_gui_shell)

1. load_env, install_gui_log_handler, get_metrics_collector
2. QApplication(sys.argv)
3. qasync/QEventLoop
4. **init_infrastructure(settings_backend=create_qsettings_backend())**
5. get_infrastructure()
6. set_chat_backend(ChatBackend()), set_knowledge_backend(KnowledgeBackend())
7. ShellMainWindow()

### 1.3 Bootstrap-Reihenfolge (app.main)

1. load_env
2. QApplication
3. QEventLoop
4. **init_infrastructure(settings_backend=create_qsettings_backend())**
5. MainWindow(client, orchestrator, settings)

### 1.4 Mögliche indirekte Frühimporte

- **ShellMainWindow** wird bei Import von run_gui_shell importiert; ShellMainWindow selbst materialisiert keine Infrastruktur bei Import.
- **ChatBackend** wird erst nach init_infrastructure instanziiert; ChatBackend.__init__ ruft get_chat_service() auf – zu diesem Zeitpunkt ist init_infrastructure bereits aufgerufen.
- **palette_loader** lädt Commands bei load_all_palette_commands() – Aufruf erfolgt aus ShellMainWindow.__init__, also nach Bootstrap.

### 1.5 Risiken (vor Governance)

| Risiko | Beschreibung |
|--------|--------------|
| Stiller Fallback | Neuer Einstiegspunkt vergisst init_infrastructure → InMemoryBackend |
| Verdrahtungsdrift | Reihenfolge init_infrastructure vor get_infrastructure wird geändert |
| Inoffizielle Einstiegspunkte | Neue Launcher ohne Governance-Review |

---

## 2. Implementierte Governance-Regeln

### 2.1 Erlaubte Einstiegspunkte

- `run_gui_shell.py` (kanonisch)
- `app.main.py` (Legacy)

### 2.2 Bootstrap-Contract

- Jeder GUI-Einstiegspunkt muss in `main()` enthalten:
  - `init_infrastructure`
  - `create_qsettings_backend`

### 2.3 Bootstrap-Reihenfolge

- `init_infrastructure` vor `get_infrastructure`
- `ShellMainWindow()` nach `init_infrastructure`

### 2.4 Verbotene Abhängigkeiten

- services darf keine GUI-Einstiegspunkte (run_gui_shell, app.main) importieren

### 2.5 Stille Fallbacks

- Runtime-Test: Nach init_infrastructure(create_qsettings_backend()) darf das Backend nicht InMemoryBackend sein

---

## 3. Neue/angepasste Tests

| Test | Datei | Regel |
|------|-------|-------|
| `test_canonical_gui_entry_points_exist` | test_startup_governance_guards.py | Einstiegspunkte existieren |
| `test_gui_entry_points_call_init_infrastructure_with_qsettings` | test_startup_governance_guards.py | Bootstrap-Contract |
| `test_app_main_delegates_to_run_gui_shell` | test_startup_governance_guards.py | app.__main__ delegiert an run_gui_shell |
| `test_run_gui_shell_init_before_get_infrastructure` | test_startup_governance_guards.py | Reihenfolge |
| `test_run_gui_shell_window_after_infrastructure` | test_startup_governance_guards.py | Fenster nach Bootstrap |
| `test_bootstrap_with_qsettings_produces_non_inmemory_backend` | test_startup_governance_guards.py | Kein stiller InMemory-Fallback |
| `test_services_do_not_import_entry_points` | test_startup_governance_guards.py | services → keine GUI-Einstiegspunkte |

---

## 4. Gefundene Risiken

| Risiko | Status |
|--------|--------|
| Stiller InMemoryBackend in produktiver GUI | **Abgesichert** durch Guards und Runtime-Test |
| Verdrahtungsdrift (Reihenfolge) | **Abgesichert** durch statische Guards |
| Inoffizielle Einstiegspunkte | **Abgesichert** durch CANONICAL_GUI_ENTRY_POINTS; neue Einstiegspunkte müssen explizit ergänzt werden |
| archive/run_legacy_gui.py | **Nicht** in CANONICAL_GUI_ENTRY_POINTS – delegiert an app.main, der den Contract erfüllt |

---

## 5. Verbleibende Drift-Risiken

| Risiko | Bewertung | Maßnahme |
|--------|-----------|----------|
| Neuer Launcher ohne Eintrag in CANONICAL_GUI_ENTRY_POINTS | **Niedrig** | Policy: Neue Einstiegspunkte nur nach Architektur-Review und Eintrag |
| Refactor von main() ohne Bootstrap-Contract | **Niedrig** | Guards schlagen bei Änderung an |
| Tests ohne GUI (z.B. headless CI) | **Akzeptabel** | test_bootstrap_with_qsettings_produces_non_inmemory_backend nutzt qapp; pytest-qt stellt QApplication bereit |

---

## 6. Minimale Korrekturen

- **Keine** – Bootstrap-Pfade waren bereits korrekt.
- **arch_guard_config.py:** CANONICAL_GUI_ENTRY_POINTS, REQUIRED_BOOTSTRAP_PATTERNS ergänzt.

---

## 7. Freigabe

**Startup-Governance ist abgesichert.**

- 7 neue Guards in `test_startup_governance_guards.py`
- 44 Architektur-Tests insgesamt (alle bestanden)
- Policy dokumentiert in `docs/architecture/STARTUP_GOVERNANCE_POLICY.md`
- Keine funktionalen Änderungen, keine UX-Änderungen

### Restpunkte

- Keine kritischen Restpunkte
- archive/run_legacy_gui.py wird nicht explizit in CANONICAL_GUI_ENTRY_POINTS geführt, da es nur an app.main delegiert; app.main erfüllt den Contract
