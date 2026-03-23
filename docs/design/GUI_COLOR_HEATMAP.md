# GUI Color Heatmap

**Zweck:** Jede Komponentengruppe einer von drei **Farbintensitäts-Klassen** zuordnen — für Zielbild **90 % neutral / 7 % accent / 3 % semantic** (Flächen- und Aufmerksamkeitsgewicht, nicht Zeilen Code).

**Legende**

| Klasse | Bedeutung |
|--------|-----------|
| **N** | *Neutral only* — keine Marken-Accent-Fläche, keine Semantic-Farbe für Zustand |
| **A** | *Accent usage* — Fokus, aktive Navigation/Tabs, primäre CTA, Links, Auswahl, dünne Interaktionsränder |
| **S** | *Semantic usage* — Success / Warning / Error / Info für Status, Badges, Logs, Graph-Status |

---

## 1. Komponenten-Matrix

| Komponente / Gruppe | Klasse | Kurzbegründung |
|---------------------|--------|----------------|
| QMainWindow (Shell) | N | App-Hintergrund |
| Top Bar (Hintergrund) | N | Nav-Fläche |
| Top Bar Aktionen (Icons) | N | Standard-Iconfarbe |
| Project Switcher (Ruhezustand) | N | Neutrales Fill |
| Project Switcher (Hover/Focus) | A | Dünner Accent-Rand (shell.qss) |
| Breadcrumb Bar | N | Muted Surface |
| Breadcrumb Items (normal) | N | Primary text |
| Breadcrumb Item (hover) | A | Link-/Accent-Text |
| Main Nav Sidebar (Fläche) | N | `nav.bg` |
| Main Nav Item (selected) | A | Active bg/fg |
| Domain Nav — Operations / Settings (selected) | A | Wie Hauptnav |
| Domain Nav — Control Center (selected) | A | Accent-tinted (aktuell stärker — siehe Report) |
| Domain Nav — QA (selected) | A | QA-Nav-Tokens |
| Runtime Debug Nav (Fläche) | N | Monitoring-Surfaces = neutral Raum |
| Runtime Debug Nav (selected) | A | Monitoring accent pair |
| Workspace Host | N | `bg.app` |
| Workspace Titles | N | Typografie |
| Inspector Host (Fläche) | N | Muted bg |
| Inspector Texte | N | Secondary primary mix |
| Dock Chrome / Titles | N | Nav-ähnlich |
| Bottom Panel Host | N | Muted |
| Bottom Panel Content Pane | N | Surface |
| Bottom Panel Tab Bar | A | Active tab / indicator |
| Cards / basePanel / settingsPanel | N | Surface + Border |
| Empty State | N | Muted / transparent |
| QGroupBox | N | Titel primary/secondary |
| Default Buttons | N | Secondary button tokens |
| Primary CTA (z. B. Neuer Chat) | A | Accent fill |
| Inputs (Ruhe) | N | Input bg |
| Inputs (Fokus) | A | Focus border |
| QList/QTree (selection) | A | Selected row |
| QTable (body) | N | Zebra neutral |
| QTable (selection) | A | Selection |
| QTabWidget (active) | A | Tab active + indicator |
| Scrollbars | N | Transparent / subtle |
| Menus / Tooltips | N | Eigene neutrale Surfaces |
| Command Palette | A | Selection + Fokus dominant |
| Dialoge (Rahmen/Inhalt) | N | Surface |
| Dialog Primary Action | A | Ein CTA |
| Chat User Bubble | N | Chat-Rollenfarben ≠ globales Accent |
| Chat Assistant Bubble | N | idem |
| Chat System Bubble | S (optional) | System- semantisch oder neutral — sparsam |
| Markdown Fließtext | N | Body |
| Markdown Links | A | Link-Farbe |
| Markdown Code | N | Code-Farben (Syntax ≠ Accent-Heat) |
| Console / Log Stream | S | Zeilenweise semantic möglich |
| Badges (Status) | S | success/warn/error/info |
| KPI Cards (Zahlen) | N | Neutral |
| KPI Cards (Health) | S | Nur bei echtem Status |
| Workflow Graph (Knoten Standard) | N | Fill neutral |
| Workflow Graph (Knoten Status) | S | completed/failed/running/… |
| Workflow Graph (Selektion) | A | Selected border |
| Charts (Serien) | N* | *Serienfarben: neutral bunt oder datengetrieben; nicht überall Brand-Accent |
| Theme Visualizer | N/A | Dev-only |
| Legacy MainWindow / ChatWidget | N+A | Mischbetrieb bis Migration |

---

## 2. Zielverteilung vs. Ist-Einschätzung

| Klasse | **Ziel** (Aufmerksamkeit / Fläche) | **Ist (geschätzt)** |
|--------|-----------------------------------|---------------------|
| **N — Neutral** | **~90 %** | **~75–82 %** — viele Flächen sind bereits neutral; Abweichung vor allem durch mehrere Accent-Kanäle gleichzeitig (Nav + Tabs + CTA + Breadcrumb-Hover + CC-Selektion) |
| **A — Accent** | **~7 %** | **~12–18 %** — Shell + Chat-Nav + Tab-Leisten + Listen-Selektion summieren sich optisch |
| **S — Semantic** | **~3 %** | **~5–8 %** — Graph-Status, Badges, Logs können Semantic schnell anheben, wenn übernutzt |

*Die Ist-Werte sind **qualitativ** (Code- und QSS-Review), keine Pixelmessung.*

---

## 3. Maßnahmen zur Zielerreichung (90 / 7 / 3)

1. **Accent:** Control Center Nav-Selektion an **Haupt-Sidebar-Selektion** angleichen (weniger zusätzliche Accent-Fläche).  
2. **Accent:** Pro View **einen** klaren Primary-CTA; weitere Aktionen sekundär neutral.  
3. **Semantic:** Graph- und Badge-Farben **nur** bei aggregiertem Status, nicht pro Zwischenzustand.  
4. **Neutral:** Inspector, Dock-Innenflächen, Cards konsequent **ohne** Accent-Tint.

---

*Siehe [COLOR_SYSTEM_ANALYSIS_REPORT.md](./COLOR_SYSTEM_ANALYSIS_REPORT.md) für Details.*
