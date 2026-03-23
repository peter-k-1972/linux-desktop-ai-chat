# GUI Review – Umsetzungsroadmap (Phase 7)

---

## Stage 1 — Funktionale Vollständigkeit / CLI-Transparenz

| Aspekt | Inhalt |
|--------|--------|
| **Ziel** | Standard-Shell deckt die **gleiche** operative QA-/Kommandozentrale-Tiefe wie der vorhandene `CommandCenterView` **oder** dokumentiert und verlinkt sie ohne Sackgasse. |
| **Bereiche** | `DashboardScreen`, `command_center_view.py`, `ShellMainWindow`, Hilfe-Artikel |
| **Reihenfolge** | (1) IA-Entscheid: einbinden vs. Deep-Link; (2) technische Einbettung; (3) Legacy nur Wartung; (4) Help aktualisieren |
| **Risiken** | Theme-/Layout-Regression; doppelte Navigation während Übergang |
| **QA-Kriterien** | Manuelle Navigation: vom Dashboard zu allen früheren Drilldowns; keine toten Buttons; `tests/ui/test_command_center_dashboard.py` weiter grün; ggf. neue Shell-UI-Tests |

---

## Stage 2 — Semantik / IA / Usability

| Aspekt | Inhalt |
|--------|--------|
| **Ziel** | Eine nachvollziehbare Rolle für **QUALITY vs. OBSERVABILITY vs. Dashboard**; weniger DE/EN-Mix; klare Empty States. |
| **Bereiche** | `navigation_registry.py`, Help, Inspector-Host, Platzhalter-Panels (Knowledge, Prompt, Agent Tasks) |
| **Reihenfolge** | IA-Dokument → Nav-Labels/Breadcrumbs → Platzhalter entfernen oder ehrlich machen → Inspector-Defaults |
| **Risiken** | Nutzer gewöhnt an bestehende Menüfolge |
| **QA-Kriterien** | Usability-Walkthrough-Skript; keine Strings „(Platzhalter)“ in produktiven Pfaden ohne „Beta“-Kontext |

---

## Stage 3 — Modernisierung / visuelle Tiefe / Motion

| Aspekt | Inhalt |
|--------|--------|
| **Ziel** | Oberflächen konsistent aus Tokens; Dashboard-Hierarchie; dezente Übergänge wo sinnvoll. |
| **Bereiche** | CC-Panels, Dashboard, Docks, optionale Animationen |
| **Reihenfolge** | Token-Migration CC → Dashboard → Motion-Experimente (feature-flagged) |
| **Risiken** | Kontrast-/Theme-Regressionen |
| **QA-Kriterien** | `docs/qa/THEME_QA_REPORT.md`-Checkliste; visuelle Regression (manuell oder Screenshots) |

---

## Stage 4 — Finale Politur / Signature Experience

| Aspekt | Inhalt |
|--------|--------|
| **Ziel** | Wiedererkennbare, ruhige „Desktop-Produkt“-Sprache; Introspection/Transparenz als optionales Markenargument. |
| **Bereiche** | Onboarding, Help-Tours, TopBar-Gruppierung, ggf. erste-run Dialog |
| **Reihenfolge** | Copy-Review → Tours → optionale Signatur-Microcopy |
| **Risiken** | Überführung mit zu viel Text |
| **QA-Kriterien** | Neue Nutzer (intern) schaffen Chat + Projektwechsel ohne CLI |

---

*Ende GUI_REVIEW_ROADMAP.md*
