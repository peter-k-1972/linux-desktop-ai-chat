# Design-Token-Architektur (Foundation → Semantic → Component)

**Ziel:** Ein schlankes, **desktop-taugliches** System für Obsidian Core / Linux Desktop Chat — optimiert für PySide6, QSS-Substitution und gezielte Python-Layouts — **ohne** Web/Mobile-Token-Überfrachtung.

---

## 1. Drei Ebenen

### 1.1 Foundation Tokens

**Was:** Rohwerte ohne UI-Bedeutung — die kleinste gemeinsame Einheit.

- **Farbe:** z. B. neutrale Skala, Brand-Rohfarbe (falls nötig), Roh-Semantik nur wenn unvermeidbar.
- **Maß:** Basiseinheit in px (bei euch: **4px-Raster**), absolute Schrittfolgen für Abstand, Radius, Strichstärke.
- **Typografie:** Font-Familien-Namen, absolute px-Größen für den Desktop, numerische Gewichte.

**Regel:** Foundation wird **selten** direkt in Komponenten importiert; sie speisen Semantic/Component.

### 1.2 Semantic Tokens

**Was:** **Bedeutung** in der UI, nicht die Komponente.

- **Farbe:** `color.fg.primary`, `color.border.focus`, `color.state.success` — vollständig in [THEME_TOKEN_SPEC.md](./THEME_TOKEN_SPEC.md) / [SEMANTIC_COLOR_USAGE.md](./SEMANTIC_COLOR_USAGE.md).
- **Nicht-Farbe:** z. B. `text.role.body`, `space.stack.gap.md`, `radius.input`, `border.width.default`, `shadow.subtle` (falls je genutzt).

**Regel:** Semantic ist die **einzige** sinnvolle Ebene für Theming („Light/Dark/High-Contrast“ wechselt Semantik, nicht Component-Regeln).

### 1.3 Component Tokens

**Was:** **Zusammensetzung** für wiederkehrende Bausteine — immer als **Referenz** auf Semantic (oder in Ausnahmefällen Foundation).

- Beispiele: `comp.button.primary.padding_x`, `comp.sidebar.nav_item.min_height`, `comp.chat.bubble.padding`.
- Component-Token **dürfen** Komponentennamen tragen; Semantic **nicht**.

**Regel:** Wenn nur **eine** Komponente einen Wert braucht → Component-Token optional; wenn **zwei+** dieselbe Regel teilen → Semantic bevorzugen.

---

## 2. Was landet wo?

### 2.1 QSS (`app/gui/themes/base/*.qss`)

- **Ja:** Farb-Semantik (als substituierte `{{color_*}}` / später `{{color_*}}` aus Resolver), **alle** visuellen Regeln, die Qt per Stylesheet kann: `padding`, `margin`, `border-*`, `font-size`, `font-weight`, `min-height`, `border-radius`, `icon-size` (wo unterstützt).
- **Bevorzugt:** Platzhalter aus dem **flattened** Token-Dict (Punkt → Unterstrich), konsistent mit [THEME_TOKEN_SPEC.md](./THEME_TOKEN_SPEC.md).
- **Nein:** Python-Logik, berechnete Werte zur Laufzeit (außer Theme-Build ersetzt sie vor `setStyleSheet`).

### 2.2 Python

- **Ja:** `QLayout` **Margins/Spacing** (Integer px), `setFixedHeight`, `setIconSize(QSize(w,h))`, `QFont` wo nötig, dynamische Größen.
- **Ja:** Auflösung über **DesignTokenRegistry** / `ThemeManager.get_tokens()` für Farben und String-Maße, die auch in QSS vorkommen — **eine Quelle**.
- **Ja:** Komponenten-Geometrie, die QSS schlecht abdeckt (Splitter, custom Painting).

### 2.3 Grenzfälle

| Thema | Empfehlung |
|--------|------------|
| Markdown-HTML | Inline-Styles aus Renderer — sollen **semantische** Typo-/Spacing-Werte aus Python-Registry beziehen, keine losen px außerhalb der Skala. |
| `QGraphicsView` / Graph | Farben aus Tokens; Geometrie eigene Mini-Spez im Component-Mapping. |

---

## 3. Verboten / Anti-Patterns

1. **Rohe Hex in Feature-Code** (`#64748b` in Domains) — nur in Theme-Definitionen oder Tests.
2. **Doppelte Wahrheit:** dieselbe Zahl als `20` in Python und `"20px"` in QSS ohne gemeinsamen Token-Namen.
3. **Komponenten in Semantic-Namen** — kein `color.button.primary` als *Foundation*; als Semantic ist `color.button.primary.bg` dagegen **erlaubt** (bereits im Farbmodell).
4. **Web-typische Token-Tiefe** (z. B. 6 Ebenen „alias of alias“) — maximal **Foundation → Semantic → Component**.
5. **Schatten als Pflicht** — Qt/Desktop: Schatten oft unnötig; **Border + Flächenstufe** bevorzugen (siehe [DESIGN_TOKEN_SPEC.md](./DESIGN_TOKEN_SPEC.md) Abschnitt Elevation).
6. **Magic Numbers in QSS**, die bereits als `ThemeTokens`-Feld existieren — durch Platzhalter ersetzen.

---

## 4. Bezug zu bestehenden Artefakten

| Artefakt | Rolle |
|----------|--------|
| [THEME_TOKEN_SPEC.md](./THEME_TOKEN_SPEC.md) | Kanonische **Farb-Semantik** + Legacy-Mapping |
| [COLOR_USAGE_MAP.md](./COLOR_USAGE_MAP.md) | Komponenten → Farbrollen |
| [ACCENT_USAGE_RULES.md](./ACCENT_USAGE_RULES.md) | Wann Accent erlaubt ist |
| [ICON_TAXONOMY.md](./ICON_TAXONOMY.md), [ICON_MAPPING.md](./ICON_MAPPING.md), [ICON_STYLE_GUIDE.md](./ICON_STYLE_GUIDE.md) | Icon-System |
| `app/gui/themes/tokens.py` | Heutige **flache** QSS-Substitution (wird schrittweise auf erweiterte IDs ausgerichtet) |
| `app/gui/shared/layout_constants.py` | Python-Layout — **soll** mit Semantic-Spacing koppeln |
| `app/gui/theme/` (Runtime-Layer) | Zentrale Auflösung für Metriken + Registry (Phase 7) |

---

## 5. Namenskonvention (nicht-Farbe)

- **Canonical (Dokumentation / API):** `category.subcategory.role.scale` — z. B. `space.md`, `text.size.sm`.
- **Flat key (QSS/Python-Dict):** Punkte → Unterstriche — `space_md`, `text_size_sm` (analog `flat_key` in `canonical_token_ids.py`).

Farben **bleiben** bei `color.*` wie in THEME_TOKEN_SPEC.
