# Runtime Lifecycle Hardening Report

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Referenz:** [RUNTIME_LIFECYCLE_ANALYSIS.md](./RUNTIME_LIFECYCLE_ANALYSIS.md), [RUNTIME_LIFECYCLE_POLICY.md](./RUNTIME_LIFECYCLE_POLICY.md)

---

## 1. Analysierter Ist-Zustand

| Aspekt | Vor Härtung | Nach Härtung |
|--------|-------------|--------------|
| Single-Instance | Kein Schutz | QLockFile aktiv |
| Shutdown-Cleanup | Kein expliziter | run_shutdown_cleanup mit sync + async |
| MetricsCollector | stop() nie aufgerufen | stop() in aboutToQuit |
| OllamaClient (aiohttp) | close() nie aufgerufen | ChatService.close() in run_shutdown_cleanup |
| Lock-Freigabe | N/A | release_single_instance_lock in aboutToQuit |
| ShellMainWindow | Kein closeEvent | closeEvent für database.commit() |

---

## 2. Gewählte Single-Instance-Strategie

**QLockFile** (PySide6.QtCore)

| Aspekt | Entscheidung |
|--------|--------------|
| Mechanismus | QLockFile – plattformstabil, Qt-nativ |
| Lock-Pfad | `$XDG_RUNTIME_DIR/linux-desktop-chat/instance.lock` oder `/tmp/linux-desktop-chat/instance.lock` |
| Stale-Timeout | 30 Sekunden |
| Zweiter Start | Exit mit Meldung, Exit-Code 1 |
| Test-Umgehung | `LINUX_DESKTOP_CHAT_SINGLE_INSTANCE=0` |
| Lock-Erwerb | Vor QApplication-Erstellung in run_gui_shell |
| Lock-Freigabe | In run_shutdown_cleanup (aboutToQuit) |

---

## 3. Shutdown-Härtungen

| Maßnahme | Implementierung |
|----------|-----------------|
| aboutToQuit-Hook | register_shutdown_hooks(app) in run_gui_shell |
| run_shutdown_cleanup | MetricsCollector.stop(), _run_async_cleanup_blocking() (ChatService.close), release_single_instance_lock() |
| ShellMainWindow.closeEvent | database.commit() vor Fensterschließung |
| quitOnLastWindowClosed | Explizit True (Standard) |
| Async-Cleanup | run_shutdown_cleanup_async() – ChatService.close() schließt aiohttp Session |

---

## 4. Implementierte Tests/Guards

| Test | Datei | Prüfung |
|------|-------|---------|
| test_run_gui_shell_uses_single_instance_check | test_lifecycle_guards.py | try_acquire_single_instance_lock, register_shutdown_hooks im Startpfad |
| test_lifecycle_module_exists | test_lifecycle_guards.py | lifecycle-Modul mit erforderlichen Funktionen |
| test_run_gui_shell_exits_on_second_instance | test_lifecycle_guards.py | sys.exit(1) bei bestehendem Lock |
| test_shell_main_window_has_close_event | test_lifecycle_guards.py | ShellMainWindow hat closeEvent für Shutdown |
| test_lifecycle_has_async_cleanup | test_lifecycle_guards.py | run_shutdown_cleanup_async vorhanden |
| test_lifecycle_module_importable | test_lifecycle.py | Import der Lifecycle-Funktionen |
| test_single_instance_lock_acquired_when_disabled | test_lifecycle.py | Lock umgehbar für Tests |
| test_run_shutdown_cleanup_no_exception | test_lifecycle.py | run_shutdown_cleanup wirft nicht |
| test_run_shutdown_cleanup_async_no_exception | test_lifecycle.py | run_shutdown_cleanup_async wirft nicht |

---

## 5. Verbleibende Restrisiken

| Risiko | Bewertung | Mitigation |
|--------|-----------|------------|
| Stale Lock nach Kill -9 | Niedrig | 30-Sekunden-Timeout entfernt Lock automatisch |
| XDG_RUNTIME_DIR nicht gesetzt | Niedrig | Fallback auf /tmp |
| Parallele pytest-Worker mit run_gui_shell.main() | Niedrig | conftest setzt SINGLE_INSTANCE=0 |
| Async-Cleanup bei sehr kurzer Laufzeit | Niedrig | 2s Timeout; Prozess-Ende schließt Ressourcen ohnehin |

---

## 6. Freigabeempfehlung

**Freigegeben** für produktiven Einsatz.

- Single-Instance-Schutz aktiv und verifiziert
- Shutdown-Cleanup (MetricsCollector, ChatService/OllamaClient, Lock) vollständig integriert
- ShellMainWindow closeEvent für DB-Konsistenz
- Tests und Guards vorhanden
- Keine Feature-Änderungen, minimal-invasiv
