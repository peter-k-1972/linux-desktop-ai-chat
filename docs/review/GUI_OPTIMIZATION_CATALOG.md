# GUI Optimierungskatalog (Phase 6)

Spalten: **Bereich** · **Problem** · **Ziel** · **konkrete Maßnahme** · **Nutzen** · **Risiko** · **Priorität** · **Abhängigkeiten**

---

## A. Kurzfristige Korrekturen

| Bereich | Problem | Ziel | Maßnahme | Nutzen | Risiko | P | Abhängigkeiten |
|---------|---------|------|----------|--------|--------|---|----------------|
| Doku | Drift zu Code | Vertrauen | `PLACEHOLDER_INVENTORY.md` + `STATUS_AUDIT.md` CC/Dashboard-Abschnitte mit Ist-Code abgleichen | Weniger falsche Prioritäten | Gering | **Hoch** | — |
| IA-Kommunikation | Doppel-QA unklar | Orientierung | Help-Artikel „Wo finde ich QA?“ mit Rollenmodell | Weniger Suchen | Gering | **Hoch** | `help/` |
| TopBar | EN-Tooltip in DE-UI | Konsistenz | Strings vereinheitlichen | Ruhe | Gering | **Mittel** | — |
| Toter Code | `agents_panels.py` Demo | Klarheit | Umbenennen/archivieren oder aus Export entfernen | Weniger Wartungsfehler | Mittel (Imports) | **Mittel** | Code-Suche |

---

## B. Mittlere UX-/Semantik-Refactors

| Bereich | Problem | Ziel | Maßnahme | Nutzen | Risiko | P | Abhängigkeiten |
|---------|---------|------|----------|--------|--------|---|----------------|
| Kommandozentrale | Zwei Welten | Ein Wahrheits-Pfad | `CommandCenterView`-Inhalt in Shell-Dashboard einbinden oder gleichwertige Drilldown-Route | Produktkohärenz | Hoch (Layout, Theme) | **Hoch** | `COMMAND_CENTER_DASHBOARD_UNIFICATION.md` |
| Navigation Registry | Runtime-Sonderworkspaces fehlen | Eine Wahrheit | Registry erweitern + Filter „Dev“ **oder** Scope-Dokumentation + Workspace Graph | Palette/Sidebar/Help synchron | Mittel | **Mittel** | — |
| Inspector | Leere Zustände | Learnability | Standard-Empty-State mit Kontext | Weniger Frustration | Gering | **Mittel** | `empty_state.py` |
| Platzhalter-Panels | Irreführend | Ehrlichkeit | Entweder Daten oder „Nicht verfügbar“ ohne Pseudo-Metrik | Vertrauen | Mittel (Backend) | **Mittel** | Services |

---

## C. Große Modernisierungsmaßnahmen

| Bereich | Problem | Ziel | Maßnahme | Nutzen | Risiko | P | Abhängigkeiten |
|---------|---------|------|----------|--------|--------|---|----------------|
| CC-Panels | Lokale Hex-Styles | Token-einheitlich | Styles auf Theme/semantic tokens migrieren | Visuelle Tiefe, Wartung | Regressionen in Light/Dark | **Hoch** | `design_tokens`, QA-Themes |
| Dashboard | Vier gleiche Karten | Hierarchie | Hero-Zeile + sekundäre Karten | Klarere Story | UX-Review nötig | **Mittel** | QA-Adapter Daten |

---

## D. Optionale „Wow“-Maßnahmen (ohne Kitsch)

| Bereich | Maßnahme | Nutzen | Risiko | P |
|---------|----------|--------|--------|---|
| Workspace-Wechsel | Subtiles Cross-Fade (nur leichte Views) | Polish | Performance | Niedrig |
| Status-Refresh | Timestamp + Mini-Spinner | Lebendigkeit | UI-Noise | Niedrig |
| Signatur | Introspection als „Transparenz“-Onboarding (einmalig) | Differenzierung | Zu nerdig | Niedrig |

---

*Ende GUI_OPTIMIZATION_CATALOG.md*
