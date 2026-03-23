# Layout & Spacing — Abschlussbericht (Audit)

**Projekt:** Linux Desktop Chat / Obsidian Core  
**Stack:** Python, PySide6, QSS, modulare Shell + Workbench  
**Ziel des Audits:** Strukturierte Bestandsaufnahme von Layout-, Spacing-, Sizing- und Dichte-Inkonsistenzen zur systematischen Beseitigung von visueller Unruhe und Bedienproblemen.

---

## 1. Wichtigste Erkenntnisse

1. **Zwei Konstanten-Welten:** `app/gui/shared/layout_constants.py` (Panel/Spacing-Helper) und `app/gui/shell/layout_constants.py` (Dock-Breiten) — Entwickler müssen beide kennen; keine automatische Konsistenz.  
2. **Kein durchgängiges äußeres Workspace-Padding:** eingebettete Screens setzen **8, 12, 16, 20, 24, 32px** ohne gemeinsame Host-Regel — beim Wechsel der Area springt die Kante.  
3. **Chat ist der stärkste Ausreißer:** fixe **1200px** Content-Breite, **48px** Buttons, **32/40** Margins und **28** Message-Spacing — kollidiert mit Mindestfenster **1000px** und mit dem Rest der App.  
4. **Control-Höhen:** QSS **32px** für Combos vs. **48px** fest in `input_panel.py` — QSS/Python-Konkurrenz.  
5. **Workbench-Listen:** **26 / 28 / 32px** Zeilenhöhen — drei Stufen ohne dokumentierte Semantik.  
6. **Formulare:** viele `QFormLayout`s ohne gemeinsame Label-Ausrichtung oder Zeilenabstand — **14px** in Settings-Dialog sticht heraus.  
7. **Header-Chrome:** drei Profile (**12×10**, **12×8**, **8×6**) ohne benannte Tokens — wirkt bei schnellem Wechsel subtil unruhig.  
8. **Dashboard** mit **32px** Außenrand ist deutlich luftiger als typische Operations-Panels (**8–16px**) — fühlt sich wie eigener Modus an.  
9. **QSS:** viele Werte tokenisiert, aber **6×12**, **4×8**, **2px** Margins weiterhin hardcoded in `shell.qss` / `workbench.qss`.  
10. **Legacy-Widgets** nutzen **15px** Spacing und andere Raster — weiterhin Risiko, wenn erreichbar.

*Detailnachweise:* [docs/design/LAYOUT_SPACING_INVENTORY.md](docs/design/LAYOUT_SPACING_INVENTORY.md)

---

## 2. Top 20 Inkonsistenzen (priorisiert)

| # | Thema | Fundstelle(n) |
|---|--------|----------------|
| 1 | Fixe Chat-Breite **1200px** | `conversation_view.py` |
| 2 | Composer-Container **1000px** fix | `chat_composer_widget.py` |
| 3 | Send/Prompt-Buttons **48px** vs. Standard **32px** | `input_panel.py` vs. `base.qss` |
| 4 | Message-Area margins **32/40** + spacing **28** | `conversation_view.py` |
| 5 | Dashboard margins **32** | `dashboard_screen.py` |
| 6 | Settings Dialog spacing **20** / Form **14** | `settings_dialog.py` |
| 7 | **10px** Workbench-Inspector inner vs. **12** Shell | `inspector_panel.py`, diverse Inspektoren |
| 8 | Explorer-Tree **26px** vs. Palette **32px** vs. Node **28px** | `workbench.qss` |
| 9 | Sidebar content **8,12,8,12** vs. Card **16** vs. Panel **20** | `sidebar.py`, CC-Panels, `layout_constants` |
| 10 | **14px** horizontal in `project_stats_panel` | KPI-Karte |
| 11 | **6px** vertikale Spacing in Meta-Blocks | `chat_details_panel.py`, `markdown_widgets.py` |
| 12 | **10px** root spacing (`empty_state.py`, `chat_navigation_panel`) | bricht 4px-Raster |
| 13 | Command Palette margins **20,20,20,16** | asymmetrisch |
| 14 | `models_panels.py` margin nur rechts **8** | asymmetrisch |
| 15 | Zwei `layout_constants`-Module | `shared/` vs. `shell/` |
| 16 | TopBar Icons **18px** vs. Workbench **18px** vs. IconManager default **24** | `top_bar.py`, `manager.py` |
| 17 | Bubble max **1160** vs. Legacy **800** | `chat_message_widget.py`, `legacy/message_widget.py` |
| 18 | Legacy **44/40/34** Mindesthöhen | `legacy/sidebar_widget.py` |
| 19 | Workspace Graph / Footer **0,0,0,12** | `workspace_graph.py` |
| 20 | Runtime-Nav eigene Typo/Dichte (QSS px) | `shell.qss` `#runtimeNavTitle` |

---

## 3. Top 10 ruhigste Bereiche (visuell konsistent im Code)

1. **Shell MainWindow central stack** — `0/0` Margins, klare Kette TopBar → Breadcrumb → Workspace.  
2. **Workbench MainWindow central column** — `0/0` + ContextBar + Tabs.  
3. **Breadcrumb Bar** — einheitlich spacing 4 + QSS Micro-Padding.  
4. **Domain-Navs (180–220)** — wiederholtes Muster Operations/CC/Runtime/QA.  
5. **Dock-Größen** — zentral in `shell/layout_constants.py`.  
6. **Canvas Base** — `24px` Workbench-Canvas-Rand, klar definiert.  
7. **Workflow-Listen/Editor (8px)** — dichtes aber konsistentes Raster.  
8. **Settings `#settingsPanel` QSS** — klare Karten-Hülle.  
9. **Bottom Panel Tabs QSS** — Pane nutzt `panel_padding`.  
10. **Chat Navigation Panel (12er Header)** — innerhalb Chat-Modul stabil.

---

## 4. Top 10 problematischste Bereiche

1. **Chat Conversation + Composer** (Breite, Höhe, Margins).  
2. **Dashboard Screen** (32px, große Grid-Gaps).  
3. **Settings Dialog** (24+20+14 Kombination).  
4. **Workbench Inspector** (10px inner + EmptyState 28 vertikal).  
5. **Control Center Workspaces** (24+16 Schichtung — sehr luftig).  
6. **Project Overview + Stats** (20 vs. 14 vs. 12 Mischung).  
7. **Markdown/HTML Rendering** — eigene px, nicht an App-Raster gebunden.  
8. **Legacy Chat/Sidebar** — abweichende Raster.  
9. **Knowledge Source Details** — asymmetrische Margins 16/20.  
10. **Agent Tasks Workspace** — partielle top-only Margins `0,8,0,0`.

---

## 5. Empfohlene Größen- und Spacing-Raster

- **4px-Basisraster**; vermeide **6, 10, 14, 28, 40** außer Allowlist.  
- **Äußere Content-Padding:** **20** (Standard-Workspace), **24** (Dialog), **32** nur Dashboard (oder auf 24 reduzieren).  
- **Karten innen:** **16**; **kompakt:** **12**; **dicht:** **8**.  
- **Control-Zeilenhöhe:** **32**; **Explorer optional 28**; **Chat-CTA max 40**.  
- **Header-Profile:** standard **12×10**, compact **12×8**, ultracompact **8×6** (benannt).  
- **Form:** Zeile **12**, Label-Gap **8**, optional Label min width **120**.  
- **Sidebar-Listen:** eine Strategie: entweder Layout-**spacing 4** oder QSS-Margin — nicht mischen.

*Formalisiert:* [docs/design/LAYOUT_SYSTEM_RULES.md](docs/design/LAYOUT_SYSTEM_RULES.md)

---

## 6. Prioritäten für Umsetzung

| Stufe | Inhalt |
|-------|--------|
| P0 | `design_metrics` + `layout_constants` zusammenführen; QSS 6×12/4×8 tokenisieren |
| P1 | Chat fixe Breiten entfernen; Button-Höhen harmonisieren |
| P2 | Inspector 10→12; Settings Dialog Spacing vereinheitlichen |
| P3 | Workbench Tree/Palette Zeilenhöhen auf 32 (oder dokumentierte 28-Klasse) |
| P4 | Dashboard 32→24; FormLayout-Policy |
| P5 | Legacy bereinigen oder isolieren |

*Schritt-für-Schritt:* [docs/design/LAYOUT_SPACING_MIGRATION_PLAN.md](docs/design/LAYOUT_SPACING_MIGRATION_PLAN.md)

---

## 7. Restrisiken / offene Fragen

1. **Zwei MainWindows:** Sollen Shell- und Workbench-Workspace-Padding **identisch** sein oder bewusst unterschiedlich (Produktentscheid)?  
2. **Chat:** Soll die Nachrichtenspalte **max-width** eher **720** (Lesbarkeit) oder **960** (Workbench-Canvas) sein?  
3. **Touch / hohe DPI:** engere Listen (2px spacing) können auf skalierten Displays zu klein wirken — ggf. Umgebungs-Flag später.  
4. **QFormLayout vs. Grid:** Migration kann RTL und lange Übersetzungen beeinflussen — Pilot auf Englisch/Deutsch testen.  
5. **Splitter-Größen:** kein Audit der initialen `setSizes` — könnte nach Padding-Anpassungen neu justiert werden müssen.

---

## Artefakt-Index

| Dokument |
|----------|
| [docs/design/LAYOUT_SPACING_INVENTORY.md](docs/design/LAYOUT_SPACING_INVENTORY.md) |
| [docs/design/COMPONENT_DENSITY_ANALYSIS.md](docs/design/COMPONENT_DENSITY_ANALYSIS.md) |
| [docs/design/SIZE_RHYTHM_AUDIT.md](docs/design/SIZE_RHYTHM_AUDIT.md) |
| [docs/design/VISUAL_GROUPING_AUDIT.md](docs/design/VISUAL_GROUPING_AUDIT.md) |
| [docs/design/ALIGNMENT_AUDIT.md](docs/design/ALIGNMENT_AUDIT.md) |
| [docs/design/WORKBENCH_LAYOUT_CONSISTENCY.md](docs/design/WORKBENCH_LAYOUT_CONSISTENCY.md) |
| [docs/design/LAYOUT_PROBLEM_CLASSES.md](docs/design/LAYOUT_PROBLEM_CLASSES.md) |
| [docs/design/LAYOUT_SYSTEM_RULES.md](docs/design/LAYOUT_SYSTEM_RULES.md) |
| [docs/design/LAYOUT_SPACING_MIGRATION_PLAN.md](docs/design/LAYOUT_SPACING_MIGRATION_PLAN.md) |

---

*Der Audit ist damit abnahmefähig: Inventar, Dichte, Raster, Workbench-Vergleich, Regelwerk und Migrationsplan liegen vor.*
