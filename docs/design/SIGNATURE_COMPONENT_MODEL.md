# Obsidian Core — Signature Component Model

**Zweck:** Semantische Familien der Shell-GUI mit Layer, Dichte und Interaktionsgewicht — Umsetzung erfolgt über bestehende Tokens und Governance ([UI_GOVERNANCE_RULES.md](./UI_GOVERNANCE_RULES.md)).  
**Bezug:** [SIGNATURE_SPATIAL_ARCHITECTURE.md](./SIGNATURE_SPATIAL_ARCHITECTURE.md)

---

## Legende

| Begriff | Bedeutung |
|---------|-----------|
| **Layer** | Siehe räumliches Modell (0–4). |
| **Dichte** | `compact` / `standard` / `comfortable` — Header-Profile und Zeilenhöhen ([LAYOUT_SYSTEM_RULES.md](./LAYOUT_SYSTEM_RULES.md)). |
| **Interaktionsgewicht** | `primary` / `secondary` / `chrome` / `passive` — wie stark die Komponente Aufmerksamkeit und Klicks zieht. |

---

## Top Bar

| Aspekt | Inhalt |
|--------|--------|
| **Semantische Rolle** | Globaler Kontext: App-Identität, **Projekt**, schnelle Querschnittsaktionen (Status, Karte, Befehle, Hilfe). |
| **Layer** | 0 (Chrome). |
| **Dichte** | `compact`; Höhe minimal, keine doppelten Toolbars. |
| **Interaktionsgewicht** | Aktionen `secondary` bis `primary` (z. B. Hilfe = secondary); App-Titel `passive`. |
| **Visueller Charakter** | Ruhig, eine Basislinie mit Icons; **eine** Arbeitssprache; Akzent nur für echte Primäraktion falls in TopBar (selten). |

---

## Primary Navigation (Sidebar)

| Aspekt | Inhalt |
|--------|--------|
| **Semantische Rolle** | Bereichswechsel: PROJECT → WORKSPACE → SYSTEM → OBSERVABILITY → QUALITY → SETTINGS. |
| **Layer** | 0 (Dock) mit Inhalten als **Listen auf Surface-1**. |
| **Dichte** | `standard` für Lesbarkeit; Sektionen einklappbar. |
| **Interaktionsgewicht** | `chrome`; aktiver Eintrag = `primary` Selection-Styling. |
| **Visueller Charakter** | Ikon + kurzer Titel; Tooltip = Beschreibung aus Registry, nicht Marketing. |

---

## Workspace Surface

| Aspekt | Inhalt |
|--------|--------|
| **Semantische Rolle** | Hauptinhalt des gewählten Bereichs; hostet Scroll und Split. |
| **Layer** | 1. |
| **Dichte** | Abhängig vom Screen; Kommandozentrale: `comfortable` oben (Hero), `standard` unten. |
| **Interaktionsgewicht** | Container `passive`; Kinder bestimmen Gewicht. |
| **Visueller Charakter** | Einheitlicher Hintergrund-Token; Breadcrumbs als dünne Orientierungszeile. |

---

## Dashboard Hero

| Aspekt | Inhalt |
|--------|--------|
| **Semantische Rolle** | Erste Antwort auf: „Wo stehe ich, und was ist wichtig?“ |
| **Layer** | 2 (Functional Panel der Klasse „hero“). |
| **Dichte** | `comfortable`; mehr Weißraum als Standard-Karten. |
| **Interaktionsgewicht** | `primary` für 1–2 CTAs (z. B. „Zu Chat“, „QA öffnen“); Rest `secondary`. |
| **Visueller Charakter** | Größere Typo-Stufe für KPI-Zeile; **kein** Vollflächen-Gradient; max. dezente Border. |

---

## Functional Card

| Aspekt | Inhalt |
|--------|--------|
| **Semantische Rolle** | Abgrenzbares Modul: Status, Liste, Formularblock. |
| **Layer** | 2. |
| **Dichte** | `standard`; Innenpadding Card-Stufe (16) oder Panel (20) je nach Rolle. |
| **Interaktionsgewicht** | Inhaltabhängig; Karte selbst `passive`, Buttons darin gewichtet. |
| **Visueller Charakter** | Einheitlicher Radius; Border-Token; Tabellen **in** der Karte visuell eingetaucht. |

---

## Inspector

| Aspekt | Inhalt |
|--------|--------|
| **Semantische Rolle** | Kontext zum selektierten Objekt; Details, Metadaten, Erklärung. |
| **Layer** | 3 (Focus Surface). |
| **Dichte** | `compact` bis `standard`; vermeidet Scroll-Wände ohne Struktur. |
| **Interaktionsgewicht** | Formulare `secondary`; reine Metadaten `passive`. |
| **Visueller Charakter** | Gleiche Familie wie Center-Cards, mit klarer Fokus-Linie bei Selection-Bezug. |

---

## Bottom Panel

| Aspekt | Inhalt |
|--------|--------|
| **Semantische Rolle** | Ergänzende Spur: Logs-Auszug, kurze Jobs, sekundäre Details — **nicht** Hauptarbeit. |
| **Layer** | 0 (Dock) / Inhalt 2. |
| **Dichte** | `compact`. |
| **Interaktionsgewicht** | `secondary`; ausblendbar. |
| **Visueller Charakter** | Zurückhaltend; keine konkurrierende Primärfarbe. |

---

## Dialog

| Aspekt | Inhalt |
|--------|--------|
| **Semantische Rolle** | Fokus auf eine Entscheidung oder ein Formular; modal oder schwebend. |
| **Layer** | 4. |
| **Dichte** | Dialog-Padding-Stufe (24); Form `standard`. |
| **Interaktionsgewicht** | Primäraktion im Footer klar; Abbrechen `secondary`. |
| **Visueller Charakter** | Backdrop dimmt; Inhalt klar begrenzt; keine ornamentalen Header-Grafiken. |

---

## Command Palette

| Aspekt | Inhalt |
|--------|--------|
| **Semantische Rolle** | Schnellnavigation und Befehle; Tastatur-first. |
| **Layer** | 4 (Overlay). |
| **Dichte** | `compact`; viele Einträge, kurze Zeilen. |
| **Interaktionsgewicht** | Auswahl = `primary`; Eingabefeld immer fokussiert beim Öffnen. |
| **Visueller Charakter** | Liste mit starker Lesbarkeit; Kategorien optisch getrennt (Spacing, nicht Regenbogen). |

---

## Empty State

| Aspekt | Inhalt |
|--------|--------|
| **Semantische Rolle** | Erklären, warum nichts da ist, und **was als Nächstes** sinnvoll ist. |
| **Layer** | 2 oder 3 (je nach Container). |
| **Dichte** | `comfortable` (kurz Text + eine Aktion). |
| **Interaktionsgewicht** | Eine `primary` oder `secondary` Aktion; kein leeres Panel ohne Text. |
| **Visueller Charakter** | Optional ein Icon aus dem kanonischen Set; keine Illustrations-Überladung. |

---

## Status Block

| Aspekt | Inhalt |
|--------|--------|
| **Semantische Rolle** | Kompakte Zustandsanzeige: OK / Warnung / Fehler / Lädt — in Karten, Inspector oder Hero. |
| **Layer** | 2–3. |
| **Dichte** | `compact`. |
| **Interaktionsgewicht** | `passive` bis `secondary` (z. B. „Details“-Link). |
| **Visueller Charakter** | Semantische Farbe aus Token; **kein** dekoratives Grün/Rot großflächig; Text immer dazu. |

---

*Ende SIGNATURE_COMPONENT_MODEL.md*
