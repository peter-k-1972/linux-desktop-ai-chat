# Root-Entrypoint-Policy

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Referenz:** [ROOT_ENTRYPOINT_ANALYSIS.md](./ROOT_ENTRYPOINT_ANALYSIS.md)

---

## 1. Kanonischer GUI-Startpfad

**Primär:** `python -m app` (über start.sh oder direkt)

**Alternativ:** `python run_gui_shell.py` (direkt, gleiche Implementierung)

**Root-main:** `python main.py` delegiert an run_gui_shell.main (nur für Benutzerkonvenienz).

---

## 2. Erlaubte Root-Dateien (Projekt-Root)

### Startskripte (erlaubt)

| Datei | Rolle |
|-------|-------|
| main.py | Delegiert an run_gui_shell.main |
| run_gui_shell.py | Kanonische GUI-Implementierung |
| start.sh | Shell-Starter für Desktop (venv, python -m app) |
| install-desktop.sh | Installiert .desktop (Hilfsskript) |
| linux-desktop-chat.desktop | Desktop-Entry-Template |

**`run_workbench_demo.py`** ist ein zulässiger **Development-/Demo-Einstieg** im Projekt-Root (Workbench/UI-Demos, nicht der kanonische Produktstart). Er ist in `tests/architecture/arch_guard_config.py` unter `ALLOWED_PROJECT_ROOT_ENTRYPOINT_SCRIPTS` eingetragen.

### Nicht erlaubt

- Keine weiteren Python-Startskripte im Root ohne Architektur-Review
- Keine zusätzlichen Shell-Starter ohne Dokumentation
- Kein src/ als Pass-through (bereinigt 2026-03-16)

---

## 3. Legacy / Dev / Install

| Kategorie | Pfad | Regel |
|-----------|------|-------|
| **Legacy** | archive/run_legacy_gui.py | Nur für Referenz; nicht produktiv |
| **Install** | install-desktop.sh | Hilfsskript; einmalig ausführen |
| **Desktop** | linux-desktop-chat.desktop | Template; install-desktop.sh setzt PROJECT_DIR |

---

## 4. Bereinigt (2026-03-16)

| Ehemals | Aktion |
|---------|--------|
| src/run.py | Entfernt (main.py delegiert direkt) |
| src/ | Entfernt (nur Pass-through) |

---

## 5. Neue Startpfade

Neue Startskripte im Root erfordern:

1. Architektur-Review
2. Erweiterung von ROOT_ENTRYPOINT_ANALYSIS.md
3. Erweiterung der Governance-Guards (tests/architecture)
4. Aktualisierung von ROOT_ENTRYPOINT_POLICY.md

---

## 6. app/ Root

Siehe arch_guard_config: ALLOWED_APP_ROOT_FILES, TEMPORARILY_ALLOWED_ROOT_FILES.

critic.py: Phase D (APP_MOVE_MATRIX).

Die verbleibenden Einträge in `TEMPORARILY_ALLOWED_ROOT_FILES` sind rollenklassifiziert
(`release_governance`, `qa_harness`, `qml_launch_governance`, `legacy_experiment`) und
nicht pauschal als Re-Export-/Bridge-Reste zu lesen.
