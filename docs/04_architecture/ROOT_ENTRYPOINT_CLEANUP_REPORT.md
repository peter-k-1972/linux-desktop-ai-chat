# Root-Entrypoint Cleanup Report

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Referenz:** [ROOT_ENTRYPOINT_ANALYSIS.md](./ROOT_ENTRYPOINT_ANALYSIS.md), [ROOT_ENTRYPOINT_POLICY.md](./ROOT_ENTRYPOINT_POLICY.md)

---

## 1. Analysierte Startpfade

| Pfad | Status | Aktion |
|------|--------|--------|
| main.py | Kanonisch | Behalten, delegiert direkt an run_gui_shell |
| run_gui_shell.py | Kanonisch | Behalten (Implementierung) |
| start.sh | Kanonisch | Behalten (Desktop-Integration) |
| install-desktop.sh | Hilfsskript | Behalten |
| app/__main__.py | Kanonisch | Behalten |
| linux-desktop-chat.desktop | Desktop | Behalten |
| archive/run_legacy_gui.py | Legacy | Behalten (archiviert) |
| src/run.py | Redundant | **Entfernt** |
| src/ | Pass-through | **Entfernt** |

---

## 2. Getroffene Entscheidungen

1. **main.py** delegiert nun direkt an `run_gui_shell.main` (ohne src/run.py-Zwischenschicht).
2. **src/** vollständig entfernt – war nur Pass-through, keine eigene Logik.
3. **Kanonischer GUI-Start:** `python -m app` oder `python run_gui_shell.py`.
4. **Root-main:** `python main.py` bleibt für Benutzerkonvenienz, delegiert an run_gui_shell.

---

## 3. Entfernte / Archivierte Skripte

| Ehemals | Aktion |
|---------|--------|
| src/run.py | Gelöscht |
| src/__init__.py | Gelöscht |
| src/ | Verzeichnis entfernt |

---

## 4. Aktualisierte Guards

| Guard | Datei | Zweck |
|-------|-------|-------|
| Root-Entrypoint-Governance | tests/architecture/test_root_entrypoint_guards.py | Nur erlaubte .py/.sh im Root |
| arch_guard_config | ALLOWED_PROJECT_ROOT_ENTRYPOINT_SCRIPTS | main.py, run_gui_shell.py, start.sh, install-desktop.sh |

---

## 5. Aktualisierte Dokumentation

- ROOT_ENTRYPOINT_ANALYSIS.md – src/run.py als entfernt markiert
- ROOT_ENTRYPOINT_POLICY.md – Bereinigung dokumentiert
- ARCHITECTURE_BASELINE_2026.md – main.py Delegation
- STARTUP_GOVERNANCE_POLICY.md, STARTUP_GOVERNANCE_REPORT.md
- FULL_SYSTEM_CHECKUP_ANALYSIS.md
- CONSOLIDATION_REPORT.md
- IMPLEMENTATION_SUMMARY.md, PHASE1_CHANGES.md

---

## 6. Verbleibende Root-Restpunkte

### Projekt-Root (erlaubt)

- main.py
- run_gui_shell.py
- start.sh
- install-desktop.sh

### app/ Root (Phase D)

- db.py, critic.py, ollama_client.py – TEMPORARILY_ALLOWED_ROOT_FILES (nicht Schwerpunkt dieses Tasks)

---

## 7. Abschluss

Root-Verzeichnis bereinigt. Kanonischer Startpfad klar definiert. Guards verhindern künftige Drift durch neue Root-Startskripte ohne Architektur-Review.
