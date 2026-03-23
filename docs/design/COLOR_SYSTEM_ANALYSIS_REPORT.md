# Color System Analysis Report

**Projekt:** Linux Desktop Chat / Obsidian Core  
**Stack:** Python, PySide6, QSS, Theme-System mit Tokens  
**Analysedatum:** 2026-03-22  
**Umfang:** `app/gui/` (Shell, Domains, Workbench, Themes), QSS `app/gui/themes/base/`, Token-Definition `app/gui/themes/canonical_token_ids.py`, Abgleich mit `docs/design/THEME_COMPONENT_MAPPING.md`.

---

## 1. Wichtigste Erkenntnisse

1. **Zwei Ebenen:** Globales QSS (Shell + Base) definiert das Großbild; einzelne Widgets und der **Legacy-Pfad** (`app/main.py`, `app/resources/styles.py`, `get_theme_colors`) können davon abweichen — das ist die Hauptquelle für Inkonsistenz.  
2. **Tokens sind bereits granular:** Die Spec deckt Foundation, Interaction, Chat, Markdown, Badges, Console, Graph-Status, Charts, Monitoring-Domain ab — die Design-Disziplin ist **wo** diese Tokens angewendet werden, nicht ob sie existieren.  
3. **Accent passiert an wenigen, wiederkehrenden Stellen:** Navigation (selected), Tabs, Fokus, Primary-CTAs, Links, Breadcrumb-Hover, Project-Switcher-Rand, ggf. Control-Center-Nav — dort sollte **ein** gemeinsames Accent-System greifen.  
4. **Runtime/Debug ist bewusst separat:** `color.domain.monitoring.*` bildet einen eigenen neutralen „Raum“; das ist sinnvoll, sollte aber nicht dazu verleiten, überall weitere parallele Paletten zu erfinden.  
5. **Semantic ist im Graph und in Badges/Logs klar verankert** — Gefahr ist **Übernutzung** auf normalen Flächen (Karten, Sidebar).

---

## 2. Problemstellen (Ist)

| Thema | Beobachtung | Referenz |
|-------|-------------|----------|
| **Mehrfach-Accent** | Nav-Selektion + Tab + CTA + Breadcrumb-Hover + teils CC-Nav mit `color_accent`/`color_accent_bg` erhöhen die wahrgenommene Accent-Fläche über das 7 %-Ziel hinaus | `shell.qss` (Control Center, Chat-Nav, Breadcrumbs) |
| **Legacy vs. Shell** | `THEME_COMPONENT_MAPPING.md` nennt Konflikte: `get_theme_colors`, light-only Karten, Inspector-Hex-Duplikate | Mapping + Audit-Verweise |
| **Primary Button in QSS** | Nicht alle Primäraktionen nutzen einheitlich `color.button.primary.*`; einige ObjectNames (Chat) sind explizit accent-gefüllt — gut, muss aber das **einzige** Muster bleiben | `shell.qss` `#chatNavNewChatButton` |
| **Semantic vs. Accent** | `STATE_INFO` und Link-Farben können sich ähneln — Gefahr der Gleichbehandlung von „klickbar“ und „informativ“ | Token-Spec + Markdown |
| **Charts / Serienfarben** | `color.chart.series.*` können wie zusätzliche Accents wirken, wenn zu knallig | Chart-Nutzung in KPI-Tabs |

---

## 3. Empfehlungen: Accentfarbe

1. **Eine** produktive Accent-Familie pro Theme (siehe [ACCENT_COLOR_FAMILIES.md](./ACCENT_COLOR_FAMILIES.md)); alternativ **Slate+Teal** oder **Blue** für maximale Ruhe.  
2. **Control Center Nav-Selektion** visuell an **Haupt-Sidebar-Selektion** annähern (gleiche Gewichtung von Fläche und Kontrast), statt zusätzliches „zweites“ Accent-System.  
3. **Links** (`FG_LINK`, `MARKDOWN_LINK`) an Accent hue koppeln, aber **leicht** von Button-Accent unterscheidbar halten (Unterstreichung / Schriftgewicht) für Klarheit.  
4. **Fokus-Ringe** barrierefrei; wenn möglich gleiche Hue wie Accent, aber eigener Token (`BORDER_FOCUS`), damit Dark-Mode-Kontrast unabhängig tweakbar bleibt.

---

## 4. Empfehlungen: Neutralpalette

1. **Strikte Hierarchie:** `bg.app` (Canvas) ≤ `bg.panel` / `bg.muted` ≤ `bg.surface` ≤ `bg.surface_elevated` — Inspector und Bottom Panel auf **muted** oder **surface_alt**, nie auf Accent-Tint.  
2. **Text:** `fg.primary` für Hauptinhalt, `fg.secondary` für Metadaten, `fg.muted` für Platzhalter — **kein** Accent für normale Überschriften.  
3. **Ränder:** `border.subtle` für die meisten Karten; `border.default` für editierbare/interaktive Container; `border.strong` sparsam.  
4. **Chat-Bubbles:** Über `color.chat.*` abstufen, **ohne** globales `state.accent` zu mischen — erhält ruhige Konversationsoberfläche.  
5. **Monitoring-Bereich:** Bei `color.domain.monitoring.*` bleiben; keine dritten „neutralen“ Varianten pro Screen erfinden.

---

## 5. Deliverables (diese Analyse)

| Datei | Inhalt |
|-------|--------|
| [GUI_COMPONENT_INVENTORY.md](./GUI_COMPONENT_INVENTORY.md) | Vollständiges GUI-Inventar |
| [COLOR_USAGE_MAP.md](./COLOR_USAGE_MAP.md) | Komponente → Background/Text/Accent/Semantic |
| [ACCENT_USAGE_RULES.md](./ACCENT_USAGE_RULES.md) | Allowlist / Denylist |
| [SEMANTIC_COLOR_USAGE.md](./SEMANTIC_COLOR_USAGE.md) | Success / Warning / Error / Info |
| [GUI_COLOR_HEATMAP.md](./GUI_COLOR_HEATMAP.md) | N/A/S-Klassifikation, Ziel 90/7/3 |
| [ACCENT_COLOR_FAMILIES.md](./ACCENT_COLOR_FAMILIES.md) | Vorschlagsfamilien Blue, Emerald, Amber, Purple, Slate+Teal |

---

## 6. Nächste sinnvolle Schritte (optional)

1. **Messbar machen:** Theme-Visualizer oder Screenshot-Tests mit Pixel-Anteil Accent (heuristisch) — aufwendig, aber für 90/7/3 hilfreich.  
2. **Legacy bereinigen:** `app/main.py`-Pfad auf Token-QSS migrieren (siehe `THEME_MIGRATION_PLAN.md`).  
3. **QSS-Audit:** Ein PR nur für `shell.qss` CC-Nav + Breadcrumb, um Accent-Fläche zu reduzieren.

---

*Ende Report.*
