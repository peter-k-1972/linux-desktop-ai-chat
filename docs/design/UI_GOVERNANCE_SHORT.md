# UI Governance — Kurzfassung

1. **Layout:** 4px-Raster; Padding-Stufen 20/16/12/24; Header-Profile standard|compact|ultra; keine neuen Magic Numbers. → [LAYOUT_SYSTEM_RULES.md](./LAYOUT_SYSTEM_RULES.md)

2. **Farbe:** Accent nur Allowlist; Semantic nur für Zustand; keine UI-Hex-Literale. → [ACCENT_USAGE_RULES.md](./ACCENT_USAGE_RULES.md), [SEMANTIC_COLOR_USAGE.md](./SEMANTIC_COLOR_USAGE.md)

3. **Icons:** Nur IconManager + Registry; SVG `currentColor`; Mapping prüfen. → [ICON_STYLE_GUIDE.md](./ICON_STYLE_GUIDE.md), [ICON_MAPPING.md](./ICON_MAPPING.md)

4. **QSS vs. Python:** Standard-Control-Höhen → QSS; Struktur/Margins/max-width → Python; keine Doppelquelle. → [QSS_PYTHON_OWNERSHIP_RULES.md](./QSS_PYTHON_OWNERSHIP_RULES.md)

5. **Review:** [UI_REVIEW_CHECKLIST.md](./UI_REVIEW_CHECKLIST.md) bei GUI-PRs.

**Vollständig:** [UI_GOVERNANCE_RULES.md](./UI_GOVERNANCE_RULES.md)
