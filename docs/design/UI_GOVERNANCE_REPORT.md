# UI Governance — Abschlussbericht

## 1. Definierte Regelblöcke

Es wurden **fünf** verbindliche Blöcke in [UI_GOVERNANCE_RULES.md](./UI_GOVERNANCE_RULES.md) definiert:

1. **Layout & Spacing** — Raster, Padding-Stufen, Header-Profile, Form-Policy.  
2. **Color & Semantic Usage** — Accent-Allowlist, semantische Zustände, keine Literalfarben.  
3. **Icons & Symbolik** — Registry/Manager, SVG-Regeln, Mapping.  
4. **QSS vs. Python Ownership** — eine kanonische Schicht pro Eigenschaft.  
5. **Review & QA** — verpflichtender Checklistenprozess (operativ in [UI_REVIEW_CHECKLIST.md](./UI_REVIEW_CHECKLIST.md)).

Zusätzlich: [UI_GOVERNANCE_SHORT.md](./UI_GOVERNANCE_SHORT.md) als Einzeiler-Übersicht.

## 2. Warum genau diese Blöcke?

Sie decken die im Projekt bereits auditierten **Hauptursachen für Wildwuchs** ab (siehe [LAYOUT_PROBLEM_CLASSES.md](./LAYOUT_PROBLEM_CLASSES.md), insb. P1–P2, P8, P10) und die geregelten Teilbereiche **Farbe**, **Icons** und **Theme/QSS**. Ein sechster Block „Typography“ wurde bewusst weggelassen — Regeln stehen in Tokens/LAYOUT_SYSTEM_RULES und würden die Kurzfassung sprengen.

## 3. Stützung durch bestehende Dokumente

| Governance-Block | Primäre Referenzen |
|------------------|-------------------|
| Layout | [LAYOUT_SYSTEM_RULES.md](./LAYOUT_SYSTEM_RULES.md), [LAYOUT_SPACING_MIGRATION_PLAN.md](./LAYOUT_SPACING_MIGRATION_PLAN.md), [LAYOUT_PROBLEM_CLASSES.md](./LAYOUT_PROBLEM_CLASSES.md), [LAYOUT_SPACING_AUDIT_REPORT.md](../../LAYOUT_SPACING_AUDIT_REPORT.md) |
| Color | [ACCENT_USAGE_RULES.md](./ACCENT_USAGE_RULES.md), [SEMANTIC_COLOR_USAGE.md](./SEMANTIC_COLOR_USAGE.md) |
| Icons | [ICON_STYLE_GUIDE.md](./ICON_STYLE_GUIDE.md), [ICON_MAPPING.md](./ICON_MAPPING.md) |
| QSS/Python | [QSS_PYTHON_OWNERSHIP_RULES.md](./QSS_PYTHON_OWNERSHIP_RULES.md), [QSS_PYTHON_CANONICAL_CASES.md](./QSS_PYTHON_CANONICAL_CASES.md) |

Keine inhaltliche Duplikation: Governance **verdichtet** und **verweist**.

## 4. Sofort gültig für neue Screens

Ab Merge dieses Satzes gelten für **neue** Panels, Dialoge und Workspaces:

- Layout-Stufen und Header-Profile wie in §2 UI_GOVERNANCE_RULES.  
- Accent/Semantic wie in §3.  
- Icons nur über Registry/Manager wie in §4.  
- Ownership wie in §5; Chat-spezifisch weiter [CHAT_LAYOUT_POLICY.md](./CHAT_LAYOUT_POLICY.md).

Bestehende Alt-Code-Pfade bleiben, müssen bei **Änderung** aber gegen die Checkliste geprüft werden.

## 5. Später automatisierbar

| Regel-Cluster | Werkzeug / Idee |
|---------------|-----------------|
| Harte Farben in UI-Python | `tools/theme_guard.py` (bestehend) |
| SVG-Icon-Regeln | `tools/icon_svg_guard.py` / `run_icon_guards` |
| QSS/Python-Doppelquellen (Heuristik) | `tools/layout_double_source_guard.py` |
| Magic Numbers in Layouts | Erweiterung Guard oder Ruff/Custom-Scan auf `setContentsMargins(?,` mit Literalen |
| Unregistrierte Icon-Pfade | Grep / Guard auf `QIcon(` + Pfad-Literale in `app/gui` |

Vollständige Hinweise in [UI_GOVERNANCE_RULES.md](./UI_GOVERNANCE_RULES.md) §8 und Checkliste „Optional CI“.

---

## Zusatzfragen

### A. Welche 5 Regeln sind ab sofort nicht mehr verhandelbar?

1. **Layout:** Abstände aus Raster / definierten Stufen — keine ad-hoc Panel-Padding-Werte ohne Ausnahme-Doku.  
2. **Accent:** Nur gemäß Accent-Allowlist — keine neuen Vollflächen-Accent-Panels.  
3. **Semantic:** Nur für echten Zustand — nicht für Dekoration oder normale Navigation.  
4. **Icons:** Produkt-UI lädt Icons nur über **IconManager + IconRegistry** (keine Direktpfade).  
5. **Ownership:** Keine doppelte Steuerung derselben Standard-Control-Höhe durch QSS **und** Python.

### B. Welche typischen Altfehler sollen verhindert werden?

- P1/P8: **Padding-Wildwuchs** und Nicht-Raster-Zahlen.  
- P2: **48px-Buttons** neben QSS-32 ohne Domänenregel.  
- P10: **QSS vs. Python konkurrierend** (z. B. Combo-Höhe doppelt).  
- Parallele **Accent-Kanäle** und **Semantic-Missbrauch** für „hübsch“.  
- **Icon-Pfad-Chaos** und uneindeutige Symbolik.

### C. Reicht das Set für neue Screens und Refactors praktisch aus?

**Ja**, als **Mindeststandard** und Review-Rahmen; **Vertiefung** bleibt in den verlinkten Specs (Chat-Policy, Dialog-Pilot, Icon-Cutover). Was die Governance **nicht** ersetzt: pixelgenaue Mockups, Animations-Spezifikation, vollständige Komponentenbibliothek — dafür sind die bestehenden Design-Dokumente und Iteration nötig.

---

*Operativ:* [UI_REVIEW_CHECKLIST.md](./UI_REVIEW_CHECKLIST.md)  
*Volltext:* [UI_GOVERNANCE_RULES.md](./UI_GOVERNANCE_RULES.md)
