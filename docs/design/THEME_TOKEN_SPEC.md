# Theme-Token-Spezifikation — verbindlich

**Quelle:** [THEME_TARGET_MODEL.md](./THEME_TARGET_MODEL.md), [docs/audits/THEME_COLOR_AUDIT.md](../audits/THEME_COLOR_AUDIT.md).  
**Kanonical Name:** `color.*` mit Punktnotation (Logik/API-Dokumentation).  
**QSS-/Python-Map-Key:** `color_*` mit Unterstrich, Punkte → Unterstriche (`color.bg.app` → `color_bg_app`). Alle Platzhalter in QSS verwenden **exakt** den Map-Key.

**Regeln:**

- Jeder Token ist ein **String** im CSS-Farbformat (`#rrggbb`, ggf. `#aarrggbb` wo Qt erlaubt).
- **Ableitbar ja:** Default-Wert wird aus anderen Tokens per Regel gesetzt; Theme darf explizit überschreiben.
- **Kontrast kritisch ja:** Paarprüfung gegen Hintergrund in [THEME_CONTRAST_RULES.md](./THEME_CONTRAST_RULES.md) Pflicht.

---

## Implementierungs-Mapping (bestehende Keys)

Die Codebasis nutzt heute u. a. `color_text`, `color_bg_surface`, … Die Migration **endet** bei den unten definierten Namen. Übergangsweise gilt:

| Legacy-Key (heute) | Ziel-Token (canonical) |
|--------------------|-------------------------|
| `color_bg` | `color.bg.app` |
| `color_nav_bg` | `color.bg.panel` |
| `color_bg_surface` | `color.bg.surface` |
| `color_bg_elevated` | `color.bg.surface_elevated` |
| `color_bg_muted` | `color.bg.surface_alt` (oder Ableitung; siehe unten) |
| `color_bg_input` | `color.input.bg` |
| `color_bg_hover` | `color.interaction.hover` |
| `color_bg_selected` | `color.interaction.selected` |
| `color_text` | `color.fg.primary` |
| `color_text_secondary` | `color.fg.secondary` |
| `color_text_muted` | `color.fg.muted` |
| `color_text_disabled` | `color.fg.disabled` |
| `color_text_inverse` | `color.fg.inverse` |
| `color_border` | `color.border.default` |
| `color_border_medium` | `color.border.subtle` / `strong` je Kontext — Migration klärt 1:1 Zuordnung |
| `color_accent` | `color.state.accent` |
| `color_success` etc. | `color.state.*` |
| `color_monitoring_*` | `color.domain.monitoring.*` |
| `color_qa_nav_*` | `color.domain.qa_nav.*` |

Bis Migration abgeschlossen: **Resolver** kann Aliase ausgeben, sodass altes QSS funktioniert; neue Arbeit nutzt nur Ziel-Keys.

---

## OKLCH-Neutralbasis (Default Light / Dark)

**Autoritative Tabelle:** [NEUTRAL_COLOR_SYSTEM.md](./NEUTRAL_COLOR_SYSTEM.md) (OKLCH-Werte, HEX, Kontrast).

**Parameter:** `oklch(L C H)` mit **H = 250**, **C = 0.01** (kaum Sättigung, kühles Neutral). Nur **L** (Lightness, 0…1) wird pro Rolle variiert. Umrechnung nach sRGB für QSS: **HEX** in `SemanticPalette` → `semantic_palette_to_theme_tokens` → `{{color_*}}`.

**Implementierte Referenz-HEX** (Built-ins `light_default` / `dark_default` in `app/gui/themes/builtin_semantic_profiles.py`):

| Canonical | Flat Key | Dark HEX | Light HEX |
|-----------|----------|----------|-----------|
| `color.bg.app` | `color_bg_app` | `#020306` | `#b0b5ba` |
| `color.bg.surface` | `color_bg_surface` | `#0d1115` | `#d1d6dc` |
| `color.bg.surface_alt` | `color_bg_surface_alt` | `#06090d` | `#ccd2d7` |
| `color.bg.surface_elevated` | `color_bg_surface_elevated` | `#191d22` | `#d9dfe5` |
| `color.border.default` | `color_border_default` | `#393e42` | `#888d92` |
| `color.fg.primary` | `color_fg_primary` | `#edf2f8` | `#000001` |
| `color.fg.secondary` | `color_fg_secondary` | `#a0a5ab` | `#25292e` |
| `color.fg.muted` | `color_fg_muted` | `#70757a` | `#4e5358` |

**Hinweise:**

- **Light-Theme:** Hintergrund-Reihenfolge entsteht durch **spiegelnde Paarung** der Dark-Stufen (App ↔ Elevated, Panel ↔ Surface, …), sodass die **monotone Aufhellung** von Workspace → Karten erhalten bleibt. **Randfarben Light** sind teils **explizit** gesetzt (nicht streng `1 − L_dark`), damit Kanten-Kontrast die Policy in `semantic_validation` erfüllt (`border_strong` vs. `bg_app`).
- **`color.bg.panel`:** weiterhin Nav/Inspector; OKLCH-L zwischen App und Surface — siehe vollständige Tabelle im Neutral-Dokument.
- **Legacy:** `color_nav_bg` = `bg.panel`, `color_bg_muted` = `bg.surface_alt` (Resolver).

---

## 1. Foundation / Base

| Canonical | Flat Key | Bedeutung | Erlaubte Nutzung | Typische Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|------------------|----------------------|-----------|-------------------|
| `color.bg.app` | `color_bg_app` | Gesamt-Canvas unterhalb von Fensterdeko | App-weiter Hintergrund, leere Flächen | `QMainWindow`, Workspace-Host | nein | ja (mit `color.fg.primary`) |
| `color.bg.window` | `color_bg_window` | Standard-Fenster-Innenfläche (falls von App abweichend) | Dialoge, sekundäre Fenster | `QDialog`, `QWidget` Root | ja ← `color.bg.app` | ja |
| `color.bg.panel` | `color_bg_panel` | Seitenleisten, feste Nebenflächen | Nav, Inspector, Dock-Inhalt | Sidebar, Inspector | nein | ja |
| `color.bg.surface` | `color_bg_surface` | Standard-Karten/Formularfläche | Panel-Inhalt, GroupBox-Fläche | Cards, Settings-Seiten | nein | ja |
| `color.bg.surface_alt` | `color_bg_surface_alt` | Leicht abweichende Fläche (Striping, zweite Spalte) | Abwechslung innerhalb Surface | Split-Views, Settings-Blöcke | ja ← Mischung surface/hover | nein |
| `color.bg.surface_elevated` | `color_bg_surface_elevated` | Stärker angehobene Fläche | Hover-Elevation simulieren, „aufgelegte“ Karten | modale Innenbereiche | ja | nein |
| `color.bg.overlay` | `color_bg_overlay` | Vollflächige Überlagerung (Modal-Scrim) | Dimming hinter Dialogen | Overlay-Widget | ja | nein |

---

## 2. Text / Foreground

| Canonical | Flat Key | Bedeutung | Nutzung | Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|---------|-------------|-----------|-------------------|
| `color.fg.primary` | `color_fg_primary` | Standard-Lesetext | Body, Listen, Tabellen | `QLabel`, `QTableView` | nein | ja |
| `color.fg.secondary` | `color_fg_secondary` | Weniger betonte Beschriftungen | Subtitles, Metadaten | Meta-Labels | ja | ja |
| `color.fg.muted` | `color_fg_muted` | Hinweise, Captions | Hilfetext, sekundäre Spalten | Captions | ja | ja |
| `color.fg.disabled` | `color_fg_disabled` | Deaktivierte Controls | Disabled state | alle disabled | ja | ja (auf `color.bg.surface` / input disabled bg) |
| `color.fg.inverse` | `color_fg_inverse` | Text auf dunklem Accent / inverse Flächen | Primärbutton-Label, Badge light-on-dark | Primary CTA | nein | ja |
| `color.fg.link` | `color_fg_link` | Hyperlinks (Markdown, QTextBrowser) | Klickbare Links | Help, Chat | ja ← `color.state.accent` mit Abweichungsrecht | ja |
| `color.fg.on_success` | `color_fg_on_success` | Text auf Success-Hintergrund | Badges, Banner | Status | nein | ja |
| `color.fg.on_warning` | `color_fg_on_warning` | Text auf Warning-Hintergrund | Banner | Alerts | nein | ja |
| `color.fg.on_error` | `color_fg_on_error` | Text auf Error-Hintergrund | Fehler-Banner | Alerts | nein | ja |
| `color.fg.on_selected` | `color_fg_on_selected` | Text auf ausgewähltem Listeneintrag (nicht Textselection) | Nav selected | Sidebar item | nein | ja |

---

## 3. Borders

| Canonical | Flat Key | Bedeutung | Nutzung | Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|---------|-------------|-----------|-------------------|
| `color.border.default` | `color_border_default` | Standard-Rahmen | Inputs, Karten | `QLineEdit`, Frames | nein | nein |
| `color.border.subtle` | `color_border_subtle` | Dezent, Trennlinien | Innere Trenner | `QFrame` HLine | ja | nein |
| `color.border.strong` | `color_border_strong` | Betonte Umrandung | Fokus-Nähe, Fehlerzustand | validation | ja | teils |
| `color.border.focus` | `color_border_focus` | Sichtbare Fokus-Umrandung | Tastaturfokus | `QLineEdit:focus` | ja ← accent | ja |

---

## 4. Interaction

| Canonical | Flat Key | Bedeutung | Nutzung | Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|---------|-------------|-----------|-------------------|
| `color.interaction.hover` | `color_interaction_hover` | Hover-Hintergrund | Listen, Buttons sekundär | `QListWidget::item:hover` | ja | nein |
| `color.interaction.pressed` | `color_interaction_pressed` | Pressed | Buttons | `:pressed` | ja | nein |
| `color.interaction.selected` | `color_interaction_selected` | Auswahl-Hintergrund (Listen/Nav) | Selection | Nav, List | nein | ja (mit on_selected fg) |
| `color.interaction.active` | `color_interaction_active` | Aktiver Zustand (Toggle on) | Tabs, Toggles | `QTabBar` | ja | nein |
| `color.interaction.focus_ring` | `color_interaction_focus_ring` | Fokus-Ring / Outline-Farbe | Accessibility | focus | ja | ja |

---

## 5. Selection (Text)

| Canonical | Flat Key | Bedeutung | Nutzung | Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|---------|-------------|-----------|-------------------|
| `color.selection.bg` | `color_selection_bg` | Textauswahl Hintergrund | Editors | `QTextEdit`, `QLineEdit` | ja | ja |
| `color.selection.fg` | `color_selection_fg` | Textauschrift auf Selection | Editors | gleiche | ja | ja |

---

## 6. State / Semantic

| Canonical | Flat Key | Bedeutung | Nutzung | Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|---------|-------------|-----------|-------------------|
| `color.state.accent` | `color_state_accent` | Primäre Marken-/Aktionsfarbe | Links, Primär-Aktionen | Buttons primary | nein | ja |
| `color.state.accent_hover` | `color_state_accent_hover` | Accent hover | Buttons | `:hover` | ja | nein |
| `color.state.accent_pressed` | `color_state_accent_pressed` | Accent pressed | Buttons | `:pressed` | ja | nein |
| `color.state.accent_muted_bg` | `color_state_accent_muted_bg` | Hintergrund für „accent-tinted“ Flächen | Chips, Info-Banner leicht | Tags | ja | nein |
| `color.state.success` | `color_state_success` | Erfolg (Icon, Rand, nicht unbedingt Fill) | Status | Icons, Labels | nein | nein |
| `color.state.warning` | `color_state_warning` | Warnung | Status | gleiche | nein | nein |
| `color.state.error` | `color_state_error` | Fehler | Validation | gleiche | nein | nein |
| `color.state.info` | `color_state_info` | Information | Hinweise | gleiche | nein | nein |

---

## 7. Buttons

| Canonical | Flat Key | Bedeutung | Nutzung | Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|---------|-------------|-----------|-------------------|
| `color.button.primary.bg` | `color_button_primary_bg` | Primärbutton Hintergrund | Hauptaktion | `QPushButton` primary | ja ← accent | ja |
| `color.button.primary.fg` | `color_button_primary_fg` | Primärbutton Text | | | ja ← inverse | ja |
| `color.button.primary.hover` | `color_button_primary_hover` | Primär hover BG | | `:hover` | ja | ja |
| `color.button.primary.pressed` | `color_button_primary_pressed` | Primär pressed | | `:pressed` | ja | ja |
| `color.button.secondary.bg` | `color_button_secondary_bg` | Sekundär BG | | secondary ObjectName | ja ← surface | ja |
| `color.button.secondary.fg` | `color_button_secondary_fg` | Sekundär Text | | | ja ← primary fg | ja |
| `color.button.secondary.border` | `color_button_secondary_border` | Sekundär Rand | | | ja ← border.default | nein |
| `color.button.secondary.hover` | `color_button_secondary_hover` | Sekundär hover | | | ja | nein |
| `color.button.disabled.bg` | `color_button_disabled_bg` | Disabled | | `:disabled` | ja | nein |
| `color.button.disabled.fg` | `color_button_disabled_fg` | Disabled Text | | | ja ← fg.disabled | ja |

---

## 8. Inputs

| Canonical | Flat Key | Bedeutung | Nutzung | Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|---------|-------------|-----------|-------------------|
| `color.input.bg` | `color_input_bg` | Eingabefeld Hintergrund | | `QLineEdit`, `QPlainTextEdit` | nein | ja |
| `color.input.fg` | `color_input_fg` | Eingabetext | | | ja ← fg.primary | ja |
| `color.input.placeholder` | `color_input_placeholder` | Platzhaltertext | | placeholder | ja ← fg.muted | ja |
| `color.input.border` | `color_input_border` | Standard-Rand | | | ja ← border.default | nein |
| `color.input.border_focus` | `color_input_border_focus` | Fokus-Rand | | `:focus` | ja ← border.focus | ja |
| `color.input.disabled_bg` | `color_input_disabled_bg` | Disabled BG | | | ja | nein |
| `color.input.disabled_fg` | `color_input_disabled_fg` | Disabled Text | | | ja ← fg.disabled | ja |

---

## 9. Navigation

| Canonical | Flat Key | Bedeutung | Nutzung | Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|---------|-------------|-----------|-------------------|
| `color.nav.bg` | `color_nav_bg` | Nav-Fläche | Haupt-Sidebar | Shell nav | nein | ja |
| `color.nav.fg` | `color_nav_fg` | Nav-Text | | | ja ← fg.primary | ja |
| `color.nav.hover_bg` | `color_nav_hover_bg` | Nav hover | | | ja ← interaction.hover | nein |
| `color.nav.active_bg` | `color_nav_active_bg` | Ausgewählter Eintrag | | | ja ← interaction.selected | ja |
| `color.nav.active_fg` | `color_nav_active_fg` | Ausgewählter Text | | | ja ← fg.on_selected | ja |

---

## 10. Tabs

| Canonical | Flat Key | Bedeutung | Nutzung | Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|---------|-------------|-----------|-------------------|
| `color.tab.bg` | `color_tab_bg` | Tab-Leiste Hintergrund | | `QTabBar` | ja | nein |
| `color.tab.fg` | `color_tab_fg` | Inaktiver Tab-Text | | | ja ← fg.muted | ja |
| `color.tab.active_bg` | `color_tab_active_bg` | Aktiver Tab | | | ja ← surface | ja |
| `color.tab.active_fg` | `color_tab_active_fg` | Aktiver Tab-Text | | | ja ← fg.primary | ja |
| `color.tab.indicator` | `color_tab_indicator` | Unterstreichung/Akzent | selected indicator | | ja ← accent | nein |

---

## 11. Tabellen

| Canonical | Flat Key | Bedeutung | Nutzung | Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|---------|-------------|-----------|-------------------|
| `color.table.bg` | `color_table_bg` | Zellenhintergrund | Datenbereich | `QTableWidget` | ja ← surface | ja |
| `color.table.fg` | `color_table_fg` | Zelltext | | | ja ← fg.primary | ja |
| `color.table.header_bg` | `color_table_header_bg` | Kopfzeile BG | | header | ja ← surface_elevated | ja |
| `color.table.header_fg` | `color_table_header_fg` | Kopfzeile Text | | | ja ← fg.secondary | ja |
| `color.table.row_alt_bg` | `color_table_row_alt_bg` | Alternierende Zeile | | alternate-background | ja ← surface_alt | nein |
| `color.table.grid` | `color_table_grid` | Gitterlinien | | gridline-color | ja ← border.subtle | nein |
| `color.table.selection_bg` | `color_table_selection_bg` | Auswahl | | | ja ← selection.bg | ja |
| `color.table.selection_fg` | `color_table_selection_fg` | Auswahltext | | | ja ← selection.fg | ja |

---

## 12. Chat

| Canonical | Flat Key | Bedeutung | Nutzung | Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|---------|-------------|-----------|-------------------|
| `color.chat.user_bg` | `color_chat_user_bg` | Nutzerblase Hintergrund | Chat UI | Bubble | nein | ja |
| `color.chat.user_fg` | `color_chat_user_fg` | Nutzerblase Text | | | ja | ja |
| `color.chat.user_border` | `color_chat_user_border` | optional Rand | | | ja | nein |
| `color.chat.assistant_bg` | `color_chat_assistant_bg` | Assistent | | | nein | ja |
| `color.chat.assistant_fg` | `color_chat_assistant_fg` | Assistent Text | | | ja | ja |
| `color.chat.assistant_border` | `color_chat_assistant_border` | Rand (Audit: rgba borders) | | | ja | nein |
| `color.chat.system_bg` | `color_chat_system_bg` | Systemnachrichten | | | ja ← surface_alt | ja |
| `color.chat.system_fg` | `color_chat_system_fg` | Systemtext | | | ja ← fg.muted | ja |

---

## 13. Markdown / Rich Text

| Canonical | Flat Key | Bedeutung | Nutzung | Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|---------|-------------|-----------|-------------------|
| `color.markdown.body` | `color_markdown_body` | Fließtext HTML | Renderer | QTextBrowser | ja ← fg.primary | ja |
| `color.markdown.heading` | `color_markdown_heading` | Überschriften | h1–h6 | | ja ← fg.primary | ja |
| `color.markdown.link` | `color_markdown_link` | Links im HTML | `<a>` | | ja ← fg.link | ja |
| `color.markdown.quote` | `color_markdown_quote` | Blockquote Text | | | ja ← fg.secondary | ja |
| `color.markdown.quote_border` | `color_markdown_quote_border` | Blockquote linke Kante | border-left | | ja ← border.strong | nein |
| `color.markdown.inline_code_bg` | `color_markdown_inline_code_bg` | Inline `code` BG | | | ja ← surface_alt | ja |
| `color.markdown.inline_code_fg` | `color_markdown_inline_code_fg` | Inline code Text | | | ja ← fg.primary | ja |
| `color.markdown.codeblock_bg` | `color_markdown_codeblock_bg` | fenced code | `<pre>` | | nein | ja |
| `color.markdown.codeblock_fg` | `color_markdown_codeblock_fg` | fenced code Text | | | nein | ja |
| `color.markdown.table_border` | `color_markdown_table_border` | Tabellenraster | | | ja ← border.default | nein |
| `color.markdown.table_header_bg` | `color_markdown_table_header_bg` | Tabellenkopf | | | ja ← table.header_bg | nein |
| `color.markdown.hr` | `color_markdown_hr` | Horizontale Linie | `<hr>` | | ja ← border.subtle | nein |

---

## 14. Syntax (Code / Konsole) — Mindestumfang

| Canonical | Flat Key | Bedeutung | Nutzung | Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|---------|-------------|-----------|-------------------|
| `color.syntax.plain` | `color_syntax_plain` | Standard Konsolentext | Console | `console_panel` | ja ← fg.primary | ja |
| `color.syntax.keyword` | `color_syntax_keyword` | Schlüsselwörter | optional | | nein | ja |
| `color.syntax.string` | `color_syntax_string` | Strings | | | nein | ja |
| `color.syntax.comment` | `color_syntax_comment` | Kommentare | | | ja ← fg.muted | ja |
| `color.syntax.number` | `color_syntax_number` | Zahlen | | | nein | nein |
| `color.syntax.function` | `color_syntax_function` | Funktionsnamen | | | nein | nein |
| `color.console.info` | `color_console_info` | Log info | Konsolen-Level | bestehend | ja ← state.info | nein |
| `color.console.warning` | `color_console_warning` | Log warn | | | ja ← state.warning | nein |
| `color.console.error` | `color_console_error` | Log error | | | ja ← state.error | nein |
| `color.console.success` | `color_console_success` | Log success | | | ja ← state.success | nein |

---

## 15. Badges

| Canonical | Flat Key | Bedeutung | Nutzung | Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|---------|-------------|-----------|-------------------|
| `color.badge.success.bg` | `color_badge_success_bg` | | Status-Chip | | ja | ja |
| `color.badge.success.fg` | `color_badge_success_fg` | | | | ja ← on_success | ja |
| `color.badge.warning.bg` | `color_badge_warning_bg` | | | | ja | ja |
| `color.badge.warning.fg` | `color_badge_warning_fg` | | | | ja ← on_warning | ja |
| `color.badge.error.bg` | `color_badge_error_bg` | | | | ja | ja |
| `color.badge.error.fg` | `color_badge_error_fg` | | | | ja ← on_error | ja |
| `color.badge.info.bg` | `color_badge_info_bg` | | | | ja | ja |
| `color.badge.info.fg` | `color_badge_info_fg` | | | | ja ← fg.inverse / primary je Theme | ja |

---

## 16. Domain: Monitoring / Runtime (Audit: color_monitoring_*)

| Canonical | Flat Key | Bedeutung | Nutzung | Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|---------|-------------|-----------|-------------------|
| `color.domain.monitoring.bg` | `color_domain_monitoring_bg` | Tiefster Hintergrund Monitoring-UI | Runtime-Debug | Panels | nein | ja |
| `color.domain.monitoring.surface` | `color_domain_monitoring_surface` | Karten in Monitoring | | | nein | ja |
| `color.domain.monitoring.border` | `color_domain_monitoring_border` | Rahmen | | | ja | nein |
| `color.domain.monitoring.text` | `color_domain_monitoring_text` | Primärtext | | | nein | ja |
| `color.domain.monitoring.muted` | `color_domain_monitoring_muted` | Sekundärtext | | | ja | ja |
| `color.domain.monitoring.accent` | `color_domain_monitoring_accent` | Akzent | | | ja ← state.accent (Abweichung erlaubt) | nein |
| `color.domain.monitoring.accent_bg` | `color_domain_monitoring_accent_bg` | Akzent-Hintergrund | | | ja | nein |

---

## 17. Domain: QA Navigation (Audit: color_qa_nav_*)

| Canonical | Flat Key | Bedeutung | Nutzung | Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|---------|-------------|-----------|-------------------|
| `color.domain.qa_nav.selected_bg` | `color_domain_qa_nav_selected_bg` | QA-Nav ausgewählt | QA Governance | Nav | nein | ja |
| `color.domain.qa_nav.selected_fg` | `color_domain_qa_nav_selected_fg` | QA-Nav Text selected | | | nein | ja |

---

## 18. Charts

| Canonical | Flat Key | Bedeutung | Nutzung | Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|---------|-------------|-----------|-------------------|
| `color.chart.bg` | `color_chart_bg` | Plot-Hintergrund | QtCharts | `agent_performance_tab` | ja ← domain.monitoring.bg | nein |
| `color.chart.axis` | `color_chart_axis` | Achsenlinien/Beschriftung | | | ja ← fg.muted | nein |
| `color.chart.grid` | `color_chart_grid` | Gitter | | | ja ← border.subtle | nein |
| `color.chart.series.1` | `color_chart_series_1` | Serie 1 | Linien/Balken | | nein | nein |
| `color.chart.series.2` | `color_chart_series_2` | Serie 2 | | | nein | nein |
| `color.chart.series.3` | `color_chart_series_3` | Serie 3 | | | nein | nein |
| `color.chart.series.other` | `color_chart_series_other` | weitere / default | | | ja | nein |

---

## 19. Workflow / Graph (Canvas)

| Canonical | Flat Key | Bedeutung | Nutzung | Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|---------|-------------|-----------|-------------------|
| `color.graph.node.fill` | `color_graph_node_fill` | Standard-Knoten Füllung | Workflow | `WorkflowNodeItem` neutral | ja ← surface | nein |
| `color.graph.node.border` | `color_graph_node_border` | Standard-Knoten Rand | | | ja ← border.default | nein |
| `color.graph.node.text` | `color_graph_node_text` | Titelzeile | | | ja ← fg.primary | ja |
| `color.graph.node.text_muted` | `color_graph_node_text_muted` | Subtext | | | ja ← fg.muted | ja |
| `color.graph.node.selected_border` | `color_graph_node_selected_border` | Auswahlrahmen | | | ja ← state.accent | ja |
| `color.graph.edge` | `color_graph_edge` | Kantenfarbe | | `workflow_edge_item` | ja ← border.strong | nein |
| `color.graph.node.status.completed.fill` | `color_graph_node_status_completed_fill` | Run-Status | | | ja ← badge.success.bg | nein |
| `color.graph.node.status.completed.border` | `color_graph_node_status_completed_border` | | | | ja ← state.success | nein |
| `color.graph.node.status.failed.fill` | `color_graph_node_status_failed_fill` | | | | ja ← badge.error.bg | nein |
| `color.graph.node.status.failed.border` | `color_graph_node_status_failed_border` | | | | ja ← state.error | nein |
| `color.graph.node.status.running.fill` | `color_graph_node_status_running_fill` | | | | ja ← accent_muted_bg | nein |
| `color.graph.node.status.running.border` | `color_graph_node_status_running_border` | | | | ja ← state.accent | nein |
| `color.graph.node.status.pending.fill` | `color_graph_node_status_pending_fill` | | | | ja ← surface | nein |
| `color.graph.node.status.pending.border` | `color_graph_node_status_pending_border` | | | | ja ← fg.muted | nein |
| `color.graph.node.status.cancelled.fill` | `color_graph_node_status_cancelled_fill` | | | | ja ← state.warning | nein |
| `color.graph.node.status.cancelled.border` | `color_graph_node_status_cancelled_border` | | | | ja ← state.warning | nein |

---

## 20. Indicators (Workbench-Tabs, Status-Dots)

| Canonical | Flat Key | Bedeutung | Nutzung | Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|---------|-------------|-----------|-------------------|
| `color.indicator.ready` | `color_indicator_ready` | Neutral OK | Tab-Badge | `canvas_tabs` | ja ← fg.muted | nein |
| `color.indicator.running` | `color_indicator_running` | Läuft | | | ja ← state.info | nein |
| `color.indicator.failed` | `color_indicator_failed` | Fehler | | | ja ← state.error | nein |
| `color.indicator.indexing` | `color_indicator_indexing` | Indexierung | | | ja ← state.warning | nein |
| `color.indicator.syncing` | `color_indicator_syncing` | Sync | | | ja ← state.accent | nein |

---

## 21. Menus / Tooltips (falls nicht nur von Qt-Standard)

| Canonical | Flat Key | Bedeutung | Nutzung | Komponenten | Ableitbar | Kontrast kritisch |
|-----------|----------|-----------|---------|-------------|-----------|-------------------|
| `color.menu.bg` | `color_menu_bg` | Kontextmenü BG | QMenu | `markdown_widgets` | ja ← surface_elevated | ja |
| `color.menu.fg` | `color_menu_fg` | Menütext | | | ja ← fg.primary | ja |
| `color.menu.hover_bg` | `color_menu_hover_bg` | Item hover | | | ja ← interaction.hover | ja |
| `color.tooltip.bg` | `color_tooltip_bg` | Tooltip | | | ja ← surface_elevated | ja |
| `color.tooltip.fg` | `color_tooltip_fg` | Tooltip Text | | | ja ← fg.primary | ja |

---

## 22. Strukturelle Tokens (Nicht-Farbe, Referenz)

Bereits in `ThemeTokens`: `spacing_*`, `radius_*`, `font_size_*`, `font_weight_*`, `font_family_*`.  
**Regel:** Diese Keys bleiben **unverändert** benannt; keine Farbe in denselben Keys mischen.

---

## Vollständigkeit

- Neue UI darf **keine** Farbe einführen, die nicht unter einem der obigen Tokens (oder expliziter Domain-Erweiterung `color.domain.*`) abgebildet werden kann.
- Erweiterung der Spec: **PR mit Aktualisierung dieser Datei** + Kontrast-Regel + ein Theme-Profil, das den Token setzt.
