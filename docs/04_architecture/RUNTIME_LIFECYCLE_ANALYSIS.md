# Runtime Lifecycle Analyse

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Stand:** Nach Lifecycle-Härtung

---

## 1. Aktueller Startpfad

| Phase | Ort | Aktion |
|-------|-----|--------|
| Entry | main.py / run_gui_shell.py / python -m app | Delegation an run_gui_shell.main |
| Bootstrap | run_gui_shell.main() | load_env, install_gui_log_handler, get_metrics_collector |
| **Single-Instance** | run_gui_shell | try_acquire_single_instance_lock() – bei Misserfolg sys.exit(1) |
| Qt | run_gui_shell | QApplication(sys.argv), setApplicationName, setDesktopFileName |
| Shutdown-Hooks | run_gui_shell | register_shutdown_hooks(app) |
| Event-Loop | run_gui_shell | qasync.QEventLoop(app), asyncio.set_event_loop(loop) |
| Infra | run_gui_shell | init_infrastructure(create_qsettings_backend()), get_infrastructure() |
| Backends | run_gui_shell | set_chat_backend(ChatBackend()), set_knowledge_backend(KnowledgeBackend()) |
| Theme | run_gui_shell | get_theme_manager().set_theme() |
| Window | run_gui_shell | ShellMainWindow(), win.show() |
| Run | run_gui_shell | loop.run_forever() oder app.exec() |

**Single-Instance:** QLockFile in app.runtime.lifecycle. Lock-Pfad: `$XDG_RUNTIME_DIR/linux-desktop-chat/instance.lock` oder `/tmp/linux-desktop-chat/instance.lock`.

---

## 2. Aktueller Shutdown-Pfad

| Phase | Trigger | Aktion |
|-------|---------|--------|
| Fenster schließen | User klickt X | ShellMainWindow.closeEvent (DB-Commit, falls vorhanden) |
| Qt Default | lastWindowClosed | QApplication.quit() (quitOnLastWindowClosed=true) |
| aboutToQuit | Qt | run_shutdown_cleanup() – MetricsCollector.stop(), async Cleanup (ChatService), release_single_instance_lock |
| qasync | aboutToQuit | _after_run_forever, Loop-Ende |
| sys.exit | run_gui_shell | sys.exit(loop.run_forever()) |

**ShellMainWindow** hat closeEvent für DB-Commit (Konsistenz mit Legacy). Shutdown-Cleanup zentral in lifecycle.run_shutdown_cleanup (inkl. async ChatService.close).

---

## 3. Potenzielle Mehrfachstart-Risiken

| Risiko | Status |
|--------|--------|
| Kein Lock | **Behoben:** QLockFile aktiv |
| Stiller Parallelstart | **Behoben:** sys.exit(1) bei zweitem Start |
| Stale Lock nach Crash | **Mitigation:** 30-Sekunden-Timeout (removeStaleLockFile) |
| Tests mit Lock | **Mitigation:** LINUX_DESKTOP_CHAT_SINGLE_INSTANCE=0 in conftest |

---

## 4. Potenzielle Shutdown-Risiken

| Komponente | Risiko | Status |
|------------|--------|--------|
| MetricsCollector | stop() nicht aufgerufen | **Behoben:** in run_shutdown_cleanup |
| OllamaClient (aiohttp) | close() nicht aufgerufen | **Behoben:** run_shutdown_cleanup_async in aboutToQuit |
| ChatService | close() nicht aufgerufen | **Behoben:** via run_shutdown_cleanup_async |
| QTimer | An Widgets gehängt | Mit Widget zerstört – kein expliziter Stop nötig |
| asyncio.create_task | Tasks laufen bis Loop-Ende | Mit Loop-Ende abgebrochen |
| EventBus | Subscriber bleiben | MetricsCollector.stop() entfernt Subscriber |
| DatabaseManager | Kein commit vor Exit | **Behoben:** closeEvent in ShellMainWindow |

---

## 5. Relevante Threads / Timer / Async

| Typ | Ort | Lebensdauer |
|-----|-----|-------------|
| QTimer | Viele Panels (introspection, agent_status, logs_monitor, etc.) | An Widget gebunden |
| asyncio.create_task | chat_workspace, providers_workspace, models_workspace, etc. | Bis Loop-Ende |
| QTimer.singleShot | Diverse (defer_load, scroll, etc.) | Einmalig |
| EventBus | MetricsCollector, DebugStore | Singleton, persistent |
| OllamaClient | Infrastructure | Singleton, aiohttp Session – close() im Shutdown |
| threading.Lock | debug_store, gui_log_buffer | Prozess-Ende beendet |

Keine expliziten threading.Thread in der App-Logik.

---

## 6. Mögliche Zombie-/Restprozess-Ursachen

| Ursache | Mitigation |
|---------|------------|
| Subprocess in palette_loader | Nur bei Bedarf, kein Dauerbetrieb |
| aiohttp Session nicht geschlossen | **Behoben:** run_shutdown_cleanup_async |
| Zweite Instanz startet | **Behoben:** Single-Instance-Lock |
| Unparented QTimer/QThread | Policy: keine unparented Objekte |

---

## 7. Singletons / Stores

| Singleton | Cleanup |
|-----------|---------|
| _ServiceInfrastructure | Kein expliziter (Prozess-Ende) |
| _event_bus | reset_event_bus() für Tests |
| _collector (MetricsCollector) | stop() in run_shutdown_cleanup |
| get_chat_service | close() via run_shutdown_cleanup_async |
| get_metrics_store | Kein expliziter |
| get_debug_store | Kein expliziter |
