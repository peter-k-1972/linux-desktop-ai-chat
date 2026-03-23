# Obsidian Core — Signature GUI Modernization Plan

**Zweck:** Stufenplan von **struktureller Wahrheit** bis **Signature Experience** — konkret, mit Aufwand/Nutzen und Risiken.  
**Bezug:** [GUI_REVIEW_ROADMAP.md](../review/GUI_REVIEW_ROADMAP.md), [COMMAND_CENTER_VISION.md](./COMMAND_CENTER_VISION.md), [SIGNATURE_GUI_PRINCIPLES.md](./SIGNATURE_GUI_PRINCIPLES.md)

---

## Stufe 1 — Structural truth (Strukturelle Wahrheit)

| Aspekt | Inhalt |
|--------|--------|
| **Ziel** | Eine Kommandozentrale, eine Erzählung; keine parallele Legacy-Tiefe für Endnutzer; keine täuschenden Platzhalter. |
| **Bereiche** | `DashboardScreen` / zukünftiger `CommandCenterWorkspace`, `CommandCenterView`-Refactor, Help, `navigation_registry` + Copy für QA-Rollen. |
| **Konkrete Maßnahmen** | (1) Drilldown-Stack in Shell einbinden; (2) Legacy-Pfad dokumentiert deprecaten; (3) Platzhalter-Panels → Daten oder ehrliche Empty States; (4) Help-Artikel „QA: wo was liegt“. |
| **Aufwand / Nutzen** | **Hoch / Sehr hoch** — größter Produktgewinn. |
| **Risiken** | Theme-Regression; doppelte Navigation während Migration; Testpflege (`tests/ui/test_command_center_dashboard.py` + Shell). |

---

## Stufe 2 — Surface hierarchy (Flächenhierarchie)

| Aspekt | Inhalt |
|--------|--------|
| **Ziel** | Layer 0–2 sind überall erkennbar: Canvas ruhig, Workspace klar, Karten konsistent — Token statt lokaler Hex-Inseln. |
| **Bereiche** | Control-Center-Panels, Dashboard-Karten, Operations-Workbench-Frames, Settings-Content. |
| **Konkrete Maßnahmen** | Pilot: ein CC-Panel vollständig auf semantische Tokens; dann Rollout-Checkliste; Hero-Zone in Kommandozentrale nach [COMMAND_CENTER_VISION.md](./COMMAND_CENTER_VISION.md). |
| **Aufwand / Nutzen** | **Mittel / Hoch** — sofort sichtbare „Premium“-Ruhe. |
| **Risiken** | Light/Dark-Kontrast-Regressionen; QSS-Python-Doppelquellen (siehe bestehende Ownership-Regeln). |

---

## Stufe 3 — Premium interaction (Interaktionspolitur)

| Aspekt | Inhalt |
|--------|--------|
| **Ziel** | Ruhige, konsistente Hover/Focus/Selection; Inspector-Wechsel ohne Ruckeln; modale Öffnung standardisiert. |
| **Bereiche** | Sidebar, InspectorHost, Command Palette, Dialoge, Listen in Chat und CC. |
| **Konkrete Maßnahmen** | Umsetzung [PREMIUM_INTERACTION_MODEL.md](./PREMIUM_INTERACTION_MODEL.md); Fokus-Ringe prüfen; optional kurze Opacity-Übergänge hinter Feature-Flag. |
| **Aufwand / Nutzen** | **Mittel / Mittel** — Wahrnehmung „fertig“, ohne visuelle Neuerfindung. |
| **Risiken** | Performance auf schwachen GPUs bei zu viel Animation; Accessibility bei zu dezenter Fokus-Kennzeichnung. |

---

## Stufe 4 — Signature experience (Markante, aber ruhige Identität)

| Aspekt | Inhalt |
|--------|--------|
| **Ziel** | Obsidian Core ist **erkennbar**: Kommandozentrale mit Hero + Introspection als Wertversprechen, ohne lautes Branding. |
| **Bereiche** | Onboarding, Help-Tours, Introspection-Workspace-Copy, TopBar-Gruppierung, erste-Lauf-Hinweis Command Palette. |
| **Konkrete Maßnahmen** | Ein durchgestalteter „First run“-Flow (optional); Microcopy-Review DE; eine **Signatur-Zeile** in der Hero-Zone (Produktname/Tagline nur wenn Platz sparend). |
| **Aufwand / Nutzen** | **Niedrig–Mittel / Hoch** für wahrgenommene Reife — wenn Stufe 1–2 stehen. |
| **Risiken** | Zu viel Text; Marketing-Sprache statt Präzision — gegen [SIGNATURE_GUI_PRINCIPLES.md](./SIGNATURE_GUI_PRINCIPLES.md) §1–2 verstoßen. |

---

## Reihenfolge-Empfehlung

1 → 2 parallel beginnbar nach Pilot → 3 → 4.

---

*Ende SIGNATURE_GUI_MODERNIZATION_PLAN.md*
