# Unvollständiges / holpriges Markdown

Dieser Absatz ist normal.

```python
def broken_fence():
    return 1
# kein schließendes Fence — Rest ist für den Parser „noch Code“

Nachfolgender Text ohne saubere Struktur.

* Liste ohne Leerzeile davor
- gemischt mit anderem Marker
  eingerückte Zeile

	Text mit Tab am Anfang (Tabs → Spaces in Normalisierung)
    und Spaces

**unclosed bold start
normale Zeile
