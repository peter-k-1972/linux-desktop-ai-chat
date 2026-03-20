# Architecture Map Report

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16

---

## 1. Verwendete Quellen

| Quelle | Verwendung |
|--------|------------|
| tests/architecture/arch_guard_config.py | TARGET_PACKAGES, Services, Provider-Strings, Root-Dateien, Governance-Domains |
| docs/04_architecture/ARCHITECTURE_BASELINE_2026.md | Layers, Domains, Registries, Entrypoints, Governance-Blöcke (strukturell) |
| docs/04_architecture/ROOT_ENTRYPOINT_POLICY.md | Entrypoint-Liste, Legacy-Markierung |

Die Map wird **nicht** aus den Policy-Dokumenten geparst, sondern aus der zentralen Konfiguration (arch_guard_config) und fest codierten Baseline-Strukturen.

---

## 2. Was die Map abdeckt

- **Executive Summary:** Projekt, Zeitstempel, Status
- **Layers:** GUI, Services, Providers, Core
- **Domains:** agents, rag, tools, debug, metrics, qa, prompts, utils
- **Canonical Entrypoints:** python -m app, run_gui_shell, main.py, start.sh; Legacy separat
- **Registries:** Model, Navigation, Screen, Command, Agent; Tools bewusst ohne Registry
- **Services:** Zentrale Service-Module aus arch_guard_config
- **Providers:** Provider-Strings, Implementierungen
- **Governance Blocks:** Policy + Test pro Block
- **Known Legacy / Transitional:** app.main, temporär erlaubte Root-Dateien, verbotene Parallelstrukturen

---

## 3. Was bewusst nicht abgedeckt wird

- Keine vollständige Policy-Texte (nur Referenz)
- Keine FORBIDDEN_IMPORT_RULES im Detail (→ arch_guard_config)
- Keine GUI_SCREEN_WORKSPACE_MAP im Detail (→ arch_guard_config)
- Keine Drift-Ergebnisse (→ ARCHITECTURE_DRIFT_RADAR)
- Keine Abhängigkeitsgraphen (→ separate Tools)

---

## 4. Eignung als schneller Projektüberblick

**Ja.** Die Map ist:

- Kompakt (eine Seite)
- Technisch präzise
- Automatisch erzeugbar
- Für Re-Onboarding und Review geeignet
- Kein Ersatz für Governance – referenziert sie nur

---

## 5. Generierung

```bash
python scripts/dev/architecture_map.py        # Nur Markdown
python scripts/dev/architecture_map.py --json # Markdown + JSON
```

Ausgabe: `docs/04_architecture/ARCHITECTURE_MAP.md` (immer), `ARCHITECTURE_MAP.json` (optional).
