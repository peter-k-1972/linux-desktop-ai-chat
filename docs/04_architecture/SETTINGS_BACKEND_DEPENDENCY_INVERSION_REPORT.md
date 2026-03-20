# Settings-Backend Dependency Inversion – Abschlussreport

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Ziel:** Beseitigung der letzten echten Layer-Verletzung `services → gui`

---

## 1. Bestandsaufnahme (Phase 1)

### 1.1 Vor dem Refactor

| Komponente | Verantwortung | Abhängigkeiten |
|------------|---------------|----------------|
| `app/core/config/settings_backend.py` | SettingsBackend (Protocol), InMemoryBackend | Keine |
| `app/core/config/settings.py` | AppSettings (arbeitet über injizierbares Backend) | core/config |
| `app/gui/qsettings_backend.py` | QSettingsBackendAdapter, create_qsettings_backend | PySide6.QtCore |
| `app/services/infrastructure.py` | Singleton: OllamaClient, DB, AppSettings | **→ app.gui.qsettings_backend** (Verletzung) |

### 1.2 Problem

`_create_default_settings_backend()` in infrastructure.py versuchte, bei Bedarf `app.gui.qsettings_backend` zu importieren. Das verletzte die Layer-Regel: **services darf gui nicht kennen**.

### 1.3 Benötigte Funktionalität

- infrastructure braucht ein `SettingsBackend` (value/setValue)
- Bereits als Protocol in `app.core.config.settings_backend` definiert
- QSettingsBackendAdapter implementiert dieses Protocol

---

## 2. Durchgeführter Refactor (Phase 2)

### 2.1 Änderungen

| Datei | Änderung |
|-------|----------|
| `app/services/infrastructure.py` | `_create_default_settings_backend()` entfernt. Kein Import von `app.gui`. Default: `InMemoryBackend()` wenn kein Backend via `init_infrastructure()` gesetzt. |
| `app/main.py` (Legacy) | `init_infrastructure(create_qsettings_backend())` vor Erstellung von MainWindow ergänzt. |
| `run_gui_shell.py` | Unverändert – ruft bereits `init_infrastructure(create_qsettings_backend())` auf. |
| `app/gui/qsettings_backend.py` | Docstring ergänzt: Implementierung von core SettingsBackend. |
| `tests/architecture/arch_guard_config.py` | Ausnahme `services/infrastructure.py → gui` entfernt. |

### 2.2 Architektur nach Refactor

```
core/config/settings_backend.py   SettingsBackend (Protocol), InMemoryBackend
         ↑
         | implementiert
         |
gui/qsettings_backend.py         QSettingsBackendAdapter (QSettings)

services/infrastructure.py       nutzt nur SettingsBackend (core)
         ↑
         | injiziert von außen
         |
run_gui_shell.py                 init_infrastructure(create_qsettings_backend())
run_legacy_gui → app.main        init_infrastructure(create_qsettings_backend())
```

- **services** kennt nur `core` (SettingsBackend, InMemoryBackend)
- **gui** implementiert die core-Abstraktion
- **Verkabelung** erfolgt im Bootstrap (run_gui_shell, app.main)

---

## 3. Verhalten

| Szenario | Backend |
|----------|---------|
| `python run_gui_shell.py` | QSettings (via init_infrastructure vor get_infrastructure) |
| `python run_legacy_gui.py` | QSettings (via init_infrastructure in app.main) |
| Tests ohne init_infrastructure | InMemoryBackend |
| CLI / andere Einstiegspunkte | InMemoryBackend |

---

## 4. Governance

- **Layer-Regel:** `services → gui` ist behoben.
- **Architektur-Tests:** 37 passed (inkl. `test_services_do_not_import_gui`).
- **Smoke-Tests:** 9 passed (test_shell_gui).

---

## 5. Keine weiteren Änderungen

- Keine neuen Features
- Keine UX-Änderungen
- Keine funktionalen Umbauten außer Settings-Backend-Zugriff
- Bestehendes Verhalten bleibt erhalten
