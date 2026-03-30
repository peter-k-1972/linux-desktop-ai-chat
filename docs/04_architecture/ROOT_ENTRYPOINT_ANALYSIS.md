# Root-Entrypoint-Analyse

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16

---

## 1. Übersicht

| Pfad | Typ | Produktiv | Delegation | Status |
|------|-----|-----------|------------|--------|
| main.py | Python | Ja | → run_gui_shell.main | Kanonisch (direkt) |
| run_gui_shell.py | Python | Ja | — (Implementierung) | **Kanonisch** |
| start.sh | Shell | Ja | → python -m app | **Kanonisch** (Desktop/venv) |
| app/__main__.py | Python | Ja | → run_gui_shell.main | **Kanonisch** |
| install-desktop.sh | Shell | Ja | Installiert .desktop | **Hilfsskript** |
| linux-desktop-chat.desktop | Desktop | Ja | Exec=start.sh | **Desktop-Integration** |
| archive/run_legacy_gui.py | Python | Nein | → app.main.main | **Legacy** |

---

## 2. Detailanalyse

### main.py (Root)

- **Zweck:** Standard-Startpunkt für `python main.py`
- **Funktionsfähig:** Ja
- **Produktiv:** Ja
- **Delegation:** `from run_gui_shell import main`
- **Bewertung:** Kanonisch. Delegiert direkt an run_gui_shell.

### run_gui_shell.py

- **Zweck:** Implementierung der GUI-Shell. Startet ShellMainWindow.
- **Funktionsfähig:** Ja
- **Produktiv:** Ja
- **Delegation:** Keine (Implementierung)
- **Bewertung:** **Kanonisch.** Enthält die eigentliche Bootstrap-Logik.

### start.sh

- **Zweck:** Shell-Starter für Desktop-Integration. Nutzt venv, startet python -m app.
- **Funktionsfähig:** Ja
- **Produktiv:** Ja
- **Delegation:** cd, activate, `exec python -m app "$@"`
- **Bewertung:** **Kanonisch.** Wird von .desktop verwendet.

### app/__main__.py

- **Zweck:** Modul-Einstiegspunkt für `python -m app`
- **Funktionsfähig:** Ja
- **Produktiv:** Ja
- **Delegation:** `from run_gui_shell import main`
- **Bewertung:** **Kanonisch.** Empfohlener Startpfad.

### src/run.py (entfernt)

- **Zweck:** War Zwischenschicht für main.py
- **Bewertung:** **Entfernt.** main.py delegiert nun direkt an run_gui_shell.

### install-desktop.sh

- **Zweck:** Installiert .desktop-Datei in ~/.local/share/applications/
- **Funktionsfähig:** Ja
- **Produktiv:** Ja (Installation)
- **Delegation:** Keine (Hilfsskript)
- **Bewertung:** **Hilfsskript.** Behalten.

### linux-desktop-chat.desktop

- **Zweck:** Desktop-Entry für Startmenü/Desktop-Verknüpfung
- **Funktionsfähig:** Ja
- **Produktiv:** Ja
- **Delegation:** Exec=PROJECT_DIR/start.sh (install-desktop.sh ersetzt PROJECT_DIR)
- **Bewertung:** **Desktop-Integration.** Behalten.

### archive/run_legacy_gui.py

- **Zweck:** Startet Legacy-GUI (MainWindow, ChatWidget)
- **Funktionsfähig:** Ja
- **Produktiv:** Nein (Legacy)
- **Delegation:** `from app.main import main as legacy_main`
- **Bewertung:** **Legacy.** Bereits archiviert.

---

## 3. Root-Dateien (app/ Root)

| Datei | Typ | Zweck | Phase |
|-------|-----|-------|-------|
| db.py | Re-Export | app.core.db.database_manager.DatabaseManager | TEMPORARILY_ALLOWED_ROOT_FILES |
| critic.py | Modul | CriticConfig, review_response (noch nicht aktiv) | TEMPORARILY_ALLOWED_ROOT_FILES |

- **db.py:** Re-Export für Rückwärtskompatibilität. Ziel: app.core.db.
- **critic.py:** Struktur für zukünftigen Critic-Modus. Noch nicht aktiv. Phase D: verschieben.

---

## 4. Durchgeführte Bereinigung

1. **main.py:** Delegiert nun direkt an run_gui_shell
2. **src/:** Entfernt (war nur Pass-through)
3. **start.sh, install-desktop.sh, linux-desktop-chat.desktop:** Behalten
4. **archive/run_legacy_gui.py:** Behalten
