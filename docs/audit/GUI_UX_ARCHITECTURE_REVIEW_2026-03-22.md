# GUI-/UX-Architekturreview — Linux Desktop Chat

**Datum:** 2026-03-22  
**Methode:** Code- und Strukturreview (PySide6-Shell, Domains, Navigation, Workspaces, Panels); **keine** Nutzerstudie.  
**Ergänzende Quelle:** `docs/audit/PROJECT_GUI_UX_REVIEW_2026-03-22.md`.

---

## Gesamtbewertung der GUI

**Note: B — gut, aber mit klaren Verbesserungsmöglichkeiten**

**Begründung:** Die **Shell** (`ShellMainWindow`) liefert eine **nachvollziehbare modulare Desktop-Struktur**: globale Sidebar nach Kontext-Sektionen, Domains mit **eigenem Sub-Nav-Muster** (Operations, Control Center, Runtime/Debug, QA, Settings), **Breadcrumbs**, **Inspector-Dock**, **TopBar** mit Projektwechsler und Schnellzugriffen. Das entspricht **heutigen Erwartungen an komplexe Desktop-Tools** (IDE-/Hub-Charakter), nicht an einen Ein-Fenster-Chat.

Gleichzeitig **schwächt** die Umsetzung das Produktversprechen „eine Arbeitsfläche“: **Sprach- und Kulturmix** (DE/EN in Navigation, QA, Settings, TopBar), **überlappende QA-Oberflächen** (Bereich „QA & Governance“ vs. Runtime **QA Cockpit** / **QA Observability**), **zwei Command-Palette-Konzepte** (Shell vs. Workbench), und **technische Labels** in Tooltips/Workbench. Das ist **kein Zustand E** (strukturell kaputt), aber **unterhalb** einer **Note A**.

---

## Stärken

| Bereich | Nachweis / Befund |
|---------|-------------------|
| **Zentrale Navigationswahrheit** | `app/core/navigation/navigation_registry.py` — eine Registry für Sidebar, Palette, Hilfe-Kontext |
| **Konsistentes Domain-Muster** | Operations/Control Center/Runtime/QA: linke Listen-Subnav + Hauptstack (`operations_nav.py`, `control_center_nav.py`, …) |
| **Chat als echter Workspace** | `ChatWorkspace`: Session-Explorer + Kontextleiste + Konversation + Eingabe + Details-Panel (`chat_workspace.py`) |
| **Settings als klassische Desktop-Settings** | Dreiteiler: Kategorien \| Inhalt \| Hilfe (`settings_workspace.py`) |
| **Globale Orientierung** | TopBar: Projekt, Status, Workspace Map, Befehle, Hilfe (`top_bar.py`) |
| **Kommandozentrale** | Dashboard mit Status-Karten (`dashboard_screen.py`) |

---

## Schwächen

1. **Zwei mentale Modelle:** Produkt-Shell vs. separater **Workbench** (`run_workbench_demo.py`) mit anderem Inspector — siehe `PROJECT_GUI_UX_REVIEW_2026-03-22.md`.  
2. **Inkonsistente Sprache:** Nav-Titel deutsch (Operations), Control-Center- und QA-Nav **englisch** (`control_center_nav.py`, `qa_governance_nav.py`), Registry-Tooltips **englisch** (`navigation_registry.py`), Settings-Hilfe-Titel **„Help“** (`settings_workspace.py` Zeilen 78–79).  
3. **Doppelte QA-Sichten:** „QA & Governance“-Screen und Runtime **QA Cockpit** / **QA Observability** mit ähnlich klingenden Beschreibungen in der Registry (`navigation_registry.py` Zeilen 144–147, 168–177).  
4. **Lange Runtime-Liste:** Neun Einträge in der Sidebar-Sektion OBSERVABILITY, teils eingeklappt — hohe **Scan-Last** (`navigation_registry.py` + `runtime_debug_nav.py` inkl. Markdown Demo / Theme Visualizer).  
5. **Technisch wirkende Texte:** Dashboard-Hinweis verweist auf **`docs/qa`-Artefakte** (`dashboard_screen.py` Zeilen 60–62) — **entwicklernah** für Endnutzer.  
6. **Workbench-Inspector** mit Stub-Sprache („stub“, englische Placeholder) — `inspector_router.py` (bereits im früheren Audit).

---

## UX-Probleme (gruppiert)

- **Kognitive Last:** Zu viele parallele „Qualitäts-/Monitoring“-Einstiege ohne klare Rollenbeschreibung in der UI.  
- **Discoverability:** Power-Features (Palette, Workspace Graph) gut in der TopBar, aber **Begriffsdoppelung** Shell-Palette vs. Workbench-Palette.  
- **Self-Explaining:** Mischung aus Produktbegriffen (Betrieb, Kommandozentrale) und Rohfachbegriffen (R4, DAG, EventBus) in Tooltips/Beschreibungen.

---

## Navigationsprobleme

- **Redundanz:** QA-Themen in **zwei Hauptbereichen** (QA & Governance, Runtime/Debug).  
- **Hierarchie:** SETTINGS und QUALITY als Sidebar-Sektionen — für Gelegenheitsnutzer wirkt „QUALITY“ wie ein zweiter Arbeitsmodus neben Operations.  
- **Sackgassen:** Keine harten toten Enden in der Registry ersichtlich; **Risiko** bei falscher Erwartung an Workbench-Inhalt (Stubs).

*(Detail: siehe `GUI_NAVIGATION_ANALYSIS_2026-03-22.md`.)*

---

## Strukturprobleme

- **Informationsarchitektur:** „Systemverwaltung“ (Control Center) vs. „Operations“ ist logisch, aber **Modellwahl** liegt oft zwischen **Chat-Kopf** und **Control Center** — Nutzer müssen **mentales Modell „wo lebt die Wahrheit?“** lernen.  
- **Arbeitsfläche:** Chat-Workspace ist stark; **kombinierte** Ansichten (z. B. Chat + Knowledge nebeneinander) sind **nicht** als Standard-Layout ersichtlich — typisch **Single-Stack** pro Area.

---

## Konkrete Verbesserungsvorschläge (ohne Implementierung)

1. **Sprachleitplan:** Eine Sprache für **alle** sichtbaren Nav- und Panel-Titel **oder** konsequente DE-UI mit **einem** englischen Fachglossar-Panel.  
2. **QA-Konsolidierung:** Nutzer-sichtbare **Erklärung** oder Zusammenführung von QA Governance vs. Runtime-QA-Panels (Rollen: „Release/Compliance“ vs. „Live-Diagnose“).  
3. **Dashboard-Copy:** Hinweis **ohne** `docs/`-Pfad; nutzerorientiert („Aktivität, Vorfälle, Systemstatus“).  
4. **Runtime-Nav:** Gruppierung (z. B. „Diagnose“ / „Monitoring“ / „Entwickler“) oder Ausblendung seltener Einträge unter „Erweitert“.  
5. **Workbench:** Produktseitig kennzeichnen oder aus dem **wahrgenommenen** Hauptpfad nehmen (Doku + ggf. kein paralleles „Palette“-Konzept ohne Erklärung).  
6. **Einheitliche Command Palette:** Ein Begriff, ein Verhalten, eine Sprache.

---

## Beantwortung: Wichtige Erkenntnisse (Auszug)

| Frage | Kurzantwort |
|-------|-------------|
| **Größte UX-Reibungsverluste?** | Sprachmix; doppelte QA-/Palette-Konzepte; technische Dashboard-/Tooltip-Sprache; Workbench-Erwartung vs. Stub. |
| **Panels zusammenlegen?** | **QA Cockpit** und **QA Observability** aus Nutzersicht prüfen (inhaltliche Doppelung laut Registry-Beschreibung naheliegend). |
| **Panels fehlen?** | Keine zentrale „**Heute weiterarbeiten**“-Ansicht außer Dashboard-Kacheln; kein **einheitliches** „Modell & Kontext“-Panel unabhängig vom Chat. |
| **Schlecht strukturierte Workspaces?** | **Runtime/Debug** (lange Liste, gemischte Zielgruppen inkl. Markdown-Demo). |
| **Stärker zentralisieren?** | **Modell/Provider-Status** und **Projektkontext** (teilweise TopBar + Chat-Bar + Settings — kohärente **eine** „Systemzeile“ erwägen). |
| **Unnötige Kontextwechsel?** | Kontext-Settings (Settings) vs. Chat (Operations); Modellpflege (Control Center) vs. Chat-Modellwahl. |
| **Übersichtsdashboards fehlen?** | Kommandozentrale existiert; **tiefe** Drilldowns in dieselben Daten wie Runtime/QA ohne **eine** geführte Story können Lücken lassen (subjektiv ohne Nutzertest). |
| **Fehlende echte Arbeitsfläche?** | Chat-Workspace **ist** eine; **plattformweit** fehlt ein durchgängiges „**ein Canvas, viele Widgets**“-Gefühl — eher **Area-Wechsel**. |

---

## Bewertung Teilaspekte

| Aspekt | Einschätzung |
|--------|----------------|
| Bedienbarkeit (erfahren) | Gut |
| Bedienbarkeit (neu) | Mittel (Fachbegriffe, viele Bereiche) |
| Informationsarchitektur | Mittel–gut |
| „Modern“ | Mittel (Qt-typisch solide, kein generischer Consumer-Chat-Look) |
| Produktorientiert vs. technisch | **Tendenz technisch** in Texten und Teilen von Runtime/QA |

---

*Ende Architekturreview.*
