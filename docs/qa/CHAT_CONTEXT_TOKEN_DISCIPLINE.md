# Chat-Kontext – Token-Disziplin

**Stand:** 2026-03-17  
**Ziel:** Kontext strukturell sparsam halten. Nicht durch Intelligenz, sondern durch klare Regeln.

---

## 1. Warum keine echte Tokenmessung?

- **Modellabhängig:** Verschiedene Modelle tokenisieren unterschiedlich.
- **Aktuell unnötig:** Für den Vergleich von Kontextvarianten reicht zunächst ein einfacher Maßstab.
- **Strukturvergleich reicht zunächst:** chars, lines, nonempty_lines ermöglichen grobe Vergleiche ohne externe Abhängigkeiten.

---

## 2. Welche Strukturmetriken werden genutzt?

| Metrik | Bedeutung |
|--------|------------|
| **chars** | Zeichenanzahl des Kontext-Fragments |
| **lines** | Anzahl Zeilen (inkl. Leerzeilen) |
| **nonempty_lines** | Anzahl nicht-leerer Zeilen |

Implementierung: `app.chat.context.get_context_fragment_stats(fragment)`.

---

## 3. Ziel

- Kontextvarianten gegeneinander grob vergleichbar machen
- Offensichtliche Prompt-Aufblähung sichtbar machen

---

## 4. Regel

Ein neuer Kontextmodus oder Detailgrad soll keine unnötige Längenexplosion erzeugen.
