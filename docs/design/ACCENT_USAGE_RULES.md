# Accent Usage Rules

**Ziel:** Ruhige GUI (~90 % neutral / ~7 % accent / ~3 % semantic) mit **einem** erkennbaren Interaktionskanal — keine parallelen „zweiten Accents“ in benachbarten Navigationsleisten.  
**Technische Anker:** `color.state.accent*`, `color.button.primary.*`, `color.fg.link`, `color.border.focus` / `color.input.border_focus`, `color.nav.active_*` (→ Legacy `color_nav_selected_*` in QSS), `color.tab.*`.

---

## 0. Ein-Kanal-Modell („Single accent spine“)

| Ebene | Rolle | Umsetzung |
|-------|--------|-----------|
| **Selektion (Ort)** | Wo bin ich in der App? | **Ein** Stil für alle Haupt-Chrome-Navs: Haupt-Sidebar, Operations-, Settings-, **Control-Center-** und **QA-Governance-**Listen → `color_nav_selected_bg` / `color_nav_selected_fg` (semantic: `nav.active_*`). |
| **Fokus (Tastatur)** | Wo wirkt Eingabe? | `color_border_focus`, `color_input_border_focus`, `color.interaction.focus_ring` — **kein** zusätzliches Vollflächen-Accent nur für Hover. |
| **Handlung (CTA)** | Was ist die eine Hauptaktion? | `color_button_primary_*` (Spec: `color.button.primary.*`) — in QSS explizit, nicht parallel `color_accent` mischen. |
| **Link (Navigation)** | Wohin führt der Text? | `color_fg_link` (`color.fg.link`) — in Themes häufig gleiche Hue wie Accent, **semantisch** eigener Token. |
| **Separater Raum** | Runtime / Debug | `color.domain.monitoring.*` bleibt eigenständig (eigener „Raum“, kein Produkt-Marketing-Accent). |

**Nicht erlaubt:** Dieselbe Listen-Selektion mal mit `accent`+`accent_muted_bg`, mal mit `nav_selected_*`, mal mit QA-spezifischem Dritt-Ton — das erzeugt mehrere gleichwertige Accent-Kanäle.

---

## 1. Erlaubt (Allowlist)

| Kontext | Erlaubte Nutzung | Token-Beispiele |
|---------|------------------|-----------------|
| **Alle App-Chrome-Nav-Selektionen** | Einheitlich selected row | `NAV_ACTIVE_BG` / `NAV_ACTIVE_FG` → QSS `color_nav_selected_*` |
| **Aktiver Tab-Inhalt** | Surface + Text; Indikator **neutral** (Standard) | `TAB_*`; Indikator default → `border_medium` (siehe `resolved_spec_tokens`) |
| **Fokussiertes Eingabefeld** | Rand / Ring | `INPUT_BORDER_FOCUS`, `BORDER_FOCUS` |
| **Primäre Schaltfläche** | Eine Hauptaktion pro Block | `BUTTON_PRIMARY_*` |
| **Links & Breadcrumb-Hover** | Textfarbe Link-Token | `FG_LINK` in QSS `color_fg_link` |
| **Text-/Listen-Selektion** | Wie Spec | `SELECTION_*`, `INTERACTION_SELECTED` |
| **Project Switcher Hover** | Dünner Rand: Fokus-Kante, nicht Voll-Accent | `color_border_focus` |
| **Graph: ausgewählter Knoten** | Rahmen | `GRAPH_NODE_SELECTED_BORDER` |
| **Fortschritt** | Eigener Token oder an Accent gekoppelt — sparsam | (optional `state.accent` oder dedizierte Progress-Tokens) |

---

## 2. Nicht erlaubt (Denylist)

| Kontext | Begründung |
|---------|------------|
| **Panel-/Card-/Dialog-Vollflächen in Accent** | Nur neutrale Surfaces |
| **Sidebar-Hintergrund gesamt** | Nur neutrale `nav.bg` |
| **Zweite Nav-Selektion mit anderem Accent-Paar** (z. B. CC ≠ Operations) | Verwässert Wiedererkennbarkeit |
| **Tab-Unterstreichung / Indicator standardmäßig in Brand-Accent** | Erhöht Accent-Fläche; Standard: neutrale Kante |
| **Markdown-Fließtext in Accent** | Nur Links |
| **Semantic durch Accent ersetzen** | Fehler/Warnung bleiben eigenständige Farben |

---

## 3. Priorität bei Konflikt

1. Semantic (Fehler/Warnung) vor Accent-Dekoration.  
2. Fokus vor Hover-Deko.  
3. Eine Primary-CTA pro Blickfeld.

---

## 4. Referenz im Repo (kanonisch)

- **QSS (Loader):** `assets/themes/base/shell.qss` — TopBar, Breadcrumbs, Navs, Chat-Nav, Chat-Input, …  
- **Synchron:** `app/gui/themes/base/shell.qss` (Kopie; bei Drift `assets/` führend).  
- **QA-Nav = Haupt-Nav:** `app/gui/themes/palette_resolve.py` setzt `color_qa_nav_selected_*` nach Resolve auf `color_nav_selected_*`.  
- **Control-Center-Nav:** QSS nutzt dieselben Tokens wie Operations-Nav.

---

## 5. Siehe auch

- [DEFAULT_ACCENT_STRATEGY.md](./DEFAULT_ACCENT_STRATEGY.md)  
- [COLOR_SYSTEM_FINAL_STRATEGY.md](./COLOR_SYSTEM_FINAL_STRATEGY.md)  
- [SEMANTIC_COLOR_USAGE.md](./SEMANTIC_COLOR_USAGE.md)

---

*Ende Accent-Regeln.*
