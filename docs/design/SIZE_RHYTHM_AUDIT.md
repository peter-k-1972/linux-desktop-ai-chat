# Höhen- und Größenraster (Size Rhythm Audit)

**Ziel:** Ein erkennbares Desktop-Raster für Controls und Chrome ableiten.  
**Quellen:** Python `setMinimumHeight`/`setFixedHeight`/Widths, QSS `min-height`, `icon-size`, `layout_constants`, `shell/layout_constants`.

---

## 1. Abgeleitetes Basis-Raster (4px)

| Stufe | px | Verwendung |
|-------|-----|------------|
| Micro | 2 | Listen-Zwischenraum (`setSpacing(2)`), QSS-Margins |
| XS | 4 | Breadcrumb spacing, Sidebar item gap |
| SM | 8 | Kompakte vertikale/horizontale Schritte, viele `8,8` Panels |
| MD | 12 | Standard-Zeilengliederung, Nav-Padding, Form-Zwischenräume |
| LG | 16 | Karten-Padding, CC-Panel-Innenabstand |
| XL | 20 | Panel-Padding (`PANEL_PADDING`), Canvas-Content |
| 2XL | 24 | Section / Dialog-Innenabstand |
| 3XL | 32 | Dashboard / Chat-Conversation (Außenbereich) — **sparsam einsetzen** |

**Konflikt:** Vorkommen von **6px**, **10px**, **14px**, **28px**, **40px** im Code — diese **brechen** das 4px-Raster und sollten bei Migration auf nächste Stufe oder bewusste Ausnahme-Liste.

---

## 2. Control-Höhen

| Element | Beobachtete Werte | Quelle | Soll (ableiten) |
|---------|-------------------|--------|-----------------|
| **QComboBox / Standard-Input** | min-height **32px** | `base.qss` | **32px** = kanonisch |
| **Chat Prompt/Send** | **48px** fixed | `input_panel.py` | Ausnahme „große Primäraktion“ oder auf **36–40** harmonisieren |
| **Legacy Sidebar Search** | 40 / 34 / 44 | `legacy/sidebar_widget.py` | legacy — durch Token-Input ersetzen |
| **Workbench Explorer Tree** | min-height **26px** | `workbench.qss` | Auf **28 oder 32** mit Palette/Combo abstimmen |
| **Palette List Item** | min-height **32px** | `workbench.qss` | aligned mit Combo |
| **Node Library** | min-height **28px** | `workbench.qss` | zwischen Explorer und Palette — vereinheitlichen |

**Fazit:** Zwei Cluster: **26–28** (Workbench-Bäume) vs. **32** (Form-Controls). Empfehlung: **alles auf 32px Zeilenhöhe** außer explizit „compact tree“ 28.

---

## 3. Tab- und Toolbar-Höhen

| Element | Beobachtung | Soll |
|---------|-------------|------|
| **Workbench Tabs** | padding `sm`×`lg` + border → visuell ~34–36px | Ziel **34–36** dokumentieren |
| **Workbench Toolbar** | padding + 18px Icons | Nach Icon **20px** (siehe Design-Token-Defaults) ~**40–44** |

---

## 4. Header / Panel-Header

| Element | Werte | Ort |
|---------|-------|-----|
| PanelHeader / Chat-Header | margins **12,10,12,10** | `panel_header.py`, `chat_navigation_panel.py` |
| Workflow-Header | **12,8,12,8** | `workflow_header.py` |
| Context Action Bar | **8,6,8,6** | `context_action_bar.py` |

**Abgeleitete Regel:** „Chrome-Zeile standard“ = **12×10** horizontal×vertical padding; „kompakt“ = **12×8**; „ultrakompakt“ nur Workbench-Kontextleiste **8×6**.

---

## 5. Dialog-Minimalgrößen (Stichprobe)

| Dialog / Panel | min_width × min_height |
|----------------|-------------------------|
| Settings | 420 × 400 |
| Topic-Editor | 280 × — |
| Workflow Create | 420 × — |
| Schedule Edit | 520 × — |
| Collection | 320 × — |

**Raster:** Breiten oft **40px-Schritte** (280, 320, 400, 420, 480, 520) — gut; Höhen weniger standardisiert.

---

## 6. Sidebars und Docks (px)

| Zone | min | default / typisch | max |
|------|-----|-------------------|-----|
| Shell Nav | 180 | **240** | 320 (`shell/layout_constants.py`) |
| Shell Inspector | 200 | **280** | 400 |
| Bottom Panel | 120 | **200** | 400 |
| Domain Navs | 180 | — | 220 (mehrere `*_nav.py`) |
| Chat Nav | 260 | — | 340 |
| Chat/Knowledge rechte Details | 200 | — | 320 |

**Zwei Raster:** **180–220** (schmale Domain-Nav) vs. **240–340** (inhaltstragende linke Spalte).

---

## 7. Icon vs. Text

| Kontext | Icon (px) | Text (QSS) |
|---------|-----------|------------|
| TopBar actions | **18** | — |
| Workbench Toolbar | **18** (QSS) | `font_size_sm` |
| IconManager default | **24** | — |
| Chat send | **20** | `font_size_md` |

**Fazit:** Icon-Typografie-Verhältnis **inkonsistent**; Ziel **16/20/24**-Leiter aus Design-Token-Spec.

---

## 8. Chat-spezifische Sondergrößen

| Widget | Wert | Problem |
|--------|------|---------|
| `ConversationView` message column | **1200px** fix | Fenster <1200 → horizontales Scrollen; widerspricht „Workbench nutzt restlichen Platz“. |
| Message layout margins | **32 / 40** | Sehr luftig vs. `20` in `conversation_panel._content_layout`. |
| Bubble max width | **1160** (`chat_message_widget.py`) vs. **800** (`legacy/message_widget.py`) | Zwei Philosophien „breit“ vs. „lesbar schmal“. |

---

## Kanonisches Größenraster (Vorschlag)

1. **Zeilenhöhe Listen/Inputs:** **32px** (Default), **28px** nur für „dense explorer“.  
2. **Primär-CTA-Höhe:** max **40px** statt 48px, außer explizite Ausnahme.  
3. **Panel-Header-Padding:** **12h × 10v**; Abweichungen dokumentieren.  
4. **Äußere Content-Padding:** **20** (Workspace), **24** (Dialog/Section), **32** nur Dashboard/Marketing-Flächen.  
5. **Sidebar-Breiten:** zwei Klassen beibehalten — **narrow nav 200±20**, **wide column 280±60**.

---

*Regeln formalisieren:* [LAYOUT_SYSTEM_RULES.md](./LAYOUT_SYSTEM_RULES.md)
