# GUI- und UX-Review — Linux Desktop Chat

**Datum:** 2026-03-22  
**Methode:** Struktur- und Code-Review (PySide6-Widgets, Navigations-Registry, Workbench); **keine** Live-Usability-Studie mit Nutzern — ergonomische Aussagen sind aus UI-Struktur und Texten abgeleitet.

---

## 1. Navigation

**Ist:** Sechs Hauptbereiche über `WorkspaceHost` + `NavigationSidebar`; Einträge aus `navigation_registry.py` (Sektionen PROJECT, WORKSPACE, SYSTEM, OBSERVABILITY, QUALITY, SETTINGS).

**Stärken:** Ein konsistenter Navigations-Einstieg; `nav_key` für Auswahl; Icons über Registry.

**Schwächen:**  
- **Sprachmix:** z. B. `"Conversations with local/cloud LLMs"` vs. deutschsprachige Sektionstitel (`sidebar.py` nutzt Registry-Titel).  
- **Zwei „Command Palettes“:** Shell nutzt `app/gui/navigation/command_palette.py` + `CommandPaletteDialog` aus `commands/palette.py`; Workbench nutzt englischsprachiges `workbench/command_palette/command_palette_dialog.py` („Run command“, „Search commands…“). Risiko: Nutzer verstehen nicht, welche Befehle wo gelten.

**Pflichtkorrekturen (MUSS):** Keine reine UX-Blockade identifiziert; **MUSS** aus Produktsicht eher: **Begriff und Sprache vereinheitlichen** (siehe Hauptaudit).

---

## 2. Workspace-Logik

**Operations:** Horizontaler Stack mit linker `OperationsNav` und `QStackedWidget` — klares Muster (`operations_screen.py`).

**Control Center / QA / Runtime / Settings:** Analog Screen + interne Workspaces (teilweise).

**Workbench (separat):** `MainWorkbench` mit Explorer + Tabs + Inspector (`workbench_controller.py`). **Nicht** der Standard-Start (`run_gui_shell.py` startet `ShellMainWindow`).

**Befund:** Die **semantische Arbeitsoberfläche** für Tagesgeschäft ist die **Shell**; Workbench wirkt wie **zweite Mental Map** — erhöhte kognitive Last für Power-User, die beide kennen.

---

## 3. Bedienbarkeit und Informationsarchitektur

**Kommandozentrale:** `DashboardScreen` mit Status-Karten — passt zu „Übersicht zuerst“ (`dashboard_screen.py`).

**Inspector (Shell):** Kontextabhängig pro Workspace (`setup_inspector` in Screens). **Positiv** für Chat/Operations.

**Inspector (Workbench):** Viele Inhalte explizit als **stub** oder **placeholder** beschriftet (`inspector_router.py`: „This placeholder will be replaced…“, „(stub)“).

**Medienbrüche:**  
- Hilfe: semantische Suche laut `help/README.md` mit **Chroma-Index** nötig — Setup-Schwelle.  
- CLI für Replay/Repro ohne gleichwertige GUI (`README.md` / `DEVELOPER_GUIDE.md`).

---

## 4. Panel- und Screen-Semantik

**Konsistent:** Operations-Workspaces folgen gemeinsamem Muster (Nav + Content).

**Asymmetrisch / untergewichtig:**  
- Workbench-Inspector-Karten beschreiben **Zukünftiges**, nicht aktuelle Steuerung.  
- `context_action_bar.py` Meldung „No active object — open a tab from the explorer or palette.“ — Englisch im sonst deutsch dominierten Kontext (**nicht belastbar**, ob dieser Pfad in der Shell aktiv genutzt wird — Code existiert).

---

## 5. Unnötige Wechsel / Klicks

**Hypothese (strukturell):** Wechsel zwischen **Settings** (Kontext) und **Operations → Chat** für Alltagsaufgaben — **normal** für Desktop-Apps; keine Evidenz für übermäßige Tiefe ohne Messung.

**Evidenz-basiert:** Zwei UI-Programme (Shell vs. Workbench) erzwingen **Medienbruch**, wenn Nutzer Workbench-Demos mit Produkt verwechseln.

---

## 6. Rückmeldung, Status, Schutz

**Positiv:** Streaming und Completion-Heuristiken sind im Backend und in Unit-Tests vertreten (`test_completion_*`, `test_chat_streaming.py`).

**Lücke (nicht belastbar im Detail):** Keine systematische Prüfung aller Buttons auf „tote Aktionen“ ohne manuelles Durchklicken; Code enthält **Stub**-Routen im Workbench (`StubFeatureCanvas` / `StubFeatureInspector` in `inspector_router.py`).

---

## 7. Redundante Wege

| Weg A | Weg B | Befund |
|-------|-------|--------|
| Operations → Workflows | Workbench → Workflow Builder / Explorer | Parallel, unterschiedliche Reife |
| Shell Command Palette | Workbench Command Palette | Unterschiedliche Implementierung & Sprache |
| Chat in Operations | ChatCanvas im Workbench | Legacy/Explorer-Pfad laut `explorer_items.py` |

---

## 8. Technisch statt produktorientiert

- Workbench-Inspector-Texte sind **implementierungsnah** („stub“, „orchestrator (stub)“) statt nutzerzentrierter Erklärung.  
- Nav-Tooltips teils **englische Fachbegriffe** ohne Lokalisierung.

---

## 9. Pflichtkorrekturen (UX/GUI)

1. **Klärung in Produkt-Doku:** Was ist Standard-Oberfläche, was Demo/Pilot (Workbench).  
2. **Einheitliche Sprache** für primäre Workflows (mindestens Palette + zentrale Tooltips).  
3. **Tests auf `ChatWorkspace`** — verhindert „grüne Suite, kaputte Haupt-UI“.

---

## 10. Verbesserungspotenzial (SOLLTE / KANN)

- Onboarding im Dashboard: Link/Hinweis auf **einen** empfohlenen Pfad (z. B. „Chat starten unter Operations“).  
- Hilfe: Ohne Chroma funktionierende **Basis-Suche** kennzeichnen.  
- Workbench: Entweder entfernen aus wahrgenommener „Produktfläche“ oder Inspector mit **echten** Daten füttern.

---

*Ende GUI/UX-Review.*
