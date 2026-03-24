# QML Foundation Design System

**Linux Desktop Chat — Qt Quick / QML**  
**Status:** verbindliche Foundation-Definition (kein Feature-Code)  
**Bezug:** ergänzt `QML_GUI_TARGET_ARCHITECTURE.md`, Slice-0/1-Planung, Domänen-Layout-Map  

---

## 1. DESIGN SYSTEM PRINCIPLES

Diese Prinzipien sind **Prüfkriterien** für Reviews und Iterationen.

| Prinzip | Bedeutung | Prüffrage |
|--------|-----------|-----------|
| **Semantisch statt dekorativ** | Farbe, Fläche, Typo und Abstand tragen **Bedeutung** (Hierarchie, Zustand, Raum), nicht Stimmungsbilder. | Entfernt man das Element — bleibt die Bedeutung erkennbar? |
| **Ruhig statt laut** | Wenige gleichzeitige visuelle Akzente; keine konkurrierenden Primärflächen. | Gibt es mehr als eine „Hauptgeschichte“ pro Blickfeld? |
| **Räumlich statt kachelhaft** | Tiefe und Flächenhierarchie modellieren **Raum** (Zimmer, Tisch, Blatt), nicht Dashboard-Kacheln. | Wirkt es wie ein Arbeitsraum mit klarem Vorder-/Hintergrund? |
| **Lesbar statt effektverliebt** | Leseflächen haben Vorrang vor Dekor, Verläufen und Spielerei. | Ist Fließtext bei Standard-Schriftgröße dauerhaft gut lesbar? |
| **Funktionale Bibliotheksatmosphäre** | Metapher: konzentrierte Lese- und Schreibarbeit, **nicht** Historienkostüm oder Ornament. | Unterstützt die Gestaltung Fokus und Orientierung — nicht „Theater“? |
| **Konsistenz vor Einzelgag** | Wiederholbare Muster schlagen einmalige UI-Experimente. | Gibt es eine bekannte Token-Rolle für diesen Zweck? |
| **Desktop-Werkzeug** | Maus, Tastatur, variable Fenstergröße; keine Mobile-First-Ästhetik (keine übergroßen Touch-Ziele als Default). | Sind Interaktionsziele für Desktop angemessen und dicht nutzbar? |

**Explizit nicht Ziel:** Verspieltheit, Neon, „Enterprise Plastic“, historisierender Kitsch, generische App-Brand-Flächen.

---

## 2. TOKEN ARCHITECTURE

### 2.1 Drei Ebenen (verbindlich)

1. **Primitive Tokens**  
   Rohwerte ohne UI-Bedeutung: numerische Stufen, Rohfarben (Palette), Roh-Dauern.  
   **Nur** in Theme-/Manifest-Schicht und in der Kette „Primitive → Semantic“ erlaubt.

2. **Semantic Tokens**  
   Bedeutung in der Anwendung: `color.text.primary`, `surface.work`, `space.section`, `elevation.overlay`, `motion.duration.medium`.  
   **Domänen-QML und wiederverwendbare Controls** konsumieren **ausschließlich** semantische Tokens (oder darauf abbildbare Theme-Properties).

3. **Component Tokens (optional, gebündelt)**  
   Benannte Gruppen semantischer Tokens für wiederkehrende Bausteine: z. B. `component.sessionShelf`, `component.readingTable`, `component.contextSurface`.  
   Sie sind **keine zweite Farbpalette**, sondern Aliase/Overrides auf derselben semantischen Schicht, um lokale Kohärenz zu wahren.

### 2.2 Was universell vs. semantisch vs. komponentenspezifisch ist

| Ebene | Beispiele | Regel |
|-------|-----------|--------|
| Universell (semantisch, app-weit) | Textrollen, Basis-Abstände, Elevation-Stufen, Motion-Dauerfamilien | Jede neue Domäne muss diese nutzen können. |
| Semantisch, bereichsbezogen | `surface.paper`, `reading.columnMaxWidth` | Bedeutung aus Produkt/IA; trotzdem über Theme, nicht hardcoded in Einzeldateien. |
| Komponentenspezifisch | Shelf-Innenabstand, Composer Mindesthöhe | Nur als **gebündelte** component tokens oder als dokumentierte Ausnahme mit Begründung. |

### 2.3 Missbrauch, der verboten ist

- **Keine** freien Hex-/RGB-Literale in Domänenkomponenten.  
- **Keine** „Mikro-Tokens“ pro Widget (z. B. `marginLeftSpecialCase7`) ohne Wiederverwendung und Review.  
- **Keine** Vermischung von Primitive und Semantic in derselben Property-API nach außen (Komponenten exportieren keine Rohpalette).  
- Semantic Tokens **nicht** als Ersatz für Layoutlogik missbrauchen (kein „Token für alles“).

**Entscheidung:** Strikte Trennung **Primitive (Theme-Quelle) → Semantic (QML-API)**. Das ist für Qt Quick wartbarer als unbegrenzte flache Token-Listen und erzwingt spätere Theming-/Dark-Light-Erweiterungen ohne Refaktor aller Screens.

---

## 3. COLOR SYSTEM

### 3.1 Semantische Farbrollen (verbindlich)

Jede Rolle: **Bedeutung**, **Einsatz**, **Kontrastrolle**, **Verbote**.

| Rolle | Bedeutung | Typischer Einsatz | Kontrastrolle | Nicht verwenden für |
|-------|-----------|-------------------|---------------|---------------------|
| **app.background** | tiefster architektonischer Grund; „Raumhülle“ | Fenster-/Stage-Hintergrund hinter allem | dunkelster oder hellster Anker je Variante | große Textmengen, interaktive Flächen allein |
| **room.background** | ambienter Bereich unterhalb von Chrome/Stage; leichte Differenz zu app | Arbeitsbereich hinter Panels, dezente Zonen | mittlere Ebene zwischen app und surfaces | Primär-Text direkt darauf ohne geprüften Kontrast |
| **surface.work** | aktive, neutrale Arbeitsfläche (Tisch) | Eingaben, Listen-Hintergrund in Arbeitszone | mittel; trägt oft Primärtext | reine Dekoration, Statusflächen |
| **surface.paper** | hell, papierartig; **Lesefläche** | Reading Table, lange Texte, Manuskript | hellste sinnvolle Lesefläche; maximaler Textkontrast | globale Fensterfüllung ohne Räumlichkeit |
| **surface.panel** | seitliche/stützende Fläche; ruhiger als paper | Navigation, Regale, Nebenpanels | etwas dunkler/gedämpfter als paper | Flächendominanz im Zentrum |
| **surface.overlay** | modale/überlagernde Schicht | Dialoge, Popover, Dim | abgesetzt durch Hell/Dunkel **oder** Elevation-Regeln | Dauerhaft sichtbare Haupt-UI |
| **text.primary** | Hauptlesetext | Fließtext, wichtige Labels | höchste Lesepriorität vs. surface.paper/work | dezente Metadaten (zu dominant) |
| **text.secondary** | untergeordnete Information | Untertitel, Spaltenköpfe, sekundäre Labels | klar lesbar, schwächer als primary | lange Absätze in kleiner Größe ohne Prüfung |
| **text.muted** | Randnotizen, Hilfstext | Captions, Platzhalter, Timestamps | nur für kurze Texte oder größere Größe | kritische Fehlermeldungen allein |
| **accent.primary** | Messing / gedämpftes Gold — **ein** Hauptsakzent | Fokus-Ring (optional), primäre CTAs, aktive Nav-Indikatoren | sparsam; hoher Kontrast nur wo erlaubt | Flächenfüllungen großflächig |
| **accent.secondary** | Petrol / entsättigtes Tintenblau | sekundäre Hervorhebungen, Info, ruhige Links | untergeordnet zu accent.primary | zweiter gleichwertiger Primärakzent |
| **focus.ring** | Tastaturfokus, Sichtbarkeit | Fokusrahmen Controls | muss unabhängig von Hover erkennbar sein | Status „alles ok“ ohne Kontext |
| **selection.bg** / **selection.text** | ausgewählte Listeneinträge, Markierungen | Listen, Tabellen | ausreichender Kontrast innerhalb surface.panel/work | beliebige Hintergründe ohne Leseprüfung |
| **state.success** | erfolgreicher Abschluss | Toasts, Badges, Inline-Hinweise | nicht nur Farbe (siehe Kap. 10) | große Flächen |
| **state.warning** | Aufmerksamkeit, kein sofortiger Schaden | Banner, Validierung | — | permanente UI-Farbe |
| **state.danger** | Fehler, zerstörerische Aktionen | Fehlertext, destructive buttons | — | Dekoration |
| **state.info** | neutrale Information | Hinweise, Hilfe | — | Alarm |
| **border.subtle** | Trennung ohne harte Kante | Panel-Umrandung, Raster | schwach sichtbar | starke Inhaltsgliederung allein |
| **border.strong** | bewusste Grenze | Fokus-Nachbar, editierbare Felder | sichtbar, aber nicht schwarz hart | überall |
| **divider.soft** | horizontale/vertikale Trennung | Listen, Sektionen | minimal luminanzsprung | Karten-„Box“-Ersatz |

### 3.2 Richtung Anthrazit / Rauchbraun / Papier / Akzent

- **Dunkle Schichten** (app, room, panel): warmes Anthrazit/Rauchbraun, **entsättigt**, keine kühlen Pure-Grays als Default.  
- **Helle Schichten** (paper, work): warmes Elfenbein/hellgrau, **matte** Wirkung (kein Glanz).  
- **Akzente**: Messing-Gold und Petrol **sparsam**; sie signalisieren Interaktion oder Hierarchie, nicht „Brand-Wände“.  

### 3.3 Optionale Primitivebene

Primitive Namen (Beispiel): `palette.ink.dark`, `palette.paper.light`, `palette.accent.gold.muted`, `palette.accent.petrol.muted`.  
**Mapping** erfolgt im Theme (eine Zeile pro semantischer Rolle). **Domänen** referenzieren nur semantische Rollen.

---

## 4. SURFACE SYSTEM

Surfaces tragen die **räumliche Hierarchie**. Reihenfolge von hinten nach vorn (konzeptionell):

| Surface-Rolle | Visuelle Rolle | Typische Inhalte | Material / Helligkeit | Tiefe / Abgrenzung |
|---------------|----------------|-------------------|------------------------|---------------------|
| **architectural background** | äußerster Raum | Fenstergrund | tief, ruhig | keine Inhalte mit hoher Detaildichte |
| **ambient layer** | weicher Zwischenraum | Stage-Margins, große Zonen | etwas heller/dunkler als architectural | kaum Border; Luminanzsprung |
| **work table surface** | neutraler Tisch | Composer-umgebende Zone, Werkzeugflächen | mittlere Helligkeit | leichte Kante oder nur Abstand |
| **paper reading surface** | Manuskript | Chat-Reading-Table, lange Inhalte | hell, papierartig | dezente Kante optional; **kein** starker Schattenzwang |
| **side surface** | Regal / Seitenstütze | Session-Shelf, Nav | gedämpft vs. Zentrum | subtile Trennung zum Zentrum |
| **overlay surface** | schwebende Ebene | Modals, Menüs | klar abgehoben | Elevation + ggf. scrim |
| **drawer surface** | seitlich einschiebbar | Inspector, sekundäre Kontexte | wie panel oder leicht erhöht | Bewegung + Schatten/Scrim nach System |
| **highlight surface** | kurzfristige Betonung | Drag-Ziel, Drop, kurzer Hinweis | minimal erhöhte Luminanz oder dezenter Rand | kurzlebig |
| **selected surface** | Auswahlzustand in Listen | aktive Session, aktiver Nav-Eintrag | über `selection.*` tokenisiert | nicht mit accent.primary flächenfüllend gleichsetzen |

**Regel:** Zentrale Lesezone (paper) darf **nicht** durch panel-ähnliche Flächen „zugeschnitten“ wirken; Seitenflächen bleiben **untergeordnet**.

---

## 5. TYPOGRAPHY SYSTEM

### 5.1 Rollen

| Rolle | Verwendung | Relative Größe | Gewicht |
|-------|------------|----------------|---------|
| **app.title** | Fenster-/App-Name (sparsam) | größte, selten | regular oder medium |
| **domain.title** | Workspace- oder Domänenkopf | groß | medium |
| **section.title** | Gruppenüberschriften in Panels | mittel-groß | medium |
| **panel.title** | Karten-/Panel-Kopf | mittel | medium |
| **body** | Fließtext, Chat-Inhalt (Lesetisch) | Basis (Referenz) | regular |
| **compact.body** | dichtere Listen, sekundäre Inhalte | −1 Stufe vs. body | regular |
| **label** | Form- und Listen-Labels | −1 bis gleich body | regular |
| **caption** | Metadaten, Timestamps, Randnotizen | klein | regular |
| **monospace.technical** | IDs, Pfade, Logs (nur wenn nötig) | gleich compact oder caption | regular |

**Max. Betonungsstufen pro Blickfeld:** 3 (z. B. section.title + body + caption). Keine zusätzliche „Marketing-Bold“-Ebene.

### 5.2 Regeln

- **Groß-/Kleinschreibung:** UI-Strings Satzschreibung bevorzugt; **KEIN** durchgehendes ALL-CAPS außer kurze Akronyme.  
- **Zeilenhöhe:** body großzügig (ruhige Lesbarkeit); captions etwas straffer, aber nicht gedrängt.  
- **Breite:** lange Textzeilen begrenzen (siehe Kap. 6); keine Vollbreite-Romane auf großen Monitoren.  
- **Vermeiden:** verspielte Display-Fonts, starke Größen-Sprünge, mehr als ein optionaler Akzent in der Typo.

---

## 6. SPACING / SIZE / GRID SYSTEM

### 6.1 Basiseinheit

**Base unit `u` = 4 px** (oder 4 dp-Äquivalent bei gerasterter Skalierung). Alle Abstände sind **Vielfache von `u`**, vorzugsweise aus einer **begrenzten Skala**.

### 6.2 Spacing-Skala (semantisch)

| Token | Vielfaches | Verwendung |
|-------|------------|------------|
| `space.xs` | 1×u | Icon-Text-Abstand, enge Gruppen |
| `space.sm` | 2×u | Standard-Innenabstand kleiner Controls |
| `space.md` | 4×u | Panel-Padding, Stack-Abstand |
| `space.lg` | 6×u | Sektionsabstand innerhalb Screen |
| `space.xl` | 8×u | große Trennung, Stage-Atemzug |

**section.spacing** = bevorzugt `space.lg` oder `space.xl` zwischen logischen Blöcken (nicht `space.sm` „alles zusammenkleben“).

### 6.3 Raster und Proportionen

- **Stage margins:** `space.lg`–`space.xl` vom Fensterrand (semantisch `layout.stageMargin`).  
- **Min/Max Contentbreiten:** Reading Table und ähnliche Lesespalten haben **max. Zeilenlänge** (semantisch `reading.columnMaxWidth`); Zentrierung oder Einrückung im verbleibenden Raum.  
- **Sidebar / Shelf:** bevorzugte Bandbreite z. B. 220–280 px (als semantic range tokenisiert, nicht pro Datei neu erfinden).  
- **Context surface:** schmaler als Reading Table; Zielband z. B. 192–240 px.  
- **Composer:** Mindesthöhe für mehrzeiliges Schreiben; Wachstum mit Deckel; **kein** permanentes Vollbild-Eingabefeld als Default.  
- **Standard-Zeilenhöhe Listen:** einheitlich über `size.listRowMinHeight` (semantisch), nicht beliebig pro Liste.

### 6.4 Ausnahmen

Ausnahmen nur mit **Kommentar + Verweis** auf Issue/ADR oder component token bundle. Max. ±1 Stufe der Skala; sonst Skala erweitern (Review).

---

## 7. RADIUS / BORDER / DIVIDER SYSTEM

### 7.1 Radien

| Token | Typische Verwendung |
|-------|---------------------|
| `radius.none` (0) | volle Kanten an architektonischen Kanten, manche splitter |
| `radius.sm` | kleine Controls, Chips, enge Elemente |
| `radius.md` | Standard-Panels, Karten, Eingabefelder |
| `radius.lg` | größere Container (sparsam) |

**Regel:** Nicht jedes Rechteck rundziehen. **Reading/paper** kann **0 oder sm** bevorzugen (manuskriptnah); **Panels** **md**. Keine durchgängigen „Pill“-Formen außer expliziten Capsules (Suche, Tags).

### 7.2 Border vs. Divider

- **Border:** wenn eine **geschlossene** Fläche klar vom Nachbarn getrennt werden muss (Eingabefeld, Panel in gleicher Helligkeit). Immer `border.subtle` oder `border.strong` — keine zufälligen Grautöne.  
- **Divider:** wenn **Inhalte innerhalb** einer Fläche gegliedert werden (Sektionen, Listen). Dünn, `divider.soft`, keine pseudo-Karten.  
- **Lichtkante:** bevorzugt bei räumlicher Abstufung **ohne** harten Rand: 1 px hellere Kante auf dunkler Unterlage (semantisch `edge.highlight`) statt Box-Shadow-Show.

---

## 8. DEPTH / SHADOW / LAYER SYSTEM

### 8.1 Elevation-Stufen (max. sinnvoll: **4**)

| Stufe | Name | Verwendung |
|-------|------|------------|
| **0** | base | app/room/surfaces ohne Anhebung |
| **1** | raised | leicht abgehobene Innenflächen (z. B. paper auf work) |
| **2** | floating | Popover, Dropdown, nicht-modale Layer |
| **3** | overlay | Modal, kritische Overlays |

### 8.2 Wann was

- **Helligkeits- und Luminanzsprung** ist Default für räumliche Trennung innerhalb eines Themes.  
- **Schatten** sparsam: Stufe 2–3, weiche, große Unschärfe, niedrige Opazität — **kein** Material-„Elevation 24“.  
- **Lichtkante** statt Border, wenn zwei Flächen ähnlich hell sind und keine Divider-Linie gewünscht ist.  
- **Kein** gestapeltes Multi-Shadow für „Premium-Gefühl“.

---

## 9. MOTION SYSTEM

### 9.1 Dauer (semantisch)

| Token | Richtwert | Verwendung |
|-------|-----------|------------|
| `motion.duration.short` | ~120–160 ms | Hover, kleine state feedback |
| `motion.duration.medium` | ~200–280 ms | Panel-Übergänge, Drawer |
| `motion.duration.long` | ~320–400 ms | Stage-Wechsel, große räumliche Bewegung |

**Easing:** durchgängig **ease-out** oder **cubic-bezier** mit gedämpftem Ende; **kein** bounce, **kein** aggressive overshoot.

### 9.2 Bewegungsarten

| Kontext | Erlaubt | Verboten |
|---------|---------|----------|
| Stage transition | Cross-fade oder sanfter Slide; Opacity + leichte Verschiebung | Starke Zooms, Parallax-Spielerei |
| Drawer reveal | Translation mit medium duration | Rubber-band |
| Overlay | Fade + leichter Y- oder Scale-Minimal (≤ 2–3 %) | Aufpoppen mit Bounce |
| Focus shift | kurze short duration oder instant mit sichtbarem Ring | blinkende Animationen |
| Hover | Farb-/Luminanzänderung bevorzugt; optional short | Layout-Springen |
| Busy / streaming | dezente, **loop-freie** oder langsame Pulse — oder bevorzugt statisch + Text | hektische Spinner-Orgie |

### 9.3 Reduced motion

Wenn System „reduce motion“: **Dauer → 0 oder ≤ 50 ms**, nur Opacity-Wechsel; keine großflächigen Translationen. Fokusringe bleiben **sichtbar** (kein Wegfall der Orientierung).

---

## 10. INTERACTION / STATE SYSTEM

Einheitliche **semantische** Zustände; visuelle Mittel sind begrenzt.

| Zustand | Visuelle Reaktion | Intensität | Erlaubt | Unerwünscht |
|---------|-------------------|------------|---------|-------------|
| **default** | Basistokens | neutral | — | Random-Opacity |
| **hover** | leichte Luminanz/Tint-Shift oder border.subtle | niedrig | short motion | Layout shift |
| **focus** | sichtbarer `focus.ring`, min. 2 px Äquivalent | mittel | Kontrast unabhängig von Hover | nur :hover sichtbar |
| **active** | leichte Pressed-Dunkelheit | niedrig | — | dauerhafter active |
| **selected** | `selection.bg` + `selection.text` | mittel | — | accent.primary als Vollfläche |
| **disabled** | reduzierte Opacity **und** eingeschränkte Interaktion | klar erkennbar | — | nur ausgrauen ohne echte Deaktivierung |
| **busy** | dezentes Indicator-Element + optional Text | niedrig | — | UI blockieren ohne Hinweis |
| **streaming** | ruhiger Fortschritt (Text/Chunk) am Inhalt | niedrig | — | flashy progress |
| **success** | Icon + Text oder dezente Farbe | niedrig–mittel | nicht nur Grün allein | Banner-Dauerfeuer |
| **warning** | Icon + Text, `state.warning` | mittel | — | Panik-Rot |
| **error** | `state.danger` + klare Copy | mittel–hoch | — | reine Farbe ohne Text |

---

## 11. ACCESSIBILITY / CONTRAST RULES

- **Fließtext (body auf paper/work):** Ziel **WCAG 2.1 AA** für normalen Text (Kontrastverhältnis ≥ 4.5 : 1); große Überschriften ≥ 3 : 1.  
- **Sekundärtext:** mindestens AA für **kurze** Texte; längere Absätze in `text.secondary` vermeiden oder Größe erhöhen.  
- **Muted / Caption:** nur kurze Strings; bei Unsicherheit Größe ↑ oder Rolle auf secondary.  
- **Fokus:** Fokusindikator immer sichtbar; Kontrast des Rings zu Umgebung ≥ 3 : 1 (nicht nur Farbe der Fläche).  
- **Status rein farblich:** nie allein; immer **Text, Icon oder Muster** ergänzen.  
- **Motion:** System-„reduce motion“ respektieren (siehe Kap. 9).  
- **Atmosphäre:** keine Ausnahme von diesen Regeln aus „Stimmung“.

---

## 12. QML INTEGRATION STRUCTURE

### 12.1 Verzeichnisstruktur (Zielbild)

```text
qml/
  foundation/
    tokens/           # optionale QML-Objekte / JSON-Referenzen nur hier
    semantics/        # Mapping-Dokumentation (README) + ggf. Loader-Hooks
  themes/
    Theme.qml         # Singleton: semantische Properties (aktueller Stand: Theme.qml)
    qmldir
  domains/            # ausschließlich semantische Theme-Properties konsumieren
  shell/
```

**Primitive Werte** liegen in **Theme-Manifesten** (bereits im Projekt angelegt) oder in einer dedizierten `tokens`-Quelle, die **nur** vom Theme-Loader geschrieben wird — nicht von Domänen-QML.

### 12.2 Zugriff aus Komponenten

- **Singleton `Theme`** (oder `LibraryTheme` als Alias-Name): exportiert **ausschließlich semantische** Properties (`Theme.surfacePaper`, `Theme.textPrimary`, `Theme.spaceMd`, …).  
- **Domänen-QML** importiert `themes 1.0` und referenziert nur `Theme.*`.  
- **Keine** Hex-Literale in `domains/**` und `shell/**` (Governance).  
- **Theme-Varianten:** separate Manifeste / Theme-Pakete mapped auf dieselbe semantische API (gleiche Property-Namen).

### 12.3 Was nicht im Theme-Singleton liegt

- Layout-Logik (Bindings, `width: parent.width`) — bleibt in Komponenten.  
- Domänenspezifische **Konstanten** ohne semantische Bedeutung — vermeiden; wenn nötig, in `component.*` Tokens auslagern.

**Entscheidung:** Ein **semantisches Theme-Singleton** statt verteilter `Qt.resolvedUrl`-Paletten in jeder Datei — bessere Refactor-Sicherheit und klare Review-Grenze.

---

## 13. TOKEN PRIORITIES FOR IMPLEMENTATION

### Phase A — Slice 0 / 1 / 2 (unverzichtbar)

Semantische Farben: app/room/work/paper/panel, text primary/secondary/muted, accent primary/secondary, border.subtle, divider.soft, focus, selection, state danger (minimal).  
Spacing: xs, sm, md, lg, xl + stage margin + reading max width + shelf/context width ranges.  
Typo: body, caption, section/panel title (kann zunächst 3–4 Rollen sein).  
Radius: none, sm, md.  
Motion: short/medium + reduce-motion policy.  
Elevation: 0–2 reicht für Shell + erste Domänen.

### Phase B — Prompt Studio / Agents / Deployment

Erweiterte states (warning, info, success), overlay elevation 3, drawer motion, `monospace.technical`, zusätzliche component bundles für Tabellen/Inspector, ggf. zweite panel-Variante.

### Phase C — Veredelung

Feinjustierung Lichtkanten, optionale Paper-Textur **als parametrische Token** (ohne Bitmap-Pflicht), erweiterte Typo-Feintuning, High-Contrast-Theme-Variante, dokumentierte Ausnahmen minimieren.

---

## 14. GOVERNANCE RULES

1. **Keine Farbliterale** in Domänen- und Shell-QML; nur `Theme` (semantisch).  
2. **Keine freien spacing-Zahlen** außerhalb der dokumentierten Skala; Ausnahmen nur mit ADR.  
3. **Neue Komponenten** müssen semantische Tokens nutzen; PR ohne Token-Verweis wird zurückgewiesen.  
4. **Höchstens 4 Elevation-Stufen**; keine ad-hoc „shadow5“.  
5. **Neue Animationen** nur mit `motion.duration.*` und erlaubten Easings; kein Bounce.  
6. **accent.primary** sparsam: ein aktiver Hauptsakzent pro Blickfeld.  
7. **Surface-Hierarchie** nicht unterlaufen (z. B. kein panel als Vollflächen-Ersatz für paper).  
8. **Accessibility-Regeln** (Kap. 11) sind harte Constraints; keine opt-out ohne dokumentierte Alternative.  
9. **Primitive ändern** nur im Theme/Manifest; semantische Namen bleiben stabil.  
10. **Reviews** prüfen gegen Kap. 1 (Prinzipien) + diese Governance-Liste.

---

**Nächster Schritt (außerhalb dieses Dokuments):** Theme-Manifeste und `Theme.qml` an die hier benannten **semantischen** Properties angleichen, Primitive zuordnen, dann Domänen schrittweise von Literals auf Tokens migrieren.
