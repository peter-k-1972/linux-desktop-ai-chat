# Obsidian Core — Signature Spatial Architecture

**Zweck:** Räumliches Schichtenmodell für Desktop-GUI (Qt/PySide6-Shell): Vorder-/Mittel-/Hintergrundlogik ohne pseudo-3D-Kitsch.  
**Bezug:** [SIGNATURE_GUI_PRINCIPLES.md](./SIGNATURE_GUI_PRINCIPLES.md), [SIGNATURE_COMPONENT_MODEL.md](./SIGNATURE_COMPONENT_MODEL.md)

---

## Schichtenüberblick

| Layer | Name | Kurzrolle |
|-------|------|-----------|
| **0** | App Canvas | Fenster, Dock-Bereiche, globales Licht (Theme) |
| **1** | Workspace Surface | Hauptarbeitsfläche pro Nav-Area |
| **2** | Functional Panels | Karten, Listen, Formulare, Editor-Container innerhalb des Workspace |
| **3** | Focus Surfaces | Inspector, kontextuelle Seitenleisten, selektierte Zeilen/Details |
| **4** | Overlay / Modal | Palette, Dialoge, Drawer, kritische Bestätigungen |

**Regel:** Je höher die Layer-Nummer, desto näher am Nutzer in der **Fokus- und Eingabehierarchie** — nicht unbedingt „physisch“ über allem (Qt-Docks können Layer 3 sein, bleiben aber fokusal).

---

## Layer 0 — App Canvas

| Aspekt | Inhalt |
|--------|--------|
| **Zweck** | Träger der gesamten Shell: Fensterrahmen, Menü-/Tool-Bar-Zone, Dock-Container, zentrale Workbench-Fläche. |
| **Typische Komponenten** | `ShellMainWindow`, `TopBar`, Dock-Widgets (Navigation, Inspector, Bottom), zentrales `WorkspaceHost`. |
| **Visuelle Rolle** | Niedrigster Kontrast zum Inhalt; Trennlinien und Flächen folgen **Background / Surface-0** aus dem Theme. |
| **Material-/Surface-Regel** | Keine „Karten“ auf Canvas-Ebene; höchstens eine dezente Trennung Dock↔Center (1px Border-Token oder kontrastarme Fläche). |
| **Interaktionsregeln** | Drag nur wo explizit (Splitter, Dock-Titel); Canvas selbst keine verspielten Hover-Effekte. |

---

## Layer 1 — Workspace Surface

| Aspekt | Inhalt |
|--------|--------|
| **Zweck** | Einheitliche „Bühne“ für den aktiven Bereich (Kommandozentrale, Operations, Control Center, …). Scroll- und Split-Logik leben hier. |
| **Typische Komponenten** | `DashboardScreen`, `OperationsScreen` + interner Stack, `SettingsWorkspace`, Breadcrumb-Zeile **oberhalb** oder **in** der Surface (IA-Entscheid: konsistent halten). |
| **Visuelle Rolle** | **Surface-1**: klar vom Canvas abgegrenzt, aber ruhiger als einzelne Karten. |
| **Material-/Surface-Regel** | Ein Hintergrund-Token pro Theme-Modus; keine Vollflächen-Gradienten. |
| **Interaktionsregeln** | Primäre Navigation wechselt die gesamte Surface; Übergänge optional subtil (Fade), keine Screen-Slide-Comedy. |

---

## Layer 2 — Functional Panels

| Aspekt | Inhalt |
|--------|--------|
| **Zweck** | Inhaltliche Module: Datenlisten, Formulare, Dashboard-Karten, Management-Panels. |
| **Typische Komponenten** | `Functional Card`, Tabellen, `section_card`, Control-Center-Frames, Chat-Bereiche, Workflow-Canvas-Container. |
| **Visuelle Rolle** | **Surface-2** (erhabenere Fläche): definierter Radius, Border- oder Schatten-Token **minimal** (Governance: kein schwerer Drop-Shadow). |
| **Material-/Surface-Regel** | Karten teilen eine Familie: gleicher Radius, gleiche Innenabstände (Panel 20 / Card 16). Tabellen **in** Karten: eingetaucht (Surface-2a: leicht abgesenkter Fill). |
| **Interaktionsregeln** | Klick führt zu Auswahl, Navigation oder Öffnen von Layer 3/4; sekundäre Aktionen nicht gleich stark wie Primäraktion (Button-Hierarchie). |

---

## Layer 3 — Focus Surfaces

| Aspekt | Inhalt |
|--------|--------|
| **Zweck** | Kontext zum jeweiligen Workspace: Details, Metadaten, „Was bedeutet das?“, ohne den Hauptfokus zu ersetzen. |
| **Typische Komponenten** | `InspectorHost`, kontextuelle Property-Panels, ausgewählte Zeile mit stärkerem Hintergrund, Inline-Editor mit Fokus-Ring. |
| **Visuelle Rolle** | **Surface-3** oder **Accent-Outline** nur für Fokus; Inspector visuell von Layer-2-Karten trennbar, aber **gleiche Designfamilie** (kein anderes „Designsystem“). |
| **Material-/Surface-Regel** | Fokus = Border- oder Ring-Token, nicht Glow. Selektion in Listen: semantische Selection-Background-Farbe. |
| **Interaktionsregeln** | Inspector aktualisiert bei Selection-Wechsel mit kurzem, ruhigen Übergang; leerer Inspector zeigt **ehrlichen** Empty State (Prinzip Semantic Honesty). |

---

## Layer 4 — Overlay / Modal

| Aspekt | Inhalt |
|--------|--------|
| **Zweck** | Kurzzeitige, fokuszwingende oder schnelle parallele Arbeit: Befehle suchen, Einstellungen modal, Bestätigungen, kritische Formulare. |
| **Typische Komponenten** | Command Palette, `SettingsDialog`, `HelpWindow`, `QMessageBox`, Theme-Visualizer-Fenster (Dev). |
| **Visuelle Rolle** | Modales Dimming (Backdrop-Token); Overlay-Inhalt auf **Surface-4** (hellster / kontrastreichster Lesekörper im Stack). |
| **Material-/Surface-Regel** | Einheitliche Dialog-Padding-Stufe (z. B. 24); abgerundete Ecken aus Token-Satz; Schatten nur wenn Theme „elevation“ definiert — sparsam. |
| **Interaktionsregeln** | Escape schließt; Fokus-Trap in modalen Dialogen; Palette: Tastatur-first; keine Animation > 300 ms für Öffnen. |

---

## Querbezug Qt → Layer

| Qt-Konstrukt | Empfohlene Layer-Zuordnung |
|--------------|----------------------------|
| `QMainWindow` + Zentralwidget | 0 + 1 |
| `QDockWidget` (Nav, Inspector, Bottom) | 0 (Chrome) + Inhalt 2/3 je nach Rolle |
| `QStackedWidget` (Workspace) | 1 Inhalt |
| `QFrame` / Cards im Center | 2 |
| `QDialog` / nicht-modale Toolfenster | 4 |

---

*Ende SIGNATURE_SPATIAL_ARCHITECTURE.md*
