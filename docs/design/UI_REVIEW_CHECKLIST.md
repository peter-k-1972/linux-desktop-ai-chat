# UI Review Checklist

Für **PRs** mit GUI-Änderungen (`app/gui/`, Themes, Icons). Abhaken oder **N/A** mit einer Zeile Begründung.

**Vollregeln:** [UI_GOVERNANCE_RULES.md](./UI_GOVERNANCE_RULES.md)

---

## Layout & Spacing

- [ ] Abstände am **4px-Raster** oder aus `design_metrics` / `layout_constants`?
- [ ] Panel-/Card-/Dialog-Padding einer **definierten Stufe** (20 / 16 / 12 / 24)?
- [ ] Panel-/Sektions-Header: **Header-Profil** (standard / compact / ultra) statt freier Margins?
- [ ] `QFormLayout` in Desktop-Dialogen: **`apply_form_layout_policy`**?
- [ ] Keine **neuen** willkürlichen Magic Numbers für gleiche Rolle wie bestehende Tokens?

## Color & Semantic

- [ ] **Accent** nur laut [ACCENT_USAGE_RULES.md](./ACCENT_USAGE_RULES.md) (Allowlist)?
- [ ] **Semantic** (Success/Warning/Error/Info) nur für **Zustand/Feedback**, nicht für normale Nav?
- [ ] Keine neuen **Hex/RGB-Literale** in UI-Code (Policy: `theme_guard` / Tokens / QSS-Platzhalter)?

## Icons

- [ ] Icons über **IconManager + IconRegistry** (keine Direktpfade)?
- [ ] Neues Asset: **SVG** mit `currentColor`, Stil [ICON_STYLE_GUIDE.md](./ICON_STYLE_GUIDE.md)?
- [ ] Bedeutung mit [ICON_MAPPING.md](./ICON_MAPPING.md) abgestimmt (keine Doppelbelegung)?

## QSS vs. Python

- [ ] **Keine Doppelquelle** für Standard-Control-Höhen (siehe [QSS_PYTHON_OWNERSHIP_RULES.md](./QSS_PYTHON_OWNERSHIP_RULES.md))?
- [ ] Layout (Margins, Spacing, max-width-Strategien) **Python**; generisches Chrome **QSS/Theme**?
- [ ] Bei Risko: `python3 tools/layout_double_source_guard.py` ausgeführt und relevante Hinweise bewertet?

## Thema & Sichtbarkeit

- [ ] Bei Farb-/Icon-Änderungen: kurz **Light + Dark** angesehen (oder N/A: rein strukturell)?

## Abschluss

- [ ] Abweichungen von der Governance im **PR-Text** genannt (Ausnahme + Verweis)?

---

**Optional CI / lokal**

- `python3 tools/theme_guard.py`
- `python3 tools/run_icon_guards.py` (wenn Icons geändert)
- `python3 tools/layout_double_source_guard.py` (nicht `--strict`, außer Team vereinbart Allowlist)
