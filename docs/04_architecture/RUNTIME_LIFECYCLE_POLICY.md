# Runtime Lifecycle Policy

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Referenz:** [RUNTIME_LIFECYCLE_ANALYSIS.md](./RUNTIME_LIFECYCLE_ANALYSIS.md)

---

## 1. Single-Instance-Regel

**Maximal eine produktive GUI-Instanz gleichzeitig.**

- Implementierung: `QLockFile` (PySide6.QtCore)
- Lock-Pfad: `$XDG_RUNTIME_DIR/linux-desktop-chat/instance.lock` oder `/tmp/linux-desktop-chat/instance.lock`
- Stale-Lock-Timeout: 30 Sekunden (nach Crash wird Lock automatisch freigegeben)

---

## 2. Verhalten bei zweitem Start

- Zweiter Startversuch erkennt bestehenden Lock
- Ausgabe: „Linux Desktop Chat läuft bereits. Nur eine Instanz ist erlaubt.“
- Exit-Code: 1
- Keine parallele Instanz, kein stiller Start

---

## 3. Umgehung (Tests)

- `LINUX_DESKTOP_CHAT_SINGLE_INSTANCE=0` deaktiviert den Lock
- Pytest setzt dies automatisch in `tests/conftest.py`

---

## 4. Shutdown-Contract

### 4.1 Registrierte Cleanup-Hooks

| Hook | Ort | Aktion |
|------|-----|--------|
| closeEvent | ShellMainWindow | database.commit() (falls Infra vorhanden) |
| aboutToQuit | app.runtime.lifecycle | run_shutdown_cleanup() |
| run_shutdown_cleanup | lifecycle.py | MetricsCollector.stop(), ChatService.close() (async), release_single_instance_lock() |

### 4.2 Reihenfolge

1. Benutzer schließt Fenster
2. ShellMainWindow.closeEvent: database.commit()
3. Qt: lastWindowClosed → QApplication.quit()
4. aboutToQuit wird emittiert
5. run_shutdown_cleanup: MetricsCollector.stop(), async ChatService.close(), Lock freigeben
6. qasync: Event-Loop beendet
7. Prozess beendet

### 4.3 Wer Cleanup registrieren darf

- Nur `app.runtime.lifecycle` registriert Hooks an QApplication
- Weitere Cleanup-Logik: zentral in `run_shutdown_cleanup()` ergänzen
- Keine verstreuten aboutToQuit-Listener in anderen Modulen

---

## 5. Erlaubte Hintergrundkomponenten

| Komponente | Lebensdauer | Cleanup |
|------------|-------------|---------|
| MetricsCollector | App-Start bis aboutToQuit | stop() in run_shutdown_cleanup |
| EventBus | Singleton, persistent | Kein expliziter (Prozess-Ende) |
| QTimer | An Widget gebunden | Mit Widget zerstört |
| asyncio.create_task | Bis Loop-Ende | Mit Loop-Ende abgebrochen |
| OllamaClient (aiohttp) | Singleton | ChatService.close() in run_shutdown_cleanup (async) |

---

## 6. Regeln gegen Zombie-Prozesse

- Keine unparented QTimer oder QThread
- Keine daemon-Threads mit offenen Ressourcen
- Subprocess-Aufrufe (z.B. palette_loader): nur bei Bedarf, kein Dauerbetrieb
- Lock wird in aboutToQuit freigegeben – auch bei normalem Exit

---

## 7. Regeln für spätere Erweiterungen

- Neue Langläufer: Cleanup in `run_shutdown_cleanup` oder `run_shutdown_cleanup_async` registrieren
- Neue Singleton mit Ressourcen: close()/stop() vor Prozess-Ende aufrufen
- Keine neuen aboutToQuit-Listener außerhalb von lifecycle.py ohne Architektur-Review

---

## 8. Qt-Konsolenwarnung: Desktop Portal (`qt.qpa.services`)

Beim Start kann unter Linux eine Meldung **Failed to register with host portal** / *Connection already associated with an application ID* erscheinen. Sie entsteht in der **Qt-QPA-/xdg-desktop-portal-Integration** (u. a. nach `QApplication` in `run_gui_shell.py`), **nicht** im Python-Businesscode, und ist in der Regel von **echten Anwendungsfehlern** (Traceback aus `app/`) zu trennen.

Details, betroffene Features und was **nicht** als „Fix“ empfohlen ist: [QT_DESKTOP_PORTAL_WARNING.md](../05_developer_guide/QT_DESKTOP_PORTAL_WARNING.md).
