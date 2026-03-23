# Obsidian Core — Premium Interaction Model

**Zweck:** Subtiles, ruhiges Interaktionsverhalten — Premium-Feeling durch **Präzision und Rückmeldung**, nicht durch Effekt-Theater.  
**Bezug:** [SIGNATURE_GUI_PRINCIPLES.md](./SIGNATURE_GUI_PRINCIPLES.md) §7, [UI_GOVERNANCE_RULES.md](./UI_GOVERNANCE_RULES.md)

---

## Grundregeln

1. **Dauer:** Standard-Übergänge **150–250 ms**; niemals > **300 ms** für UI-Chrome (außer dokumentierte Ausnahme).  
2. **Easing:** Linear oder leichtes `ease-out`; kein `ease-in-out` mit langer Mittelphase für große Flächen.  
3. **Reduktion:** Wenn unsicher, **keine** Animation — statisches Feedback (Farbe, Border, Icon) reicht.  
4. **Barrierefreiheit:** Fokus ist **immer** sichtbar; Animationen respektieren `prefers-reduced-motion` (Qt: wo unterstützt, sonst kurze Dauer).

---

## Hover

| Kontext | Verhalten |
|---------|-----------|
| **Klickbare Liste / Sidebar** | Hintergrund minimal aufhellen/absenken (Hover-Surface-Token); Cursor Pointer. |
| **Icon-Only-Buttons** | Tooltip verpflichtend; Hover = leichte Hintergrundfläche oder Icon-Tint — **kein** Scale > 1,05. |
| **Tabellenzeilen** | Zeilen-Hover dezent; unterscheidbar von **Selection**. |

**Don't:** Glow, Schlagschatten-Verstärkung, Bounce.

---

## Focus

| Kontext | Verhalten |
|---------|-----------|
| **Tastatur-Fokus** | Sichtbarer Ring (Focus-Token), mindestens 2px, nicht nur Farbwechsel. |
| **Maus-Fokus** | Gleicher Ring optional bei Klick-Inhalt; in dichten Grids Ring bevorzugen. |

**Don't:** `outline: none` ohne Ersatz.

---

## Selection

| Kontext | Verhalten |
|---------|-----------|
| **Einzelwahl** | Selection-Background + ggf. dezente linke Akzentlinie für Listen. |
| **Multi-Selection** | Gleiche Familie, visuell erkennbar angehäuft. |
| **Wechsel** | Inhalt im Inspector aktualisiert sich **ohne** Blinken; optional 120 ms Cross-Fade für Text. |

**Don't:** Selection-Farbe mit hoher Sättigung auf großen Flächen.

---

## Expand / Collapse

| Kontext | Verhalten |
|---------|-----------|
| **Sidebar-Sektionen** | Pfeil dreht oder wechselt; Höhe **sofort** oder max. 200 ms — kein „elastic“. |
| **Akkordeon in Forms** | Ein Panel offen pro Gruppe, wenn IA das verlangt; sonst unabhängig. |

**Don't:** Stagger-Animation über viele Kinder.

---

## Inspector-Übergänge

| Szenario | Verhalten |
|----------|-----------|
| **Neue Selection** | Optional: kurzer Fade (Opacity 0,85 → 1) oder Content-Swap ohne Animation. |
| **Fehler beim Laden** | Inline-Status im Inspector, kein Toast-Spam. |

**Don't:** Slide-in aus dem Rand für jeden Wechsel.

---

## Panel-Emphasis

| Szenario | Verhalten |
|----------|-----------|
| **Warnung im Panel** | Semantische Border links oder dezentes Banner-Token — **kein** pulsierendes Rot. |
| **„Neu“ oder Hinweis** | Ein Badge-Token oder Text; keine Animation. |

---

## Modal / Overlay-Öffnung

| Szenario | Verhalten |
|----------|-----------|
| **Dialog** | Backdrop erscheint in ≤ 150 ms; Dialog skaliert **nicht** von 0 — optional Opacity 0 → 1. |
| **Command Palette** | Zentriert einblenden; Fokus in Eingabefeld; Escape schließt. |

**Don't:** Bounce-Einstieg, starke Blur-Stacks (Performance + Kitsch-Risiko).

---

## Loading / Progress

| Szenario | Verhalten |
|----------|-----------|
| **Unbekannte Dauer** | Indeterminierte Progressbar oder dezenter Spinner **im Kontext** (Karte/Button), nicht Vollbild. |
| **Bekannte Dauer** | Deterministische Bar; Prozent optional. |
| **Chat-Streaming** | Bereits etabliertes Placeholder-Bubble-Pattern beibehallen — technisch, nicht „Deko“. |

**Don't:** Vollflächen-Loading-Overlays für Mikroaktionen.

---

## Zusammenfassung

| Interaktion | Premium = |
|-------------|-----------|
| Hover | subtil, lesbar |
| Focus | verlässlich |
| Selection | klar, ruhig |
| Motion | kurz oder absent |
| Loading | kontextuell, ehrlich |

---

*Ende PREMIUM_INTERACTION_MODEL.md*
