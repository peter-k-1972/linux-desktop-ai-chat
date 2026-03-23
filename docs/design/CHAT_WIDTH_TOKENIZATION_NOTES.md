# Chat-Breite — Tokenisierung / IST-Analyse (Phase 1)

## Aktuelle Quelle (vor bzw. bei Auftrennung)

| Pfad | Quelle |
|------|--------|
| Python (`conversation_view.py`, `chat_composer_widget.py`) | `design_metrics.CHAT_CONTENT_MAX_WIDTH_PX` |
| Legacy-QSS (`app/resources/styles.py`) | **Zweite Quelle:** Literal `max-width: 800px` in zwei Theme-Strings |

**Hinweis:** Der Shell-/Workbench-Pfad (`app/gui/themes/loader.py` + `assets/themes/base/*.qss`) enthält **kein** `#chatContainer` — nur der Legacy-Einstieg (`app/main.py` → `get_stylesheet`) nutzt `styles.py`.

## Zielquelle

Eine kanonische Definition: **`design_metrics.CHAT_CONTENT_MAX_WIDTH_PX`**.

## Technische Integrationsstrategie

- **Kein** neues Token in Theme-JSON und **kein** `{{chat_content_max_width_px}}` in `styles.py`, weil diese Datei **nicht** durch `loader._substitute_tokens` läuft, sondern als Python **f-String-Generator** existiert.
- Stattdessen: **`from app.gui.theme import design_metrics as _dm`** und Interpolation `max-width: {_dm.CHAT_CONTENT_MAX_WIDTH_PX}px` in beiden Stylesheet-Funktionen.
- Damit lesen Python-Layouts und das erzeugte QSS denselben Wert zur Laufzeit — ohne zweite Konstante und ohne Magic Number in `styles.py`.

**Alternative (nicht gewählt):** Platzhalter in extrahierter `.qss`-Datei + Aufnahme in `load_stylesheet` — würde `main.py`/Legacy-Pfad auf ThemeManager umstellen oder eine dritte Kombinationslogik erfordern (größerer Eingriff).

## Risiken

- **Importzyklus:** `design_metrics` importiert nicht `styles.py` — unkritisch.
- **Workbench vs. Legacy:** Nutzer, die nur ThemeManager-QSS laden, sehen weiterhin kein `#chatContainer`-Rule aus dieser Datei (unverändert).
- **Zukünftige Verschiebung nach Theme-Tokens:** Wenn `styles.py` später in reine QSS + Loader migriert wird, kann derselbe Wert als Token aus `get_tokens_dict()` kommen; bis dahin bleibt `design_metrics` die Single Source of Truth.
