# Paket 0 — Analyse: Vertrauensbasis QA & Metriken (IMP-002)

**Bezug:** `PROJECT_IMPROVEMENT_PACKAGES_2026-03-22.md` (Paket 0), `PROJECT_IMPROVEMENT_ROADMAP_2026-03-22.md` (Wave 1), Backlog IMP-002.

## Ziel

QA- und Release-Artefakte sollen den **nachweisbaren** pytest-Stand widerspiegeln: Sammlungszahl, Repro-Kommando, Git-Revision; veraltetes `TEST_AUDIT_REPORT.md` klar als historisch kennzeichnen.

## Enthaltene Maßnahmen

- `FINAL_TEST_STATUS.md` aktualisieren (Sammlung, Teilmengen, Commit, Tool-Versionen).
- `tests/TEST_AUDIT_REPORT.md` mit sichtbarem Deprecation-Banner und Verweis auf aktuelle Quellen.
- Optional: `docs/RELEASE_ACCEPTANCE_REPORT.md` um einen Verweis auf maßgebliche Testzahlen ergänzen.

## IST — relevante Dateien

| Datei | Rolle |
|-------|--------|
| `FINAL_TEST_STATUS.md` | Zentrale Test-Metrik für Release/Leser |
| `tests/TEST_AUDIT_REPORT.md` | Veraltete Gap-Analyse (2025-03-15) |
| `docs/RELEASE_ACCEPTANCE_REPORT.md` | Verweist auf FINAL_TEST_STATUS |
| `tests/README.md` | Kanonische Suite-Beschreibung |

## Messung (lokale Arbeitskopie)

- **Git:** `afcac5914534c3f36818ab4ef1e72440b47b3d6d` (Kurz `afcac59`), Commit-Datum 2026-03-20.
- **Python:** 3.12.3 (`.venv-ci`)
- **pytest:** 9.0.2
- **`pytest tests --collect-only`:** **1838** Tests in ~1,03 s
- **Teilmengen (collect-only):** `tests/architecture/` 115, `tests/unit/` 612, `tests/smoke/` 61

## Risiken

- **Vollständiger Lauf:** Spot-Check `pytest tests --maxfail=5` brach mit **Architektur-Guard-Failures** ab (Import-Richtungen, Provider-Imports, `run_workbench_demo.py` im Root). Das ist **außerhalb IMP-002** nicht zu beheben ohne neues Paket; die Doku darf **nicht** pauschal „Exit 0“ für den aktuellen Stand behaupten, wenn dem widersprochen wird.
- Änderung an `FINAL_TEST_STATUS` kann Release-Leser irritieren, wenn sie nur „1681“ kennen — deshalb **Erklärung** (Sammlung wächst mit Suite; alter Freeze-Referenzwert genannt).

## Entscheidung

- Sammlungs- und Teilmengen-Zahlen **ersetzen** die veraltete 1681/494-Zeile.
- Abschnitt **Vollständiger Lauf** trennen: (a) historischer Freeze-Hinweis, (b) aktueller Verifikationshinweis inkl. Spot-Check-Befund vom 2026-03-22.

---

*Analyse vor Implementierung — Paket 0.*
