# App Core Decoupling Plan

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Status:** Plan – keine physischen Moves  
**Referenz:** APP_REFACTOR_EXECUTION_REPORT.md, APP_TARGET_PACKAGE_ARCHITECTURE.md

---

## Übersicht

Zwei Module blockieren den Move nach `app/core`, weil sie PySide6/Qt-Abhängigkeiten haben:

1. `app/context/active_project.py` – QObject, Signal
2. `app/settings.py` – QSettings

Dieser Plan beschreibt die minimale Entkopplung ohne Big-Bang-Refactoring.

---

## 1. Modul: app/context/active_project.py

### 1.1 Aktuelle Qt-Abhängigkeiten

| Import | Verwendung |
|--------|------------|
| `PySide6.QtCore.QObject` | Basisklasse von `ActiveProjectContext` |
| `PySide6.QtCore.Signal` | `active_project_changed = Signal(object, object)` |

### 1.2 Warum der Move blockiert ist

- `app.core` darf laut Zielarchitektur **keine** PySide6-Imports enthalten.
- `ActiveProjectContext` erbt von `QObject` und nutzt `Signal` für UI-Updates.
- Konsumenten (ProjectsWorkspace, BreadcrumbManager, ProjectOverviewPanel, …) verbinden sich via `ctx.active_project_changed.connect(callback)` – Qt-Signal-API.

### 1.3 Aktuelle Nutzer des Signals

| Datei | Nutzung |
|-------|---------|
| `app/gui/domains/operations/projects/projects_workspace.py` | `ctx.active_project_changed.connect(self._on_active_project_changed)` |
| Weitere GUI-Breadcrumbs, Introspection etc. | `get_active_project_context()` für Lese-Zugriff |

### 1.4 Minimale Refactoring-Strategie

**Option A: Callback-Interface (empfohlen)**

- `ActiveProjectContext` erbt nicht mehr von `QObject`.
- Statt Signal: `_listeners: List[Callable[[Optional[int], Optional[Dict]], None]]`.
- `subscribe(callback)` / `unsubscribe(callback)` – analog zu `project_events`.
- `set_active()` / `set_none()` rufen alle Listener auf.
- GUI-Komponenten rufen `subscribe()` statt `connect()`.

**Option B: Event-Bus (bereits vorhanden)**

- `project_events` existiert bereits. `ProjectContextManager` emittiert `project_context_changed`.
- `ActiveProjectContext` könnte als reiner State-Holder bleiben; Benachrichtigung über `project_events`.
- Problem: `ActiveProjectContext` und `ProjectContextManager` sind aktuell synchronisiert – beide müssen existieren. Doppelte Event-Quelle vermeiden.

**Empfehlung:** Option A – Callback-Interface. Weniger Änderungen an bestehenden Abhängigkeiten; klare API.

### 1.5 Empfohlene Zielstruktur

```
app/core/context/
├── __init__.py
├── active_project.py          # Kein QObject, kein Signal
├── project_context_manager.py # (bereits in core)
```

**active_project.py (nach Refactor):**

```python
from typing import Any, Callable, Dict, List, Optional

class ActiveProjectContext:
    """Globaler Kontext für das aktive Projekt. Kein Qt."""

    def __init__(self):
        self._project_id: Optional[int] = None
        self._project: Optional[Dict[str, Any]] = None
        self._listeners: List[Callable[[Optional[int], Optional[Dict]], None]] = []

    def subscribe(self, callback: Callable[[Optional[int], Optional[Dict]], None]) -> None:
        self._listeners.append(callback)

    def unsubscribe(self, callback: Callable[[Optional[int], Optional[Dict]], None]) -> None:
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify(self) -> None:
        for cb in self._listeners:
            cb(self._project_id, self._project)

    # ... set_active, set_none, clear, properties ...
    # Bei set_active/set_none: self._notify() statt self.active_project_changed.emit(...)
```

**Adapter für GUI (optional, Rückwärtskompatibilität):**

Wenn `ProjectsWorkspace` weiterhin Qt-Signal-API nutzen soll: `gui/adapters/active_project_qt_adapter.py` – wrappt `ActiveProjectContext` und emittiert Qt-Signal bei `_notify()`. Core bleibt Qt-frei.

### 1.6 Risiko

| Risiko | Mitigation |
|--------|------------|
| Vergessene Listener-Registrierung | Projekte nutzen bereits `subscribe_project_events`; `subscribe` ist analog |
| Tests brechen | `set_active_project_context(ctx)` für Tests beibehalten; Mock-Context ohne Qt |
| Projekte nutzt `connect()` | Einzige Stelle: `projects_workspace.py` – auf `subscribe()` umstellen |

### 1.7 Tests zur Absicherung

- `tests/test_projects.py` – Projekt-CRUD; `get_active_project_context()` Lese-Zugriff
- Neuer Test: `test_active_project_context_notifies_listeners` – subscribe, set_active, assert callback aufgerufen
- Optional: `test_active_project_context_no_qt` – `import app.context.active_project` ohne PySide6

---

## 2. Modul: app/settings.py

### 2.1 Aktuelle Qt-Abhängigkeiten

| Import | Verwendung |
|--------|------------|
| `PySide6.QtCore.QSettings` | `self.settings = QSettings("OllamaChat", "LinuxDesktopChat")` |
| `self.settings.value(key, default)` | Laden aller Einstellungen |
| `self.settings.setValue(key, value)` | Speichern aller Einstellungen |

### 2.2 Warum der Move blockiert ist

- `QSettings` ist Qt-spezifisch (nutzt Plattform-APIs: Windows Registry, macOS plist, Linux INI).
- `app.core` darf keine PySide6-Imports. AppSettings ist aber App-weite Konfiguration – Kernlogik.

### 2.3 Minimale Refactoring-Strategie

**SettingsBackend-Interface**

```python
# app/core/config/settings_backend.py (Protocol)
from typing import Any, Optional

class SettingsBackend(Protocol):
    def value(self, key: str, default: Any = None) -> Any: ...
    def setValue(self, key: str, value: Any) -> None: ...
```

**AppSettings** bleibt fachlich; `self.settings` wird injizierbar:

```python
class AppSettings:
    def __init__(self, backend: Optional[SettingsBackend] = None):
        self._backend = backend or _default_backend()

def _default_backend() -> SettingsBackend:
    from PySide6.QtCore import QSettings
    return QSettings("OllamaChat", "LinuxDesktopChat")
```

- `AppSettings` selbst importiert QSettings nur in `_default_backend()` – lazy, optional.
- Für Tests: `AppSettings(backend=FakeSettingsBackend())` – kein Qt.
- Für Produktion: `_default_backend()` liefert QSettings – Verhalten unverändert.

**Alternative:** `app/core/config/settings.py` enthält nur die Datenstruktur und `load`/`save` – das Backend wird von außen injiziert. GUI-Bootstrap liefert `QSettingsBackend`; Tests liefern `DictBackend` oder `InMemoryBackend`.

### 2.4 Empfohlene Zielstruktur

```
app/core/config/
├── __init__.py
├── settings_backend.py
├── settings.py
└── qsettings_backend.py
```

- `settings_backend.py`: Protocol `SettingsBackend`
- `settings.py`: `AppSettings` mit `backend: SettingsBackend` – keine direkten Qt-Imports
- `qsettings_backend.py`: `QSettingsBackend` implementiert `SettingsBackend`; hier liegt der QSettings-Import. **Dieses Modul bleibt in app/gui oder app/core mit optionalem Import** – oder als separates Modul, das nur bei GUI-Start geladen wird.

**Pragmatische Variante:** `QSettingsBackend` in `app/core/config/settings.py` als optionaler Import:

```python
def _default_backend() -> "SettingsBackend":
    try:
        from PySide6.QtCore import QSettings
        return QSettingsBackendAdapter(QSettings("OllamaChat", "LinuxDesktopChat"))
    except ImportError:
        return InMemoryBackend()
```

- `app.core` würde dann bei Import von `settings` ggf. PySide6 laden – **Core nicht mehr Qt-frei**.
- **Besser:** `AppSettings` bleibt in Root oder `app/core/config`; `backend` wird **immer** von außen übergeben. `run_gui_shell.py` / `Infrastructure` erstellt `QSettings(...)` und übergibt es an `AppSettings(backend=...)`. `AppSettings` selbst hat keinen Qt-Import.

### 2.5 Empfohlene Zielstruktur (bereinigt)

```
app/core/config/
├── __init__.py
├── settings_backend.py
├── settings.py
```

- `app/core/config/settings_backend.py`: Protocol + `InMemoryBackend` (für Tests)
- `app/core/config/settings.py`: `AppSettings(backend: SettingsBackend)` – keine Qt-Imports
- `app/gui/bootstrap.py` oder `app/services/infrastructure.py`: Erstellt `QSettings(...)`, wrappt in `QSettingsBackendAdapter`, übergibt an `AppSettings(backend=...)`. Der QSettings-Import liegt ausschließlich in GUI/Infrastructure.

### 2.6 Risiko

| Risiko | Mitigation |
|--------|------------|
| Viele Aufrufer von `AppSettings()` | `Infrastructure` ist zentraler Erstellungsort; alle anderen erhalten Settings von dort |
| `AppSettings()` in Tests | Tests nutzen `AppSettings(backend=InMemoryBackend())` oder Fixture |
| QSettings-Verhalten (plattformspezifisch) | QSettingsBackendAdapter delegiert 1:1; Verhalten unverändert |

### 2.7 Tests zur Absicherung

- `tests/test_model_settings_bindings.py` – AppSettings load/save
- `tests/test_app.py` – AppSettings-Instanziierung
- Neuer Test: `test_app_settings_with_in_memory_backend` – ohne Qt
- Smoke: `test_app_startup.py` – AppSettings lädt

---

## 3. Reihenfolge

1. **active_project.py** – Refactor zu Callback-Interface; `projects_workspace.py` auf `subscribe()` umstellen
2. **settings.py** – SettingsBackend-Interface; Infrastructure/Bootstrap liefert Backend
3. **Move** – `app/context/` → `app/core/context/`, `app/settings.py` → `app/core/config/settings.py` (nur nach Refactor)

---

## 4. Keine vorbereitenden Code-Änderungen in dieser Phase

Laut Aufgabenstellung: „Noch KEINE physischen Datei-Moves für diese zwei Module. Zuerst nur saubere Entkopplungsplanung und, falls risikoarm möglich, kleine vorbereitende Codeänderungen.“

**Optionale vorbereitende Änderungen (risikoarm):**

- `active_project.py`: Keine – Refactor würde Signal-API brechen; besser als geschlossener Schritt.
- `settings.py`: `SettingsBackend` Protocol + `InMemoryBackend` in neuem Modul anlegen; `AppSettings` noch nicht ändern – ermöglicht spätere schrittweise Migration.

**Empfehlung:** Keine Code-Änderungen in dieser Phase. Plan steht; Umsetzung in separatem Schritt.
