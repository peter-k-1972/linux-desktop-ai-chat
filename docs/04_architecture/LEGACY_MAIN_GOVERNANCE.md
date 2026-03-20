# Legacy app.main – Governance

**Datum:** 2026-03-16  
**Kontext:** Full System Checkup Restpoint Remediation

---

## Status

`app.main` ist **Legacy** und nur für die Archiv-GUI relevant.

| Aspekt | Status |
|--------|--------|
| Produktiver Einstieg | **Nein** – Standard: `python main.py` → `run_gui_shell` |
| Nutzung | Nur `archive/run_legacy_gui.py` |
| Bootstrap-Contract | Erfüllt (init_infrastructure, create_qsettings_backend) |
| Provider-Verdrahtung | Direkt (LocalOllamaProvider, CloudOllamaProvider) – bewusst Legacy |

---

## Architekturentscheidung

- **Kein Umbau:** app.main bleibt als Legacy-Startup für archive/run_legacy_gui.
- **Keine Delegation an run_gui_shell:** Die Legacy-GUI (MainWindow, ChatWidget, CommandCenterView) ist anders als die Shell-GUI (ShellMainWindow). Kein gemeinsamer Pfad.
- **Dokumentation:** Klar als Legacy markiert; keine neuen Features; bei Archivierung von run_legacy_gui kann app.main mit entfernt werden.

---

## CANONICAL_GUI_ENTRY_POINTS

app.main bleibt in CANONICAL_GUI_ENTRY_POINTS, weil es den Bootstrap-Contract erfüllt und als gültiger GUI-Einstieg (Legacy) gilt. Die Startup-Governance prüft, dass alle Entrypoints init_infrastructure aufrufen – app.main tut das.

---

## Empfehlung

Bei vollständiger Archivierung von `archive/run_legacy_gui.py`:
1. app.main entfernen oder nach archive/ verschieben
2. CANONICAL_GUI_ENTRY_POINTS bereinigen
3. KNOWN_GUI_PROVIDER_EXCEPTIONS und KNOWN_IMPORT_EXCEPTIONS anpassen
