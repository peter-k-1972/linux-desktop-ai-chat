# User vs. Assistant – Renderpfad-Vergleich

**Stand:** 2026-03-17  
**Ziel:** 1:1-Vergleich der Renderpfade; User wächst korrekt, Assistant nicht.

---

## 1. Widget-Klasse

| Aspekt | User | Assistant | Unterschied |
|--------|------|-----------|-------------|
| Klasse | `ChatMessageBubbleWidget` | `ChatMessageBubbleWidget` | **Keiner** |
| role | `"user"` | `"assistant"` | Nur Styling (Farbe) |

**Fazit:** Dieselbe Klasse, kein Unterschied.

---

## 2. SizePolicy

| Widget | User | Assistant |
|--------|------|-----------|
| Bubble (QFrame) | `Expanding, Minimum` | `Expanding, Minimum` |
| _content (QTextEdit) | `Expanding, Minimum` | `Expanding, Minimum` |
| role_label | (default) | (default) |
| _status_badge | (default) | (default) |

**Fazit:** Identisch.

---

## 3. setFixedHeight / setMaximumHeight

| Ort | User | Assistant |
|-----|------|-----------|
| Bubble | Keine | Keine |
| _content | Keine | Keine |

**Fazit:** Keine festen Höhen.

---

## 4. wordWrap

| Widget | User | Assistant |
|--------|------|-----------|
| _content | `WrapAtWordBoundaryOrAnywhere` | Gleich |
| _status_badge | `setWordWrap(True)` | Gleich |

**Fazit:** Identisch.

---

## 5. adjustSize / updateGeometry nach Textänderung

| Pfad | User | Assistant |
|------|------|-----------|
| Erstellung | `_add_message("user", text)` → Bubble mit vollem Text | `add_assistant_placeholder()` → Bubble mit `"..."` |
| Text setzen | Einmalig in `_setup_ui` via `_content.setPlainText(text)` | Einmalig `"..."`, dann `set_content(text)` |
| updateGeometry | `_content.setPlainText` → `updateGeometry()` (in _MessageContentEdit) | Gleich |
| Bubble updateGeometry | Nicht nötig (kein nachträglicher Update) | `set_content` → `bubble.updateGeometry()` |

**Kritischer Unterschied:**  
- **User:** Bubble wird mit **vollem Text** erstellt und einmal layoutet.  
- **Assistant:** Bubble wird mit **"..."** erstellt, layoutet, dann **nachträglich** per `set_content` aktualisiert.

---

## 6. Parent-Layout / Bubble-Container

| Aspekt | User | Assistant |
|--------|------|-----------|
| Einfügen | `insertWidget(count-1, bubble)` | `insertWidget(count-1, bubble)` |
| Layout | `_content_layout` (QVBoxLayout) | Gleich |
| Position | Vor `addStretch()` | Gleich |
| `_last_assistant_bubble` | Nicht gesetzt | Gesetzt bei Placeholder |

**Fazit:** Gleicher Parent, gleiche Einfügeposition.

---

## 7. Ablauf-Unterschied (Kern)

```
USER:
  _add_message("user", "langer Text")
    → ChatMessageBubbleWidget("user", "langer Text")
    → _setup_ui: _content.setPlainText("langer Text")
    → insertWidget
    → Layout läuft: Bubble hat vollen Text, sizeHint korrekt

ASSISTANT (Streaming/Load):
  add_assistant_placeholder() ODER _add_message("assistant", text)
  
  Fall A – Placeholder:
    → ChatMessageBubbleWidget("assistant", "...")
    → _setup_ui: _content.setPlainText("...")
    → insertWidget
    → Layout läuft: Bubble klein
    → update_last_assistant("langer Text")
    → set_content("langer Text")
    → _content.setPlainText("langer Text") + updateGeometry()
    → bubble.updateGeometry()
    → Layout soll neu laufen – hier kann es haken

  Fall B – _add_message (z.B. load_messages):
    → ChatMessageBubbleWidget("assistant", "langer Text")
    → identisch zu User – sollte funktionieren
```

---

## 8. Mögliche Ursache

**Hypothese:** Beim Assistant-Placeholder-Pfad wird `updateGeometry()` aufgerufen, aber das **Parent-Layout** (_content_layout) oder der **Scroll-Content** (_content) wird nicht zu einer Neuberechnung gezwungen.

- `bubble.updateGeometry()` markiert die Bubble als geändert.
- Das Layout von `_content` könnte die Änderung nicht zuverlässig weiterreichen.
- Der Scroll-Bereich könnte die neue Größe des Contents ignorieren.

**Vorschlag:** Nach `set_content` zusätzlich das Parent-Layout invalidieren bzw. den Content-Widget des Scroll-Bereichs aktualisieren.
