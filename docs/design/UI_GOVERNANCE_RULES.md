# UI Governance — verbindliche Regeln

**Geltung:** Neue und geänderte Screens, Panels, Dialoge, Widgets in `app/gui/`.  
**Nicht:** Vollständiges Design-Handbuch — Details stehen in den verlinkten Quellen.

---

## 1. Ziel und Geltungsbereich

- **Ziel:** Gleiche visuelle Sprache, keine stillen Doppelquellen, reviewbare Entscheidungen.  
- **Pflicht:** Diese Regeln einhalten oder **Ausnahme dokumentieren** (PR-Beschreibung oder kurzer Kommentar + Verweis auf erlaubten Ausnahme-Typ in den Quellen).  
- **Quellen (Source of Truth):** siehe §6.

---

## 2. Regelblock A — Layout & Spacing

**Zweck:** Raster, Abstände, Header-Dichte — konsistent mit Workbench und Audits.

| Verpflichtend | Details |
|---------------|---------|
| **4px-Raster** | Abstände bevorzugt aus `design_metrics` / `layout_constants` (`SPACE_*`, `PANEL_PADDING`, …). |
| **Definierte Padding-Stufen** | Panel 20, Card 16, kompakt 12, Dialog 24 — siehe [LAYOUT_SYSTEM_RULES.md](./LAYOUT_SYSTEM_RULES.md). |
| **Header-Chrome** | `apply_header_profile_margins` + Profile **standard / compact / ultra** — kein freies 9×11×13-Mixen. |
| **Form-Zeilen** | `apply_form_layout_policy` wo `QFormLayout` in Desktop-Dialogen. |

**Verboten**

- Neue **Magic Numbers** für gleiche Rolle (z. B. drittes „fast 16px“-Padding).  
- **14px / 10px** als Panel-Rand ohne dokumentierte Ausnahme ([LAYOUT_SYSTEM_RULES.md](./LAYOUT_SYSTEM_RULES.md) §1).  

**Ausnahmen**

- Inhaltsabhängige Min/Max (Editor-Höhe, Splitter) — **Python-Owner**, dokumentiert in [QSS_PYTHON_CANONICAL_CASES.md](./QSS_PYTHON_CANONICAL_CASES.md).  

**Gut / Schlecht**

- Gut: `apply_panel_layout(lay)` bzw. `dm.PANEL_PADDING_PX`.  
- Schlecht: `setContentsMargins(17, 13, 19, 11)` ohne Begründung.

**Review-Check:** Raster? Bekannte Stufe? Header-Profil benannt?

---

## 3. Regelblock B — Color & Semantic Usage

**Zweck:** Ruhige Oberfläche, ein erkennbarer Interaktionskanal, Zustände semantisch.

| Verpflichtend | Details |
|---------------|---------|
| **Accent** | Nur laut **Allowlist** — [ACCENT_USAGE_RULES.md](./ACCENT_USAGE_RULES.md) (Nav-Selektion, Primary-CTA, Fokus, Link-Token, …). |
| **Semantic (Success/Warning/Error/Info)** | Nur für **Zustand / Feedback**, nicht für normale Navigation — [SEMANTIC_COLOR_USAGE.md](./SEMANTIC_COLOR_USAGE.md). |
| **Technisch** | Keine Hex-/RGB-Literale in Produktiv-GUI-Code außerhalb erlaubter Pfade (`theme_guard`-Policy); Theme-Tokens / `ThemeTokenId` / QSS-`{{…}}`. |

**Verboten**

- **Vollflächen** Panels/Cards in Brand-Accent.  
- **Zweite Nav-Selektionsfarbe** neben dem vereinheitlichten Nav-Selected-Paar.  
- Semantic-Farben für „hübsch“ ohne semantische Bedeutung.  

**Ausnahmen**

- Runtime/Debug-Domains laut Spec; dokumentierte Legacy-Pfade bis Cutover.  

**Gut / Schlecht**

- Gut: Primary-Button über `BUTTON_PRIMARY_*`; Fehlerzeile über `STATE_ERROR`.  
- Schlecht: `#2563eb` in Python-Widget für „normalen“ Hintergrund.

**Review-Check:** Accent nur Allowlist? Semantic nur bei echtem Zustand?

---

## 4. Regelblock C — Icons & Symbolik

**Zweck:** Ein Icon = eine Bedeutung, theme-fähig, auffindbar.

| Verpflichtend | Details |
|---------------|---------|
| **Ladung** | `IconManager` + **IconRegistry** (oder dokumentierter Nachfolger) — kein `QIcon("pfad/zu.svg")` für Produkt-UI. |
| **Assets** | SVG mit **`currentColor`**, Stil laut [ICON_STYLE_GUIDE.md](./ICON_STYLE_GUIDE.md); Zuordnung [ICON_MAPPING.md](./ICON_MAPPING.md). |
| **Neues Icon** | Taxonomie-Ordner, Guard `tools/icon_svg_guard.py` / `run_icon_guards` wo vorgesehen. |

**Verboten**

- **Direktpfade** zu Icon-Dateien in Feature-Code (Ausnahme: Dev-Tools mit Freigabe).  
- **Mehrdeutige Doppelbelegung** derselben Glyphe für widersprüchliche Aktionen (Mapping prüfen).  

**Ausnahmen**

- Explizit als Legacy markierte Stellen bis Cutover ([ICON_CUTOVER_PLAN.md](./ICON_CUTOVER_PLAN.md) o. ä.).  

**Gut / Schlecht**

- Gut: `IconManager.get(IconRegistry.SAVE, size=20, state="primary")`.  
- Schlecht: `setIcon(QIcon("assets/icons/random.svg"))`.

**Review-Check:** Registry-Eintrag? SVG-Regel? Größe aus erlaubter Skala?

---

## 5. Regelblock D — QSS vs. Python (Ownership)

**Zweck:** Eine kanonische Schicht pro Eigenschaft — keine stillen Konflikte.

| Verpflichtend | Details |
|---------------|---------|
| **Generische Control-Höhe** (Standard-Button, Combo, LineEdit im Theme-Pfad) | **QSS-Owner** — kein paralleles `setMinimumHeight(32)` nur zur „Verdopplung“. |
| **Layout-Struktur** | Margins, Spacing, Stretch, Splitter, responsive max-width — **Python-Owner** + `design_metrics` wo definiert. |
| **Domänenspezial** (z. B. Chat Send 40px) | Wie [QSS_PYTHON_CANONICAL_CASES.md](./QSS_PYTHON_CANONICAL_CASES.md) / [CHAT_LAYOUT_POLICY.md](./CHAT_LAYOUT_POLICY.md). |

**Verboten**

- Standardhöhe **gleichzeitig** in globalem QSS und Python fixieren (redundant oder widersprüchlich).  
- **Ad-hoc** `setStyleSheet("… min-height: Npx …")` für Standard-Controls, wenn globales QSS dieselbe Rolle hat — siehe [QSS_PYTHON_OWNERSHIP_RULES.md](./QSS_PYTHON_OWNERSHIP_RULES.md) §3.  

**Ausnahmen**

- Zwei App-Pfade (Legacy `styles.py` vs. Theme-Loader) — bis Vereinigung dokumentiert; Bubble-Styling o. ä. als explizite Ausnahme.  

**Gut / Schlecht**

- Gut: Combo ohne Python-Mindesthöhe, Theme `base.qss` regelt.  
- Schlecht: `QComboBox` + `setMinimumHeight(32)` neben identischer QSS-Regel.

**Review-Check:** Owner laut Canonical Cases? Guard-Hinweis `tools/layout_double_source_guard.py` bei Risko?

---

## 6. Regelblock E — Review & QA (Pflichtprozess)

**Zweck:** Jede relevante GUI-Änderung ist gegen diese Regeln prüfbar.

| Verpflichtend | Details |
|---------------|---------|
| **Checkliste** | [UI_REVIEW_CHECKLIST.md](./UI_REVIEW_CHECKLIST.md) abarbeiten (oder gleichwertig in PR-Template verlinken). |
| **Abweichung** | Kurz **warum** + Verweis auf erlaubte Ausnahme oder Issue für Nacharbeit. |
| **Themen** | Bei sichtbaren UI-Änderungen: **light + dark** kurz prüfen, wenn Farben/Icons betroffen. |

**Verboten**

- „Nur optisch“ ohne Checkliste bei neuen Panels/Dialogen.  

**Review-Check:** Checkliste angehakt oder begründete Abweichungen dokumentiert?

---

## 7. Source of Truth (Vertiefung)

| Thema | Dokument |
|-------|----------|
| Layout-Raster, Header, Dialoge | [LAYOUT_SYSTEM_RULES.md](./LAYOUT_SYSTEM_RULES.md), [layout_constants.py](../../app/gui/shared/layout_constants.py), [design_metrics.py](../../app/gui/theme/design_metrics.py) |
| Migration / Problemklassen | [LAYOUT_SPACING_MIGRATION_PLAN.md](./LAYOUT_SPACING_MIGRATION_PLAN.md), [LAYOUT_PROBLEM_CLASSES.md](./LAYOUT_PROBLEM_CLASSES.md) |
| Spacing-Audit (Überblick) | [LAYOUT_SPACING_AUDIT_REPORT.md](../../LAYOUT_SPACING_AUDIT_REPORT.md) |
| Accent / Semantic | [ACCENT_USAGE_RULES.md](./ACCENT_USAGE_RULES.md), [SEMANTIC_COLOR_USAGE.md](./SEMANTIC_COLOR_USAGE.md) |
| Icons | [ICON_STYLE_GUIDE.md](./ICON_STYLE_GUIDE.md), [ICON_MAPPING.md](./ICON_MAPPING.md), [ICON_COLOR_RULES.md](./ICON_COLOR_RULES.md) |
| QSS ↔ Python | [QSS_PYTHON_OWNERSHIP_RULES.md](./QSS_PYTHON_OWNERSHIP_RULES.md), [QSS_PYTHON_CANONICAL_CASES.md](./QSS_PYTHON_CANONICAL_CASES.md), [QSS_PYTHON_DOUBLE_SOURCE_AUDIT.md](./QSS_PYTHON_DOUBLE_SOURCE_AUDIT.md) |
| Farb-Guard (CI-Hinweis) | `tools/theme_guard.py` |

---

## 8. Automatisierung (später / optional)

Siehe [UI_GOVERNANCE_REPORT.md](./UI_GOVERNANCE_REPORT.md) §5 und [UI_REVIEW_CHECKLIST.md](./UI_REVIEW_CHECKLIST.md) — u. a. `theme_guard`, `icon_svg_guard`, `layout_double_source_guard`, Magic-Number-Linter-Ideen.

---

*Kurzfassung:* [UI_GOVERNANCE_SHORT.md](./UI_GOVERNANCE_SHORT.md)
