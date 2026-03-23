# Komponenten-Dichte-Analyse

**Skala:** `zu dicht` | `ausgewogen` | `zu luftig` | `inkonsistent`  
**Evidenz:** `LAYOUT_SPACING_INVENTORY.md`, QSS, repräsentative Layout-Dateien.

---

## Shell (Kommandozentrale)

| Bereich | Klassifikation | Begründung (Fundstellen) |
|---------|----------------|---------------------------|
| **Top Bar** | ausgewogen | QSS `spacing_md`/`spacing_lg` Padding; Icons 18px (`top_bar.py`) — kompakt aber lesbar. |
| **Sidebar (Hauptnav)** | ausgewogen | `8,12,8,12` Margins + List-Spacing 2–4px (`sidebar.py`) — dicht, für Nav akzeptabel. |
| **Breadcrumb Bar** | ausgewogen | QSS 4×8px Item-Padding; `bar.py` spacing 4 — flache zweite Zeile. |
| **Workspace Host** | inkonsistent | Viele Domains bringen eigene 16/24/32er Ränder mit; kein durchgängiger Host-Padding. |
| **Inspector Host** | ausgewogen | Shell-Inspektoren meist `12` Margins + `inspector_host.py` spacing 12. |
| **Bottom Panel** | ausgewogen | QSS Tab+Pane mit `panel_padding`; Dock min-height 200 (`layout_constants.py`). |

---

## Workbench

| Bereich | Klassifikation | Begründung |
|---------|----------------|------------|
| **Explorer** | ausgewogen | `0` Margins am Root; Tree QSS min-height 26px — kompakt. |
| **Canvas / Tabs** | ausgewogen | Tab-Padding `sm`×`lg`; keine übermäßigen Flächen. |
| **Inspector (Workbench)** | zu dicht / ausgewogen | `INSPECTOR_INNER_MARGIN_PX=10` (`inspector_panel.py`) **unter** üblichen 12/16 — wirkt enger als Shell-Inspector. |
| **Console** | ausgewogen | Legend `12,6,12,6` — kompakt Footer. |
| **Context Action Bar** | zu dicht | `8,6,8,6` — niedrigste vertikale Chrome-Zeile im Vergleich zu `panel_header` 10px vertikal. |
| **Command Palette** | ausgewogen | Root `20`×`20`×`20`×`16`, spacing 14 — leicht asymmetrisch, insgesamt ok. |

---

## Domänen-Workspaces (Auswahl)

| Bereich | Klassifikation | Begründung |
|---------|----------------|------------|
| **Control Center Workspaces** | zu luftig | Wrapper `24,24,24,24` + inner oft `16` + `setSpacing(16)` — stapelt großzügig. |
| **Operations — Chat** | inkonsistent | Composer `24/16` asymmetrisch; `ConversationView` **32/40** + fixe 1200px — extrem vs. Nav `12`. |
| **Operations — Chat Navigation** | ausgewogen | 12er Raster Header/Body; Filter-Row `0,4,0,4`. |
| **Operations — Projects** | inkonsistent | Overview `20` spacing/margins; List `12`; KPI `14/12` — drei Dichte-Stile. |
| **Operations — Prompt Studio** | ausgewogen | Splitter-basiert; viel `0` am Root, Editor `16` — nachvollziehbar. |
| **Operations — Workflows** | ausgewogen | Viele `8,8` Panels — dicht, editor-tauglich. |
| **Operations — Knowledge** | inkonsistent | Details `16,20,16,16` + Buttons mit harten px in Styles (siehe früheres Audit). |
| **Settings (eingebettet)** | ausgewogen | `16,20,16,16` + spacing 8 — konsistent mit „Einstellungen = etwas luftiger“. |
| **Settings Dialog** | zu luftig | `24` Margins, Form spacing `14`, äußeres spacing `20` — für kleines Fenster viel Weißraum. |
| **Dashboard** | zu luftig | `32` äußerer Rand, grid spacing `20`/`24` — wirkt wie „Marketing-Grid“. |
| **QA / Runtime Screens** | ausgewogen | Folgen CC-Pattern `spacing 16`; Monitoring-Farbraum separat, Dichte ähnlich Ops. |
| **Legacy Widgets** | inkonsistent | `sidebar_widget` spacing 15, `project_chat_list` 24 margins — bricht 4px-Raster. |

---

## Formulare, Listen, Tabellen

| Bereich | Klassifikation | Begründung |
|---------|----------------|------------|
| **Formlayouts (global)** | inkonsistent | Viele `QFormLayout` ohne einheitliche Label-Breite/horizontal spacing. |
| **Tabellen (CC)** | ausgewogen | CC-Panels setzen oft `16` Padding + volle Höhe — Standard-Arbeitsdichte. |
| **Chat-Liste / kleine Zeilen** | zu dicht | `spacing(2)` in Listen — gut für Dichte, riskant für Touch (Desktop ok). |

---

## Kurzfazit

- **Ruhig/kompakt** sind Workbench-Explorer, Workflow-Panels, Breadcrumb und Nav-Sidebar.  
- **Unruhe** entsteht vor allem durch **wechselnde äußere Ränder (8/12/16/24/32)** und **Chat-Conversation (1200px + 32/40)**.  
- **Workbench-Inspector** mit **10px** Innenrand wirkt gegenüber **12/16**-Shell schärfer — subtile Inkonsistenz.

---

*Weiter:* [WORKBENCH_LAYOUT_CONSISTENCY.md](./WORKBENCH_LAYOUT_CONSISTENCY.md), [LAYOUT_PROBLEM_CLASSES.md](./LAYOUT_PROBLEM_CLASSES.md).
