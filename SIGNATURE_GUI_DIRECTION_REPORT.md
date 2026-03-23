# Obsidian Core — Signature GUI Direction Report

**Rolle:** Abschlussbericht zur Signatur-GUI-Architektur (Zielmodell).  
**Detailquellen:** `docs/design/SIGNATURE_GUI_PRINCIPLES.md`, `SIGNATURE_SPATIAL_ARCHITECTURE.md`, `COMMAND_CENTER_VISION.md`, `SIGNATURE_COMPONENT_MODEL.md`, `PREMIUM_INTERACTION_MODEL.md`, `SIGNATURE_GUI_MODERNIZATION_PLAN.md`, `SIGNATURE_GUI_DO_DONT.md`  
**Kontext:** [GUI_COMPLETE_REVIEW_REPORT.md](./GUI_COMPLETE_REVIEW_REPORT.md)

---

## 1. Executive Summary

Die **Signature GUI** für Obsidian Core / Linux Desktop Chat ist als **ruhiger Operations-Desktop** definiert: klare **räumliche Schichten** (Canvas → Workspace → Karten → Fokus → Overlay), **semantische Ehrlichkeit** gegenüber dem Nutzer und eine **einzige, tiefe Kommandozentrale** im Standardpfad. Das „Premium“-Gefühl entsteht durch **Präzision** (Raster, Tokens, konsistente Komponentenfamilien) und **subtile Interaktion**, nicht durch Glassmorphism, Glow oder schwere Schatten. Die größte strukturelle Maßnahme ist die **Fusion von Dashboard und Legacy-`CommandCenterView`** zu einem kohärenten Erlebnis innerhalb der Shell, ergänzt um klare Rollen für QA-Einstiege (Executive vs. Arbeit vs. Live).

---

## 2. Die 5 wichtigsten Signatur-Merkmale

1. **Calm Power** — souveräne, zurückhaltende Oberfläche mit gezieltem Akzent.  
2. **Layered Control** — Überblick in der Kommandozentrale, Ausführung in Operations, Konfiguration im Control Center, Beweis in QA, Live in Runtime.  
3. **Semantic Honesty** — keine täuschenden Demo-Daten; klare Empty States.  
4. **Spatial clarity** — fünf Layer (0–4) mit nachvollziehbaren Materialregeln.  
5. **Quiet motion** — kurze, optionale Übergänge; Fokus und Selection tragen das Feedback.

---

## 3. Die räumliche Architektur

| Layer | Name | Kurz |
|-------|------|------|
| 0 | App Canvas | Fenster, Docks, TopBar — ruhigster Hintergrund |
| 1 | Workspace Surface | Hauptinhalt des Nav-Bereichs |
| 2 | Functional Panels | Karten, Listen, Editoren |
| 3 | Focus Surfaces | Inspector, Selektion, Detail |
| 4 | Overlay / Modal | Palette, Dialoge, Hilfe |

Details: [docs/design/SIGNATURE_SPATIAL_ARCHITECTURE.md](./docs/design/SIGNATURE_SPATIAL_ARCHITECTURE.md).

---

## 4. Die Zielvision der Kommandozentrale

- **Hero-Zone** mit Projekt-/Laufzeit-Kern + QA-Executive in **einer** prioritären Zeile/Fläche.  
- **Health & Priority** als kompakte Aggregation mit Sprüngen in QA/Betrieb — keine zweite vollständige QA-UI.  
- **Active Work** entweder echter Mini-Feed oder ehrliche Orientierung mit Links.  
- **Drilldowns** aus dem bestehenden `CommandCenterView`-Stack werden **in die Shell** übernommen; Legacy nur noch Wartung/Entfernung.  
- **Quick Actions** als sekundäre Zeile unter der Hero-Zone.

Details: [docs/design/COMMAND_CENTER_VISION.md](./docs/design/COMMAND_CENTER_VISION.md).

---

## 5. Die 10 wichtigsten Modernisierungsmaßnahmen

1. Shell-Kommandozentrale mit vollem Drilldown-Stack (Stufe 1 Modernisierungsplan).  
2. IA + Copy: Rolle von Dashboard vs. QUALITY vs. OBSERVABILITY.  
3. Hero-Hierarchie statt vier gleichwertiger Karten.  
4. CC- und Dashboard-Panels: lokale Hex-Styles → semantische Tokens (Pilot + Rollout).  
5. Inspector: Standard-Empty-State überall.  
6. TopBar: eine Sprache; Status-Aktion semantisch an Dashboard/Hero koppeln.  
7. Platzhalter-Panels durch echte Daten oder ehrliche States ersetzen.  
8. `PREMIUM_INTERACTION_MODEL` für Hover/Focus/Selection vereinheitlichen.  
9. Settings Project/Workspace füllen oder bis dahin Navigationsentscheidung treffen.  
10. Onboarding/Help: Introspection und Kommandozentrale als Differenzierungsstory.

---

## 6. Die größten Risiken

| Risiko | Mitigation |
|--------|------------|
| Regressions in Light/Dark bei Token-Migration | Theme-QA-Checkliste, Pilot-Screens |
| Längere Migrationsphase mit doppelter Navigation | Feature-Flag oder klare Deprecation-Daten für Legacy |
| Überanimation trotz Richtlinie | Code-Review + kurze Dauer caps in Doku |
| Zu viel Text in Hero/Onboarding | Copy-Review gegen Calm Power |
| Qt-Plattform-Unterschiede bei Effekten | Auf Opacity/Border fokussieren, Blur sparsam |

---

## 7. Welche Bereiche zuerst umgebaut werden sollten

1. **Kommandozentrale** (fusion Dashboard + `CommandCenterView`) — höchster Produkt- und IA-Impact.  
2. **QA-Einstiege** (Copy, ggf. Deep-Links) — entlastet Verwirrung sofort.  
3. **Control Center Panels** (Tokenisierung) — sichtbarer „Premium“-Gewinn pro Arbeitsalltag.  
4. **Inspector + Empty States** — günstig, hohe Wahrnehmung von Qualität.  
5. **TopBar** — schnelle semantische und sprachliche Korrektur.

---

## A. Wodurch unterscheidet sich Obsidian Core visuell von typischen Dev-Tools?

Typische Dev-Tools betonen **Rohdaten, dunkle Themes mit hohem Kontrast-Rauschen und viele gleichwertige Panels**. Obsidian Core setzt auf **geschichtete Ruhe**: weniger gleichzeitige Signale, klare **Executive-Ebene** in der Kommandozentrale, **semantische Farbe** statt bunter Deko, und eine **durchdesignierte Shell** (Nav, Inspector, Bottom) statt eines einzelnen „IDE-artigen“ Monsters. Introspection ist **produktiv erklärt**, nicht nur ein Debug-Fenster.

---

## B. Worin liegt das „Wow“, ohne kitschig zu werden?

Das Wow liegt in **Kohärenz und Vertrauen**: alles fühlt sich aus **einem** System an — Abstände, Kanten, Typo, States. Die Kommandozentrale beantwortet **sofort** die Frage „Wo stehe ich?“, und jede Fläche hat eine **klare Rolle**. Nutzer merken **Präzision** (Raster, Tokens, ruhige Hover) und **Tiefe ohne Trick** (Layer statt Schatten-Theater). Kurz: **Premium ist Ordnung + Ehrlichkeit**, nicht Glitzer.

---

## C. Welche 5 Elemente müssen perfekt werden, damit die GUI begehrenswert wirkt?

1. **Kommandozentrale (Hero + Drilldowns)** — das Herzstück.  
2. **Surface-Hierarchie** — keine visuellen Inseln mit Fremd-Hex.  
3. **Inspector** — immer verständlich, nie leer ohne Erklärung.  
4. **Primary Navigation** — klare Bereiche, stressfreie Scanbarkeit.  
5. **Interaktionsgrundlage** — Focus, Selection, Hover konsistent und barrierearm.

---

*Ende SIGNATURE_GUI_DIRECTION_REPORT.md*
