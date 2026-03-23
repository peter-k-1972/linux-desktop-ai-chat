# Obsidian Core — Signature GUI Do & Don't

**Zweck:** Schnelle Entscheidungshilfe für Design und Implementierung — ergänzt [UI_GOVERNANCE_RULES.md](./UI_GOVERNANCE_RULES.md).

---

## DO

| Thema | Richtiges Verhalten | Kurzbeispiel |
|-------|---------------------|--------------|
| **Surface-Stufen** | Canvas → Workspace → Karte → eingetauchte Tabelle klar unterscheidbar, alles aus Tokens. | Control Center: eine Kartenhülle, Tabelle ohne zweiten weißen „Schachtel“-Rahmen ohne Regel. |
| **Ruhige Accent-Nutzung** | Akzent für Primäraktion, Links, Fokus — nicht für Dekoration. | Ein „Zu QA“-Button akzentuiert; nicht drei nebeneinander. |
| **Starke Hero-Hierarchie** | Kommandozentrale: erste Zeile trägt Kontext + KPIs; Rest staffelt sich. | Siehe [COMMAND_CENTER_VISION.md](./COMMAND_CENTER_VISION.md). |
| **Ehrliche Empty States** | Kurzer Grund + eine nächste Aktion; kein Schweigen. | Inspector: „Nichts ausgewählt — in der Liste ein Element wählen.“ |
| **Kontextuelle Introspection** | Runtime/Introspection erklärt **was** und **wohin**, nicht nur Rohdaten. | „Aktiver Bereich: Operations / Chat“ mit Link zur Hilfe. |
| **Präzises Spacing** | 4px-Raster, benannte Padding-Stufen. | `PANEL_PADDING` / Card 16 — keine 17 px „weil schön“. |
| **Semantische Farbe** | Rot/Gelb/Grün nur mit Bedeutung (Fehler/Warnung/Erfolg). | Status-Block mit Label „Ollama nicht erreichbar“, nicht nur rote Fläche. |
| **Konsistente Typo-Stufen** | `primaryTitle`, `panelTitle`, `panelMeta` aus etabliertem Muster. | Dashboard-Titel vs. Karten-Titel nicht austauschbar wahllos. |

---

## DON'T

| Thema | Falsches Verhalten | Warum |
|-------|-------------------|--------|
| **Glassmorphism überall** | Milchglas, starke Blur-Unterlagen auf jeder Karte. | Lesbarkeit, Performance, „2021 UI Kit“-Klischee. |
| **Bunte Statusflächen als Deko** | Große grüne/gelbe Flächen ohne semantischen Inhalt. | Wirkt Spielzeug, verwässert echte Warnungen. |
| **Schwere Schatten** | Lange, weiche Drop-Shadows unter jeder Karte. | Widerspricht ruhiger Materialität; Qt-Theming heterogen. |
| **Glow-Ränder** | Leuchtende Rahmen um Panels. | Effektkitsch, A11y-Kontrastprobleme. |
| **Überladene Dashboards** | Zehn gleichwichtige Widgets ohne Priorität. | Keine Kommandozentrale, sondern „alles auf einmal“. |
| **Doppelte semantische Einstiege** | Dieselbe Aufgabe an drei Orten ohne erklärbare Rolle. | Verwirrung (QA in Dashboard, QUALITY, OBSERVABILITY). |
| **Platzhalter als Produkt** | Text „(Platzhalter)“ oder Demo-Zahlen ohne Kennzeichnung. | Bricht Semantic Honesty. |
| **Aggressive Micro-Animationen** | Bounce, elastisches Scroll, pulsierende Icons. | Widerspricht Calm Power / Quiet Confidence. |
| **Gradient-Hintergründe im Arbeitsbereich** | Vollflächige Verläufe hinter Formularen. | Ablenkung; Ausnahme nur Marketing-Splash außerhalb Shell. |
| **Icon-Wildwuchs** | Unterschiedliche Stile gemischt (Outline + Filled + Emoji). | Nutze kanonisches Icon-Set ([ICON_STYLE_GUIDE.md](./ICON_STYLE_GUIDE.md)). |

---

## Grenzfälle

| Situation | Empfehlung |
|-----------|------------|
| **Marketing-Screen** (Website, nicht App) | Andere Regel — nicht mit Shell vermischen. |
| **Dev-only Tools** (Theme Visualizer) | Darf technischer wirken, aber keine anderen Governance-Ausnahmen ohne Kommentar. |
| **Dichte Daten** (große Tabellen) | `compact` Profil; verzichte auf Animation; Fokus auf Scanbarkeit. |

---

*Ende SIGNATURE_GUI_DO_DONT.md*
