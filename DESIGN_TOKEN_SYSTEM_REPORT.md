# Design-Token-System — Abschlussbericht

**Projekt:** Linux Desktop Chat / Obsidian Core  
**Umfang:** Kanonisches Token-Modell für Farbe, Icon, Typografie, Spacing, Radius, Border, Größe, Oberfläche/Elevation und Zustände — nutzbar mit PySide6 und QSS.

---

## 1. Wichtigste Audit-Ergebnisse

- **Zwei parallele Metrik-Systeme:** `ThemeTokens` (String-`px` für QSS) und `layout_constants` (Integer für Layouts) mit überlappenden Bedeutungen (`panel_padding` / `PANEL_PADDING`).
- **Magic Numbers in QSS:** u. a. `6px 12px`, `4px 8px`, feste `12px`/`11px` bei Runtime-Nav, `icon-size: 18px`, Scrollbar-Geometrie ohne Platzhalter.
- **Inkonsistente Zeilenhöhen:** `1.35` / `1.4` / `1.5` nur lokal; kein gemeinsames Token.
- **Icon-Größen:** 18 / 20 / 24 / 32 je Kontext; `IconManager`-Default 24 vs. Workbench-Toolbar 18px.
- **Listen-/Tree-Zeilenhöhen:** 26px (Explorer), 28px (Node-Library), 32px (Palette/Combo).
- **Legacy-Inline-Farben** in mehreren Operations-/Knowledge-Panels (Hex) — bricht Dark-Theme und widerspricht `ThemeManager`.

*Detail:* [docs/design/VISUAL_SYSTEM_AUDIT.md](docs/design/VISUAL_SYSTEM_AUDIT.md)

---

## 2. Vorgeschlagene Token-Architektur

- **Foundation:** 4px-Raster, absolute px für Desktop-Typo, Roh-Farben nur in Theme-Definition.
- **Semantic:** Bedeutung (`color.fg.primary`, `space.md`, `text.role.body`, `radius.input`, …).
- **Component:** Zusammensetzung für wiederkehrende Teile (`comp.button.md` implizit über Mapping-Dokument).

*Detail:* [docs/design/DESIGN_TOKEN_ARCHITECTURE.md](docs/design/DESIGN_TOKEN_ARCHITECTURE.md)

---

## 3. Definierte Token-Gruppen

| Gruppe | Dokument |
|--------|----------|
| COLOR | Referenz [THEME_TOKEN_SPEC.md](docs/design/THEME_TOKEN_SPEC.md), Nutzung [COLOR_USAGE_MAP.md](docs/design/COLOR_USAGE_MAP.md) |
| ICON | [DESIGN_TOKEN_SPEC.md](docs/design/DESIGN_TOKEN_SPEC.md) § ICON + bestehendes `IconManager` / `icon_states` |
| TYPOGRAPHY, SPACING, RADIUS, BORDER, SIZE, ELEVATION, STATE | [DESIGN_TOKEN_SPEC.md](docs/design/DESIGN_TOKEN_SPEC.md) |
| Desktop-Defaults | [DESIGN_TOKEN_DEFAULTS.md](docs/design/DESIGN_TOKEN_DEFAULTS.md) |
| Komponenten-Mapping | [DESIGN_COMPONENT_TOKEN_MAPPING.md](docs/design/DESIGN_COMPONENT_TOKEN_MAPPING.md) |

---

## 4. Größte Inkonsistenzen (Ist)

1. Python-Layouts vs. QSS-Spacing (gleiche Zahlen, andere Namen).  
2. Harte px und Hex in Domain-Widgets.  
3. Mehrere „Standard“-Zeilenhöhen für Fließtext.  
4. Toolbar-Icon 18px vs. empfohlenes `icon.size.md` 20px.  
5. Runtime-Nav-Typo umgeht `ThemeTokens`.

---

## 5. Empfohlene Umsetzungs-Prioritäten

1. **`design_metrics` in `layout_constants` verankern** (Import statt Duplikat).  
2. **Workbench `icon-size` auf 20px** und Send-Button-Icon auf `ICON_MD_PX`.  
3. **QSS-Bereinigung** der häufigsten Magic Numbers (Project Switcher, Breadcrumb, Runtime-Nav).  
4. **Entfernen der Hex-Inline-Styles** in Operations/Knowledge zugunsten `ThemeTokenId` + Resolver.  
5. **Markdown-Renderer** an Metriken aus Registry/Metrics koppeln.  
6. **ThemeTokens-Aliase** für kanonische Namen (`space_*` neben `spacing_*`) optional.

---

## 6. Offene Risiken

- **QSS-Subset:** Nicht alle Qt-Properties verhalten sich plattformgleich; zu aggressive Vereinheitlichung kann KDE/GNOME-Unterschiede sichtbar machen.  
- **Em-basierte Tab-Breiten** vs. px-Raster — bewusst beibehalten oder später umstellen.  
- **Schatten:** Überbewertung führt zu Frust; Dokumentation empfiehlt Border/Surface — wenn dennoch Schatten, nur optional pro Theme.  
- **Doppel-Paket `themes` vs. `theme`:** Kurz `app/gui/theme/` nur als Runtime-Hilfe; langfristig klar kommunizieren oder zusammenführen.

---

## 7. Nächste konkrete Implementierungsschritte

1. Import von `app.gui.theme.design_metrics` in `app/gui/shared/layout_constants.py` (Konstanten ableiten, keine Logikänderung).  
2. `workbench.qss`: `icon-size: 18px` → `20px` oder Platzhalter sobald in `ThemeTokens` ergänzt.  
3. `shell.qss`: Runtime-Nav auf `{{font_size_sm}}` / `{{font_weight_semibold}}`.  
4. Ein Panel mit Hex (z. B. `project_stats_panel.py`) auf `ThemeManager.color` migrieren als Referenz-PR.  
5. Optional: `ThemeTokens` um `icon_size_md: str = "20px"` erweitern und in QSS referenzieren.

**Runtime-Layer (Phase 7):** angelegt:

- `app/gui/theme/design_metrics.py` — Integer-px  
- `app/gui/theme/design_tokens.py` — kanonische Id-Strings  
- `app/gui/theme/design_token_registry.py` — `space_px`, `text_size_px`, `radius_px`, `icon_size_px`, `color`

---

## Artefakt-Index

| Datei |
|-------|
| [docs/design/VISUAL_SYSTEM_AUDIT.md](docs/design/VISUAL_SYSTEM_AUDIT.md) |
| [docs/design/DESIGN_TOKEN_ARCHITECTURE.md](docs/design/DESIGN_TOKEN_ARCHITECTURE.md) |
| [docs/design/DESIGN_TOKEN_SPEC.md](docs/design/DESIGN_TOKEN_SPEC.md) |
| [docs/design/DESIGN_TOKEN_DEFAULTS.md](docs/design/DESIGN_TOKEN_DEFAULTS.md) |
| [docs/design/DESIGN_COMPONENT_TOKEN_MAPPING.md](docs/design/DESIGN_COMPONENT_TOKEN_MAPPING.md) |
| [docs/design/DESIGN_TOKEN_MIGRATION_PLAN.md](docs/design/DESIGN_TOKEN_MIGRATION_PLAN.md) |

---

*Erstellt als Grundlage für einen folgenden Implementierungs-Agenten; keine vollständige Code-Migration in diesem Schritt.*
