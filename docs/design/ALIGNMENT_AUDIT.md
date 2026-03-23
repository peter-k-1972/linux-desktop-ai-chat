# Alignment Audit

**Scope:** Horizontale/vertikale Ausrichtung, Einzüge, Icon↔Text, Header, Kanten mit Nachbarn, Chat/Markdown/Toolbars.

---

## 1. Labels und Formfelder

| Thema | Befund | Fundstellen |
|-------|--------|-------------|
| **QFormLayout Standard** | Viele Formulare ohne `setLabelAlignment(Qt.AlignRight)` oder feste Label-Spalte | `settings_dialog.py`, `projects_workspace.py`, `workflow_create_dialog.py`, `ai_models_settings_panel.py`, … |
| **Feste Label-Breiten** | Teilweise `setMinimumWidth(90)` / 180 für Combos | `model_settings_panel.py`, `chat_header_widget.py` |
| **Inkonsistenz** | Einige Dialoge linksbündige Labels, andere implizit — **Kanten der Eingabefelder springen** zwischen Screens | drift |

**Empfehlung:** Eine Policy: entweder **durchgängig QFormLayout mit AlignRight** + `fieldGrowthPolicy` oder **GridLayout** mit Spalte 0 = Labels (min width **96 oder 120px** Desktop).

---

## 2. Einzugstiefen

| Muster | Befund |
|--------|--------|
| **Nested Layouts mit 0-Margins** | Häufig `content_layout` 0 + Parent 12/16 — Einrückung nur über äußeren Container; **konsistent wenn dokumentiert**. |
| **Partielle rechte Einrückung** | `models_panels.py` `setContentsMargins(0, 0, 8, 0)` — nur rechts 8px; **asymmetrisch**, vermutlich Scrollbar-Korrektur — sollte kommentiert/tokenisiert sein. |

---

## 3. Icons zu Text

| Ort | Befund |
|-----|--------|
| **TopBar** | QAction mit 18px Icon, kein expliziter Text neben Icon — Ausrichtung Qt-Standard. |
| **Workbench Toolbar** | QToolButton padding `sm`×`md` + 18px icon — vertikal zentriert durch Qt. |
| **Nav-Sidebar** | Icons über `IconManager` in Liste — Abstand von Text abhängig von Item-Padding (QSS + Code). |
| **Risiko** | Unterschiedliche **Item-Padding** (Nav 12×16 vs. List 10×12 in `layout_constants`) → **optisch verschobene Icon-Baselines** zwischen Sidebars. |

---

## 4. Header-Ausrichtung

| Komponente | Muster |
|------------|--------|
| `PanelHeader` | Titel + Subtitle, `spacing 2` zwischen Textzeilen — linksbündig. |
| `chat_navigation_panel` header | Project row + actions — typisch `HBox` + `addStretch` für rechte Buttons — **konsistent**. |
| `command_center_view` | `header.addStretch` — rechte Actions — **konsistent**. |
| **Breadcrumb** | Einzeiler, spacing 4 — linksbündig unter TopBar — aligned mit Workspace. |

---

## 5. Linke/rechte Kanten

| Konflikt | Beschreibung |
|----------|--------------|
| **Shell Workspace vs. eingebettete Panels** | Workspace-Host oft 0-Margin; eingebettete Screens bringen 16/24 — **Kante des Workspace-Inhalts** springt zwischen Areas. |
| **Dock-Titel vs. Inhalt** | QSS Dock title padding `sm`×`md` (Workbench) vs. Inspector inner 10px — **Inhalt nicht bündig** mit Titel-Text-Rand. |
| **Splitterneighbor** | Keine globale `setHandleWidth` Policy sichtbar — Standard 6–8px — akzeptabel. |

---

## 6. Tabellen und Listen vs. Panel

| Thema | Befund |
|-------|--------|
| **Table in CC-Panel** | 16px Panel-Margin → Tabelle beginnt eingerückt — konsistent. |
| **Tree in Explorer** | `padding: xs 0` in QSS — **kein** symmetrischer horizontaler Einzug zur Dock-Kante — beabsichtigt randlos. |
| **Chat-Liste** | `0` content margins am list host — volle Breite der Nav-Spalte — ok. |

---

## 7. Chat-Bubbles und Markdown

| Thema | Befund |
|-------|--------|
| **Bubbles** | QSS `#messageBubble` margin `4px 0` — vertikaler Rhythmus; horizontale Ausrichtung durch Layout im Parent. |
| **ConversationView** | Zentrierung per `HBox` + Stretch — **symmetrisch**. |
| **Markdown** | Renderer setzt eigene `margin`/`padding` in HTML — **nicht** an Shell-Ränder gekoppelt — kann von Panel-Padding abweichen. |

---

## 8. Dialoge

| Thema | Befund |
|-------|--------|
| **Button-Leiste** | `settings_dialog.py` `btn_layout` margins `24,0,24,0` — Buttons bündig mit Form 24 — **gut**. |
| **Form vs. Buttons** | Wenn `main_layout` nur `0,0,0,12` unten — **Lücke** zwischen Form und Buttons variabel — prüfen pro Dialog. |

---

## Priorisierte Alignment-Fixes

1. **FormLayout-Policy** dokumentieren und auf Settings + häufige Operations-Dialoge anwenden.  
2. **Icon+Text-Listen:** einheitliche horizontale Item-Padding-Klasse (Nav = Content-Spalte).  
3. **Workbench Dock:** Inspector inner margin an Titel-Padding anbinden (10→12 oder Titel an 10).  
4. **Markdown:** Margin-Token aus `design_metrics` statt Magic Numbers.

---

*Workbench-Gesamtbild:* [WORKBENCH_LAYOUT_CONSISTENCY.md](./WORKBENCH_LAYOUT_CONSISTENCY.md)
