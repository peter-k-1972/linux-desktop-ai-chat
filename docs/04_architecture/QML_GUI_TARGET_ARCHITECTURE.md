# Qt Quick / QML — Verbindliches Architektur- und GUI-Zieldokument

**Projekt:** Linux Desktop Chat  
**Status:** Zielbild (keine Implementierung, kein QML-Code in diesem Dokument)  
**Kontext:** PySide6-App mit bestehender Schichtung **GUI → Presenter → Port → Adapter → Service**; `ui_contracts` Qt-frei und ORM-frei; QML ist zusätzlicher GUI-Client auf dieselben Contracts.

---

## 1. EXPERIENCE MODEL

### 1.1 Räumliche Kernidee

Die Anwendung wird als **ein zusammenhängender Wissensraum** verstanden — nicht als Menübaum mit lose gekoppelten Fenstern. Der Nutzer bewegt sich zwischen **Räumen mit klarer Rolle** (Lesesaal, Katalog, Dienstwege, Druckerei, Archiv), die dieselbe **visuelle und navigative Grammatik** teilen. Tiefe, Licht und Materialität signalisieren **Hierarchie und Fokus**, nicht Dekoration.

**Entscheidung:** Ein primärer **App-Raum** mit **wechselnder Bühne (Stage)** und stabilen **Rand-Systemen** (Navigation, Kontext, globale Befehle). Begründung: schafft Orientierung ohne Dashboard-Dichte; entspricht Qt-Quick-Realität (ein `Window`, mehrere inhaltliche Substages).

### 1.2 Navigation — wie sie sich anfühlt

- **Wechsel der Domäne** wirkt wie **Raumwechsel auf derselben Etage**: gleiche Lichtlogik, gleiche Kantenqualität, anderer Inhalt; kein harter Kontextwechsel à la „neue App“.
- **Innerhalb einer Domäne** dominiert **lineare und laterale Arbeit**: vertikale Leselisten, horizontale Arbeitsinseln, optionale seitliche **Inspector**-Schichten.
- **Rückkehr** zu zuletzt bearbeiteten Kontexten ist **vorhersehbar** (aktive Domäne, Selektion, Fokus bleiben nachvollziehbar modelliert — siehe Abschnitt 6).

**Entscheidung:** **Eine globale Navigationsleiste oder -säule** (Domänen) + **lokale Subnavigation** pro Domäne (Tabs, Segmente, oder zweite Säule — domänenspezifisch im Domain Blueprint). Begründung: globale Orientierung darf nicht in jeder Domäne neu erfunden werden.

### 1.3 Abgrenzung zu klassischen Business-UIs

| Klassische Business-UI | Ziel-GUI |
|------------------------|----------|
| Raster aus gleichwertigen Karten | Hierarchische Flächen mit klarer Primärarbeit |
| Hohe Informationsdichte als Standard | Dichte nur dort, wo Arbeit es erfordert; sonst Luft und Fokus |
| Formular-first | **Objekt-first** (Gespräch, Prompt, Agentenauftrag, Release, Einstellungsklasse) mit kontextuellen Editoren |
| Globale Alarmfarben | **Ruhe + gezielte** Statusinseln |
| Modale Ketten | **Overlays mit klarem Zweck**; modale Tiefe begrenzt |

### 1.4 Rolle von Raum, Licht, Materialität, Fokus, Ruhe

- **Raum:** Substages liegen auf **Tiefenebenen** (Vordergrund = Interaktion, Hintergrund = Kontext). Kein „alles flach auf #222“.
- **Licht:** **Warme Arbeitsinseln** (Lesetisch, Katalogkarte, Schreibtisch des Agenten) heben **aktive** Bereiche; globale Grundfläche bleibt **gedämpft**.
- **Materialität:** **Matt**, **papierartig** für Inhalt; **metallisch dezent** für **Ränder, Führung, Akzent** — nie spiegelnd oder „Sci-Fi-Chrome“.
- **Fokus:** Genau **ein primärer Fokus** pro Stage-View (z. B. aktiver Chat, aktives Prompt, aktiver Task); sekundäre Panels sind **untergeordnet sichtbar**.
- **Ruhe:** Animation und Licht **unterstützen Orientierung** (Erscheinen, Tiefe, Übergang), keine Unterhaltung.

### 1.5 Globale Interaktionsprinzipien

1. **Primäraktion sichtbar** auf der Arbeitsfläche; sekundäre Aktionen in Überlagerungen, Kontextleisten oder Command-Layer.
2. **Direktmanipulation** dort, wo sie die mentale Last senkt (Scroll, Ziehen von Splittern, klare Klicks); **explizite Bestätigung** bei destruktiven oder weitreichenden Operationen.
3. **Tastatur:** Navigation und Befehle **first-class** (siehe 3.10); Mauspfade bleiben kurz.
4. **Konsistenz vor Domänen-„Besonderheit“:** Domänen unterscheiden sich durch **Inhalt und Fluss**, nicht durch ein neues UI-Vokabular.
5. **Lesbarkeit vor Effekt:** Kontrast und Schriftgröße werden nie zugunsten von Stil geopfert.

### 1.6 Wissensarchitektur statt Screen-Sammlung

Die GUI wird dokumentiert und implementiert als:

- **Domänen** mit **Arbeitsobjekten**, **Panels** und **Flows**
- **Globale Querschnitte**: Suche/Befehle, Benachrichtigungen, Status, Einstellungen
- **Stable chrome** + **wechselnde Substages**

Screenshots als Planungsartefakt sind sekundär; **Objekt- und Flussdiagramme** (intern) sind primär.

---

## 2. VISUAL SYSTEM SPEC

### 2.1 Farbrollen (verbindlich)

Farben werden **nicht** als freie Palette verwendet, sondern als **semantische Rollen** (Theme-Tokens). Mindestrollen:

| Rolle | Zweck |
|-------|--------|
| `canvas.base` | Tiefster Raum (Anthrazit / sehr dunkles Braun) |
| `canvas.elevated` | Erhöhte Flächen (Panels, Kartenrücken) |
| `surface.work` | Papier-/Arbeitsfläche (warmes Elfenbein / helles Grau, stark reduzierte Sättigung) |
| `surface.muted` | Sekundäre Flächen, Listenhintergrund |
| `border.subtle` | Trennung ohne harte Konkurrenz zum Inhalt |
| `border.focus` | Fokusring / aktive Kante (präzise, nicht neon) |
| `text.primary` | Haupttext auf Arbeitsfläche |
| `text.secondary` | Metadaten, Timestamps |
| `text.onDark` | Text auf dunklem Canvas |
| `accent.primary` | Messing / gedämpftes Gold — **sparsam**, für Primärakzent |
| `accent.secondary` | Tintenblau / Petrol — **sekundär**, für Links, sekundäre Markierung |
| `state.success` | Zurückhaltend, nicht Grün-Alarm |
| `state.warning` | Warm, nicht Orange-Plakat |
| `state.error` | Klar, aber nicht grell |
| `state.info` | Petrol-nah, dezent |

**Regel:** Kein UI-Element verwendet „Rohexagon“-Farben ohne Rollenzuordnung.

**Entscheidung:** **Zwei Oberflächenfamilien** — dunkles **Canvas** für Chrome und Raum; helle **work surface** für längeres Lesen und Schreiben. Begründung: Reduziert Ermüdung, stützt die Bibliotheks-Metapher, erfüllt Lesbarkeit.

### 2.2 Materialsystem

- **Matt:** Keine glänzenden Verläufe als Standard.
- **Papier:** Leichte **Textur nur global dezent** (optional, performancegeprüft); keine per-Kachel-„Pergament-Cliparts“.
- **Metall:** **Haarlinien-Rahmen**, **kantengeführte** 1-px-Linien, **sehr gedämpfte** Spiegelung nur als **Lichtkante**, nicht als Fläche.

**Regel:** Materialien **einmal** im Foundation-Layer definieren; Domänen **erben**, sie erfinden keine neuen Materialien.

### 2.3 Lichtlogik

- **Globales Umgebungslicht:** niedrig, kühl-warm neutral auf Canvas.
- **Arbeitslicht:** warm, **lokal** auf `surface.work` und **aktive** Listeneinträge.
- **Kantenlicht:** **präzise** 1-px bis 2-px **Highlight** an **oberer/linker** Kante von erhöhten Flächen (konventionsbasiert, konsistent).

**Regel:** Licht **niemals** die einzige Informationsquelle für Status sein — immer **Text/Symbol** redundant.

### 2.4 Tiefenmodell

Drei **benannte** Ebenen (Token/Enum-Konzept, nicht beliebiges `z`):

1. **Base** — Canvas  
2. **Raised** — Panels, schwebende Karten  
3. **Overlay** — Modale, Popover, Toasts  

**Regel:** Schatten **kurz**, **weich**, **niedrige Opazität**; keine langen Dropshadows („Material Design 2014“).

**Entscheidung:** Tiefe **primär** über **Kante + leichte Schatten + Kontrast**, nicht über **perspektivische** 3D-Effekte. Begründung: Qt Quick Performance und reduzierte Kitsch-Gefahr.

### 2.5 Bewegungsprinzipien

- Dauer: **kurz** (ca. 120–220 ms für UI-Transpositionen), **mittel** (ca. 220–400 ms für Raumwechsel).
- Kurven: **ease-out** / **cubic** — **kein** elastisches Federn.
- Inhalt: **Fade + subtile Verschiebung** (max. wenige dp); **kein** Parallax-Spiel.
- **Regel:** Animation **überspringbar** wenn Nutzer schnell navigiert (kein erzwungener „Film“).

**Entscheidung:** **Ein einheitliches Bewegungs-Tokenset** (Dauer, Kurve) im Theme; Abweichungen nur mit Architektur-Review.

### 2.6 Typografiesystem

- **UI-Fließtext:** humanistische / neugrotesk Sans, **gut lesbar**, **ruhig**.
- **Überschriften:** charaktervoll aber **zurückhaltend** (optional Serif oder „book Sans“-Schnitt — **eine** Familie für Display, nicht Mischwild).
- **Größenstufen:** definierte Skala (z. B. 12/14/16/20/24) — **keine** freien Font-Pixel in Domänen-QML.
- **Zahlen/Monospace:** nur für **Code, IDs, Rohdaten** in Prompt/Agent/Deployment-Kontexten.

**Regel:** Mindestkontrast einhalten (siehe 2.10); **kein** Text unter 12 px für Pflichtinformationen.

### 2.7 Flächenhierarchie

1. **Primärarbeit** — größte zusammenhängende `surface.work`-Region.  
2. **Kontext** — seitlich oder sekundär, kleiner, `canvas.elevated` oder `surface.muted`.  
3. **Globales Chrome** — dünn, hoch kontrastreich genug für Orientierung, aber **flächenarm**.

**Regel:** Keine dritten „Haupt“-Flächen; wenn mehr nötig → **Tabs, Inspector, Overlay** statt weiterer gleichgewichtiger Spalte.

### 2.8 Akzentlogik

- **Gold/Messing:** **eine** primäre Interaktion pro Blickfeld markieren (Button, aktive Nav, aktiver Tab).
- **Petrol:** **sekundäre** Hinweise, Links, „weiterführend“.
- **Regel:** Akzentfläche **gesamt** < ca. 5–8 % der sichtbaren UI; sonst visueller Lärm.

### 2.9 Statusdarstellung

- **Inline** im Objekt (Zeile, Badge am Rand) vor **global** (Toast).
- **Farbe + Form + Text** (mindestens zwei Kanäle).
- **Busy:** dezentes **Glimmen** oder **linearer** Fortschritt — kein Comic-Spinner.

### 2.10 Kontrastregeln

- Arbeitsfläche: **WCAG-orientiert**; kritische Texte **AA** mindestens.
- Fokusring: **immer** sichtbar bei Tastaturbedienung.
- **Entscheidung:** Kontrast-Tests gehören zu **Slice-DoD** für Foundation + eine Domäne Referenz.

### 2.11 Reduktionsregeln (Anti-Kitsch / Anti-Überladung)

1. Keine **ornamentalen** SVG-Rahmen, **keine** Skeuomorph-Illustrationen als UI-Grundlage.  
2. Keine **mehrfarbigen** Gradienten als Flächenfüllung.  
3. Keine **Spiel-**Microinteractions (wackeln, bounce).  
4. **Höchstens ein** „Besonderer“ visueller Effekt pro Release-Train (sonst entkoppelt).  
5. **Metapher** erklärt **Ort und Fluss** — sie **ersetzt** keine Labels und keine Klartext-Hilfen.

---

## 3. QML SYSTEM ARCHITECTURE

### 3.1 App Shell

Die Shell umfasst:

- **Root Window** mit **exakt einem** primären Navigations- und Stage-Container
- **Globale Theming** (Farben, Typo, Dichte)
- **Overlay-Stack** (Modal, Drawer, Popover, Toast)
- **Shortcut / Command**-Anbindung an Python (Command-Port oder dedizierte Fassade)

**Regel:** Shell-QML kennt **keine** Business-Entscheidungen — nur **Routen-Ziele** und **Layout**.

### 3.2 Root-Komponenten (konzeptionell)

1. `AppRoot` — lädt Theme, setzt Locale/Schrift, initialisiert Bridge  
2. `AppChrome` — äußerer Rahmen (Domänenwahl, globale Aktionen, optional Titel/status)  
3. `StageHost` — zeigt aktuelle **Stage**  
4. `OverlayHost` — stapelt Overlays  
5. `CommandLayer` — unsichtbar/logisch; verbindet Shortcuts

**Entscheidung:** **Single Document Interface** innerhalb eines Fensters; **kein** MDI-Fensterwald. Begründung: passt zu Bibliotheks-Raum-Metapher und reduziert Qt-Fensterkomplexität.

### 3.3 Navigationsmodell

- **Globale Domänen-Navigation** ist **zustandsbeobachtend**: aktive Domäne kommt aus Python (Presenter/Navigations-State), nicht aus verstreuten QML-`property`-Derivaten.
- **Deep links** (optional später): Domäne + Subroute + Objekt-ID als **von Python autoritative** Route.

**Entscheidung:** **Router-State lebt in Python**; QML **bindet** daran. Begründung: eine Wahrheit, Port-kompatibel, testbar ohne Scene Graph.

### 3.4 Stage- / Substage-Modell

- **Stage:** voller Inhaltsbereich für eine Domäne (wechselt bei Domänenwechsel).
- **Substage:** innerhalb der Domäne (z. B. Liste → Detail → Editor); wird **domänenspezifisch** modelliert, aber über **gemeinsliche** Stage-Container-Patterns.

**Regel:** Jede Domäne definiert **max. 2 sichtbare** Substage-Ebenen gleichzeitig (z. B. Liste + Detail); weitere Tiefe → Overlay oder Inspector.

### 3.5 Overlay-Konzept

Overlays sind **typisiert**:

| Typ | Verwendung |
|-----|------------|
| `Modal` | Blockierende Bestätigung, kritische Eingabe |
| `Drawer` | Kontext-Inspector, Filter, sekundäre Spalte mobilisiert |
| `Popover` | Kontextmenü, kleine Optionen |
| `Toast` | kurze, nicht-blockierende Systemmeldung |

**Regel:** **Ein** modaler Stack; Modale **nie** rekursiv ohne Not — Alternative: sequenzieller Dialog in Python-gesteuertem Flow.

### 3.6 Domain-Scaffold

Jede Domäne erhält eine **einzige** Einstiegskomponente (Konzeptname z. B. `ChatStage.qml`), die:

- ihre **Substage**-Struktur kapselt  
- **Ports/Presenter** nur über die **Bridge-API** sieht  
- **keine** fachfremden Domänen importiert

### 3.7 Foundation-Layer

Enthält **ausschließlich** wiederverwendbare, domänenneutrale Bausteine:

- Layout primitives (Splitter-Region, Scroll-Region mit konsistentem Verhalten)
- Buttons, Inputs, Chips, Listenelement-Basen
- Typography, Icon-Platzhalter-Regeln
- Effects (Schatten, Kantenlicht) als parametrisierte Komponenten

**Regel:** Foundation importiert **nicht** aus `domains/`.

### 3.8 Wiederverwendbare Komponentenfamilien

- **Navigation:** `NavRail` / `NavBar` (eine Variante wird produktiv — nicht beide langfristig pflegen ohne Grund)
- **Data display:** `ObjectRow`, `MetaStrip`, `SectionHeader`, `CodeSurface`
- **Composition:** `WorkSurface`, `ContextPanel`, `InspectorDrawer`
- **Feedback:** `Toast`, `InlineBanner`, `ProgressStrip`

**Entscheidung:** **NavRail** (vertikal) für Domänen auf Desktop; horizontale Subnavigation innerhalb der Stage. Begründung: skaliert mit vielen Domänen, spielt horizontalen Platz für Arbeit frei.

### 3.9 Theme- / Token-System

- QML liest **semantische Tokens** (Farbe, Typo, Dichte, Motion), gesetzt von Python aus **bestehender Theme-Infrastruktur** oder einer dünnen QML-spezifischen Abbildung.
- **Regel:** Keine Hex-Werte in Domänen-QML; nur `Theme.xxx` / `Qt.styleHints` wo sinnvoll.

### 3.10 Routing / Navigation State

- Python hält: `activeDomain`, `domainSubroute`, ggf. `selectedObjectId`, **Back-Stack optional**.
- QML reagiert: **Property-Bindings** + **Signals** für Nutzerintention (`userRequestedOpenPrompt(id)`).
- **Regel:** QML führt **keine** alleinige „History“ für fachliche Objekte.

### 3.11 Keyboard- / Command-Ebene

- Globale Shortcuts (z. B. Command-Palette, Suche, Domänenwechsel) werden in **Python** registriert (Single Point), QML kann **fokusabhängige** Shortcuts melden.
- **Regel:** Keine doppelte Shortcut-Logik in QML-JS und Python — **Python gewinnt** bei Konflikt.

---

## 4. DOMAIN BLUEPRINTS

Globale Regel für alle Domänen: **Metapher erklärt Ort**, **Presenter erklärt Verhalten**, **QML zeigt Zustand**.

### 4.1 Chat — Lesetisch / Lesesaal

| Aspekt | Spec |
|--------|------|
| **Raumrolle** | Ort des **längeren, fokussierten Lesens und Schreibens**; „ruhiger Saal“. |
| **Primärarbeit** | **Konversationsfluss** (Transkript) auf `surface.work`; Eingabe als **integrierter** unterer oder eingebetteter Arbeitsstreifen — kein losgelöstes „Formular unten“. |
| **Unterstützend** | Themen/Threads-Navigation, Metadaten, ggf. Kontext-Inspector (Quellen, angehängte Artefakte). |
| **Zentrale UI-Objekte** | Thema/Thread, Nachricht, Eingabefeld, Streaming-Partial-Block, Fehlermarkierung. |
| **Typische Flüsse** | Thema wählen → lesen → antworten → Stream beobachten → bei Fehler **inline** korrigieren/ wiederholen. |
| **Panels / Drawer** | **Navigation** links oder schmal; **Inspector** rechts optional; **Aktionen** kontextuell an Nachricht. |
| **Metapher funktional** | Reduziert **Karten-Denke**; betont **Kohärenz** und vertieftes Arbeiten. |
| **Explizit verboten** | Chat als **Dashboard-Kachel**; **Bubble-Orgie** ohne Leserhythmus; **reine** „Notification-UI“. |

### 4.2 Prompt Studio — Bücherregal + Kartenkatalog

| Aspekt | Spec |
|--------|------|
| **Raumrolle** | **Ordnen, Finden, Bearbeiten, Versionieren** von Textartefakten. |
| **Primärarbeit** | **Editor** auf `surface.work`; Lesepane für Vorschau nur wenn sie den Schreibfluss nicht spaltet. |
| **Unterstützend** | Bibliotheks-/Listenansicht, Template-Galerie (kompakt), Versions-/Metadaten-Inspector. |
| **Zentrale UI-Objekte** | Prompt, Version, Template, Testeingabe, Evaluations-/Testergebnis (als sachliche, nicht „Spiel“-Darstellung). |
| **Typische Flüsse** | Suchen → öffnen → bearbeiten → Version anlegen → im Testlabor gegen Modell prüfen. |
| **Panels / Drawer** | Links **Katalog**; rechts **Inspector**; Testlabor als **Substage** oder **unterer** Arbeitsmodus — fest pro Slice festzulegen, aber **ein** Primärfokus. |
| **Metapher funktional** | Erzwingt **Hierarchie** (Werk → Ausgabe → Version) statt flacher Liste. |
| **Explizit verboten** | **Spielzeug-**„Karten“ mit unnötigen Schatten; **überladene** Template-Visuals. |

### 4.3 Agenten — Bibliothekare / Arbeitsstationen / Dienstwege

| Aspekt | Spec |
|--------|------|
| **Raumrolle** | **Aufträge, Zustände, Werkzeuge** sichtbar machen; kein „Magie-Knopf“. |
| **Primärarbeit** | **Aktueller Auftrag / Task-Detail** und **Fortschritt**; Logs/Traces **lesbar**, filterbar. |
| **Unterstützend** | Registry (was existiert), Runtime (was läuft), Inspector für Technik ohne Doppelung der Primäransicht. |
| **Zentrale UI-Objekte** | Agent/Worker-Definition, Task-Run, Schritt, Fehlerobjekt, Ressourcenhinweis. |
| **Typische Flüsse** | Agent auswählen → Task starten/beobachten → bei Fehler **Diagnose** öffnen → Retry/Eskalation. |
| **Panels / Drawer** | **Operations-ähnlich** aber **ruhig**: tabellarische und chronologische Ansichten mit **klarer** Typografie statt Ampel-Theater. |
| **Metapher funktional** | **Dienstweg** klar: wer macht was, wo steckt es fest. |
| **Explizit verboten** | Gamification (XP, Badges); **hollywoodsche** Statusanimationen. |

### 4.4 Deployment — Druckerei / Verlag / Binderei

| Aspekt | Spec |
|--------|------|
| **Raumrolle** | **Release bilden, ausrollen, beobachten** — analog zu **Fertigungs-** und **Logistik-Kette**. |
| **Primärarbeit** | **Release** oder **Rollout** als Objekt zentral; Tabellen **dicht aber sortiert**. |
| **Unterstützend** | Targets, Umgebungen, Historie/Protokoll, Signoff-Status. |
| **Zentrale UI-Objekte** | Release, Target, Rollout, Policy/Constraint, Protokollereignis. |
| **Typische Flüsse** | Release anlegen → Artefakte zuordnen → Rollout planen → Status beobachten → bei Fehler **Rollback/Stop** (wenn Domain das hergibt). |
| **Panels / Drawer** | Master-Detail mit **starker** tabellarischer Komponente; Detail als Inspector. |
| **Metapher funktional** | Unterstützt **Ordnung und Nachverfolgbarkeit** — keine „Deploy-Button-only“-Oberfläche ohne Kontext. |
| **Explizit verboten** | **Verspielte** Pipeline-Grafiken die **mehr Platz** als Nutzen haben. |

### 4.5 Settings — Archivverwaltung / Hausordnung / Haustechnik

| Aspekt | Spec |
|--------|------|
| **Raumrolle** | **Strukturierte, ruhige** Konfiguration; niedrige emotionale Temperatur. |
| **Primärarbeit** | **Kategorie** links, **Einstellungsblöcke** rechts auf `surface.work`. |
| **Unterstützend** | Suche in Einstellungen, Reset auf Standard, Hinweise zu Risiken (dezent). |
| **Zentrale UI-Objekte** | Kategorie, Setting-Key, Kontrolle (Toggle, Auswahl, Pfad), Validierungshinweis. |
| **Typische Flüsse** | Suchen → ändern → **explizit** anwenden oder auto-save **nur** wenn Port das garantiert; Fehler **feldgebunden**. |
| **Panels / Drawer** | **Klassische** Zwei-Spalten-Navigation; mobile → Drawer (falls jemals relevant). |
| **Metapher funktional** | **Ordnung** und **Vertrauen**; keine versteckten Experimente. |
| **Explizit verboten** | **„Developer Dungeon“**-Ästhetik; kryptische IDs ohne Label. |

---

## 5. PROJECT STRUCTURE

Verzeichnisstruktur als **Zielbaum** (anpassbar, aber nicht willkürlich):

```text
qml/
  AppRoot.qml
  shell/
    AppChrome.qml
    StageHost.qml
    OverlayHost.qml
    NavRail.qml
  foundation/
    layout/
    controls/
    typography/
    effects/
    feedback/
  themes/
    Theme.qml                    # oder Loader + JSON/Mapping von Python
    tokens/
      color_tokens.json          # optional: rein datengetrieben
      type_scale.json
      motion_tokens.json
  components/
    navigation/
    lists/
    editors/
    inspectors/
    dialogs/
  domains/
    chat/
    prompt_studio/
    agent_tasks/
    deployment/
    settings/
  assets/
    fonts/
    icons/                       # bevorzugt SVG oder Qt-kompatible Vektoren
    textures/                    # sparsam, optional

python_bridge/
  __init__.py
  qml_application.py             # Engine, Load, Root-Context-Setup
  bridge_facade.py               # Ein Einlass für QML: properties, signals, slots
  presenters/                    # dünne Kopplung: pro Domäne oder pro Shell
    shell_presenter.py
    chat_presenter.py
    ...
  mappers/                       # DTO → QML-sichere Strukturen (falls nötig)
  tests/
    test_bridge_contracts.py
    test_navigation_state.py

# Presenter-Fassaden (falls nicht schon unter app/ui_application):
# Bestehende Presenter bleiben führend; QML-spezifische Fassade nur wo nötig
app/ui_application/              # (bestehend)
  presenters/
  ports/
  ...

tests/
  qml/
    screenshot_baseline/           # optional später
    unit/                          # falls QmlTest eingesetzt wird
```

**Regeln:**

- `domains/*` darf `foundation/*`, `components/*`, `themes/*` importieren — **nicht** umgekehrt.
- `shell/*` darf **keine** domänenspezifischen Typen kennen — nur generische Stage-Loader.
- **Assets** sind **keine** Logik; Versionierung wie im restlichen Projekt.

---

## 6. STATE / DATA FLOW MODEL

### 6.1 Zustände in QML (erlaubt)

- **Reiner UI-Zustand:** Scrollposition, Splitter-Verhältnis, expand/collapse von **nicht-fachlichen** Paneelen, Hover, transienter Fokus innerhalb einer Komponente
- **Ephemer:** aktuell geöffnetes Kontextmenü, Drag-Preview
- **Lokale Validierung nur visuell:** Format-Hinweis vor Roundtrip, solange **Python** finale Autorität bleibt

### 6.2 Zustände in Python (verpflichtend)

- **Selektion** fachlicher Objekte (aktiver Chat, aktiver Prompt, aktiver Task, aktives Release, …)
- **Navigations- und Routenzustand**
- **Command-Ausführung**, **Transactions**, **Fehlerdomäne**
- **Streaming-Inhalte** als modellierter Textzustand (Chunks, partials)
- **Caching** fachlicher Daten, **Berechtigung**, **Feature-Flags**

**Regel:** Wenn zwei QML-Instanzen denselben Zustand brauchen, liegt er **nicht** in QML.

### 6.3 Datenbindung

- **Ein** Bridge-Objekt (oder klar benante Subobjekte) exponiert **QObject properties** mit stabilen Typen (primitive, QStringList, oder registrierte **Value Types**/Modelle).
- **Listen:** `QAbstractItemModel` oder **explizite** ListModel-Updates von Python — **Entscheidung:** bevorzugt **Model aus Python** für große Datenmengen (Chat-Historie, Tabellen). Begründung: weniger JS, bessere Performance, klarere Verantwortung.

### 6.4 Commands

- Nutzeraktion in QML → **Signal** `intentXyz(payload)` → Python **slot** → Presenter → Port → Adapter → Service.
- **Regel:** Keine `import` von Services in QML; keine URL/DB/Pfad-Logik in QML.

### 6.5 Async und Rückfluss

- Langläufer: Python startet, **Status** über Properties (`idle`, `running`, `failed`) + **Fehlertext**; QML **beobachtet**.
- **Regel:** **Kein** Polling in QML-JS als Standard; **Signals von Python** oder Model-Updates.

### 6.6 Streaming (Chat)

- Partial-Text als **vom Presenter verwalteter** String oder **Chunk-Liste** mit stabiler ID; QML rendert **nur**.
- **Regel:** Tokenisierung/Markdown-Parsing-Policy in **Python** (oder bestehende Renderer-Pipeline), nicht ad-hoc in QML.

### 6.7 Fehler, Empty, Busy

- **Fehler:** domänenübergreifend gleiche **Muster**: `InlineBanner` + **Retry**-Aktion über Command; kritisch → Modal.
- **Empty:** sachliche **Leerzustände** mit **einer** primären Aktion (z. B. „Neues Thema“).
- **Busy:** **global** nur bei blockierenden Operationen; **lokal** bei Teilbereichen (Skeleton/Progress).

### 6.8 Selection / Focus / Active Domain

- **Active Domain:** Python → Shell bindet Nav-Hervorhebung und Stage-Loader.
- **Selection:** Python **führt**; QML spiegelt; bei Klick QML **signalisiert** Intent.
- **Focus:** QML verwaltet Tastaturfokus; **fachliche** „Fokusobjekt“-ID bleibt in Python synchron, wenn es Auswirkungen über Komponenten hat (z. B. Inspector-Inhalt).

---

## 7. SLICE ROADMAP

Jeder Slice ist **vertikal** (UI + Bridge + mindestens ein Port-Pfad) und **merge-fähig**.

### Slice 0: QML-Foundation / App-Start / Shell-Skelett

| Feld | Inhalt |
|------|--------|
| **Ziel** | Laufende QML-Oberfläche im bestehenden Prozess oder Side-by-Side-Start; Theme-Tokens angebunden; leere Stage. |
| **Bausteine** | `AppRoot`, `python_bridge` minimal, `Theme`, Foundation-Layout (leer), Placeholder-`surface.work`. |
| **Abhängigkeiten** | PySide6 Quick, Build/Resource-Pipeline für QML, Entscheidung Ein-Fenster-Modus. |
| **Definition of Done** | Start ohne Crash; Tokens sichtbar; **kein** Domänencode. |
| **Risiken** | Resource-Loading-Pfade, HiDPI — früh testen. |

### Slice 1: App Shell + Navigation + Raumlogik

| Feld | Inhalt |
|------|--------|
| **Ziel** | `NavRail`, `StageHost`, Domänenwechsel **funktional** über Python-State. |
| **Bausteine** | Shell, Router-Properties, leere `domains/*` Placeholder, OverlayHost leer. |
| **Abhängigkeiten** | Shell-Presenter oder Nav-Fassade auf bestehende App-Lifecycle. |
| **Definition of Done** | Domäne wählbar; Stage lädt richtigen Placeholder; Tastatur: Domänen rotierbar (optional minimal). |
| **Risiken** | Doppelte Nav-Logik mit alter GUI — **governance** strikt. |

### Slice 2: Chat

| Feld | Inhalt |
|------|--------|
| **Ziel** | Lesen/Senden eines Threads; Streaming sichtbar; Fehler sichtbar. |
| **Bausteine** | `ChatStage`, Transcript-View, Eingabe, Model oder Property-Stream vom Chat-Presenter/Port. |
| **Abhängigkeiten** | `Chat`-Port, Streaming-Pfad, DTO-Mapping. |
| **Definition of Done** | Happy Path + Fehler + Busy; **keine** Businesslogik in QML. |
| **Risiken** | Performance langer Listen — früh Model wählen. |

### Slice 3: Prompt Studio

| Feld | Inhalt |
|------|--------|
| **Ziel** | Liste, Editor, Versionen oder Templates **gemäß** bestehendem Port-Umfang. |
| **Bausteine** | Katalog + Editor + Inspector; ggf. Testlabor-Substage. |
| **Abhängigkeiten** | Prompt-Studio-Port/Presenter. |
| **Definition of Done** | CRUD/Versionierung wie alte GUI-Fähigkeiten (reduziert akzeptabel nur wenn dokumentiert). |
| **Risiken** | Zu viele Substages — auf **einen** Primärmodus begrenzen. |

### Slice 4: Agenten

| Feld | Inhalt |
|------|--------|
| **Ziel** | Registry + Runtime + Task-Detail **in ruhiger** Dichte. |
| **Bausteine** | Tabellen/Listen, Detail-Inspector, Log-Ansicht. |
| **Abhängigkeiten** | Agent-Tasks-Ports, Runtime-Adapter. |
| **Definition of Done** | Start/Stop/Status wie Port erlaubt; Fehlerpfad. |
| **Risiken** | Log-Flut — Pagination/Filter **in Python**. |

### Slice 5: Deployment

| Feld | Inhalt |
|------|--------|
| **Ziel** | Releases / Targets / Rollouts **master-detail**. |
| **Bausteine** | Tabellen, Formulare in `surface.work`, modale Bestätigungen. |
| **Abhängigkeiten** | Deployment-Ports. |
| **Definition of Done** | Kern-CRUD und sichtbare Status; keine „Dummy-Pipeline“. |
| **Risiken** | Validierungsregeln nur serverseitig — UI muss Fehler tragen. |

### Slice 6: Settings

| Feld | Inhalt |
|------|--------|
| **Ziel** | Kategorien + kontextuelle Panels; Modell-/Theme-Auswahl falls im Scope. |
| **Bausteine** | Zwei-Spalten-Settings-Scaffold, wiederverwendbare Controls. |
| **Abhängigkeiten** | Settings-Port, ggf. Ollama/Katalog-Adapter. |
| **Definition of Done** | Parität mit kritischen Settings der alten GUI (Liste dokumentieren). |
| **Risiken** | Settings-Explosion — Suche ab Slice 6 oder 7. |

### Slice 7: Command Layer / Polish / Accessibility

| Feld | Inhalt |
|------|--------|
| **Ziel** | Command-Palette/Shortcuts, Konsistenzreview, Fokusführung, Kontrastaudit. |
| **Bausteine** | `CommandLayer`, globale Dialoge, Feinschliff Motion/Tokens. |
| **Abhängigkeiten** | bestehende Command-Infrastruktur (falls vorhanden). |
| **Definition of Done** | Tastaturpfade für Kernflows; keine blockierenden A11y-Verstöße in neuen Screens. |
| **Risiken** | Shortcut-Konflikte mit OS/Desktop — zentrale Registry nötig. |

---

## 8. RISKS / GOVERNANCE RULES

### 8.1 Architektur

1. **Kein direkter Servicezugriff aus QML** — nur Bridge → Presenter → Port → Adapter → Service.  
2. **Keine doppelte Businesslogik** in QML-JavaScript — komplexe Ableitungen gehören nach Python.  
3. **Ports bleiben die API** — QML-spezifische Erweiterungen nur über **Presenter-Fassaden**, nicht durch Port-Aufweichung.  
4. **ui_contracts** bleiben Qt-frei; QML-DTOs sind **Abbilder**, keine neuen Wahrheiten.  
5. **Alte PySide-Widget-GUI und QML** müssen **parallel** bau- und startbar bleiben, bis explizit anders beschlossen.

### 8.2 QML / JavaScript

1. **Keine unkontrollierte** JS-Logik: maximale Zeilen/Datei und **Linting** (teamdefiniert); Review bei neuen `.js`-Modulen in QML.  
2. **Keine Netzwerk-** oder **Dateisystem-**Aufrufe aus QML.  
3. **Performance:** große Listen nur über **C++/Python-Modelle** oder chunking; keine **Timer-Schleifen** für Datenladen.

### 8.3 Design / Metapher

1. Metapher **darf** Orientierung verbessern — wenn sie **verwirrt**, zurück zur **sachlichen** Benennung.  
2. **Domänen teilen** dieselbe **visuelle Grammatik** (Tokens, Typo, Motion).  
3. **Animationen** dürfen **keine** Lesbarkeit oder **Klickflächen** verdecken; **reduziert** bevorzugt gegenüber „impressive“.  
4. **Effektshow** ist **falsch**, wenn sie **Frame-Drops** oder **fokale Unruhe** erzeugt.

### 8.4 Qualität / Barrierefreiheit

1. **Kontrast** und **Fokusindikatoren** sind **Pflicht** für alle neuen Foundation-Controls.  
2. **Screenreader** (wo Qt Quick es erlaubt): sinnvolle `Accessible.name` / Rollen — **nicht** nachthought nur am Ende.  
3. **Lokalisierung:** keine hardcodierten Strings in QML ohne `qsTr`/`QT_TR_NOOP`-Strategie (Projektstandard festlegen).

### 8.5 Prozess

1. Jeder Slice endet mit **DoD** aus diesem Dokument + **kurzem** Architektur-Check (Bridge-only).  
2. **Abweichungen** von diesem Dokument **explizit** im MR beschreiben (ein Satz reicht).  
3. **Neue domänenübergreifende** Komponenten nur in `components/` oder `foundation/` — **kein** Copy-Paste zwischen `domains/`.

---

**Dokumentende.** Dieses Zieldokument ist die verbindliche Referenz für Slice 0/1-Planung und für Design/Architektur-Reviews der Qt-Quick-Oberfläche, bis es durch ein ersetzendes Version-Dokument abgelöst wird.
