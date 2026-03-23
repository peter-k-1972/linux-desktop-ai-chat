# GUI-Panelstruktur — Review Linux Desktop Chat

**Datum:** 2026-03-22  
**Methode:** Struktur aus Modulen unter `app/gui/domains/`, Layout in zentralen `*_workspace.py` / `*_screen.py`; Inspector-Dock; Settings-Layout.

---

## Panelübersicht (Shell-Hauptpfad)

### Globale Rahmen-Panels

| Element | Rolle | Datei (Referenz) |
|---------|--------|-------------------|
| **Navigation (Dock links)** | Sektionen + Einträge | `docking_config.py`, `sidebar.py` |
| **WorkspaceHost (Zentral)** | Stacked Screens pro Area | `workspace_host.py` |
| **Inspector (Dock rechts)** | Kontext je Screen/Workspace | `InspectorHost`, pro Workspace `setup_inspector` |
| **Bottom Panel** | Monitore / zusätzliche Ausgabe | `BottomPanelHost` |
| **TopBar** | Globalaktionen, Projekt | `top_bar.py` |

### Operations — Chat (`ChatWorkspace`)

| Panel | Position | Funktion |
|-------|----------|----------|
| `ChatNavigationPanel` | Links | Sessions |
| `ChatContextBar` | Oben Mitte | Projekt/Chat/Topic-Kontext |
| `ChatConversationPanel` | Mitte | Verlauf |
| `ChatInputPanel` | Unten Mitte | Eingabe, Modell/Rolle (Kopfzeilen-Logik im Panel-Kontext) |
| `ChatDetailsPanel` | Rechts im Workspace | Detailinfos / Metadaten |

**Bewertung:** Klares **Drei-Spalten-Fundament** (Sessions | Hauptarbeit | Details) mit **vertikaler** Unterteilung im Zentrum — **stark** für Fokusarbeit; Details-Spalte kann auf kleinen Displays **eng** wirken (kein responsives Urteil ohne Auflösungstest).

### Settings (`SettingsWorkspace`)

| Bereich | Inhalt |
|---------|--------|
| Links | Kategorien (`SettingsNavigation`) |
| Mitte | Kategorie-Widgets (`ApplicationCategory`, …) |
| Rechts | `SettingsHelpPanel` („Help“ + erklärender Text) |

**Bewertung:** **Standard-Desktop-Pattern**, gut verständlich; Titel **„Help“** englisch neben deutschsprachigem Fließtext — **inkonsistent**.

### Weitere Domains (Muster)

- **Operations** (ohne Chat): typisch **Subnav links + Inhalt** (Projekte, Knowledge, …).  
- **Control Center:** Subnav + Workspace-Stack.  
- **QA & Governance:** Subnav + Analyse-Panels (Gap, Coverage, … laut Paketstruktur).  
- **Runtime/Debug:** Subnav + spezifische Monitoring-Panels.

---

## Dialoge / Cards

- Kontextmenüs und Dialoge am Chat-Kontext (`project_switcher_dialog`, Kontextmenü Kontextleiste) — **fokussiert**.  
- **SectionCard** u. a. im Workbench-Inspector — Kartenlayout für erklärende Texte (`inspector_router.py`).

---

## Bewertung

### Logischer Schnitt

- **Gut:** Chat-Workspace, Settings, domain-typische **Nav | Content**.  
- **Mittel:** Runtime/Debug mischt **Entwicklerwerkzeuge** (Markdown Demo, Theme Visualizer) mit **Betriebsmonitoring** — **eine** Leiste, **verschiedene Zielgruppen**.

### Überladung

- **Potenziell überladen:** Lange **Runtime-Subnav**; QA-Governance-Workspaces mit **mehreren** Analyse-Panels untereinander (Scroll — aus Modulnamen/Gap-Workspace abgeleitet).  
- **Chat:** Funktional dicht, aber **fachlich berechtigt** (Chat-Produkt).

### Zu wenig Inhalt / Platzhalter

- **Workbench-Inspector:** überwiegend **Stub-/Zukunftstexte** (Audit).  
- **Empty States:** in vielen Panels bewusst (z. B. Platzhalter-QLabels) — **okay**, wenn copy **nutzerorientiert** ist.

### Redundanzen

- **Zwei QA-Cockpit-artige** Einträge in der **globalen** Navigationsliste (Runtime) **plus** QA-Screen — inhaltliche Überschneidung **wahrscheinlich** aus Nutzersicht.  
- **Models** in Control Center vs. Modellwahl im Chat — **fachlich** keine Redundanz, aber **kognitive** („wo stelle ich das Default ein?“).

---

## Fehlende Panels (aus Produktperspektive)

| Lücke | Begründung |
|-------|------------|
| **Einheitliches „Systemstatus“-Panel im Chat** | Status eher TopBar/Dashboard — im Chat-Flow **nicht** zentral gebündelt. |
| **Kombinierte Operations-Ansicht** | Kein Standard-„Split“ Chat + Knowledge **in einem** Workspace ohne Wechsel (nicht im Code als primäres Layout ersichtlich). |
| **Nutzerorientiertes Onboarding-Panel** | Dashboard erklärt eher **Datenquellen** als geführte Erstnutzung. |

---

## Verbesserungsvorschläge

1. **Runtime-Subnav:** Gruppen-Überschriften (QListWidget nicht nur flach) oder **zwei** virtuelle Tabs „Betrieb“ / „Entwicklung“.  
2. **Settings Help:** Titel **„Hilfe“** und einheitliche Sprache.  
3. **QA-Doppelungen:** Entscheidung, welches Panel **Primary** für „Testübersicht“ ist — zweites zurückstufen oder umbenennen.  
4. **Chat Details:** Auf kleinen Screens optional **einklappbar** / in Inspector auslagern (Konzept, kein Code).  
5. **Workbench:** Stubs durch **„Demo – nicht Produktiv“**-Banner ersetzen (Copy-Only).

---

*Ende Panelreview.*
