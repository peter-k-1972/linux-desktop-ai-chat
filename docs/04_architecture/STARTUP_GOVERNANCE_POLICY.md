# Startup Governance Policy

**Projekt:** Linux Desktop Chat  
**Referenz:** `docs/architecture/STARTUP_GOVERNANCE_REPORT.md`  
**Tests:** `tests/architecture/test_startup_governance_guards.py`

---

## 1. Ziel

Startup- und Bootstrap-Konsistenz absichern: definierte Einstiegspunkte, klare Reihenfolge, Schutz vor Frühzugriffen und Verdrahtungsdrift.

---

## 2. Erlaubte Einstiegspunkte

| Einstiegspunkt | Pfad | Typ | Delegation |
|----------------|------|-----|------------|
| **Standard-GUI** | `run_gui_shell.py` | Kanonisch | — |
| **Standard-GUI** | `app/__main__.py` | Kanonisch | → run_gui_shell.main |
| **Standard-GUI** | `main.py` (Root) | Kanonisch | → run_gui_shell.main |
| **Legacy-GUI** | `archive/run_legacy_gui.py` | Legacy | → app.main.main |

### 2.1 Verbotene Direktstarts

- Kein direkter Import und Aufruf von `ShellMainWindow()` oder `MainWindow()` ohne vorherigen Bootstrap
- Kein direkter Aufruf von `get_infrastructure()` oder `get_chat_service()` etc. vor `init_infrastructure()` in GUI-Kontext
- Keine neuen inoffiziellen Einstiegspunkte ohne Governance-Review

**Abgrenzung:** `main.py` und `app/__main__.py` sind kanonische **Delegations-Einstiegspunkte**, aber keine eigenständigen Bootstrap-Implementierungen. Den direkten Bootstrap-Contract `init_infrastructure(create_qsettings_backend())` tragen die Implementierungen `run_gui_shell.py` und `app/main.py`.

---

## 3. Bootstrap-Reihenfolge (GUI)

Für produktive GUI-Läufe gilt:

1. **Umgebung:** `load_env()` (falls verwendet)
2. **Qt:** `QApplication(sys.argv)`
3. **Event-Loop:** qasync/QEventLoop (falls async)
4. **Infrastruktur:** `init_infrastructure(settings_backend=create_qsettings_backend())`
5. **Materialisierung:** `get_infrastructure()` (optional, triggert Erstellung)
6. **Backends:** `set_chat_backend(ChatBackend())`, `set_knowledge_backend(KnowledgeBackend())` (Shell)
7. **Fenster:** `ShellMainWindow()` oder `MainWindow()` (Legacy)

### 3.1 Wer init_infrastructure() aufrufen darf

- **Nur:** direkte GUI-Bootstrap-Module (`run_gui_shell.py`, `app/main.py`)
- **Delegations-Einstiegspunkte:** `main.py`, `app/__main__.py` rufen nicht selbst `init_infrastructure()` auf, sondern delegieren an `run_gui_shell.main`
- **Nicht:** services, core, agents, tools, prompts, rag, providers

### 3.2 Wann GUI-Komponenten erzeugt werden dürfen

- **Erst nach** `init_infrastructure(settings_backend=...)` und vor dem ersten `get_infrastructure()`-Aufruf durch Services
- ShellMainWindow, ChatBackend, KnowledgeBackend: nach Schritt 4

---

## 4. Module ohne Infrastruktur-Materialisierung beim Import

Folgende Module dürfen **nicht** bei Import-Zeit `get_infrastructure()`, `get_chat_service()`, `get_model_service()` etc. aufrufen:

- `app.gui.shell.main_window` (ShellMainWindow)
- `app.gui.bootstrap` (register_all_screens)
- `app.gui.workspace.workspace_host`
- `app.gui.navigation.*` (Sidebar, CommandPalette)
- Alle Domain-Screens (DashboardScreen, OperationsScreen, …)

Materialisierung erfolgt lazy in Methoden/Callbacks, nicht bei Klassen- oder Modul-Import.

---

## 5. Test-/CLI-Fallbacks

| Kontext | Backend | Verhalten |
|---------|---------|-----------|
| **Tests** | InMemoryBackend | Kein `init_infrastructure()` oder `init_infrastructure(None)`; Tests nutzen `set_infrastructure(mock)` |
| **CLI/Tools** | InMemoryBackend | Kein GUI-Bootstrap; falls Infrastruktur genutzt wird: InMemoryBackend |
| **Produktive GUI** | QSettingsBackend | `init_infrastructure(create_qsettings_backend())` vor erstem Service-Zugriff |

### 5.1 Stille Fallbacks vermeiden

- Produktive GUI-Läufe dürfen **nicht** versehentlich mit InMemoryBackend starten
- Einstiegspunkte müssen explizit `init_infrastructure(create_qsettings_backend())` aufrufen
- Guards prüfen, dass Bootstrap-Code diese Aufrufe enthält

---

## 6. Ausnahmen

- Keine stillen Ausnahmen
- Neue direkte Bootstrap-Implementierungen nur nach Architektur-Review und Eintrag in `CANONICAL_GUI_ENTRY_POINTS`
