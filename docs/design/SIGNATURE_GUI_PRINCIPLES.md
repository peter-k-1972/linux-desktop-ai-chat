# Obsidian Core — Signature GUI Principles

**Status:** Zielmodell (Design-System- und Architektur-Leitlinie)  
**Geltung:** Ergänzt [UI_GOVERNANCE_RULES.md](./UI_GOVERNANCE_RULES.md); bei Konflikt zuerst Governance-Tokens, dann diese Prinzipien für Semantik und Priorität.  
**Bezug:** [GUI_COMPLETE_REVIEW_REPORT.md](../../GUI_COMPLETE_REVIEW_REPORT.md), [SIGNATURE_SPATIAL_ARCHITECTURE.md](./SIGNATURE_SPATIAL_ARCHITECTURE.md)

---

## 1. Calm Power (Ruhe mit Autorität)

| Aspekt | Inhalt |
|--------|--------|
| **Bedeutung** | Die Oberfläche wirkt souverän und belastbar, nicht laut oder „demo-haft“. Dichte und Kontrast sind kontrolliert; wichtige Signale haben Raum. |
| **Praktische Auswirkung** | Begrenzte Akzentfläche; viel neutrale Fläche; Typografie und Raster tragen die Hierarchie. Keine konkurrierenden „Highlight-Bänder“ in einem Screen. |
| **Verbotene Gegenmuster** | Neon-Akzente, Rainbow-Status, viele gleich starke Farbflächen, aggressive Gradient-Hintergründe im Arbeitsbereich. |

---

## 2. Semantic Honesty (Semantische Ehrlichkeit)

| Aspekt | Inhalt |
|--------|--------|
| **Bedeutung** | Was die GUI zeigt, entspricht dem, was das System weiß oder explizit als „nicht verfügbar“ kennzeichnet. Keine Demo-Daten, die wie Live-Daten aussehen. |
| **Praktische Auswirkung** | Empty States mit Erklärung und nächstem Schritt; keine Strings „(Platzhalter)“ in produktiven Pfaden; Loading/Fehlerzustände klar getrennt. |
| **Verbotene Gegenmuster** | Statische Tabellen mit erfundenen Zeilen; grüne „Healthy“-Labels ohne Messung; verschweigene CLI-only-Pfade für Kernaufgaben. |

---

## 3. Layered Control (Geschichtete Kontrolle)

| Aspekt | Inhalt |
|--------|--------|
| **Bedeutung** | Steuerung ist in Ebenen organisiert: Überblick → Arbeitsfläche → Detail/Inspector → tiefe Drilldowns. Nutzer steigen bewusst ab, statt alles gleichwertig zu sehen. |
| **Praktische Auswirkung** | Kommandozentrale liefert Executive-Level; Operations führt Handlung aus; Control Center konfiguriert Systembausteine; QA/Runtime vertiefen Beweis und Telemetrie — mit klaren Rollen (siehe [COMMAND_CENTER_VISION.md](./COMMAND_CENTER_VISION.md)). |
| **Verbotene Gegenmuster** | Vier gleichwertige Dashboard-Kacheln ohne Held; dieselbe Information an drei Stellen ohne erklärbare Rolle; Inspector als zweiter Hauptscreen ohne Kontext. |

---

## 4. Operational Depth (Operative Tiefe)

| Aspekt | Inhalt |
|--------|--------|
| **Bedeutung** | Das Produkt ist ein **Operations-Desktop**: Projekte, Läufe, Qualität und Laufzeit sind erste Bürger, nicht versteckte Admin-Panels. |
| **Praktische Auswirkung** | Schnellzugriffe von der Kommandozentrale auf „was läuft / was blockiert / was als Nächstes“; konsistente Sprungpunkte in QA und Betrieb. |
| **Verbotene Gegenmuster** | Reiner „Chat-only“-Eindruck trotz vorhandener Governance-Features; tiefe Funktionen nur über Legacy-Pfade oder CLI. |

---

## 5. Precision (Präzision)

| Aspekt | Inhalt |
|--------|--------|
| **Bedeutung** | Ausrichtung, Abstände, Beschriftungen und Zustände folgen einem messbaren System — nicht dem Bauchgefühl einzelner Screens. |
| **Praktische Auswirkung** | 4px-Raster, definierte Panel-Paddings, semantische Farbrollen aus Tokens; einheitliche Header-Profile für gleiche Komponentenklassen ([LAYOUT_SYSTEM_RULES.md](./LAYOUT_SYSTEM_RULES.md)). |
| **Verbotene Gegenmuster** | Lokale Hex- und Pixel-Sonderfälle für dieselbe Komponentenrolle; inkonsistente Begriffe für dasselbe Objekt in Sidebar vs. Inspector. |

---

## 6. Introspection (Durchschaubarkeit)

| Aspekt | Inhalt |
|--------|--------|
| **Bedeutung** | Das System kann **transparent** machen, wo es steht: Navigation, Kontext, Dienste, jüngste Ereignisse — als Produktwert, nicht nur als Debug-Grabbelkiste. |
| **Praktische Auswirkung** | Runtime/Introspection als klar benannter Bereich; Breadcrumbs und Hilfe-Kontext; optionale „Was passiert gerade?“-Spur in der Kommandozentrale (aggregiert, nicht Roh-Log). |
| **Verbotene Gegenmuster** | Undokumentierte versteckte Modus-Tasten; nur Englisch in kritischen Erklärpanels bei sonst deutscher UI; technische IDs ohne menschliches Label. |

---

## 7. Quiet Confidence in Motion (Ruhige Interaktion)

| Aspekt | Inhalt |
|--------|--------|
| **Bedeutung** | Bewegung und Feedback bestätigen Handlung, unterhalten aber nicht. |
| **Praktische Auswirkung** | Kurze, dezente Übergänge (150–250 ms) wo sinnvoll; Fokus-Ringe sichtbar; Hover nur zur Bestätigung von Klickflächen ([PREMIUM_INTERACTION_MODEL.md](./PREMIUM_INTERACTION_MODEL.md)). |
| **Verbotene Gegenmuster** | Bounce, starke Parallax, Glow-Pulse, lange animierte Hero-Loops im Arbeits-UI. |

---

## 8. Single Command Surface Story (Eine Kommandozentrale-Erzählung)

| Aspekt | Inhalt |
|--------|--------|
| **Bedeutung** | Es gibt **eine** verstandene „Kommandozentrale“ im Standardprodukt: executive Überblick plus erreichbare Tiefe — keine parallele Wahrheit zwischen Shell und Legacy. |
| **Praktische Auswirkung** | `CommandCenterView`-Drilldowns und `DashboardScreen` fusionieren zu einem kohärenten Erlebnis (ein Host, eine Navigationstiefe); Legacy nur noch Wartung oder entfernt. |
| **Verbotene Gegenmuster** | Zwei verschiedene „Kommandozentrale“-Implementierungen für Endnutzer; Hinweistexte, die auf UI verweisen, die im Standardpfad nicht existiert. |

---

*Ende SIGNATURE_GUI_PRINCIPLES.md*
